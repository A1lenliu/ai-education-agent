"""
数据处理模块
包含数据加载、预处理和批处理功能
"""

import os
import json
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union, Any
from dataclasses import dataclass
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import PreTrainedTokenizer

@dataclass
class InputExample:
    """单个训练/测试样本的基础类"""
    guid: str  # 样本唯一标识符
    text_a: str  # 第一段文本
    text_b: Optional[str] = None  # 第二段文本（可选）
    label: Optional[str] = None  # 样本标签（可选）

@dataclass
class InputFeatures:
    """转换为模型输入特征的基础类"""
    input_ids: List[int]
    attention_mask: List[int]
    token_type_ids: Optional[List[int]] = None
    label_id: Optional[Union[int, float]] = None

class TextDataset(Dataset):
    """通用文本数据集"""
    
    def __init__(self, features: List[InputFeatures]):
        self.features = features
        
    def __len__(self) -> int:
        return len(self.features)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        feature = self.features[idx]
        return {
            'input_ids': torch.tensor(feature.input_ids, dtype=torch.long),
            'attention_mask': torch.tensor(feature.attention_mask, dtype=torch.long),
            'token_type_ids': torch.tensor(feature.token_type_ids, dtype=torch.long) if feature.token_type_ids else None,
            'label_id': torch.tensor(feature.label_id, dtype=torch.long) if feature.label_id is not None else None
        }

class DataProcessor:
    """数据处理基类"""
    
    def get_train_examples(self, data_dir: str) -> List[InputExample]:
        """获取训练样本"""
        raise NotImplementedError()
    
    def get_dev_examples(self, data_dir: str) -> List[InputExample]:
        """获取验证样本"""
        raise NotImplementedError()
    
    def get_test_examples(self, data_dir: str) -> List[InputExample]:
        """获取测试样本"""
        raise NotImplementedError()
    
    def get_labels(self) -> List[str]:
        """获取标签列表"""
        raise NotImplementedError()
    
    @classmethod
    def _read_json(cls, input_file: str) -> List[Dict[str, Any]]:
        """从JSON文件读取数据"""
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def _read_csv(cls, input_file: str) -> pd.DataFrame:
        """从CSV文件读取数据"""
        return pd.read_csv(input_file)
    
    @classmethod
    def _read_txt(cls, input_file: str) -> List[str]:
        """从TXT文件读取数据"""
        with open(input_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]

class ClassificationProcessor(DataProcessor):
    """文本分类任务数据处理器"""
    
    def __init__(self, label_list: Optional[List[str]] = None):
        self.label_list = label_list
    
    def get_train_examples(self, data_dir: str) -> List[InputExample]:
        """获取训练样本"""
        return self._create_examples(
            self._read_csv(os.path.join(data_dir, "train.csv")), "train"
        )
    
    def get_dev_examples(self, data_dir: str) -> List[InputExample]:
        """获取验证样本"""
        return self._create_examples(
            self._read_csv(os.path.join(data_dir, "dev.csv")), "dev"
        )
    
    def get_test_examples(self, data_dir: str) -> List[InputExample]:
        """获取测试样本"""
        return self._create_examples(
            self._read_csv(os.path.join(data_dir, "test.csv")), "test"
        )
    
    def get_labels(self) -> List[str]:
        """获取标签列表"""
        if self.label_list is None:
            raise ValueError("Label list is not provided")
        return self.label_list
    
    def _create_examples(self, df: pd.DataFrame, set_type: str) -> List[InputExample]:
        """从DataFrame创建样本"""
        examples = []
        for i, row in df.iterrows():
            guid = f"{set_type}-{i}"
            text_a = row['text']
            label = str(row['label']) if 'label' in row else None
            examples.append(InputExample(guid=guid, text_a=text_a, label=label))
        return examples

def convert_examples_to_features(
    examples: List[InputExample],
    tokenizer: PreTrainedTokenizer,
    max_length: int,
    label_map: Dict[str, int],
    pad_token=0,
    pad_token_segment_id=0,
) -> List[InputFeatures]:
    """将样本转换为特征"""
    features = []
    
    for ex_index, example in enumerate(examples):
        inputs = tokenizer(
            example.text_a,
            example.text_b,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_token_type_ids=True
        )
        
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]
        token_type_ids = inputs["token_type_ids"]
        
        label_id = label_map[example.label] if example.label is not None else None
        
        features.append(
            InputFeatures(
                input_ids=input_ids,
                attention_mask=attention_mask,
                token_type_ids=token_type_ids,
                label_id=label_id
            )
        )
    
    return features

def create_dataloader(
    features: List[InputFeatures],
    batch_size: int,
    is_training: bool = True
) -> DataLoader:
    """创建DataLoader"""
    dataset = TextDataset(features)
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=is_training,
        num_workers=0
    ) 