import asyncio
import os
from agent import ReActAgent
from tools import ToolSet
from llm_client import DeepSeekLLMClient

async def main():
    # 创建工具集
    tool_set = ToolSet()
    
    # 创建DeepSeek LLM客户端，禁用SSL验证
    llm_client = DeepSeekLLMClient(verify_ssl=False)
    
    # 创建ReAct智能体
    agent = ReActAgent(llm_client)
    
    # 注册工具
    for name, tool_info in tool_set.tools.items():
        agent.add_tool(
            name=name,
            description=tool_info["description"],
            parameters=tool_info["parameters"]
        )
    
    # 运行智能体
    query = "请分析这个项目的主要功能和结构"
    try:
        result = await agent.run(query)
        print(f"查询: {query}")
        print(f"结果: {result}")
    except Exception as e:
        print(f"运行出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 