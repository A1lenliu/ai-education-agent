"""
模型配置文件
包含模型训练和推理的基本配置参数
"""

import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

@dataclass
class ModelConfig:
    """基础模型配置类"""
    model_name: str = "bert-base-chinese"  # 默认使用中文BERT基础模型
    model_type: str = "bert"               # 模型类型
    max_seq_length: int = 512              # 最大序列长度
    batch_size: int = 16                   # 批次大小
    learning_rate: float = 5e-5            # 学习率
    num_train_epochs: int = 3              # 训练轮数
    warmup_steps: int = 0                  # 预热步数
    weight_decay: float = 0.01             # 权重衰减
    save_steps: int = 1000                 # 保存检查点的步数
    output_dir: str = "./saved_models"     # 模型保存路径
    
    # 多语言支持配置
    multilingual: bool = True              # 是否支持多语言
    
    # 模型微调配置
    do_train: bool = True                  # 是否进行训练
    do_eval: bool = True                   # 是否进行评估
    
    # 优化器配置
    optimizer_type: str = "adamw"          # 优化器类型
    
    # 设备配置
    device: str = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典格式"""
        return {k: v for k, v in self.__dict__.items()}

@dataclass
class TextClassificationConfig(ModelConfig):
    """文本分类任务配置"""
    num_labels: int = 2                    # 分类标签数量
    task_type: str = "classification"      # 任务类型
    
@dataclass
class SequenceLabelingConfig(ModelConfig):
    """序列标注任务配置"""
    num_labels: int = 9                    # 实体类型数量
    task_type: str = "ner"                 # 任务类型
    
@dataclass
class TextGenerationConfig(ModelConfig):
    """文本生成任务配置"""
    model_name: str = "gpt2-chinese"       # 默认使用中文GPT2模型
    model_type: str = "gpt2"               # 模型类型
    task_type: str = "generation"          # 任务类型
    max_length: int = 100                  # 生成文本的最大长度
    temperature: float = 0.7               # 生成温度
    top_k: int = 50                        # top-k采样
    top_p: float = 0.9                     # top-p采样
    
@dataclass
class RAGModelConfig(ModelConfig):
    """检索增强生成模型配置"""
    retriever_model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"  # 检索器模型
    generator_model_name: str = "gpt2-chinese"                           # 生成器模型
    task_type: str = "rag"                                               # 任务类型
    index_batch_size: int = 128                                          # 索引批次大小
    vector_size: int = 384                                               # 向量维度
    top_k_retrieval: int = 5                                             # 检索的文档数量 