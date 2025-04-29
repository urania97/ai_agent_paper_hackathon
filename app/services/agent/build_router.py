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
    if re.search("FINAL ANSWER", last_message.content, re.IGNORECASE):  # 刚开始的提示词里指定了以FINAL ANSWER为结束标志
        # 任何代理决定工作完成
        return "__end__"
    # elif "Final Answer" in last_message.content:
    #      return "__end__"
    # elif "Final ANSWER" in last_message.content:
    #      return "__end__"
    # elif "FINAL Answer" in last_message.content:
    #      return "__end__"
    # elif "final answer" in last_message.content:
    #      return "__end__"
    return "other_agent"
