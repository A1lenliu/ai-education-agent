from typing import Dict, Any
import json
import os
import glob
import re
import ast
import subprocess
from datetime import datetime
import hashlib
import shutil
import logging

logger = logging.getLogger(__name__)

class ToolSet:
    def __init__(self):
        self.tools = {}
        # 设置基础目录为项目根目录
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logger.info(f"设置基础目录: {self.base_dir}")
        self._register_default_tools()
    
    def _resolve_path(self, path: str) -> str:
        """解析路径，如果是相对路径则基于基础目录"""
        if os.path.isabs(path):
            return path
        return os.path.join(self.base_dir, path)
    
    def _register_default_tools(self):
        """注册默认的工具集"""
        # 文件读取工具
        self.register_tool(
            name="read_file",
            description="读取指定文件的内容",
            parameters={
                "file_path": "要读取的文件路径（相对于项目根目录）",
                "start_line": "开始行号（可选）",
                "end_line": "结束行号（可选）"
            },
            handler=self._read_file
        )
        
        # 文件搜索工具
        self.register_tool(
            name="search_files",
            description="在指定目录中搜索文件",
            parameters={
                "directory": "要搜索的目录路径（相对于项目根目录，默认为项目根目录）",
                "pattern": "文件匹配模式（例如：*.py）"
            },
            handler=self._search_files
        )
        
        # 代码分析工具
        self.register_tool(
            name="analyze_code",
            description="分析代码文件的结构和内容",
            parameters={
                "file_path": "要分析的代码文件路径（相对于项目根目录）"
            },
            handler=self._analyze_code
        )

        # 文件内容搜索工具
        self.register_tool(
            name="search_content",
            description="在文件中搜索特定内容",
            parameters={
                "directory": "要搜索的目录路径（相对于项目根目录，默认为项目根目录）",
                "pattern": "要搜索的内容（支持正则表达式）",
                "file_pattern": "文件匹配模式（例如：*.py）"
            },
            handler=self._search_content
        )

        # 代码复杂度分析工具
        self.register_tool(
            name="analyze_complexity",
            description="分析代码的复杂度",
            parameters={
                "file_path": "要分析的代码文件路径（相对于项目根目录）"
            },
            handler=self._analyze_complexity
        )

        # 文件统计工具
        self.register_tool(
            name="file_stats",
            description="获取文件的统计信息",
            parameters={
                "file_path": "要统计的文件路径（相对于项目根目录）"
            },
            handler=self._file_stats
        )

        # 目录结构分析工具
        self.register_tool(
            name="analyze_directory",
            description="分析目录结构",
            parameters={
                "directory": "要分析的目录路径（相对于项目根目录，默认为项目根目录）",
                "max_depth": "最大递归深度（可选）"
            },
            handler=self._analyze_directory
        )

        # 文件比较工具
        self.register_tool(
            name="compare_files",
            description="比较两个文件的内容",
            parameters={
                "file1_path": "第一个文件路径（相对于项目根目录）",
                "file2_path": "第二个文件路径（相对于项目根目录）"
            },
            handler=self._compare_files
        )

        # 代码依赖分析工具
        self.register_tool(
            name="analyze_dependencies",
            description="分析代码的依赖关系",
            parameters={
                "file_path": "要分析的代码文件路径（相对于项目根目录）"
            },
            handler=self._analyze_dependencies
        )

        # 文件备份工具
        self.register_tool(
            name="backup_file",
            description="创建文件的备份",
            parameters={
                "file_path": "要备份的文件路径（相对于项目根目录）",
                "backup_dir": "备份目录（相对于项目根目录，可选）"
            },
            handler=self._backup_file
        )

        # 代码注释分析工具
        self.register_tool(
            name="analyze_comments",
            description="分析代码中的注释情况",
            parameters={
                "file_path": "要分析的代码文件路径（相对于项目根目录）"
            },
            handler=self._analyze_comments
        )

        # 代码风格检查工具
        self.register_tool(
            name="check_code_style",
            description="检查代码风格是否符合 PEP 8 规范",
            parameters={
                "file_path": "要检查的代码文件路径（相对于项目根目录）"
            },
            handler=self._check_code_style
        )

        # 代码重复检测工具
        self.register_tool(
            name="detect_duplicates",
            description="检测代码中的重复片段",
            parameters={
                "directory": "要检查的目录路径（相对于项目根目录，默认为项目根目录）",
                "min_lines": "最小重复行数（可选，默认为6）"
            },
            handler=self._detect_duplicates
        )

        # 代码测试覆盖率分析工具
        self.register_tool(
            name="analyze_test_coverage",
            description="分析代码的测试覆盖率",
            parameters={
                "file_path": "要分析的代码文件路径（相对于项目根目录）"
            },
            handler=self._analyze_test_coverage
        )

        # 代码文档生成工具
        self.register_tool(
            name="generate_docs",
            description="为代码生成文档",
            parameters={
                "file_path": "要生成文档的代码文件路径（相对于项目根目录）",
                "output_format": "输出格式（可选：'markdown' 或 'html'，默认为 'markdown'）"
            },
            handler=self._generate_docs
        )
        
        # 教育内容总结工具
        self.register_tool(
            name="summarize_education_content",
            description="总结教育内容文档，提取重要信息和关键点",
            parameters={
                "file_path": "要总结的教育内容文件路径（相对于项目根目录）",
                "max_points": "最大提取要点数量（可选，默认为5）",
                "focus_area": "关注的特定领域或方面（可选）"
            },
            handler=self._summarize_education_content
        )
        
        # 多语言翻译工具
        self.register_tool(
            name="translate_content",
            description="将文本内容翻译成指定语言",
            parameters={
                "text": "要翻译的文本内容",
                "target_language": "目标语言（如：英语、中文、日语、法语等）",
                "source_language": "源语言（可选，默认自动检测）"
            },
            handler=self._translate_content
        )
        
        # 代码解释工具
        self.register_tool(
            name="explain_code",
            description="解释代码片段或函数的功能和工作原理",
            parameters={
                "file_path": "要解释的代码文件路径（相对于项目根目录）",
                "start_line": "开始行号（可选）",
                "end_line": "结束行号（可选）",
                "detail_level": "解释详细程度（简单、中等、详细，默认为中等）"
            },
            handler=self._explain_code
        )
        
        # 学习路径生成工具
        self.register_tool(
            name="generate_learning_path",
            description="根据学习目标生成个性化学习路径",
            parameters={
                "topic": "学习主题",
                "learner_level": "学习者水平（初级、中级、高级）",
                "time_frame": "计划的学习时间框架（如：2周、1个月）",
                "focus_areas": "希望关注的特定领域（可选）"
            },
            handler=self._generate_learning_path
        )
        
        # 知识图谱构建工具
        self.register_tool(
            name="build_knowledge_graph",
            description="构建特定主题的知识图谱",
            parameters={
                "topic": "知识图谱主题",
                "depth": "知识图谱深度（1-3，默认为2）",
                "include_related": "是否包含相关主题（可选，默认为True）"
            },
            handler=self._build_knowledge_graph
        )
        
        # 教学素材推荐工具
        self.register_tool(
            name="recommend_teaching_materials",
            description="根据教学目标推荐适合的教学素材",
            parameters={
                "subject": "学科领域",
                "grade_level": "年级水平",
                "learning_objective": "学习目标",
                "material_type": "素材类型（如：视频、阅读材料、练习）（可选）",
                "duration": "建议的课程时长（可选）"
            },
            handler=self._recommend_teaching_materials
        )
    
    def register_tool(self, name: str, description: str, parameters: Dict[str, Any], handler):
        """注册新工具"""
        self.tools[name] = {
            "description": description,
            "parameters": parameters,
            "handler": handler
        }
    
    async def _read_file(self, file_path: str, start_line: int = None, end_line: int = None) -> str:
        """读取文件内容的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if start_line is not None and end_line is not None:
                    lines = lines[start_line-1:end_line]
                return ''.join(lines)
        except Exception as e:
            return f"读取文件时出错: {str(e)}"
    
    async def _search_files(self, directory: str = None, pattern: str = "*.py") -> str:
        """搜索文件的工具实现"""
        try:
            if directory is None:
                directory = self.base_dir
            resolved_dir = self._resolve_path(directory)
            files = glob.glob(os.path.join(resolved_dir, pattern))
            return json.dumps(files, ensure_ascii=False)
        except Exception as e:
            return f"搜索文件时出错: {str(e)}"
    
    async def _analyze_code(self, file_path: str) -> str:
        """分析代码的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return f"文件 {file_path} 的基本信息：\n" + \
                       f"- 总行数: {len(content.splitlines())}\n" + \
                       f"- 文件大小: {len(content)} 字节"
        except Exception as e:
            return f"分析代码时出错: {str(e)}"

    async def _search_content(self, directory: str = None, pattern: str = None, file_pattern: str = "*.py") -> str:
        """搜索文件内容的工具实现"""
        try:
            if directory is None:
                directory = self.base_dir
            resolved_dir = self._resolve_path(directory)
            results = []
            for file_path in glob.glob(os.path.join(resolved_dir, file_pattern)):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            results.append({
                                "file": file_path,
                                "line": content[:match.start()].count('\n') + 1,
                                "content": match.group()
                            })
                except Exception:
                    continue
            return json.dumps(results, ensure_ascii=False)
        except Exception as e:
            return f"搜索内容时出错: {str(e)}"

    async def _analyze_complexity(self, file_path: str) -> str:
        """分析代码复杂度的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
                # 计算圈复杂度
                complexity = 1  # 基础复杂度
                for node in ast.walk(tree):
                    if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.AsyncWith)):
                        complexity += 1
                    elif isinstance(node, ast.BoolOp):
                        complexity += len(node.values) - 1
                
                # 计算函数数量
                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                
                return f"代码复杂度分析结果：\n" + \
                       f"- 圈复杂度: {complexity}\n" + \
                       f"- 函数数量: {len(functions)}\n" + \
                       f"- 函数列表: {[f.name for f in functions]}"
        except Exception as e:
            return f"分析复杂度时出错: {str(e)}"

    async def _file_stats(self, file_path: str) -> str:
        """获取文件统计信息的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            stats = os.stat(resolved_path)
            return f"文件统计信息：\n" + \
                   f"- 大小: {stats.st_size} 字节\n" + \
                   f"- 创建时间: {datetime.fromtimestamp(stats.st_ctime)}\n" + \
                   f"- 修改时间: {datetime.fromtimestamp(stats.st_mtime)}\n" + \
                   f"- 访问时间: {datetime.fromtimestamp(stats.st_atime)}\n" + \
                   f"- 权限: {oct(stats.st_mode)[-3:]}"
        except Exception as e:
            return f"获取文件统计信息时出错: {str(e)}"

    async def _analyze_directory(self, directory: str = None, max_depth: int = 3) -> str:
        """分析目录结构的工具实现"""
        try:
            if directory is None:
                directory = self.base_dir
            resolved_dir = self._resolve_path(directory)
            
            def get_tree(path: str, depth: int = 0) -> Dict[str, Any]:
                if depth > max_depth:
                    return {"name": os.path.basename(path), "type": "file"}
                
                result = {"name": os.path.basename(path), "type": "directory", "children": []}
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        result["children"].append(get_tree(item_path, depth + 1))
                    else:
                        result["children"].append({"name": item, "type": "file"})
                return result
            
            tree = get_tree(resolved_dir)
            return json.dumps(tree, ensure_ascii=False, indent=2)
        except Exception as e:
            return f"分析目录结构时出错: {str(e)}"

    async def _compare_files(self, file1_path: str, file2_path: str) -> str:
        """比较文件内容的工具实现"""
        try:
            resolved_path1 = self._resolve_path(file1_path)
            resolved_path2 = self._resolve_path(file2_path)
            with open(resolved_path1, 'r', encoding='utf-8') as f1, \
                 open(resolved_path2, 'r', encoding='utf-8') as f2:
                content1 = f1.read()
                content2 = f2.read()
                
                # 计算文件哈希
                hash1 = hashlib.md5(content1.encode()).hexdigest()
                hash2 = hashlib.md5(content2.encode()).hexdigest()
                
                if hash1 == hash2:
                    return "文件内容完全相同"
                
                # 计算行数差异
                lines1 = content1.splitlines()
                lines2 = content2.splitlines()
                
                return f"文件比较结果：\n" + \
                       f"- 文件1行数: {len(lines1)}\n" + \
                       f"- 文件2行数: {len(lines2)}\n" + \
                       f"- 行数差异: {abs(len(lines1) - len(lines2))}"
        except Exception as e:
            return f"比较文件时出错: {str(e)}"

    async def _analyze_dependencies(self, file_path: str) -> str:
        """分析代码依赖关系的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
                
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.append(name.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for name in node.names:
                            imports.append(f"{module}.{name.name}")
                
                return f"依赖分析结果：\n" + \
                       f"- 导入模块: {', '.join(imports)}"
        except Exception as e:
            return f"分析依赖关系时出错: {str(e)}"

    async def _backup_file(self, file_path: str, backup_dir: str = None) -> str:
        """创建文件备份的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            if backup_dir is None:
                backup_dir = os.path.join(os.path.dirname(resolved_path), "backups")
            resolved_backup_dir = self._resolve_path(backup_dir)
            os.makedirs(resolved_backup_dir, exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.basename(file_path)}_{timestamp}"
            backup_path = os.path.join(resolved_backup_dir, backup_name)
            
            # 复制文件
            shutil.copy2(resolved_path, backup_path)
            
            return f"文件备份成功：\n" + \
                   f"- 原文件: {file_path}\n" + \
                   f"- 备份文件: {backup_path}"
        except Exception as e:
            return f"创建备份时出错: {str(e)}"

    async def _analyze_comments(self, file_path: str) -> str:
        """分析代码注释的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                
                # 统计注释
                comment_lines = [line for line in lines if line.strip().startswith('#')]
                docstring_lines = []
                in_docstring = False
                
                for line in lines:
                    if '"""' in line or "'''" in line:
                        in_docstring = not in_docstring
                    elif in_docstring:
                        docstring_lines.append(line)
                
                total_lines = len(lines)
                comment_count = len(comment_lines)
                docstring_count = len(docstring_lines)
                
                return f"代码注释分析结果：\n" + \
                       f"- 总行数: {total_lines}\n" + \
                       f"- 注释行数: {comment_count}\n" + \
                       f"- 文档字符串行数: {docstring_count}\n" + \
                       f"- 注释覆盖率: {(comment_count + docstring_count) / total_lines * 100:.2f}%"
        except Exception as e:
            return f"分析注释时出错: {str(e)}"

    async def _check_code_style(self, file_path: str) -> str:
        """检查代码风格的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            # 使用 pycodestyle 检查代码风格
            import pycodestyle
            style_guide = pycodestyle.StyleGuide()
            result = style_guide.check_files([resolved_path])
            
            if result.total_errors == 0:
                return "代码风格检查通过，符合 PEP 8 规范"
            else:
                return f"代码风格检查发现 {result.total_errors} 个问题：\n" + \
                       "\n".join([f"- 行 {error.line}: {error.text}" for error in result.messages])
        except Exception as e:
            return f"检查代码风格时出错: {str(e)}"

    async def _detect_duplicates(self, directory: str = None, min_lines: int = 6) -> str:
        """检测代码重复的工具实现"""
        try:
            if directory is None:
                directory = self.base_dir
            resolved_dir = self._resolve_path(directory)
            
            # 收集所有 Python 文件
            python_files = []
            for root, _, files in os.walk(resolved_dir):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
            
            # 检测重复代码
            duplicates = []
            for i, file1 in enumerate(python_files):
                with open(file1, 'r', encoding='utf-8') as f1:
                    content1 = f1.read()
                    lines1 = content1.splitlines()
                    
                    for file2 in python_files[i+1:]:
                        with open(file2, 'r', encoding='utf-8') as f2:
                            content2 = f2.read()
                            lines2 = content2.splitlines()
                            
                            # 查找重复片段
                            for i in range(len(lines1) - min_lines + 1):
                                for j in range(len(lines2) - min_lines + 1):
                                    if lines1[i:i+min_lines] == lines2[j:j+min_lines]:
                                        duplicates.append({
                                            'file1': file1,
                                            'file2': file2,
                                            'lines': lines1[i:i+min_lines],
                                            'line1': i+1,
                                            'line2': j+1
                                        })
            
            if not duplicates:
                return "未发现重复代码片段"
            
            return "发现以下重复代码片段：\n" + \
                   "\n".join([f"- 文件 {d['file1']} 和 {d['file2']} 在第 {d['line1']} 行和第 {d['line2']} 行有重复代码" 
                            for d in duplicates])
        except Exception as e:
            return f"检测重复代码时出错: {str(e)}"

    async def _analyze_test_coverage(self, file_path: str) -> str:
        """分析测试覆盖率的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            # 使用 coverage.py 分析测试覆盖率
            import coverage
            cov = coverage.Coverage()
            cov.start()
            
            # 执行测试
            import subprocess
            subprocess.run(['python', '-m', 'pytest', resolved_path], check=True)
            
            cov.stop()
            cov.save()
            
            # 获取覆盖率报告
            report = cov.report()
            
            return f"测试覆盖率分析结果：\n{report}"
        except Exception as e:
            return f"分析测试覆盖率时出错: {str(e)}"

    async def _generate_docs(self, file_path: str, output_format: str = 'markdown') -> str:
        """生成代码文档的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            # 使用 pdoc 生成文档
            import pdoc
            
            module = pdoc.Module(resolved_path)
            if output_format == 'markdown':
                docs = pdoc.text(module)
            else:
                docs = pdoc.html(module)
            
            # 保存文档
            output_path = resolved_path.replace('.py', f'.{output_format}')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(docs)
            
            return f"文档已生成：{output_path}"
        except Exception as e:
            return f"生成文档时出错: {str(e)}"
    
    async def _summarize_education_content(self, file_path: str, max_points: int = 5, focus_area: str = None) -> str:
        """总结教育内容的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 内容分析逻辑
            lines = content.splitlines()
            
            # 提取标题
            titles = [line.strip('# ') for line in lines if line.startswith('#')]
            main_title = titles[0] if titles else "未找到标题"
            
            # 提取关键要点 - 这里简化实现，实际应用中可以使用更复杂的NLP技术
            bullet_points = []
            
            # 查找列表项（以 - 或 * 开头的行）
            for line in lines:
                line = line.strip()
                if (line.startswith('- ') or line.startswith('* ')) and len(line) > 2:
                    bullet_points.append(line[2:])
            
            # 如果指定了关注区域，过滤相关内容
            if focus_area:
                # 查找包含关注区域的部分
                focus_content = []
                in_focus = False
                for line in lines:
                    if focus_area.lower() in line.lower() and line.startswith('#'):
                        in_focus = True
                        focus_content.append(line)
                    elif in_focus and line.startswith('#'):
                        in_focus = False
                    elif in_focus:
                        focus_content.append(line)
                
                # 从关注内容中提取要点
                focus_bullet_points = []
                for line in focus_content:
                    line = line.strip()
                    if (line.startswith('- ') or line.startswith('* ')) and len(line) > 2:
                        focus_bullet_points.append(line[2:])
                
                if focus_bullet_points:
                    bullet_points = focus_bullet_points
            
            # 限制要点数量
            bullet_points = bullet_points[:max_points]
            
            # 生成总结
            summary = f"《{main_title}》内容总结：\n\n"
            if not bullet_points:
                summary += "未能提取到明确的要点，建议使用更精确的分析方法。\n"
            else:
                for i, point in enumerate(bullet_points, 1):
                    summary += f"{i}. {point}\n"
            
            # 计算字数和阅读时间
            word_count = len(content.split())
            reading_minutes = word_count // 200  # 假设平均阅读速度为每分钟200词
            
            summary += f"\n文档统计：\n- 字数：约 {word_count} 词\n- 预计阅读时间：约 {reading_minutes} 分钟"
            
            return summary
            
        except Exception as e:
            return f"总结教育内容时出错: {str(e)}"
    
    async def _translate_content(self, text: str, target_language: str, source_language: str = None) -> str:
        """翻译内容的工具实现"""
        try:
            # 这里仅模拟翻译功能，实际应用中应使用专业翻译API（如Google Translate API等）
            
            # 定义一些基本的翻译映射表（仅示例用）
            translations = {
                "中文": {
                    "hello": "你好",
                    "world": "世界",
                    "welcome": "欢迎",
                    "thanks": "谢谢",
                    "learning": "学习",
                    "education": "教育",
                    "artificial intelligence": "人工智能",
                    "computer": "计算机",
                    "teaching": "教学",
                    "student": "学生",
                },
                "英语": {
                    "你好": "hello",
                    "世界": "world",
                    "欢迎": "welcome",
                    "谢谢": "thanks",
                    "学习": "learning",
                    "教育": "education",
                    "人工智能": "artificial intelligence",
                    "计算机": "computer",
                    "教学": "teaching",
                    "学生": "student",
                }
            }
            
            # 模拟翻译过程
            if target_language in ["中文", "Chinese", "中国语", "汉语"]:
                target = "中文"
            elif target_language in ["英语", "English", "英文"]:
                target = "英语"
            else:
                return f"目前只支持中文和英语之间的翻译。您请求的目标语言 '{target_language}' 暂不支持。"
            
            # 简单替换词汇
            translated_text = text
            for word, translation in translations.get(target, {}).items():
                translated_text = translated_text.replace(word, translation)
            
            return f"原文：\n{text}\n\n翻译（{target}）：\n{translated_text}\n\n注意：这是简单模拟翻译，仅替换了少量关键词。"
            
        except Exception as e:
            return f"翻译内容时出错: {str(e)}"
    
    async def _explain_code(self, file_path: str, start_line: int = None, end_line: int = None, detail_level: str = "中等") -> str:
        """解释代码的工具实现"""
        try:
            resolved_path = self._resolve_path(file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                # 如果指定了行号范围，只解释该范围内的代码
                if start_line is not None and end_line is not None:
                    if start_line < 1:
                        start_line = 1
                    if end_line > len(lines):
                        end_line = len(lines)
                    code_lines = lines[start_line-1:end_line]
                else:
                    code_lines = lines
                
                code = ''.join(code_lines)
            
            # 确定文件类型
            file_extension = os.path.splitext(file_path)[1].lower()
            
            # 分析代码结构
            code_info = {}
            
            if file_extension == '.py':
                # Python代码分析
                try:
                    tree = ast.parse(code)
                    
                    # 统计函数和类
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    imports = []
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for name in node.names:
                                imports.append(name.name)
                        elif isinstance(node, ast.ImportFrom):
                            for name in node.names:
                                imports.append(f"{node.module}.{name.name}")
                    
                    code_info['functions'] = functions
                    code_info['classes'] = classes
                    code_info['imports'] = imports
                except:
                    code_info['note'] = "无法完整解析Python代码"
                    
            elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
                # JavaScript/TypeScript代码分析（非常简化的分析）
                function_pattern = r'function\s+(\w+)'
                class_pattern = r'class\s+(\w+)'
                import_pattern = r'import\s+.*?from\s+[\'"](.+?)[\'"]'
                
                functions = re.findall(function_pattern, code)
                classes = re.findall(class_pattern, code)
                imports = re.findall(import_pattern, code)
                
                code_info['functions'] = functions
                code_info['classes'] = classes
                code_info['imports'] = imports
            
            # 生成代码解释
            explanation = f"## 代码解释：{file_path}\n\n"
            
            # 添加代码片段
            explanation += "### 代码片段：\n```\n"
            explanation += code
            explanation += "\n```\n\n"
            
            # 根据详细程度调整解释内容
            explanation += "### 基本结构分析：\n"
            
            if 'functions' in code_info:
                explanation += f"- 函数数量：{len(code_info['functions'])}\n"
                if code_info['functions']:
                    explanation += "  - 函数名：" + ", ".join(code_info['functions']) + "\n"
            
            if 'classes' in code_info:
                explanation += f"- 类数量：{len(code_info['classes'])}\n"
                if code_info['classes']:
                    explanation += "  - 类名：" + ", ".join(code_info['classes']) + "\n"
            
            if 'imports' in code_info:
                explanation += f"- 导入模块数量：{len(code_info['imports'])}\n"
                if code_info['imports'] and (detail_level == "详细" or detail_level == "中等"):
                    explanation += "  - 导入模块：" + ", ".join(code_info['imports']) + "\n"
            
            # 添加代码复杂度分析
            explanation += "\n### 代码功能概述：\n"
            if file_extension == '.py':
                explanation += "这段Python代码"
                if 'classes' in code_info and code_info['classes']:
                    explanation += f"定义了{len(code_info['classes'])}个类"
                    if 'functions' in code_info and code_info['functions']:
                        explanation += f"和{len(code_info['functions'])}个函数。"
                    else:
                        explanation += "。"
                elif 'functions' in code_info and code_info['functions']:
                    explanation += f"定义了{len(code_info['functions'])}个函数。"
                else:
                    explanation += "主要包含脚本代码。"
            elif file_extension in ['.js', '.jsx']:
                explanation += "这段JavaScript代码"
                if 'classes' in code_info and code_info['classes']:
                    explanation += f"定义了{len(code_info['classes'])}个类"
                    if 'functions' in code_info and code_info['functions']:
                        explanation += f"和{len(code_info['functions'])}个函数。"
                    else:
                        explanation += "。"
                elif 'functions' in code_info and code_info['functions']:
                    explanation += f"定义了{len(code_info['functions'])}个函数。"
                else:
                    explanation += "主要包含脚本代码。"
            
            # 根据详细级别添加更多内容
            if detail_level == "详细":
                # 添加行数分析
                code_lines_count = len(code_lines)
                empty_lines = len([line for line in code_lines if line.strip() == ''])
                explanation += f"\n### 详细统计：\n"
                explanation += f"- 总行数：{code_lines_count}\n"
                explanation += f"- 空行数：{empty_lines}\n"
                explanation += f"- 代码密度：{(code_lines_count - empty_lines) / code_lines_count:.2f}\n"
                
                # 添加复杂度估算
                if file_extension == '.py':
                    try:
                        # 简单估算认知复杂度
                        loop_count = code.count('for ') + code.count('while ')
                        condition_count = code.count('if ') + code.count('elif ') + code.count('else:')
                        complexity_score = loop_count * 2 + condition_count
                        
                        explanation += f"- 估计复杂度：\n"
                        explanation += f"  - 循环结构数：{loop_count}\n"
                        explanation += f"  - 条件结构数：{condition_count}\n"
                        explanation += f"  - 总体复杂度评分：{complexity_score}\n"
                    except:
                        pass
            
            explanation += "\n### 使用建议：\n"
            explanation += "- 在理解该代码时，请注意函数调用关系和数据流向\n"
            if 'imports' in code_info and code_info['imports']:
                explanation += "- 确保相关依赖模块已正确安装\n"
            
            return explanation
        
        except Exception as e:
            return f"解释代码时出错: {str(e)}"
    
    async def _generate_learning_path(self, topic: str, learner_level: str, time_frame: str, focus_areas: str = None) -> str:
        """生成学习路径的工具实现"""
        try:
            # 确定学习级别
            if learner_level.lower() in ["beginner", "初级", "入门"]:
                level = "初级"
            elif learner_level.lower() in ["intermediate", "中级"]:
                level = "中级"
            elif learner_level.lower() in ["advanced", "高级", "专家"]:
                level = "高级"
            else:
                level = "中级"  # 默认为中级
            
            # 确定时间框架
            if "周" in time_frame or "week" in time_frame.lower():
                weeks = int(''.join(filter(str.isdigit, time_frame))) if any(c.isdigit() for c in time_frame) else 4
            elif "月" in time_frame or "month" in time_frame.lower():
                weeks = int(''.join(filter(str.isdigit, time_frame))) * 4 if any(c.isdigit() for c in time_frame) else 4
            elif "天" in time_frame or "day" in time_frame.lower():
                weeks = int(''.join(filter(str.isdigit, time_frame))) / 7 if any(c.isdigit() for c in time_frame) else 4
            else:
                weeks = 4  # 默认为4周
            
            # 解析关注领域
            focus_list = []
            if focus_areas:
                focus_list = [area.strip() for area in focus_areas.split(',')]
            
            # 生成学习路径
            path = f"## 《{topic}》{level}学习路径 ({time_frame})\n\n"
            
            # 添加概述
            path += "### 学习概述\n\n"
            path += f"本学习路径为{level}水平的学习者设计，涵盖{topic}的关键知识点和技能，"
            path += f"计划在{time_frame}内完成。"
            if focus_list:
                path += f"学习将特别关注：{', '.join(focus_list)}。"
            path += "\n\n"
            
            # 生成每周学习内容
            path += "### 学习进度规划\n\n"
            
            # 根据不同级别和主题定制内容
            topics_by_level = {
                "初级": [
                    "基础概念和术语",
                    "核心原理入门",
                    "基本技能实践",
                    "简单应用案例"
                ],
                "中级": [
                    "深入理论学习",
                    "高级概念和方法",
                    "综合技能练习",
                    "实际问题解决"
                ],
                "高级": [
                    "前沿理论研究",
                    "专业技能提升",
                    "复杂问题分析",
                    "创新应用开发"
                ]
            }
            
            # 选择合适的内容
            level_topics = topics_by_level.get(level, topics_by_level["中级"])
            
            # 根据周数分配内容
            weeks_int = int(weeks) if weeks >= 1 else 1
            topics_per_week = max(1, len(level_topics) // weeks_int)
            
            for week in range(1, weeks_int + 1):
                path += f"#### 第{week}周\n\n"
                
                # 计算本周主题
                start_idx = (week - 1) * topics_per_week
                end_idx = min(start_idx + topics_per_week, len(level_topics))
                weekly_topics = level_topics[start_idx:end_idx]
                
                # 如果是最后一周，添加所有剩余主题
                if week == weeks_int and end_idx < len(level_topics):
                    weekly_topics.extend(level_topics[end_idx:])
                
                for i, subtopic in enumerate(weekly_topics, 1):
                    path += f"- **{subtopic}**\n"
                    # 根据学习级别生成合适的学习活动
                    if level == "初级":
                        path += "  - 学习基础概念和定义\n"
                        path += "  - 完成引导式练习\n"
                        path += "  - 参与初级讨论和问答\n"
                    elif level == "中级":
                        path += "  - 深入学习理论和方法\n"
                        path += "  - 完成挑战性练习\n"
                        path += "  - 参与案例分析和小组讨论\n"
                    else:  # 高级
                        path += "  - 研究前沿论文和高级材料\n"
                        path += "  - 解决复杂问题和实际应用\n"
                        path += "  - 参与专题研讨和创新项目\n"
                
                path += "\n"
            
            # 添加推荐资源
            path += "### 推荐学习资源\n\n"
            
            if level == "初级":
                path += "#### 入门教材\n"
                path += "- 《" + topic + "基础入门》\n"
                path += "- 《" + topic + "初学者指南》\n\n"
                path += "#### 在线课程\n"
                path += "- " + topic + "入门系列视频课程\n"
                path += "- " + topic + "基础实践工作坊\n"
            elif level == "中级":
                path += "#### 进阶教材\n"
                path += "- 《" + topic + "进阶指南》\n"
                path += "- 《" + topic + "实践与应用》\n\n"
                path += "#### 在线课程\n"
                path += "- " + topic + "高级应用课程\n"
                path += "- " + topic + "案例分析研讨会\n"
            else:  # 高级
                path += "#### 专业教材\n"
                path += "- 《" + topic + "高级理论与实践》\n"
                path += "- 《" + topic + "前沿研究》\n\n"
                path += "#### 在线课程\n"
                path += "- " + topic + "专家级研讨课程\n"
                path += "- " + topic + "创新应用工作坊\n"
            
            path += "\n#### 补充资源\n"
            path += "- 专业论坛和社区\n"
            path += "- 实践项目和案例库\n"
            path += "- 专家访谈和讲座\n"
            
            # 添加评估方式
            path += "\n### 学习评估方式\n\n"
            path += "- 阶段性知识测验\n"
            path += "- 实践项目评估\n"
            path += "- 同行互评和反馈\n"
            if level == "高级":
                path += "- 原创研究或项目作品\n"
            
            # 添加成功标准
            path += "\n### 学习成功标准\n\n"
            if level == "初级":
                path += "- 掌握" + topic + "的基本概念和术语\n"
                path += "- 能够解决简单的相关问题\n"
                path += "- 完成基础实践项目\n"
            elif level == "中级":
                path += "- 深入理解" + topic + "的核心理论和方法\n"
                path += "- 能够解决中等复杂度的相关问题\n"
                path += "- 完成综合性实践项目\n"
            else:  # 高级
                path += "- 掌握" + topic + "的高级概念和前沿理论\n"
                path += "- 能够解决复杂的相关问题和实际应用\n"
                path += "- 完成创新性研究或项目\n"
            
            return path
            
        except Exception as e:
            return f"生成学习路径时出错: {str(e)}"
    
    async def _build_knowledge_graph(self, topic: str, depth: int = 2, include_related: bool = True) -> str:
        """构建知识图谱的工具实现"""
        try:
            # 验证参数
            if depth < 1:
                depth = 1
            elif depth > 3:
                depth = 3
            
            # 生成知识图谱（这里是简化实现，实际应用中可以使用更复杂的图谱构建算法）
            graph = f"# {topic} 知识图谱\n\n"
            
            # 添加图谱描述
            graph += f"## 概述\n\n"
            graph += f"此知识图谱展示了与 {topic} 相关的核心概念及其关系，深度设置为 {depth} 级。"
            if include_related:
                graph += " 包含相关联的周边主题。"
            graph += "\n\n"
            
            # 生成中心主题
            graph += f"## 中心主题：{topic}\n\n"
            
            # 生成一级子主题（使用简单的模拟数据）
            primary_concepts = self._generate_subconcepts(topic, 5)
            
            # 使用Markdown格式构建知识图谱
            for i, concept in enumerate(primary_concepts, 1):
                graph += f"### {i}. {concept}\n\n"
                
                # 如果深度>1，为每个一级概念生成二级概念
                if depth >= 2:
                    secondary_concepts = self._generate_subconcepts(concept, 3)
                    for j, sec_concept in enumerate(secondary_concepts, 1):
                        graph += f"#### {i}.{j} {sec_concept}\n\n"
                        
                        # 如果深度>2，为每个二级概念生成三级概念
                        if depth >= 3:
                            tertiary_concepts = self._generate_subconcepts(sec_concept, 2)
                            for k, ter_concept in enumerate(tertiary_concepts, 1):
                                graph += f"- {i}.{j}.{k} **{ter_concept}**\n"
                            graph += "\n"
            
            # 添加相关主题（如果需要）
            if include_related:
                graph += "## 相关主题\n\n"
                related_topics = self._generate_related_topics(topic, 4)
                
                for related in related_topics:
                    graph += f"- **{related}**: 与{topic}相关的领域，关注...\n"
            
            # 添加参考信息
            graph += "\n## 学习资源\n\n"
            graph += "- 教材和参考书\n"
            graph += "- 在线课程和教程\n"
            graph += "- 实践项目和案例\n"
            graph += "- 专家讲座和研讨会\n"
            
            return graph
            
        except Exception as e:
            return f"构建知识图谱时出错: {str(e)}"
    
    def _generate_subconcepts(self, parent_concept: str, count: int) -> list:
        """为知识图谱生成子概念（简化实现）"""
        # 这里使用简单的模拟数据，实际应用中可以使用更复杂的NLP技术或知识库
        concepts_map = {
            "人工智能": ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "强化学习"],
            "机器学习": ["监督学习", "无监督学习", "半监督学习"],
            "深度学习": ["神经网络", "CNN", "RNN", "Transformer"],
            "编程语言": ["Python", "Java", "JavaScript", "C++", "Go"],
            "Python": ["数据科学", "Web开发", "自动化", "人工智能应用"],
            "数据科学": ["数据分析", "数据可视化", "统计分析"],
            "教育技术": ["在线学习", "自适应学习", "教育游戏化", "虚拟现实教育", "学习分析"],
            "自适应学习": ["个性化学习路径", "实时反馈系统", "学习者模型"],
            "数学": ["代数", "几何", "微积分", "统计学", "离散数学"],
            "历史": ["古代史", "中世纪史", "近代史", "现代史", "区域历史研究"],
            "物理学": ["力学", "热力学", "电磁学", "量子物理", "相对论"],
            "生物学": ["分子生物学", "生态学", "进化论", "遗传学", "细胞生物学"],
            "文学": ["小说", "诗歌", "戏剧", "散文", "文学批评"],
            "心理学": ["认知心理学", "发展心理学", "社会心理学", "临床心理学", "教育心理学"],
            "教育学": ["课程设计", "教学方法", "教育评估", "教育心理学", "教育管理"]
        }
        
        # 尝试从映射中获取子概念
        if parent_concept in concepts_map:
            return concepts_map[parent_concept][:count]
        
        # 如果没有预定义的映射，生成通用子概念
        return [f"{parent_concept}的基础", f"{parent_concept}的应用", 
                f"{parent_concept}的研究方法", f"{parent_concept}的发展历史", 
                f"{parent_concept}的未来趋势"][:count]
    
    def _generate_related_topics(self, topic: str, count: int) -> list:
        """为知识图谱生成相关主题（简化实现）"""
        # 相关主题映射
        related_map = {
            "人工智能": ["计算机科学", "认知科学", "机器人学", "数据科学", "伦理学"],
            "机器学习": ["统计学", "数据挖掘", "模式识别", "最优化理论"],
            "编程语言": ["软件工程", "计算机体系结构", "算法", "数据结构"],
            "教育技术": ["教育学", "学习科学", "教育心理学", "人机交互"],
            "数学": ["物理学", "计算机科学", "工程学", "经济学", "统计学"],
            "物理学": ["数学", "天文学", "化学", "工程学", "材料科学"],
            "生物学": ["医学", "生物化学", "生态学", "进化论", "遗传学"],
            "心理学": ["神经科学", "社会学", "人类学", "医学", "教育学"]
        }
        
        # 尝试从映射中获取相关主题
        if topic in related_map:
            return related_map[topic][:count]
        
        # 如果没有预定义的映射，生成通用相关主题
        return ["教育应用", "研究方法", "技术支持", "理论基础"][:count]
    
    async def _recommend_teaching_materials(self, subject: str, grade_level: str, learning_objective: str, 
                                          material_type: str = None, duration: str = None) -> str:
        """推荐教学素材的工具实现"""
        try:
            # 解析年级水平
            if any(term in grade_level.lower() for term in ["小学", "elementary", "primary"]):
                level_category = "小学"
            elif any(term in grade_level.lower() for term in ["初中", "middle", "junior"]):
                level_category = "初中"
            elif any(term in grade_level.lower() for term in ["高中", "high", "senior"]):
                level_category = "高中"
            elif any(term in grade_level.lower() for term in ["大学", "college", "university"]):
                level_category = "大学"
            else:
                level_category = "通用"
            
            # 解析素材类型
            material_categories = []
            if material_type:
                if any(term in material_type.lower() for term in ["视频", "video"]):
                    material_categories.append("视频资源")
                if any(term in material_type.lower() for term in ["阅读", "reading", "书", "book"]):
                    material_categories.append("阅读材料")
                if any(term in material_type.lower() for term in ["练习", "exercise", "作业", "homework"]):
                    material_categories.append("练习和作业")
                if any(term in material_type.lower() for term in ["实验", "experiment", "活动", "activity"]):
                    material_categories.append("实验和活动")
            
            # 如果没有指定素材类型，默认包含所有类型
            if not material_categories:
                material_categories = ["视频资源", "阅读材料", "练习和作业", "实验和活动"]
            
            # 解析时长（如果有）
            time_description = ""
            if duration:
                time_description = f"（适合{duration}课时）"
            
            # 生成推荐内容
            recommendation = f"# 《{subject}》{level_category}教学素材推荐\n\n"
            
            # 添加学习目标和概述
            recommendation += "## 学习目标\n\n"
            recommendation += f"{learning_objective}\n\n"
            
            recommendation += "## 推荐教学素材\n\n"
            
            # 为每个素材类型生成推荐
            for category in material_categories:
                recommendation += f"### {category}{time_description}\n\n"
                
                # 根据不同类型和学科生成相应的素材建议
                if category == "视频资源":
                    recommendation += "1. **核心概念视频讲解**\n"
                    recommendation += f"   - 内容：{subject}的基本概念和原理讲解\n"
                    recommendation += "   - 特点：图文并茂，通俗易懂，适合初学者\n"
                    recommendation += "   - 建议用途：课前预习或课后复习\n\n"
                    
                    recommendation += "2. **互动演示视频**\n"
                    recommendation += f"   - 内容：{subject}关键知识点的可视化演示\n"
                    recommendation += "   - 特点：动态呈现，直观形象\n"
                    recommendation += "   - 建议用途：课堂引入或难点讲解\n\n"
                    
                    recommendation += "3. **实际应用案例视频**\n"
                    recommendation += f"   - 内容：{subject}在实际场景中的应用示例\n"
                    recommendation += "   - 特点：贴近实际，增强学习动机\n"
                    recommendation += "   - 建议用途：拓展学习或课堂讨论引入\n"
                
                elif category == "阅读材料":
                    recommendation += "1. **核心教材章节**\n"
                    recommendation += f"   - 内容：《{subject}标准教程》相关章节\n"
                    recommendation += "   - 特点：系统性强，内容权威\n"
                    recommendation += "   - 建议用途：基础阅读材料\n\n"
                    
                    recommendation += "2. **补充阅读文章**\n"
                    recommendation += f"   - 内容：与{subject}学习目标相关的专题文章\n"
                    recommendation += "   - 特点：针对性强，深入浅出\n"
                    recommendation += "   - 建议用途：拓展阅读或差异化学习\n\n"
                    
                    recommendation += "3. **图解参考材料**\n"
                    recommendation += f"   - 内容：{subject}概念图解和流程图\n"
                    recommendation += "   - 特点：直观易懂，便于记忆\n"
                    recommendation += "   - 建议用途：复习参考或墙面展示\n"
                
                elif category == "练习和作业":
                    recommendation += "1. **基础练习题集**\n"
                    recommendation += f"   - 内容：{subject}基本概念和原理的巩固练习\n"
                    recommendation += "   - 特点：难度递进，覆盖核心知识点\n"
                    recommendation += "   - 建议用途：课堂练习或课后作业\n\n"
                    
                    recommendation += "2. **应用型问题集**\n"
                    recommendation += f"   - 内容：{subject}在实际场景中的应用问题\n"
                    recommendation += "   - 特点：情境化设计，培养思维能力\n"
                    recommendation += "   - 建议用途：课堂讨论或小组作业\n\n"
                    
                    recommendation += "3. **自我评估测验**\n"
                    recommendation += f"   - 内容：{subject}学习成果的综合测评\n"
                    recommendation += "   - 特点：全面覆盖，即时反馈\n"
                    recommendation += "   - 建议用途：单元复习或阶段性评估\n"
                
                elif category == "实验和活动":
                    recommendation += "1. **引导式探究活动**\n"
                    recommendation += f"   - 内容：探索{subject}核心原理的结构化实验\n"
                    recommendation += "   - 特点：步骤清晰，操作简单\n"
                    recommendation += "   - 建议用途：新概念引入或原理验证\n\n"
                    
                    recommendation += "2. **合作学习项目**\n"
                    recommendation += f"   - 内容：基于{subject}知识的小组协作项目\n"
                    recommendation += "   - 特点：促进交流，培养合作能力\n"
                    recommendation += "   - 建议用途：综合应用或拓展学习\n\n"
                    
                    recommendation += "3. **创新实践活动**\n"
                    recommendation += f"   - 内容：运用{subject}知识解决开放性问题\n"
                    recommendation += "   - 特点：开放性强，培养创新思维\n"
                    recommendation += "   - 建议用途：能力提升或综合实践\n"
            
            # 添加教学建议
            recommendation += "\n## 教学建议\n\n"
            recommendation += "1. **素材组合使用**\n"
            recommendation += "   - 视频资源作为概念引入，阅读材料作为深入学习，练习和活动作为应用巩固\n"
            recommendation += "   - 根据学习者特点选择适当的素材组合\n\n"
            
            recommendation += "2. **差异化教学策略**\n"
            recommendation += "   - 为不同程度的学习者提供不同难度的材料\n"
            recommendation += "   - 灵活调整素材使用顺序和方式\n\n"
            
            recommendation += "3. **评估与反馈**\n"
            recommendation += "   - 使用多元评估方式检验学习效果\n"
            recommendation += "   - 及时收集学习者反馈，调整教学内容和方法\n"
            
            return recommendation
            
        except Exception as e:
            return f"推荐教学素材时出错: {str(e)}"
    
    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """执行指定的工具"""
        if tool_name not in self.tools:
            raise ValueError(f"未知的工具: {tool_name}")
        
        tool = self.tools[tool_name]
        return await tool["handler"](**tool_args) 