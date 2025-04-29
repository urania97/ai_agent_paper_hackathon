# 辅助函数，用于为给定的代理创建节点
from langchain_core.messages import ToolMessage, AIMessage

"""
图的agent节点。决定做什么操作(也就是调用下llm)
1.把历史消息放入提示词，然后让llm回答。(此时的state里就有历史消息，也就是messages，而sender再字典里，也无关紧要，虽然传入进去了，但是底层没用)
2.返回消息和发送方
"""


def agent_node(state, agent, name):
    # 调用代理
    result = agent.invoke(state)
    # 将代理输出转换为适合附加到全局状态的格式
    if isinstance(result, ToolMessage):
        pass
    else:
        # 先result.dict(exclude={"type", "name"}) 返回一个去除type和name的字典，然后通过**变成关键字参数，最后把name传进去
        # 相当于曲线救国，把消息的name改成了。
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)

    return {
        "messages": [result],  # 会追加到消息后边
        # 由于我们有一个严格的工作流程，我们可以
        # 跟踪发送者，以便知道下一个传递给谁。
        "sender": name,
    }
