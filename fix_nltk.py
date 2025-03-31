import os
import ssl
import nltk
import shutil
import time
import sys

def download_nltk_resources():
    """下载NLTK所需的资源"""
    print("开始修复NLTK资源...")
    
    # 禁用SSL证书验证
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # 下载基本资源
    print("1. 下载punkt资源包...")
    nltk.download('punkt')
    
    # 检查punkt资源是否下载成功
    try:
        nltk.data.find('tokenizers/punkt')
        print("   - punkt资源下载成功")
    except LookupError:
        print("   - punkt资源下载失败")
        sys.exit(1)
    
    # 处理英文punkt_tab资源
    nltk_data_dir = os.path.expanduser('~/nltk_data')
    punkt_dir = os.path.join(nltk_data_dir, 'tokenizers', 'punkt')
    punkt_tab_dir = os.path.join(nltk_data_dir, 'tokenizers', 'punkt_tab')
    punkt_tab_english_dir = os.path.join(punkt_tab_dir, 'english')
    
    # 创建特定的目录结构
    print("2. 创建punkt_tab目录结构...")
    os.makedirs(punkt_tab_english_dir, exist_ok=True)
    print(f"   - 创建目录: {punkt_tab_english_dir}")
    
    # 复制english.pickle到punkt_tab/english/
    english_pickle = os.path.join(punkt_dir, 'english.pickle')
    if os.path.exists(english_pickle):
        dest_file = os.path.join(punkt_tab_english_dir, 'punkt.pickle')
        shutil.copy2(english_pickle, dest_file)
        print(f"   - 复制: {english_pickle} -> {dest_file}")
    else:
        print(f"   - 警告: 找不到源文件 {english_pickle}")
    
    # 也下载其他可能有用的语言模型
    print("3. 下载可能需要的其他资源...")
    resources = [
        'averaged_perceptron_tagger',
        'wordnet'
    ]
    
    for resource in resources:
        print(f"   - 下载 {resource}...")
        nltk.download(resource)
    
    print("\nNLTK资源修复完成！")

if __name__ == "__main__":
    download_nltk_resources() 