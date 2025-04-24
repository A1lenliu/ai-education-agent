#!/bin/bash
# 安装模型训练所需的最小依赖项
# 这个脚本只安装必要的依赖，不包括matplotlib等可视化库

echo "开始安装模型训练所需的最小依赖项..."

# 检查是否安装了pip
if ! command -v pip &> /dev/null; then
    echo "未找到pip，请先安装Python和pip"
    exit 1
fi

# 安装最小依赖项
echo "安装最小依赖项..."
pip install numpy pandas tqdm

# 检查是否安装成功
echo "检查安装是否成功..."
INSTALL_OK=1

# 检查numpy
if ! python -c "import numpy" &> /dev/null; then
    echo "numpy 安装失败"
    INSTALL_OK=0
fi

# 检查pandas
if ! python -c "import pandas" &> /dev/null; then
    echo "pandas 安装失败"
    INSTALL_OK=0
fi

# 检查tqdm
if ! python -c "import tqdm" &> /dev/null; then
    echo "tqdm 安装失败"
    INSTALL_OK=0
fi

if [ $INSTALL_OK -eq 1 ]; then
    echo "所有最小依赖项安装成功!"
    echo ""
    echo "使用说明："
    echo "现在你可以运行无图表版本的模拟训练脚本："
    echo "  python mock_training_no_plots.py --output_dir ./output --model_name bert-base-chinese --task_type classification --num_train_epochs 3"
    echo ""
    echo "如果需要完整功能（包括图表生成），请运行完整的安装脚本：install_dependencies.sh"
else
    echo "部分依赖项安装失败，请检查错误信息并重试。"
fi 