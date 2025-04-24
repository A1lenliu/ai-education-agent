"""
模型训练包
提供模型训练、评估和推理的工具集
"""

from .model_config import (
    ModelConfig,
    TextClassificationConfig,
    SequenceLabelingConfig,
    TextGenerationConfig,
    RAGModelConfig,
)

from .data_processor import (
    InputExample,
    InputFeatures,
    TextDataset,
    DataProcessor,
    ClassificationProcessor,
    convert_examples_to_features,
    create_dataloader,
)

from .trainer import (
    Trainer,
    ClassificationTrainer,
)

from .data_augmentation import (
    TextAugmenter,
    RandomDeleteAugmenter,
    RandomSwapAugmenter,
    RandomInsertAugmenter,
    SynonymReplaceAugmenter,
    BackTranslationAugmenter,
    CompositeAugmenter,
    create_default_augmenter,
)

from .ner_processor import (
    NERExample,
    NERFeatures,
    NERDataset,
    NERProcessor,
    NERTrainer,
    convert_ner_examples_to_features,
    create_ner_dataloader,
)

__version__ = "0.1.0"
__all__ = [
    # 配置
    "ModelConfig",
    "TextClassificationConfig",
    "SequenceLabelingConfig", 
    "TextGenerationConfig",
    "RAGModelConfig",
    
    # 数据处理
    "InputExample",
    "InputFeatures",
    "TextDataset",
    "DataProcessor",
    "ClassificationProcessor",
    "convert_examples_to_features",
    "create_dataloader",
    
    # 训练器
    "Trainer",
    "ClassificationTrainer",
    
    # 数据增强
    "TextAugmenter",
    "RandomDeleteAugmenter",
    "RandomSwapAugmenter",
    "RandomInsertAugmenter",
    "SynonymReplaceAugmenter",
    "BackTranslationAugmenter",
    "CompositeAugmenter",
    "create_default_augmenter",
    
    # 序列标注
    "NERExample",
    "NERFeatures",
    "NERDataset",
    "NERProcessor",
    "NERTrainer",
    "convert_ner_examples_to_features",
    "create_ner_dataloader",
] 