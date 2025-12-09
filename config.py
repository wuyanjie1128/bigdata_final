import os

# NOTE:
# Never hardcode real keys in GitHub.
# Use environment variables instead.

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_BASE_URL = os.getenv(
    "DASHSCOPE_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# Default model for OpenAI-compatible vision calls
QWEN_VL_MODEL = os.getenv("QWEN_VL_MODEL", "qwen-vl-plus")
