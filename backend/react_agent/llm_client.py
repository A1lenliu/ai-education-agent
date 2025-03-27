import os
import json
import aiohttp
import asyncio
import ssl
from typing import Optional, Dict, Any
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
                    "content": "你是一个遵循ReAct范式的AI助手。请严格按照以下格式回复：\n"
                              "Thought: 思考下一步行动\n"
                              "Action: 工具名称\n"
                              "Action Input: 工具参数\n"
                              "Observation: 工具返回结果\n"
                              "Answer: 最终答案"
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
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=data,
                    ssl=ssl_context,
                    timeout=30  # 添加超时设置
                ) as response:
                    logger.info(f"DeepSeek API 响应状态码: {response.status}")
                    response_text = await response.text()
                    logger.debug(f"DeepSeek API 响应内容: {response_text}")
                    
                    if response.status != 200:
                        error_msg = f"API调用失败: {response_text}"
                        logger.error(error_msg)
                        raise Exception(error_msg)
                    
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
        except Exception as e:
            error_msg = f"生成响应时出错: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
    
    async def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        retry_delay: float = 1.0,
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
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay * (attempt + 1)) 