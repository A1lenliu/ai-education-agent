from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

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

class ReActAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.conversation_history: List[Dict[str, str]] = []  # 修改为字典列表
        self.tools_info: Dict[str, Any] = {}
        logger.info("ReActAgent 初始化完成")
        
    def add_tool(self, name: str, description: str, parameters: Dict[str, Any]):
        """添加工具到智能体的工具集中"""
        self.tools_info[name] = {
            "description": description,
            "parameters": parameters
        }
        logger.info(f"添加工具: {name}")
    
    def _format_prompt(self) -> str:
        """格式化提示词，包含历史对话和工具信息"""
        prompt = "你是一个遵循ReAct范式的AI助手。请按照以下格式回复:\n\n"
        
        # 添加历史对话
        for msg in self.conversation_history:
            prompt += f"{msg['role']}: {msg['content']}\n"
        
        # 添加工具信息
        prompt += "\n可用工具:\n"
        for name, tool in self.tools_info.items():
            prompt += f"- {name}: {tool['description']}\n"
            prompt += f"  参数: {tool['parameters']}\n"
        
        prompt += "\n请按照以下格式回复:\n"
        prompt += "Thought: 思考过程\n"
        prompt += "Action: 要使用的工具名称\n"
        prompt += "Action Input: 工具参数\n"
        prompt += "Observation: 工具执行结果\n"
        prompt += "Answer: 最终答案\n"
        
        logger.debug(f"生成的提示词: {prompt}")
        return prompt
    
    def _parse_llm_response(self, response: str) -> Action:
        """解析LLM的响应，提取下一步行动"""
        logger.debug(f"解析LLM响应: {response}")
        lines = response.strip().split('\n')
        
        # 首先检查是否有 Answer
        for line in lines:
            if line.startswith("Answer:"):
                logger.info("检测到 Answer 类型响应")
                return Action(ActionType.ANSWER, line[7:].strip())
        
        # 如果没有 Answer，检查其他类型
        current_action = None
        for line in lines:
            if line.startswith("Thought:"):
                logger.info("检测到 Thought 类型响应")
                current_action = Action(ActionType.THOUGHT, line[8:].strip())
            elif line.startswith("Action:"):
                logger.info("检测到 Action 类型响应")
                current_action = Action(ActionType.ACTION, "", tool_name=line[7:].strip())
            elif line.startswith("Action Input:"):
                logger.info("检测到 Action Input 类型响应")
                if current_action and current_action.type == ActionType.ACTION:
                    current_action.tool_args = eval(line[12:].strip())
            elif line.startswith("Observation:"):
                logger.info("检测到 Observation 类型响应")
                current_action = Action(ActionType.OBSERVATION, line[11:].strip())
        
        if current_action:
            return current_action
            
        logger.error(f"无法解析LLM响应: {response}")
        raise ValueError("无法解析LLM响应")
    
    async def run(self, query: str) -> str:
        """运行智能体处理查询"""
        logger.info(f"开始处理查询: {query}")
        self.conversation_history = []  # 清空历史记录
        self.conversation_history.append({"role": "user", "content": query})
        
        max_iterations = 10  # 设置最大迭代次数
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"开始第 {iteration} 次迭代")
            
            # 获取LLM响应
            logger.info("获取LLM响应...")
            response = await self.llm_client.generate(self._format_prompt())
            logger.info(f"收到LLM响应: {response}")
            
            # 解析响应
            action = self._parse_llm_response(response)
            logger.info(f"解析得到动作: {action.type}")
            
            # 处理动作
            if action.type == ActionType.ANSWER:
                logger.info("收到最终答案，结束处理")
                self.conversation_history.append({"role": "assistant", "content": action.content})
                return action.content
            elif action.type == ActionType.THOUGHT:
                logger.info(f"思考: {action.content}")
                self.conversation_history.append({"role": "assistant", "content": f"Thought: {action.content}"})
            elif action.type == ActionType.ACTION:
                logger.info(f"执行动作: {action.tool_name}")
                if action.tool_name not in self.tools_info:
                    logger.error(f"未知的工具: {action.tool_name}")
                    raise ValueError(f"未知的工具: {action.tool_name}")
                
                result = await self._execute_tool(action.tool_name, action.tool_args)
                logger.info(f"工具执行结果: {result}")
                
                self.conversation_history.append({
                    "role": "assistant",
                    "content": f"Action: {action.tool_name}\nAction Input: {action.tool_args}\nObservation: {result}"
                })
            elif action.type == ActionType.OBSERVATION:
                logger.info(f"观察: {action.content}")
                self.conversation_history.append({"role": "assistant", "content": f"Observation: {action.content}"})
        
        logger.warning("达到最大迭代次数，返回最后一个响应")
        return self.conversation_history[-1]["content"]
    
    async def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """执行工具调用"""
        if tool_name not in self.tools_info:
            logger.error(f"未知的工具: {tool_name}")
            raise ValueError(f"未知的工具: {tool_name}")
        
        logger.info(f"执行工具 {tool_name}，参数: {tool_args}")
        
        # 根据工具名称执行相应的操作
        if tool_name == "read_file":
            try:
                with open(tool_args["file_path"], 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"文件内容: {content}"
            except Exception as e:
                return f"读取文件时出错: {str(e)}"
                
        elif tool_name == "search_files":
            try:
                import glob
                import os
                files = glob.glob(os.path.join(tool_args["directory"], tool_args["pattern"]))
                return f"找到的文件: {files}"
            except Exception as e:
                return f"搜索文件时出错: {str(e)}"
                
        elif tool_name == "analyze_code":
            try:
                with open(tool_args["file_path"], 'r', encoding='utf-8') as f:
                    content = f.read()
                return f"文件分析结果:\n- 总行数: {len(content.splitlines())}\n- 文件大小: {len(content)} 字节"
            except Exception as e:
                return f"分析代码时出错: {str(e)}"
        
        return f"工具 {tool_name} 的执行结果" 