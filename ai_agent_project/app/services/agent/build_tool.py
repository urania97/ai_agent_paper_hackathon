import os
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_experimental.tools import PythonREPLTool
# from langchain_core.core import tool

# ✅ 先拿环境变量
tavily_api_key = os.getenv("TAVILY_API_KEY", None)

# ✅ 判断是否有 Key
if tavily_api_key:
    tavily_tool = TavilySearchResults(
        tavily_api_key=tavily_api_key,
        max_results=5,
        k=5,
        name="tavily_search",
        description="Search for recent information"
    )
    print("✅ Tavily search tool loaded.")
else:
    tavily_tool = None
    print("⚠️ Tavily API Key not found. Search tool disabled.")

# ✅ 这个是原本的 Python 解释器工具
python_repl = PythonREPLTool()

