#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
模型训练脚本
用于执行模型训练过程
"""

import os
import logging
import argparse
import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    set_seed,
)

from model_config import (
    ModelConfig,
    TextClassificationConfig,
)
from data_processor import (
    ClassificationProcessor,
    convert_examples_to_features,
    create_dataloader,
)
from trainer import ClassificationTrainer

# 设置日志
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="模型训练脚本")
    
    # 基本参数
    parser.add_argument("--data_dir", type=str, required=True, help="数据目录")
    parser.add_argument("--output_dir", type=str, required=True, help="输出目录")
    parser.add_argument("--model_name", type=str, default="bert-base-chinese", help="模型名称")
    parser.add_argument("--model_type", type=str, default="bert", help="模型类型")
    
    # 训练参数
    parser.add_argument("--task_type", type=str, default="classification", help="任务类型(classification|ner|generation)")
    parser.add_argument("--batch_size", type=int, default=16, help="批次大小")
    parser.add_argument("--learning_rate", type=float, default=5e-5, help="学习率")
    parser.add_argument("--num_train_epochs", type=int, default=3, help="训练轮数")
    parser.add_argument("--max_seq_length", type=int, default=128, help="最大序列长度")
    parser.add_argument("--seed", type=int, default=42, help="随机种子")
    
    # 分类任务特定参数
    parser.add_argument("--num_labels", type=int, default=2, help="标签数量")
    parser.add_argument("--label_names", type=str, default=None, help="标签名称，用逗号分隔")
    
    args = parser.parse_args()
    
    # 设置随机种子
    set_seed(args.seed)
    
    # 创建输出目录
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    
    # 根据任务类型选择配置
    if args.task_type == "classification":
        config = TextClassificationConfig(
            model_name=args.model_name,
            model_type=args.model_type,
            num_labels=args.num_labels,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            num_train_epochs=args.num_train_epochs,
            max_seq_length=args.max_seq_length,
            output_dir=args.output_dir,
        )
        
        # 处理标签
        label_list = args.label_names.split(",") if args.label_names else [str(i) for i in range(args.num_labels)]
        processor = ClassificationProcessor(label_list=label_list)
        
        # 加载模型和分词器
        logger.info(f"加载模型和分词器：{args.model_name}")
        tokenizer = AutoTokenizer.from_pretrained(args.model_name)
        model = AutoModelForSequenceClassification.from_pretrained(
            args.model_name,
            num_labels=args.num_labels
        )
        
        # 准备训练数据
        train_examples = processor.get_train_examples(args.data_dir)
        logger.info(f"加载训练样本数量：{len(train_examples)}")
        
        # 标签映射
        label_map = {label: i for i, label in enumerate(processor.get_labels())}
        
        # 转换为特征
        train_features = convert_examples_to_features(
            train_examples,
            tokenizer,
            max_length=args.max_seq_length,
            label_map=label_map
        )
        
        # 创建数据加载器
        train_dataloader = create_dataloader(
            train_features,
            batch_size=args.batch_size,
            is_training=True
        )
        
        # 准备验证数据（如果有）
        eval_dataloader = None
        dev_examples = processor.get_dev_examples(args.data_dir)
        if dev_examples:
            logger.info(f"加载验证样本数量：{len(dev_examples)}")
            eval_features = convert_examples_to_features(
                dev_examples,
                tokenizer,
                max_length=args.max_seq_length,
                label_map=label_map
            )
            eval_dataloader = create_dataloader(
                eval_features,
                batch_size=args.batch_size,
                is_training=False
            )
        
        # 创建训练器
        trainer = ClassificationTrainer(
            model=model,
            tokenizer=tokenizer,
            config=config
        )
        
        # 执行训练
        logger.info("开始训练...")
        train_results = trainer.train(train_dataloader, eval_dataloader)
        logger.info(f"训练完成！最佳得分：{train_results['best_score']:.4f}")
        
        # 保存标签映射
        with open(os.path.join(args.output_dir, "label_map.json"), "w") as f:
            import json
            json.dump(label_map, f)
        
    else:
        logger.error(f"不支持的任务类型：{args.task_type}")
        return

if __name__ == "__main__":
    main() 