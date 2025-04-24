from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
import random
import string
from datetime import datetime
import json

# 设置日志
logger = logging.getLogger(__name__)

class ActionType(Enum):
    THOUGHT = "Thought"
    ACTION = "Action"
    OBSERVATION = "Observation"
    ANSWER = "Answer"

@dataclass
class Action:
    type: ActionType
    content: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None

class ReActAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.conversation_history: List[Dict[str, str]] = []
        self.tools_info: Dict[str, Any] = {}
        self.current_goal: Optional[str] = None
        self.current_context: Dict[str, Any] = {}
        self.tool_results: List[Dict[str, Any]] = []
        self.max_iterations = 5  # 增加最大迭代次数到5次
        self.current_iteration = 0
        logger.info("ReActAgent 初始化完成")
    
    def _generate_tool_call_id(self) -> str:
        """生成随机的工具调用ID"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    def _format_system_prompt(self) -> str:
        """生成系统提示"""
        current_date = datetime.now().strftime("%Y-%m-%d")
        prompt = f"""You are an AI assistant following the ReAct framework. Today is {current_date}.

You must strictly respond in the following format, even if you already know the answer:

1. First, you must think:
Thought: Analyze the current situation and decide the next action

2. Then, you must take action:
Action: tool_name
Action Input: tool parameters (in JSON format)

3. Next, you must observe the result:
Observation: result of the tool execution

4. Finally, you can give the answer:
Answer: your final answer

Important rules:
- You must follow the order described above
- Each stage must include the corresponding prefix (Thought:, Action:, Observation:, Answer:)
- Even if you already know the answer, you must go through the thinking, action, and observation steps
- If you encounter an error, use the Error: prefix
- Never skip any steps to give the answer directly
- The content of each step must be clear and not contain content from other steps
- Thought content must include the "Thought:" prefix
- Action content must include "Action:" and "Action Input:" prefixes
- Observation content must include the "Observation:" prefix
- Answer content must include the "Answer:" prefix
- All responses must be in English, regardless of the language of the user's query

Available tools:
{self._format_tools_info()}

Example:
User: Find all Python files
Assistant:
Thought: I need to search for all Python files in the project
Action: search_files
Action Input: {{"pattern": "*.py"}}
Observation: Found the following Python files: ['file1.py', 'file2.py']
Answer: I found 2 Python files: file1.py and file2.py
"""
        return prompt
    
    def _format_tools_info(self) -> str:
        """格式化工具信息"""
        tools_info = []
        for name, tool in self.tools_info.items():
            tools_info.append(f"- {name}: {tool['description']}")
            tools_info.append(f"  参数: {tool['parameters']}")
        return "\n".join(tools_info)
    
    def _format_prompt(self) -> str:
        """格式化完整的提示词"""
        prompt = self._format_system_prompt() + "\n\n"
        
        # 添加当前目标
        if self.current_goal:
            prompt += f"当前目标: {self.current_goal}\n\n"
        
        # 添加历史对话
        prompt += "历史对话:\n"
        for msg in self.conversation_history:
            if msg["role"] == "tool":
                prompt += f"Tool ({msg.get('tool_call_id', 'unknown')}): {msg['content']}\n"
            else:
                prompt += f"{msg['role']}: {msg['content']}\n"
        
        # 添加工具结果
        if self.tool_results:
            prompt += "\n工具执行结果:\n"
            for result in self.tool_results:
                prompt += f"- 工具: {result['tool']}\n"
                prompt += f"  参数: {result['parameters']}\n"
                prompt += f"  结果: {result['result']}\n"
        
        return prompt
    
    async def execute(self, query: str) -> Dict[str, Any]:
        """执行入口方法"""
        logger.info(f"开始处理查询: {query}")
        self.current_iteration = 0
        self.conversation_history = []
        self.tool_results = []
        self.current_goal = query
        
        # 添加用户消息
        self.conversation_history.append({
            "role": "user",
            "content": query
        })
        
        # 开始 ReAct 循环
        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            logger.info(f"开始第 {self.current_iteration} 次迭代")
            
            # 思考阶段
            response = await self.think()
            if not response:
                break
            
            # 决策阶段
            should_continue = await self.decide(response)
            if not should_continue:
                break
        
        # 返回结果
        return {
            "response": response,  # 直接返回 LLM 的原始响应
            "history": self.conversation_history,
            "tool_results": self.tool_results
        }
    
    async def think(self) -> Optional[str]:
        """思考阶段"""
        try:
            # 获取 LLM 响应
            response = await self.llm_client.generate(self._format_prompt())
            logger.info(f"LLM 响应:\n{response}")  # 添加日志记录
            
            # 检查是否包含最终答案
            if "Answer:" in response:
                # 提取答案之前的所有内容
                parts = response.split("Answer:")
                if len(parts) > 1:
                    # 处理答案之前的内容
                    pre_answer = parts[0].strip()
                    
                    # 按照顺序处理每个部分
                    current_content = pre_answer
                    
                    # 处理所有思考、行动和观察步骤
                    while current_content:
                        # 1. 处理思考部分
                        if "Thought:" in current_content:
                            thought_parts = current_content.split("Thought:")
                            thought_content = thought_parts[1].split("Action:")[0].strip()
                            # 添加思考消息到对话历史
                            self.conversation_history.append({
                                "role": "assistant",
                                "content": f"Thought: {thought_content}",
                                "type": "thought"
                            })
                            logger.info(f"Thought: {thought_content}")  # 添加日志记录
                            current_content = thought_parts[1].split("Action:")[1] if len(thought_parts[1].split("Action:")) > 1 else ""
                        
                        # 2. 处理动作部分
                        if "Action:" in current_content and "Action Input:" in current_content:
                            action_parts = current_content.split("Action:")
                            action_input_parts = action_parts[1].split("Action Input:")
                            
                            tool_name = action_input_parts[0].strip()
                            tool_args = action_input_parts[1].split("Observation:")[0].strip()
                            
                            # 添加动作消息到对话历史
                            action_content = f"Action: {tool_name}\nAction Input: {tool_args}"
                            self.conversation_history.append({
                                "role": "assistant",
                                "content": action_content,
                                "type": "action"
                            })
                            logger.info(f"Action: {tool_name}\nAction Input: {tool_args}")  # 添加日志记录
                            
                            # 执行工具
                            await self.act(tool_name, tool_args)
                            current_content = action_input_parts[1].split("Observation:")[1] if len(action_input_parts[1].split("Observation:")) > 1 else ""
                        
                        # 3. 处理观察部分
                        if "Observation:" in current_content:
                            observation_content = current_content.split("Observation:")[1].split("Thought:")[0].strip()
                            # 添加观察消息到对话历史
                            self.conversation_history.append({
                                "role": "assistant",
                                "content": f"Observation: {observation_content}",
                                "type": "observation"
                            })
                            logger.info(f"Observation: {observation_content}")  # 添加日志记录
                            current_content = current_content.split("Observation:")[1].split("Thought:")[1] if len(current_content.split("Observation:")[1].split("Thought:")) > 1 else ""
                        
                        # 如果没有更多内容，退出循环
                        if not current_content or not any(x in current_content for x in ["Thought:", "Action:", "Observation:"]):
                            break
                    
                    # 4. 最后添加答案
                    answer = parts[1].strip()
                    # 添加答案消息到对话历史
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": f"Answer: {answer}",
                        "type": "answer"
                    })
                    logger.info(f"Answer: {answer}")  # 添加日志记录
                    return response  # 返回完整的 LLM 响应
            
            # 如果没有找到答案，继续思考
            return response
        except Exception as e:
            logger.error(f"思考阶段出错: {str(e)}")
            self.conversation_history.append({
                "role": "assistant",
                "content": str(e),
                "type": "error"
            })
            return None
    
    async def decide(self, response: str) -> bool:
        """决策阶段"""
        try:
            # 检查是否有最终答案
            if "Answer:" in response:
                answer = response.split("Answer:")[-1].strip()
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"Answer: {answer}",  # 保留前缀
                    "type": "answer"
                })
                return False
            
            # 如果没有答案，继续思考
            return True
        except Exception as e:
            logger.error(f"决策阶段出错: {str(e)}")
            self.conversation_history.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "type": "error"
            })
            return False
    
    async def act(self, tool_name: str, tool_args: str) -> None:
        """行动阶段"""
        try:
            if tool_name not in self.tools_info:
                raise ValueError(f"未知的工具: {tool_name}")
            
            # 生成工具调用ID
            tool_call_id = self._generate_tool_call_id()
            
            # 执行工具
            tool_result = await self._execute_tool(tool_name, tool_args)
            
            # 添加工具执行结果到对话历史
            self.conversation_history.append({
                "role": "assistant",
                "content": f"Observation: {tool_result}",
                "type": "observation"
            })
            
            # 更新工具结果
            self.tool_results.append({
                "tool": tool_name,
                "parameters": tool_args,
                "result": tool_result
            })
        except Exception as e:
            logger.error(f"行动阶段出错: {str(e)}")
            self.conversation_history.append({
                "role": "assistant",
                "content": str(e),
                "type": "error"
            })
    
    async def _execute_tool(self, tool_name: str, tool_args: str) -> Any:
        """执行工具调用"""
        try:
            # 解析工具参数
            if isinstance(tool_args, str):
                try:
                    # 清理和规范化 JSON 字符串
                    tool_args = tool_args.strip()
                    # 如果参数是单行字符串，尝试直接解析
                    if tool_args.startswith('{') and tool_args.endswith('}'):
                        tool_args = json.loads(tool_args)
                    else:
                        # 如果是多行字符串，尝试提取 JSON 部分
                        import re
                        json_match = re.search(r'\{.*\}', tool_args, re.DOTALL)
                        if json_match:
                            tool_args = json.loads(json_match.group())
                        else:
                            raise ValueError("无法从输入中提取有效的 JSON 数据")
                except json.JSONDecodeError as e:
                    logger.error(f"解析工具参数失败: {str(e)}")
                    raise ValueError(f"工具参数格式错误: {str(e)}")
            
            # 执行工具
            return await self.tools_info[tool_name]["handler"](**tool_args)
        except Exception as e:
            raise ValueError(f"执行工具 {tool_name} 时出错: {str(e)}")
    
    def add_tool(self, name: str, description: str, parameters: Dict[str, Any], handler):
        """添加工具到智能体的工具集中"""
        self.tools_info[name] = {
            "description": description,
            "parameters": parameters,
            "handler": handler
        }
        logger.info(f"添加工具: {name}") 