# 导入基本消息类、用户消息类和工具消息类
from langchain_core.messages import (
    HumanMessage
)
# 导入聊天提示模板和消息占位符
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.tools import BaseTool



# 定义一个函数，用于创建代理
def create_agent(llm, tools, system_message: str):
    """创建一个代理。"""

    # 过滤掉无效的工具（比如 None）
    tools = [tool for tool in tools if isinstance(tool, BaseTool)]
    # 创建一个聊天提示模板
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an academic research assistant specializing in transforming colloquial language into scholarly inquiry topics. "
                "Your core function requires deep semantic analysis and cross-disciplinary knowledge integration "
                "to reveal hidden research topics from the users' input."
                "If you or another assistant complete the task or deliverable,"
                "prefix your response with FINAL ANSWER to signal the team to stop."
                "If another assistant also can not solve this problem, and you receive same question twice,"
                "prefix your response with FINAL ANSWER to signal the team to stop."
                "You may use the following tools: {tool_names}. \n{system_message}",
                # " 你是一个有帮助的AI助手，与其他助手合作。"
                # " 使用提供的工具来推进问题的回答。"
                # " 如果你不能完全回答，没关系，另一个拥有不同工具的助手"
                # " 会接着你的位置继续帮助。执行你能做的以取得进展。"
                # " 如果你或其他助手有最终答案或交付物，"
                # " 在你的回答前加上FINAL ANSWER，以便团队知道停止。"
                # " 你可以使用以下工具: {tool_names}。\n{system_message}",


            ),  # 系统消息
            # 消息占位符 
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    # 传递系统消息参数
    prompt = prompt.partial(system_message=system_message)
    # 传递工具名称参数
    prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

    # 返回RunnableSequence，先用消息messages填充提示词，再llm_with_tools进行调用 (类型是：langchain_core.runnables.base.RunnableSequence)
    return prompt | llm.bind_tools(tools)

