#!/usr/bin/env python3
# 修复RAG服务数据库

import os
import shutil
import logging
import sys

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_rag_database():
    """清理并重新创建RAG向量数据库目录"""
    try:
        # 获取知识库目录路径
        kb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
        chroma_db_dir = os.path.join(kb_dir, "chroma_db")
        
        # 确保知识库目录存在
        if not os.path.exists(kb_dir):
            os.makedirs(kb_dir)
            logger.info(f"创建知识库目录: {kb_dir}")
        
        # 如果ChromaDB目录存在，则备份并删除
        if os.path.exists(chroma_db_dir):
            backup_dir = f"{chroma_db_dir}_backup_{int(os.path.getmtime(chroma_db_dir))}"
            try:
                shutil.move(chroma_db_dir, backup_dir)
                logger.info(f"现有ChromaDB目录已备份至: {backup_dir}")
            except Exception as e:
                # 如果无法移动，则直接删除
                logger.warning(f"无法创建备份: {str(e)}，直接删除目录")
                shutil.rmtree(chroma_db_dir)
        
        # 创建一个新的空目录
        os.makedirs(chroma_db_dir, exist_ok=True)
        logger.info(f"创建了新的ChromaDB目录: {chroma_db_dir}")
        
        # 尝试运行简单测试以验证ChromaDB是否正常工作
        try:
            import chromadb
            import numpy as np
            
            # 创建客户端和嵌入函数
            client = chromadb.PersistentClient(path=chroma_db_dir)
            
            # 创建自定义嵌入函数
            class SimpleEmbeddingFunction:
                def __init__(self, dimension=384):
                    self.dimension = dimension
                
                def __call__(self, input):
                    """按照ChromaDB的要求实现__call__方法，只接受input参数"""
                    result = []
                    
                    # 确保input是一个列表
                    texts = input if isinstance(input, list) else [input]
                    
                    for text in texts:
                        # 对文本进行简单哈希处理并标准化
                        hash_values = []
                        for i in range(self.dimension):
                            # 使用不同的种子值生成哈希
                            seed = i + 1
                            hash_val = 0
                            for j, char in enumerate(text):
                                hash_val += (ord(char) * (seed + j)) % 1000
                            hash_values.append(hash_val)
                        
                        # 标准化向量
                        vec = np.array(hash_values, dtype=float)
                        norm = np.linalg.norm(vec)
                        if norm > 0:
                            vec = vec / norm
                        
                        result.append(vec.tolist())
                    
                    return result
            
            # 使用自定义嵌入函数创建集合
            embedding_function = SimpleEmbeddingFunction()
            collection = client.create_collection(
                name="test_collection",
                embedding_function=embedding_function
            )
            
            # 添加一个示例文档
            collection.add(
                documents=["这是一个示例文档，用于测试RAG服务的功能。"],
                ids=["example_doc"],
                metadatas=[{
                    "title": "示例文档",
                    "author": "AI教育助手",
                    "doc_id": "example_doc",
                    "chunk_id": 0,
                    "chunk_total": 1
                }]
            )
            
            # 添加AI教育文档
            ai_doc = """
            人工智能教育是指将人工智能技术和理念融入教育领域，既包括关于AI的教育（学习AI知识），
            也包括通过AI促进教育（利用AI工具和方法改进学习体验）。在当今数字化时代，AI教育变得
            越来越重要，它帮助学生培养未来所需的技能，同时也为教育工作者提供了新的教学工具和方法。
            
            人工智能教育的核心内容包括:
            1. 机器学习基础：了解算法如何从数据中学习模式
            2. 神经网络：探索模仿人脑结构的计算模型
            3. 自然语言处理：研究计算机如何理解和生成人类语言
            4. 计算机视觉：学习机器如何"看见"和理解视觉信息
            5. 机器人技术：结合AI与物理系统创建智能机器
            
            在中小学教育中，AI课程通常侧重于:
            - 编程思维与计算思维的培养
            - 使用图形化编程工具创建简单的AI应用
            - 理解AI技术如何影响生活和社会
            - 培养对技术的批判性思考能力
            
            在大学教育中，AI课程则更深入地探讨:
            - 高级机器学习算法
            - 深度学习框架的应用
            - AI系统设计与实现
            - AI伦理与社会影响研究
            
            AI教育的未来发展趋势包括:
            1. 个性化学习：AI系统能够根据学生的学习风格和进度定制教育内容
            2. 自适应评估：动态调整难度和内容以最优化学习效果
            3. 智能辅导系统：提供实时反馈和指导
            4. 教育数据分析：帮助教育者做出更明智的教学决策
            
            总之，人工智能教育不仅是关于技术的学习，更是培养学生在人工智能时代所需的关键能力，
            包括批判性思维、创造力、解决问题的能力以及跨学科协作的意识。
            """
            
            collection.add(
                documents=[ai_doc],
                ids=["ai_education_doc"],
                metadatas=[{
                    "title": "人工智能教育简介",
                    "author": "AI教育助手",
                    "doc_id": "ai_education_doc",
                    "chunk_id": 0,
                    "chunk_total": 1,
                    "tags": "AI, 教育, 人工智能"
                }]
            )
            
            # 创建集合成功
            logger.info("ChromaDB 测试集合创建成功!")
            
            # 尝试查询文档
            results = collection.query(
                query_texts=["人工智能教育"],
                n_results=1
            )
            
            if results and results["documents"] and len(results["documents"][0]) > 0:
                logger.info("ChromaDB 查询测试成功!")
            
            # 测试成功后仍保留集合，供用户使用
            # client.delete_collection(name="test_collection")
        except ImportError:
            logger.error("ChromaDB库未安装，请运行: pip install chromadb")
            return False
        except Exception as e:
            logger.error(f"ChromaDB测试失败: {str(e)}")
            return False
        
        logger.info("RAG数据库修复成功!")
        return True
    except Exception as e:
        logger.error(f"修复RAG数据库时出错: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("开始修复RAG服务数据库...")
    success = fix_rag_database()
    if success:
        logger.info("RAG服务数据库修复完成，现在可以启动RAG服务了")
        sys.exit(0)
    else:
        logger.error("RAG服务数据库修复失败")
        sys.exit(1) 