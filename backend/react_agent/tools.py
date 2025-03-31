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
    
    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """执行指定的工具"""
        if tool_name not in self.tools:
            raise ValueError(f"未知的工具: {tool_name}")
        
        tool = self.tools[tool_name]
        return await tool["handler"](**tool_args) 