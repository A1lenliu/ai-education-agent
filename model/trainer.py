"""
模型训练器模块
实现模型训练、评估和预测的功能
"""

import os
import json
import logging
import numpy as np
import torch
from torch.utils.data import DataLoader, RandomSampler, SequentialSampler
from transformers import (
    AdamW,
    get_linear_schedule_with_warmup,
    PreTrainedModel,
    PreTrainedTokenizer,
)
from typing import Dict, List, Tuple, Optional, Union, Any
from tqdm import tqdm, trange
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, f1_score, classification_report

from .model_config import ModelConfig
from .data_processor import (
    InputExample,
    InputFeatures,
    convert_examples_to_features,
    create_dataloader,
)

logger = logging.getLogger(__name__)

class Trainer:
    """模型训练器基类"""
    
    def __init__(
        self,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        config: ModelConfig,
        device: Optional[torch.device] = None,
    ):
        """
        初始化训练器
        
        Args:
            model: 预训练模型
            tokenizer: 分词器
            config: 模型配置
            device: 设备（CPU或GPU）
        """
        self.model = model
        self.tokenizer = tokenizer
        self.config = config
        self.device = device or torch.device(config.device)
        
        # 将模型移至指定设备
        self.model.to(self.device)
        
        # 训练状态跟踪
        self.global_step = 0
        self.epoch = 0
        self.best_score = 0.0
        
        # 训练历史记录
        self.train_losses = []
        self.eval_losses = []
        self.train_accuracies = []
        self.eval_accuracies = []
    
    def train(
        self,
        train_dataloader: DataLoader,
        eval_dataloader: Optional[DataLoader] = None,
        num_epochs: int = None,
    ) -> Dict[str, float]:
        """
        训练模型
        
        Args:
            train_dataloader: 训练数据加载器
            eval_dataloader: 评估数据加载器
            num_epochs: 训练轮数
            
        Returns:
            训练结果统计
        """
        num_epochs = num_epochs or self.config.num_train_epochs
        total_steps = len(train_dataloader) * num_epochs
        
        # 准备优化器和学习率调度器
        optimizer = self._get_optimizer()
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=self.config.warmup_steps,
            num_training_steps=total_steps
        )
        
        logger.info("***** 开始训练 *****")
        logger.info(f"  样本数量 = {len(train_dataloader.dataset)}")
        logger.info(f"  训练轮数 = {num_epochs}")
        logger.info(f"  批次大小 = {self.config.batch_size}")
        logger.info(f"  总训练步数 = {total_steps}")
        
        self.model.zero_grad()
        
        # 训练循环
        for epoch in range(num_epochs):
            self.epoch = epoch
            epoch_iterator = tqdm(train_dataloader, desc=f"Epoch {epoch}")
            epoch_loss = 0.0
            epoch_steps = 0
            
            self.model.train()
            for step, batch in enumerate(epoch_iterator):
                # 将批次数据移至设备
                batch = {k: v.to(self.device) if v is not None else v for k, v in batch.items()}
                
                outputs = self._training_step(batch)
                loss = outputs["loss"]
                
                loss.backward()
                epoch_loss += loss.item()
                epoch_steps += 1
                
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                scheduler.step()
                self.model.zero_grad()
                
                self.global_step += 1
                
                if self.global_step % self.config.save_steps == 0:
                    self._save_model()
            
            avg_loss = epoch_loss / epoch_steps
            self.train_losses.append(avg_loss)
            logger.info(f"Epoch {epoch} - 平均损失: {avg_loss:.4f}")
            
            # 评估模型
            if eval_dataloader is not None:
                eval_results = self.evaluate(eval_dataloader)
                self.eval_losses.append(eval_results["loss"])
                
                # 保存最佳模型
                if eval_results.get("accuracy", 0) > self.best_score:
                    self.best_score = eval_results.get("accuracy", 0)
                    self._save_model(is_best=True)
        
        # 保存最终模型
        self._save_model()
        
        # 绘制训练曲线
        self._plot_training_curves()
        
        return {
            "epochs": num_epochs,
            "global_step": self.global_step,
            "best_score": self.best_score,
            "train_loss": self.train_losses[-1] if self.train_losses else None,
            "eval_loss": self.eval_losses[-1] if self.eval_losses else None,
        }
    
    def evaluate(self, eval_dataloader: DataLoader) -> Dict[str, float]:
        """
        评估模型
        
        Args:
            eval_dataloader: 评估数据加载器
            
        Returns:
            评估结果统计
        """
        logger.info("***** 开始评估 *****")
        logger.info(f"  样本数量 = {len(eval_dataloader.dataset)}")
        logger.info(f"  批次大小 = {self.config.batch_size}")
        
        self.model.eval()
        eval_loss = 0.0
        eval_steps = 0
        all_preds = []
        all_labels = []
        
        for batch in tqdm(eval_dataloader, desc="Evaluating"):
            batch = {k: v.to(self.device) if v is not None else v for k, v in batch.items()}
            
            with torch.no_grad():
                outputs = self._evaluate_step(batch)
                loss = outputs["loss"]
                preds = outputs["predictions"]
                
                eval_loss += loss.item()
                eval_steps += 1
                
                all_preds.extend(preds.detach().cpu().numpy())
                if "label_id" in batch and batch["label_id"] is not None:
                    all_labels.extend(batch["label_id"].detach().cpu().numpy())
        
        avg_loss = eval_loss / eval_steps
        
        results = {"loss": avg_loss}
        
        # 计算指标
        if all_labels:
            accuracy = accuracy_score(all_labels, all_preds)
            f1 = f1_score(all_labels, all_preds, average='weighted')
            results["accuracy"] = accuracy
            results["f1"] = f1
            self.eval_accuracies.append(accuracy)
            
            logger.info(f"Evaluation - Loss: {avg_loss:.4f}, Accuracy: {accuracy:.4f}, F1: {f1:.4f}")
            logger.info("\n" + classification_report(all_labels, all_preds))
        
        return results
    
    def predict(self, test_dataloader: DataLoader) -> np.ndarray:
        """
        使用模型进行预测
        
        Args:
            test_dataloader: 测试数据加载器
            
        Returns:
            预测结果数组
        """
        logger.info("***** 开始预测 *****")
        logger.info(f"  样本数量 = {len(test_dataloader.dataset)}")
        
        self.model.eval()
        all_preds = []
        
        for batch in tqdm(test_dataloader, desc="Predicting"):
            batch = {k: v.to(self.device) if v is not None else v for k, v in batch.items()}
            
            with torch.no_grad():
                outputs = self._predict_step(batch)
                preds = outputs["predictions"]
                all_preds.extend(preds.detach().cpu().numpy())
        
        return np.array(all_preds)
    
    def _get_optimizer(self) -> torch.optim.Optimizer:
        """
        获取优化器
        
        Returns:
            优化器实例
        """
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.config.weight_decay,
            },
            {
                "params": [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        
        return AdamW(
            optimizer_grouped_parameters,
            lr=self.config.learning_rate,
        )
    
    def _save_model(self, is_best: bool = False) -> None:
        """
        保存模型
        
        Args:
            is_best: 是否为最佳模型
        """
        output_dir = os.path.join(self.config.output_dir, f"checkpoint-{self.global_step}")
        if is_best:
            output_dir = os.path.join(self.config.output_dir, "best_model")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存模型
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        # 保存训练配置
        with open(os.path.join(output_dir, "training_config.json"), "w") as f:
            json.dump(self.config.to_dict(), f)
        
        logger.info(f"模型已保存至 {output_dir}")
    
    def _plot_training_curves(self) -> None:
        """绘制训练曲线"""
        fig, ax = plt.subplots(1, 2, figsize=(15, 5))
        
        # 损失曲线
        ax[0].plot(self.train_losses, label='训练损失')
        if self.eval_losses:
            ax[0].plot(self.eval_losses, label='验证损失')
        ax[0].set_xlabel('Epoch')
        ax[0].set_ylabel('Loss')
        ax[0].set_title('训练和验证损失')
        ax[0].legend()
        
        # 准确率曲线
        if self.eval_accuracies:
            ax[1].plot(self.eval_accuracies, label='验证准确率')
            ax[1].set_xlabel('Epoch')
            ax[1].set_ylabel('Accuracy')
            ax[1].set_title('验证准确率')
            ax[1].legend()
        
        # 保存图表
        curves_dir = os.path.join(self.config.output_dir, "curves")
        if not os.path.exists(curves_dir):
            os.makedirs(curves_dir)
        plt.savefig(os.path.join(curves_dir, f"training_curves.png"))
        plt.close()
    
    def _training_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """
        执行单个训练步骤
        
        Args:
            batch: 批次数据
            
        Returns:
            步骤结果
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def _evaluate_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """
        执行单个评估步骤
        
        Args:
            batch: 批次数据
            
        Returns:
            步骤结果
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def _predict_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """
        执行单个预测步骤
        
        Args:
            batch: 批次数据
            
        Returns:
            步骤结果
        """
        raise NotImplementedError("子类必须实现此方法")

class ClassificationTrainer(Trainer):
    """分类任务训练器"""
    
    def _training_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """执行单个训练步骤"""
        outputs = self.model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            token_type_ids=batch.get("token_type_ids"),
            labels=batch.get("label_id")
        )
        
        return {
            "loss": outputs.loss,
            "logits": outputs.logits,
        }
    
    def _evaluate_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """执行单个评估步骤"""
        outputs = self.model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            token_type_ids=batch.get("token_type_ids"),
            labels=batch.get("label_id")
        )
        
        predictions = torch.argmax(outputs.logits, dim=-1)
        
        return {
            "loss": outputs.loss,
            "predictions": predictions,
        }
    
    def _predict_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """执行单个预测步骤"""
        outputs = self.model(
            input_ids=batch["input_ids"],
            attention_mask=batch["attention_mask"],
            token_type_ids=batch.get("token_type_ids")
        )
        
        predictions = torch.argmax(outputs.logits, dim=-1)
        
        return {
            "predictions": predictions,
        } 