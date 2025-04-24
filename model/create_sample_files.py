#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成样例文件
用于创建测试数据，以便与模拟训练和预测一起使用
"""

import os
import csv
import argparse
import random
import json

def create_classification_data(output_dir, num_samples=100):
    """
    创建文本分类样例数据
    
    Args:
        output_dir: 输出目录
        num_samples: 样本数量
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义标签
    labels = ["教育", "技术", "经济", "娱乐", "体育"]
    
    # 为每个标签创建一些示例文本
    example_texts = {
        "教育": [
            "如何提高学生的学习效率是每位教师都关心的问题。",
            "在线教育平台为学生提供了更多自主学习的机会。",
            "教育改革应当注重学生的全面发展。",
            "批判性思维是现代教育中不可或缺的一部分。",
            "教育的目的不仅是传授知识，更是培养人格。",
            "好的教育应当激发学生的学习兴趣和好奇心。",
            "远程学习在疫情期间展现出了巨大的潜力。",
            "教育应当因材施教，关注个体差异。",
            "终身学习的理念已经成为现代教育的重要方向。",
            "教师应该不断更新自己的知识体系和教学方法。"
        ],
        "技术": [
            "人工智能技术正在改变我们的生活方式。",
            "区块链技术为金融行业带来了革命性变化。",
            "云计算使企业的IT架构变得更加灵活。",
            "5G技术的普及将促进物联网的发展。",
            "大数据分析帮助企业做出更明智的决策。",
            "虚拟现实技术为游戏产业开辟了新的可能性。",
            "量子计算有望解决传统计算机难以处理的问题。",
            "自动驾驶技术正在逐步成熟。",
            "边缘计算减少了数据传输的延迟。",
            "自然语言处理技术使机器能够更好地理解人类语言。"
        ],
        "经济": [
            "全球通货膨胀引发了市场的担忧。",
            "央行调整利率政策以应对经济波动。",
            "供应链中断导致了某些商品的价格上涨。",
            "经济复苏步伐不一，区域差异明显。",
            "国际贸易摩擦对全球经济造成了不确定性。",
            "数字经济成为经济增长的新引擎。",
            "可持续发展理念正在影响经济政策的制定。",
            "消费升级推动了高品质产品和服务的需求。",
            "小微企业在促进就业和创新方面发挥着重要作用。",
            "绿色金融为环保项目提供了资金支持。"
        ],
        "娱乐": [
            "新上映的电影票房创下了历史纪录。",
            "流媒体平台正在改变人们的观影习惯。",
            "这位歌手的新专辑获得了广泛好评。",
            "电子游戏产业规模不断扩大。",
            "短视频平台为内容创作者提供了新的舞台。",
            "综艺节目的创新形式吸引了年轻观众。",
            "传统文化元素在现代娱乐作品中得到了新的诠释。",
            "虚拟偶像的出现为娱乐产业带来了新的可能性。",
            "粉丝经济成为娱乐产业的重要组成部分。",
            "音乐节吸引了大量热爱音乐的年轻人。"
        ],
        "体育": [
            "国家队在本次比赛中表现出色，赢得了金牌。",
            "这位运动员打破了世界纪录。",
            "足球比赛吸引了数万名观众。",
            "冬季奥运会将在明年举行。",
            "体育产业的商业价值日益凸显。",
            "青少年体育教育受到越来越多的重视。",
            "电子竞技正在被更多人认可为一种体育形式。",
            "体育赛事的直播为平台带来了大量流量。",
            "健身已经成为许多城市居民的生活方式。",
            "极限运动的爱好者数量不断增加。"
        ]
    }
    
    # 生成训练数据
    train_data = []
    for _ in range(int(num_samples * 0.7)):  # 70%用于训练
        label = random.choice(labels)
        text = random.choice(example_texts[label])
        # 添加一些随机变化
        if random.random() < 0.5:
            text = text.replace("。", "。" + random.choice(["此外，", "同时，", "另外，", "值得注意的是，", ""]))
        train_data.append({"text": text, "label": label})
    
    # 生成验证数据
    dev_data = []
    for _ in range(int(num_samples * 0.15)):  # 15%用于验证
        label = random.choice(labels)
        text = random.choice(example_texts[label])
        # 添加一些随机变化
        if random.random() < 0.5:
            text = text.replace("。", "。" + random.choice(["此外，", "同时，", "另外，", "值得注意的是，", ""]))
        dev_data.append({"text": text, "label": label})
    
    # 生成测试数据
    test_data = []
    for _ in range(int(num_samples * 0.15)):  # 15%用于测试
        label = random.choice(labels)
        text = random.choice(example_texts[label])
        # 添加一些随机变化
        if random.random() < 0.5:
            text = text.replace("。", "。" + random.choice(["此外，", "同时，", "另外，", "值得注意的是，", ""]))
        test_data.append({"text": text, "label": label})
    
    # 写入CSV文件
    for data, filename in [(train_data, "train.csv"), (dev_data, "dev.csv"), (test_data, "test.csv")]:
        with open(os.path.join(output_dir, filename), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "label"])
            writer.writeheader()
            writer.writerows(data)
        print(f"已创建文件: {os.path.join(output_dir, filename)}")
    
    # 创建一个单独的测试文本文件
    with open(os.path.join(output_dir, "test_samples.txt"), "w", encoding="utf-8") as f:
        for item in test_data:
            f.write(f"{item['text']}\n")
        print(f"已创建文件: {os.path.join(output_dir, 'test_samples.txt')}")

def create_ner_data(output_dir, num_samples=50):
    """
    创建命名实体识别样例数据
    
    Args:
        output_dir: 输出目录
        num_samples: 样本数量
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 定义一些词语和对应的实体类型
    entity_examples = {
        "PER": ["张三", "李四", "王五", "赵六", "钱七", "孙八", "周九", "吴十",
               "马云", "李彦宏", "马化腾", "刘强东", "雷军", "王健林", "任正非", "李嘉诚"],
        "ORG": ["阿里巴巴", "腾讯", "百度", "京东", "小米", "华为", "字节跳动", "美团",
               "清华大学", "北京大学", "复旦大学", "上海交通大学", "中国人民大学", "浙江大学", "南京大学", "武汉大学"],
        "LOC": ["北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都",
               "重庆", "西安", "天津", "苏州", "长沙", "青岛", "宁波", "郑州"]
    }
    
    # 定义一些句子模板
    templates = [
        "{PER}在{LOC}工作。",
        "{PER}是{ORG}的创始人。",
        "{ORG}总部位于{LOC}。",
        "{PER}参观了{LOC}的{ORG}。",
        "{PER}和{PER}共同创办了{ORG}。",
        "{ORG}在{LOC}设立了分支机构。",
        "{PER}毕业于{ORG}。",
        "{LOC}举办了一场会议，{PER}作为{ORG}的代表参加了。",
        "{ORG}的{PER}访问了{LOC}。",
        "{PER}在{LOC}的{ORG}工作。"
    ]
    
    # 生成NER数据
    def generate_ner_samples(n):
        samples = []
        for _ in range(n):
            template = random.choice(templates)
            
            # 替换模板中的实体
            entities = []
            words = []
            
            # 记录当前句子中已使用的实体，避免重复
            used_entities = {entity_type: [] for entity_type in entity_examples}
            
            # 当前处理到的位置
            current_pos = 0
            
            while "{" in template[current_pos:]:
                start = template.find("{", current_pos)
                end = template.find("}", start)
                
                if start > current_pos:
                    # 添加普通文本
                    plain_text = template[current_pos:start]
                    words.extend(list(plain_text))
                
                # 处理实体
                entity_type = template[start+1:end]
                available_entities = [e for e in entity_examples[entity_type] if e not in used_entities[entity_type]]
                
                if not available_entities:
                    available_entities = entity_examples[entity_type]
                
                entity_text = random.choice(available_entities)
                used_entities[entity_type].append(entity_text)
                
                entity_words = list(entity_text)
                entity_start = len(words)
                entity_end = entity_start + len(entity_words)
                
                # BIO标注
                for i, word in enumerate(entity_words):
                    words.append(word)
                    if i == 0:
                        tag = f"B-{entity_type}"
                    else:
                        tag = f"I-{entity_type}"
                    entities.append({"text": word, "type": entity_type, "tag": tag})
                
                current_pos = end + 1
            
            # 处理模板末尾的普通文本
            if current_pos < len(template):
                plain_text = template[current_pos:]
                words.extend(list(plain_text))
            
            # 创建样本数据
            word_tags = []
            for i, word in enumerate(words):
                is_entity = False
                for entity in entities:
                    if entity["text"] == word and len(word_tags) < len(words):
                        word_tags.append(entity["tag"])
                        is_entity = True
                        break
                if not is_entity and len(word_tags) < len(words):
                    word_tags.append("O")
            
            # 确保words和word_tags长度一致
            assert len(words) == len(word_tags), f"长度不匹配：words={len(words)}, tags={len(word_tags)}"
            
            # 字符级别的处理
            final_text = "".join(words)
            final_words = list(final_text)
            final_tags = []
            
            i = 0
            while i < len(final_text):
                is_entity = False
                for entity in entities:
                    if final_text[i:].startswith(entity["text"]):
                        entity_len = len(entity["text"])
                        final_tags.append(entity["tag"])
                        i += 1
                        # 处理剩余字符
                        for j in range(1, entity_len):
                            if i < len(final_text):
                                final_tags.append(f"I-{entity['type']}")
                                i += 1
                        is_entity = True
                        break
                if not is_entity:
                    final_tags.append("O")
                    i += 1
            
            # 确保长度匹配
            if len(final_tags) > len(final_words):
                final_tags = final_tags[:len(final_words)]
            elif len(final_tags) < len(final_words):
                final_tags.extend(["O"] * (len(final_words) - len(final_tags)))
            
            samples.append({
                "text": final_text,
                "words": final_words,
                "labels": final_tags
            })
        return samples
    
    # 生成训练数据、验证数据和测试数据
    train_samples = generate_ner_samples(int(num_samples * 0.7))  # 70%用于训练
    dev_samples = generate_ner_samples(int(num_samples * 0.15))   # 15%用于验证
    test_samples = generate_ner_samples(int(num_samples * 0.15))  # 15%用于测试
    
    # 写入JSON文件
    for samples, filename in [(train_samples, "train.json"), (dev_samples, "dev.json"), (test_samples, "test.json")]:
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
            json.dump(samples, f, ensure_ascii=False, indent=2)
        print(f"已创建文件: {os.path.join(output_dir, filename)}")
    
    # 创建一个单独的测试文本文件
    with open(os.path.join(output_dir, "test_samples.txt"), "w", encoding="utf-8") as f:
        for item in test_samples:
            f.write(f"{item['text']}\n")
        print(f"已创建文件: {os.path.join(output_dir, 'test_samples.txt')}")

def main():
    parser = argparse.ArgumentParser(description="生成样例数据文件")
    
    parser.add_argument("--task_type", type=str, default="classification", 
                      choices=["classification", "ner"], 
                      help="任务类型")
    parser.add_argument("--output_dir", type=str, default="./data", 
                       help="输出目录")
    parser.add_argument("--num_samples", type=int, default=100, 
                       help="生成的样本数量")
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"生成 {args.task_type} 任务的样例数据，数量：{args.num_samples}，输出目录：{args.output_dir}")
    
    if args.task_type == "classification":
        create_classification_data(args.output_dir, args.num_samples)
    elif args.task_type == "ner":
        create_ner_data(args.output_dir, args.num_samples)
    
    print("样例数据生成完成！")

if __name__ == "__main__":
    main() 