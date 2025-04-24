#!/bin/bash
# 安装模型训练所需的依赖项

echo "开始安装模型训练所需的依赖项..."

# 确认项目目录路径
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODEL_DIR="$PROJECT_DIR/model"

echo "项目目录: $PROJECT_DIR"
echo "模型目录: $MODEL_DIR"

# 检查是否安装了pip
if ! command -v pip &> /dev/null; then
    echo "未找到pip，请先安装Python和pip"
    exit 1
fi

# 创建虚拟环境（可选）
echo "是否创建虚拟环境? (y/n)"
read -r create_venv

if [[ "$create_venv" == "y" || "$create_venv" == "Y" ]]; then
    # 检查是否安装了virtualenv
    if ! command -v virtualenv &> /dev/null; then
        echo "安装virtualenv..."
        pip install virtualenv
    fi
    
    echo "创建虚拟环境..."
    if [ -d "$PROJECT_DIR/venv" ]; then
        echo "虚拟环境已存在。是否重新创建? (y/n)"
        read -r recreate_venv
        if [[ "$recreate_venv" == "y" || "$recreate_venv" == "Y" ]]; then
            rm -rf "$PROJECT_DIR/venv"
            virtualenv "$PROJECT_DIR/venv"
        fi
    else
        virtualenv "$PROJECT_DIR/venv"
    fi
    
    # 激活虚拟环境
    echo "激活虚拟环境..."
    if [[ "$OSTYPE" == "darwin"* || "$OSTYPE" == "linux-gnu"* ]]; then
        # MacOS或Linux
        source "$PROJECT_DIR/venv/bin/activate"
    elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        source "$PROJECT_DIR/venv/Scripts/activate"
    else
        echo "无法识别的操作系统类型: $OSTYPE"
        exit 1
    fi
fi

# 安装基本依赖项
echo "安装基本依赖项..."
pip install -r "$MODEL_DIR/requirements.txt"

# 安装最少依赖项（不包括matplotlib，用于运行无图表版本的脚本）
echo "安装最少依赖项(用于无图表版本)..."
pip install numpy pandas tqdm

echo "依赖项安装完成！"

# 运行测试以验证安装
echo "运行简单测试以验证安装..."
python -c "import numpy; import pandas; import tqdm; print('基本库导入成功！')"

# 简单使用说明
echo ""
echo "=== 使用说明 ==="
echo "1. 如果安装了所有依赖项，可以使用 mock_training.py 运行完整的模拟训练："
echo "   python $MODEL_DIR/mock_training.py --output_dir ./output --model_name bert-base-chinese --task_type classification --num_train_epochs 3"
echo ""
echo "2. 如果只安装了基本依赖项，可以使用 mock_training_no_plots.py 运行无图表版本的模拟训练："
echo "   python $MODEL_DIR/mock_training_no_plots.py --output_dir ./output --model_name bert-base-chinese --task_type classification --num_train_epochs 3"
echo ""
echo "3. 模拟预测："
echo "   python $MODEL_DIR/mock_predict.py --model_path ./output/best_model --input_file ./sample.txt --output_file ./predictions.txt"
echo ""
echo "4. 如果你创建了虚拟环境，使用前请先激活："
echo "   source $PROJECT_DIR/venv/bin/activate  # Linux/MacOS"
echo "   $PROJECT_DIR/venv/Scripts/activate     # Windows"
echo ""
echo "安装和配置完成！" 