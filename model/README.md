# 模型训练框架

本目录包含了用于训练和推理文本处理模型的代码框架，支持多种自然语言处理任务，如文本分类、序列标注和文本生成。

## 目录结构

```
model/
  ├── model_config.py     # 模型配置定义
  ├── data_processor.py   # 数据处理工具
  ├── trainer.py          # 模型训练器
  ├── train_model.py      # 训练脚本
  ├── predict.py          # 推理脚本
  └── README.md           # 说明文档
```

## 功能特点

- 支持多种预训练语言模型（BERT、RoBERTa、GPT-2等）
- 支持文本分类、序列标注、文本生成等多种任务
- 内置数据处理和特征工程工具
- 提供训练、评估和推理功能
- 支持多语言，默认配置适合中文处理

## 环境要求

- Python 3.7+
- PyTorch 1.8+
- Transformers 4.5+
- pandas, numpy, scikit-learn, matplotlib等

## 安装依赖

```bash
pip install torch transformers pandas numpy scikit-learn matplotlib tqdm
```

## 数据格式

### 文本分类任务

训练数据应组织为CSV格式，包含以下列：
- `text`: 文本内容
- `label`: 分类标签

样例（train.csv）:
```
text,label
这是一个很好的产品，我非常喜欢,正面
服务态度太差了，不会再购买,负面
价格合理，质量尚可,中性
```

## 使用方法

### 文本分类模型训练

```bash
python train_model.py \
  --data_dir /path/to/data \
  --output_dir /path/to/save/model \
  --model_name bert-base-chinese \
  --task_type classification \
  --num_labels 3 \
  --label_names 负面,中性,正面 \
  --batch_size 16 \
  --learning_rate 2e-5 \
  --num_train_epochs 5 \
  --max_seq_length 128
```

### 使用训练好的模型进行预测

```bash
python predict.py \
  --model_path /path/to/saved/model \
  --input_file /path/to/test.csv \
  --output_file /path/to/predictions.csv \
  --text_column text \
  --batch_size 32
```

## 高级配置

### 自定义数据处理

你可以通过继承`DataProcessor`类来创建自定义的数据处理器：

```python
from data_processor import DataProcessor, InputExample

class MyCustomProcessor(DataProcessor):
    def get_train_examples(self, data_dir):
        # 实现自定义的训练数据加载逻辑
        pass
        
    def get_labels(self):
        # 返回标签列表
        return ["标签1", "标签2", "标签3"]
```

### 自定义训练器

你可以通过继承`Trainer`类来创建自定义的训练器：

```python
from trainer import Trainer

class MyCustomTrainer(Trainer):
    def _training_step(self, batch):
        # 实现自定义的训练步骤
        pass
```

## 示例应用场景

1. **教育内容分类**：对教育资源进行主题分类，如数学、语文、历史等
2. **情感分析**：分析学生对课程的评价反馈
3. **自动问答**：训练模型以回答教育相关问题
4. **文本摘要**：为教育材料生成摘要
5. **关键词提取**：从教育文档中提取关键概念和术语

## 常见问题

**Q: 如何使用GPU进行训练？**  
A: 系统会自动检测并使用可用的GPU。确保已安装CUDA和相应版本的PyTorch。

**Q: 如何处理超长文本？**  
A: 可以通过设置`--max_seq_length`参数来调整处理的最大文本长度。对于更长的文本，可以考虑分段处理或使用支持更长序列的模型。

**Q: 如何保存训练好的模型？**  
A: 模型会自动保存到`--output_dir`指定的目录中。每个检查点包含模型权重、配置和分词器。

**Q: 如何使用自定义预训练模型？**  
A: 通过`--model_name`参数指定本地模型路径或Hugging Face模型名称。

## 联系方式

如有问题或建议，请提交Issue或联系项目维护者。 