from typing import Literal
import re

# 定义路由器函数
def router(state) -> Literal["call_tool", "__end__", "other_agent"]:
    # 这是路由器
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        # 上一个代理正在调用工具
        return "call_tool"
    if re.search("FINAL ANSWER", last_message.content, re.IGNORECASE):  #
        # 任何代理决定工作完成
        return "__end__"
    return "other_agent"
