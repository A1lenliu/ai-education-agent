import os
import json
import aiohttp
import asyncio
import ssl
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class DeepSeekLLMClient:
    def __init__(self, api_key: Optional[str] = None, verify_ssl: bool = False):
        """初始化DeepSeek LLM客户端
        
        Args:
            api_key: DeepSeek API密钥，如果不提供则从环境变量获取
            verify_ssl: 是否验证SSL证书
        """
        self.api_key = api_key or "sk-3b20bd773e754d5889566ff5455a93ce"
        if not self.api_key:
            raise ValueError("未提供DeepSeek API密钥，请通过参数传入或设置DEEPSEEK_API_KEY环境变量")
        
        self.api_base = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"  # 使用正确的模型名称
        self.verify_ssl = verify_ssl
        self.timeout = 60  # 增加超时时间到60秒
        logger.info(f"DeepSeek LLM客户端初始化完成，API基础URL: {self.api_base}")
        
    async def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        """生成文本响应
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成token数
            
        Returns:
            str: 生成的文本响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个遵循 ReAct 范式的 AI 助手。你必须严格按照以下格式回复，即使你已经知道答案：

1. 首先必须进行思考：
Thought: 分析当前情况并决定下一步行动

2. 然后必须执行行动：
Action: 工具名称
Action Input: 工具参数（JSON格式）

3. 接着必须观察结果：
Observation: 工具执行结果

4. 最后才能给出答案：
Answer: 最终答案

重要规则：
- 必须按照上述顺序生成消息
- 每个阶段都必须包含对应的前缀（Thought:、Action:、Observation:、Answer:）
- 即使已经知道答案，也必须先执行思考、行动和观察步骤
- 如果遇到错误，使用 Error: 前缀
- 禁止跳过任何步骤直接给出答案
- 每个步骤的内容必须清晰明确，不要包含其他步骤的内容
- 思考内容必须包含 "Thought:" 前缀
- 动作内容必须包含 "Action:" 和 "Action Input:" 前缀
- 观察内容必须包含 "Observation:" 前缀
- 答案内容必须包含 "Answer:" 前缀"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        try:
            logger.info(f"准备发送请求到 DeepSeek API: {self.api_base}/chat/completions")
            logger.debug(f"请求数据: {json.dumps(data, ensure_ascii=False)}")
            
            # 创建SSL上下文
            ssl_context = None if self.verify_ssl else False
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=data,
                    ssl=ssl_context
                ) as response:
                    logger.info(f"DeepSeek API 响应状态码: {response.status}")
                    
                    if response.status != 200:
                        response_text = await response.text()
                        error_msg = f"API调用失败: {response_text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    response_text = await response.text()
                    logger.debug(f"DeepSeek API 响应内容: {response_text}")
                    
                    result = json.loads(response_text)
                    if "choices" not in result or not result["choices"]:
                        error_msg = "API响应中没有找到choices字段"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                        
                    return result["choices"][0]["message"]["content"]
                    
        except aiohttp.ClientError as e:
            error_msg = f"网络请求错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
        except asyncio.TimeoutError as e:
            error_msg = f"请求超时: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"生成响应时出错: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: float = 2.0,  # 增加重试延迟
        **kwargs
    ) -> str:
        """带重试机制的文本生成
        
        Args:
            prompt: 输入提示词
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            **kwargs: 传递给generate方法的其他参数
            
        Returns:
            str: 生成的文本响应
        """
        last_error = None
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)  # 指数退避
                    logger.warning(f"第 {attempt + 1} 次尝试失败，{wait_time} 秒后重试: {str(e)}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"达到最大重试次数 ({max_retries})，最后一次错误: {str(e)}")
                    raise last_error
                    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> str:
        """
        使用消息格式进行聊天补全
        
        Args:
            messages: 消息列表，包含role和content
            max_tokens: 最大生成token数
            temperature: 温度参数，控制随机性
            max_retries: 最大重试次数
            
        Returns:
            str: 生成的文本响应
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        # 重试逻辑
        last_error = None
        for attempt in range(max_retries):
            try:
                logger.info(f"准备发送chat completion请求，尝试 #{attempt+1}")
                logger.debug(f"请求消息: {json.dumps(messages, ensure_ascii=False)}")
                
                # 创建SSL上下文
                ssl_context = None if self.verify_ssl else False
                
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json=data,
                        ssl=ssl_context
                    ) as response:
                        logger.info(f"DeepSeek API 响应状态码: {response.status}")
                        
                        if response.status != 200:
                            response_text = await response.text()
                            error_msg = f"Chat completion API调用失败: {response_text}"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                        
                        response_text = await response.text()
                        result = json.loads(response_text)
                        
                        if "choices" not in result or not result["choices"]:
                            error_msg = "API响应中没有找到choices字段"
                            logger.error(error_msg)
                            raise Exception(error_msg)
                            
                        return result["choices"][0]["message"]["content"]
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = 2.0 * (attempt + 1)  # 指数退避
                    logger.warning(f"Chat completion第 {attempt + 1} 次尝试失败，{wait_time} 秒后重试: {str(e)}")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Chat completion达到最大重试次数 ({max_retries})，最后一次错误: {str(e)}")
                    raise last_error 