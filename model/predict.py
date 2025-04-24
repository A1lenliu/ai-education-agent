#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型推理脚本
用于使用训练好的模型进行预测
"""

import os
import json
import logging
import argparse
import numpy as np
import pandas as pd
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)

# 设置日志
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def predict_classification(model_path, texts, max_length=128, batch_size=32):
    """
    使用分类模型进行预测
    
    Args:
        model_path: 模型路径
        texts: 文本列表
        max_length: 最大序列长度
        batch_size: 批次大小
        
    Returns:
        预测标签列表和概率列表
    """
    # 加载模型和分词器
    logger.info(f"加载模型和分词器：{model_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    
    # 加载标签映射
    label_map_path = os.path.join(model_path, "label_map.json")
    if os.path.exists(label_map_path):
        with open(label_map_path, "r") as f:
            label_map = json.load(f)
            id_to_label = {v: k for k, v in label_map.items()}
    else:
        logger.warning("找不到标签映射文件，将使用索引作为标签")
        num_labels = model.config.num_labels
        id_to_label = {i: str(i) for i in range(num_labels)}
    
    # 设置设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()
    
    # 批处理预测
    all_predictions = []
    all_probs = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        
        # 编码输入
        inputs = tokenizer(
            batch_texts,
            max_length=max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # 将输入移至设备
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # 预测
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            
            # 获取预测的类别和概率
            probs = torch.nn.functional.softmax(logits, dim=-1)
            predictions = torch.argmax(probs, dim=-1)
            
            # 转换为 numpy 数组
            predictions = predictions.cpu().numpy()
            probs = probs.cpu().numpy()
            
            all_predictions.extend(predictions)
            all_probs.extend(probs)
    
    # 转换预测索引为标签
    predicted_labels = [id_to_label[pred] for pred in all_predictions]
    
    return predicted_labels, all_probs

def main():
    parser = argparse.ArgumentParser(description="模型推理脚本")
    
    # 基本参数
    parser.add_argument("--model_path", type=str, required=True, help="模型路径")
    parser.add_argument("--input_file", type=str, required=True, help="输入文件路径（CSV或TXT）")
    parser.add_argument("--output_file", type=str, required=True, help="输出文件路径")
    parser.add_argument("--text_column", type=str, default="text", help="文本列名（仅适用于CSV）")
    parser.add_argument("--max_length", type=int, default=128, help="最大序列长度")
    parser.add_argument("--batch_size", type=int, default=32, help="批次大小")
    
    args = parser.parse_args()
    
    # 读取输入数据
    if args.input_file.endswith('.csv'):
        df = pd.read_csv(args.input_file)
        texts = df[args.text_column].tolist()
    elif args.input_file.endswith('.txt'):
        with open(args.input_file, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f.readlines()]
    else:
        logger.error("不支持的输入文件格式，仅支持CSV或TXT")
        return
    
    logger.info(f"加载了 {len(texts)} 条文本")
    
    # 进行预测
    predicted_labels, prediction_probs = predict_classification(
        args.model_path,
        texts,
        max_length=args.max_length,
        batch_size=args.batch_size
    )
    
    # 保存预测结果
    if args.input_file.endswith('.csv'):
        df['predicted_label'] = predicted_labels
        
        # 添加概率列
        num_labels = len(prediction_probs[0])
        for i in range(num_labels):
            df[f'prob_{i}'] = [probs[i] for probs in prediction_probs]
        
        df.to_csv(args.output_file, index=False)
    else:
        with open(args.output_file, 'w', encoding='utf-8') as f:
            for text, label, probs in zip(texts, predicted_labels, prediction_probs):
                probs_str = ','.join([f"{p:.4f}" for p in probs])
                f.write(f"{text}\t{label}\t{probs_str}\n")
    
    logger.info(f"预测完成，结果已保存至 {args.output_file}")

if __name__ == "__main__":
    main() 