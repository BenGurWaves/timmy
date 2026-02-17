
import os
import importlib
import logging
from typing import Dict, Type
from .base import BaseTool

logger = logging.getLogger(__name__)

class ToolManager:
    def __init__(self, tool_dir: str = os.path.dirname(__file__)):
        self.tools: Dict[str, BaseTool] = {}
        self._load_tools(tool_dir)
        logger.info(f"ToolManager initialized. Loaded {len(self.tools)} tools.")

    def _load_tools(self, tool_dir: str):
        for filename in os.listdir(tool_dir):
            if filename.endswith(".py") and filename != "__init__.py" and filename != "base.py":
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"tools.{module_name}")
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseTool) and attr is not BaseTool:
                            tool_instance = attr()
                            self.tools[tool_instance.name] = tool_instance
                            logger.info(f"Loaded tool: {tool_instance.name}")
                except Exception as e:
                    logger.error(f"Error loading tool {module_name}: {e}")

    def list_tools(self) -> Dict[str, str]:
        return {name: tool.description for name, tool in self.tools.items()}

    def execute_tool(self, tool_name: str, *args, **kwargs):
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool \'{tool_name}\' not found.")
        logger.info(f"Executing tool: {tool_name} with args: {args}, kwargs: {kwargs}")
        return tool.execute(*args, **kwargs)
