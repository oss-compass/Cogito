import os

class PromptManager:
    def __init__(self, prompts_dir="prompts"):
        # 获取当前文件所在的目录，确保路径是相对于包的绝对路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.prompts_dir = os.path.join(base_dir, prompts_dir)

    def load(self, filename: str, **kwargs) -> str:
        """
        读取提示词文件，并支持 python f-string 风格的变量替换。
        
        Args:
            filename: prompts 目录下的文件名 (e.g., "researchor.txt")
            **kwargs: 需要注入到提示词中的变量 (e.g., report_template="...")
        """
        file_path = os.path.join(self.prompts_dir, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 如果有传入参数，尝试格式化内容
            if kwargs:
                try:
                    return content.format(**kwargs)
                except KeyError as e:
                    # 为了防止 prompt 中有 {{variable}} 是给 LLM 用的而不是给我们替换的，
                    # 如果直接 format 失败，这是一个简单的容错。
                    # 在更复杂的系统中，建议使用 jinja2。
                    print(f"Warning: Formatting prompt failed: {e}. Returning raw content.")
                    return content
            return content
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found at: {file_path}")

# 单例实例，方便导入使用
prompts = PromptManager()