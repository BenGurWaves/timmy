"""
code_writer.py

This skill allows the Timmy AI agent to write and modify code, leveraging the coding models
from the Brain component and the FileSystemTool for file operations.
"""

from typing import Any, Dict
from skills.base import Skill
from brain import Brain # Assuming Brain class is accessible
from tools.filesystem import FileSystemTool

class CodeWriterSkill(Skill):
    """
    A skill for writing, modifying, and reviewing code.
    """

    def __init__(self, brain: Brain):
        super().__init__(
            name="Code Writer",
            description="Writes, modifies, and reviews code using coding models and file system access."
        )
        self.brain = brain
        self.filesystem_tool = FileSystemTool()

    def execute(self, operation: str, file_path: str = "", prompt: str = "", code_content: str = "") -> Dict[str, Any]:
        """
        Executes a code writing operation.

        Args:
            operation (str): The type of code operation ("write", "modify", "review").
            file_path (str): The path to the code file.
            prompt (str): The prompt for the coding model.
            code_content (str): The code content to write or modify (for "write" or "modify" operations).

        Returns:
            Dict[str, Any]: The result of the code writing operation.
        """
        print(f"Executing Code Writer Skill for operation: {operation}")

        if operation == "write":
            if not file_path or not code_content:
                return {"status": "error", "message": "File path and code content are required for writing code."}
            result = self.filesystem_tool.write_file(file_path, code_content)
            return result

        elif operation == "modify":
            if not file_path or not prompt:
                return {"status": "error", "message": "File path and a modification prompt are required for modifying code."}
            
            # Read existing code
            read_result = self.filesystem_tool.read_file(file_path)
            if read_result["status"] == "error":
                return read_result
            existing_code = read_result["content"]

            # Ask the coding model to modify the code
            modification_prompt = f"""Given the following code:

```python
{existing_code}
```

Please modify it according to the following instructions:
{prompt}

Provide only the modified code, no additional explanations.
"""
            modified_code = self.brain.code(modification_prompt)

            # Write the modified code back to the file
            write_result = self.filesystem_tool.write_file(file_path, modified_code)
            return write_result

        elif operation == "review":
            if not file_path:
                return {"status": "error", "message": "File path is required for reviewing code."}
            
            # Read existing code
            read_result = self.filesystem_tool.read_file(file_path)
            if read_result["status"] == "error":
                return read_result
            code_to_review = read_result["content"]

            # Ask the coding model to review the code
            review_prompt = f"""Please review the following code for best practices, potential bugs, and areas for improvement:

```python
{code_to_review}
```

Provide a detailed review and suggestions.
"""
            review_result = self.brain.code(review_prompt)
            return {"status": "success", "file_path": file_path, "review": review_result}

        else:
            return {"status": "error", "message": f"Unknown code writing operation: {operation}"}
