# 辅助函数，用于为给定的代理创建节点
from langchain_core.messages import ToolMessage, AIMessage

"""
图的agent节点。决定做什么操作(也就是调用下llm)
1.把历史消息放入提示词，然后让llm回答。
2.返回消息和发送方
"""


def agent_node(state, agent, name):
    # 调用代理
    result = agent.invoke(state)
    # 将代理输出转换为适合附加到全局状态的格式
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)

    return {
        "messages": [result], 
        "sender": name,
    }
