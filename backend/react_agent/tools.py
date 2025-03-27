from typing import Dict, Any
import json
import os

class ToolSet:
    def __init__(self):
        self.tools = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认的工具集"""
        # 文件读取工具
        self.register_tool(
            name="read_file",
            description="读取指定文件的内容",
            parameters={
                "file_path": "要读取的文件路径",
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
                "directory": "要搜索的目录路径",
                "pattern": "文件匹配模式（例如：*.py）"
            },
            handler=self._search_files
        )
        
        # 代码分析工具
        self.register_tool(
            name="analyze_code",
            description="分析代码文件的结构和内容",
            parameters={
                "file_path": "要分析的代码文件路径"
            },
            handler=self._analyze_code
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
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if start_line is not None and end_line is not None:
                    lines = lines[start_line-1:end_line]
                return ''.join(lines)
        except Exception as e:
            return f"读取文件时出错: {str(e)}"
    
    async def _search_files(self, directory: str, pattern: str) -> str:
        """搜索文件的工具实现"""
        try:
            import glob
            files = glob.glob(os.path.join(directory, pattern))
            return json.dumps(files, ensure_ascii=False)
        except Exception as e:
            return f"搜索文件时出错: {str(e)}"
    
    async def _analyze_code(self, file_path: str) -> str:
        """分析代码的工具实现"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 这里可以添加更复杂的代码分析逻辑
                return f"文件 {file_path} 的基本信息：\n" + \
                       f"- 总行数: {len(content.splitlines())}\n" + \
                       f"- 文件大小: {len(content)} 字节"
        except Exception as e:
            return f"分析代码时出错: {str(e)}"
    
    async def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Any:
        """执行指定的工具"""
        if tool_name not in self.tools:
            raise ValueError(f"未知的工具: {tool_name}")
        
        tool = self.tools[tool_name]
        return await tool["handler"](**tool_args) 