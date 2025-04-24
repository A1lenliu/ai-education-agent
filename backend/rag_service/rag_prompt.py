"""
RAG服务的提示模板
"""

# RAG系统提示模板
RAG_SYSTEM_PROMPT = """你是一个专业的知识库问答助手，你的任务是：
1. 基于提供的知识库内容回答用户问题
2. 只使用提供的知识库内容作为信息来源
3. 如果知识库中没有相关信息，明确告知用户"我在知识库中找不到相关信息"
4. 不要编造不在知识库中的信息
5. 回答要全面、准确、客观
6. 回答要有逻辑性和条理性
7. 适当使用知识库中的专业术语
8. 返回用英文回答

请记住，你的作用是帮助用户从知识库中获取信息，不要生成不在知识库中的内容。"""

# 基于检索结果的RAG提示模板
def generate_rag_prompt(query: str, context_docs: list) -> dict:
    """
    生成RAG提示
    
    Args:
        query: 用户查询
        context_docs: 检索到的文档上下文
        
    Returns:
        完整的提示消息列表
    """
    # 构建上下文文本
    contexts = []
    for i, doc in enumerate(context_docs):
        # 从文档中提取文本
        text = doc.get("text", "")
        # 添加编号和文本
        contexts.append(f"[文档{i+1}] {text}")
    
    # 连接所有上下文
    context_text = "\n\n".join(contexts)
    
    # 创建用户提示，包含上下文和问题
    user_prompt = f"""基于以下知识库中检索到的信息回答问题：

知识库内容：
{context_text}

用户问题：{query}

请用英文回答上述问题。"""

    # 返回完整的消息列表格式
    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    return messages 