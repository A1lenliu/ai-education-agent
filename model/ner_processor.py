"""
序列标注（NER）数据处理模块
用于加载和处理序列标注任务的数据
"""

import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any
import torch
from torch.utils.data import Dataset, DataLoader

from .data_processor import DataProcessor, InputExample

class NERExample:
    """序列标注样本"""
    
    def __init__(self, guid: str, words: List[str], labels: List[str]):
        """
        初始化序列标注样本
        
        Args:
            guid: 样本唯一标识符
            words: 分词后的单词列表
            labels: 对应的标签列表
        """
        self.guid = guid
        self.words = words
        self.labels = labels

class NERFeatures:
    """序列标注特征"""
    
    def __init__(
        self,
        input_ids: List[int],
        attention_mask: List[int],
        token_type_ids: List[int],
        label_ids: List[int]
    ):
        """
        初始化序列标注特征
        
        Args:
            input_ids: 输入ID列表
            attention_mask: 注意力掩码
            token_type_ids: 标记类型ID列表
            label_ids: 标签ID列表
        """
        self.input_ids = input_ids
        self.attention_mask = attention_mask
        self.token_type_ids = token_type_ids
        self.label_ids = label_ids

class NERDataset(Dataset):
    """序列标注数据集"""
    
    def __init__(self, features: List[NERFeatures]):
        """
        初始化数据集
        
        Args:
            features: 特征列表
        """
        self.features = features
    
    def __len__(self) -> int:
        return len(self.features)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        feature = self.features[idx]
        return {
            'input_ids': torch.tensor(feature.input_ids, dtype=torch.long),
            'attention_mask': torch.tensor(feature.attention_mask, dtype=torch.long),
            'token_type_ids': torch.tensor(feature.token_type_ids, dtype=torch.long),
            'label_ids': torch.tensor(feature.label_ids, dtype=torch.long)
        }

class NERProcessor(DataProcessor):
    """序列标注数据处理器"""
    
    def __init__(self, labels: Optional[List[str]] = None):
        """
        初始化处理器
        
        Args:
            labels: 标签列表
        """
        if labels is None:
            self.labels = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC", "B-MISC", "I-MISC"]
        else:
            self.labels = labels
        
        # 创建标签映射
        self.label2id = {label: i for i, label in enumerate(self.labels)}
        self.id2label = {i: label for i, label in enumerate(self.labels)}
    
    def get_train_examples(self, data_dir: str) -> List[NERExample]:
        """获取训练样本"""
        return self._create_examples(self._read_json(os.path.join(data_dir, "train.json")), "train")
    
    def get_dev_examples(self, data_dir: str) -> List[NERExample]:
        """获取验证样本"""
        return self._create_examples(self._read_json(os.path.join(data_dir, "dev.json")), "dev")
    
    def get_test_examples(self, data_dir: str) -> List[NERExample]:
        """获取测试样本"""
        return self._create_examples(self._read_json(os.path.join(data_dir, "test.json")), "test")
    
    def get_labels(self) -> List[str]:
        """获取标签列表"""
        return self.labels
    
    def _create_examples(self, lines: List[Dict[str, Any]], set_type: str) -> List[NERExample]:
        """
        从原始数据创建样本
        
        Args:
            lines: 数据行
            set_type: 数据集类型
            
        Returns:
            NERExample列表
        """
        examples = []
        for i, line in enumerate(lines):
            guid = f"{set_type}-{i}"
            
            # 假设数据格式为：{"words": [...], "labels": [...]}
            words = line.get("words", [])
            labels = line.get("labels", [])
            
            # 检查words和labels长度是否匹配
            if not words:
                continue
            
            if not labels:
                # 如果没有标签，则全部标为"O"
                labels = ["O"] * len(words)
            
            assert len(words) == len(labels), f"words和labels长度不匹配: {len(words)} vs {len(labels)}"
            
            examples.append(NERExample(guid=guid, words=words, labels=labels))
        
        return examples

def convert_ner_examples_to_features(
    examples: List[NERExample],
    label2id: Dict[str, int],
    tokenizer,
    max_seq_length: int = 128,
    pad_token_label_id: int = -100
) -> List[NERFeatures]:
    """
    将样本转换为特征
    
    Args:
        examples: 样本列表
        label2id: 标签到ID的映射
        tokenizer: 分词器
        max_seq_length: 最大序列长度
        pad_token_label_id: 填充标签ID
        
    Returns:
        特征列表
    """
    features = []
    
    for ex_index, example in enumerate(examples):
        tokens = []
        label_ids = []
        
        for word, label in zip(example.words, example.labels):
            # 对单词进行分词
            word_tokens = tokenizer.tokenize(word)
            
            # 对于子词标注问题：只将第一个子词标为真实标签，其余标为-100（忽略）
            if word_tokens:
                tokens.extend(word_tokens)
                
                # 对第一个子词使用真实标签
                label_ids.append(label2id[label])
                
                # 对剩余子词使用-100（在计算损失时忽略）
                label_ids.extend([pad_token_label_id] * (len(word_tokens) - 1))
        
        # 截断序列
        if len(tokens) > max_seq_length - 2:  # 考虑[CLS]和[SEP]
            tokens = tokens[:(max_seq_length - 2)]
            label_ids = label_ids[:(max_seq_length - 2)]
        
        # 添加特殊标记
        special_tokens_count = 2  # [CLS] 和 [SEP]
        
        # [CLS] token
        tokens = [tokenizer.cls_token] + tokens + [tokenizer.sep_token]
        # 特殊标记的标签设为-100（忽略）
        label_ids = [pad_token_label_id] + label_ids + [pad_token_label_id]
        
        # 生成token类型ID
        token_type_ids = [0] * len(tokens)
        
        # 生成输入ID
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        
        # 生成注意力掩码
        attention_mask = [1] * len(input_ids)
        
        # 填充序列
        padding_length = max_seq_length - len(input_ids)
        
        input_ids = input_ids + ([tokenizer.pad_token_id] * padding_length)
        attention_mask = attention_mask + ([0] * padding_length)
        token_type_ids = token_type_ids + ([0] * padding_length)
        label_ids = label_ids + ([pad_token_label_id] * padding_length)
        
        assert len(input_ids) == max_seq_length
        assert len(attention_mask) == max_seq_length
        assert len(token_type_ids) == max_seq_length
        assert len(label_ids) == max_seq_length
        
        features.append(
            NERFeatures(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
                label_ids=label_ids
            )
        )
    
    return features

def create_ner_dataloader(
    features: List[NERFeatures],
    batch_size: int,
    is_training: bool = True
) -> DataLoader:
    """
    创建数据加载器
    
    Args:
        features: 特征列表
        batch_size: 批次大小
        is_training: 是否为训练数据
        
    Returns:
        数据加载器
    """
    dataset = NERDataset(features)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=is_training,
        num_workers=0
    )

class NERTrainer:
    """序列标注任务训练器"""
    
    def __init__(self, model, tokenizer, config, device=None):
        """
        初始化训练器
        
        Args:
            model: 模型
            tokenizer: 分词器
            config: 配置
            device: 设备
        """
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # 将模型移至设备
        self.model.to(self.device)
    
    def train(self, train_dataloader, eval_dataloader=None):
        """
        训练模型
        
        Args:
            train_dataloader: 训练数据加载器
            eval_dataloader: 评估数据加载器
            
        Returns:
            训练结果
        """
        # 这里应实现完整的训练循环，类似于 trainer.py 中的 ClassificationTrainer
        # 由于实现类似，这里省略具体代码
        pass
    
    def evaluate(self, eval_dataloader):
        """
        评估模型
        
        Args:
            eval_dataloader: 评估数据加载器
            
        Returns:
            评估结果
        """
        pass
    
    def predict(self, text):
        """
        使用模型进行预测
        
        Args:
            text: 输入文本
            
        Returns:
            预测的实体列表
        """
        # 分词
        tokens = self.tokenizer.tokenize(text)
        
        # 添加特殊标记
        tokens = [self.tokenizer.cls_token] + tokens + [self.tokenizer.sep_token]
        
        # 转换为ID
        input_ids = self.tokenizer.convert_tokens_to_ids(tokens)
        
        # 生成注意力掩码
        attention_mask = [1] * len(input_ids)
        
        # 如果序列太长，截断
        max_seq_length = self.config.max_seq_length
        if len(input_ids) > max_seq_length:
            input_ids = input_ids[:max_seq_length]
            attention_mask = attention_mask[:max_seq_length]
            tokens = tokens[:max_seq_length]
        
        # 填充序列
        padding_length = max_seq_length - len(input_ids)
        
        input_ids = input_ids + ([self.tokenizer.pad_token_id] * padding_length)
        attention_mask = attention_mask + ([0] * padding_length)
        
        # 转换为张量
        input_ids = torch.tensor([input_ids], dtype=torch.long).to(self.device)
        attention_mask = torch.tensor([attention_mask], dtype=torch.long).to(self.device)
        
        # 预测
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
            predictions = outputs[0].argmax(dim=2)
        
        # 转换预测结果
        predictions = predictions[0].cpu().numpy()
        
        # 处理预测结果，提取实体
        entities = []
        current_entity = {"type": None, "start": -1, "end": -1, "text": ""}
        
        # 跳过特殊标记
        for i, (token, pred_id) in enumerate(zip(tokens[1:-1], predictions[1:-1])):
            if pred_id == 0:  # "O"标签
                # 如果当前正在处理一个实体，保存它
                if current_entity["type"] is not None:
                    entities.append(current_entity)
                    current_entity = {"type": None, "start": -1, "end": -1, "text": ""}
            else:
                pred_label = self.config.id2label.get(pred_id, "O")
                
                # 处理B-开头的标签（新实体开始）
                if pred_label.startswith("B-"):
                    # 如果当前正在处理一个实体，保存它
                    if current_entity["type"] is not None:
                        entities.append(current_entity)
                    
                    # 开始一个新实体
                    entity_type = pred_label[2:]  # 去掉"B-"前缀
                    current_entity = {
                        "type": entity_type,
                        "start": i,
                        "end": i,
                        "text": token
                    }
                # 处理I-开头的标签（实体继续）
                elif pred_label.startswith("I-"):
                    entity_type = pred_label[2:]  # 去掉"I-"前缀
                    
                    # 如果当前没有处理实体或类型不匹配，忽略
                    if current_entity["type"] is None or current_entity["type"] != entity_type:
                        continue
                    
                    # 扩展当前实体
                    current_entity["end"] = i
                    current_entity["text"] += token
        
        # 如果最后还有未保存的实体
        if current_entity["type"] is not None:
            entities.append(current_entity)
        
        return entities 