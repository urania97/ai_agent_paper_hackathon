from dotenv import load_dotenv

# 先加载环境变量，默认是找当前目录下的.env文件
load_dotenv()


# 导入操作符和类型注解
import re
import functools
import operator
from typing import Annotated, Sequence, TypedDict, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph
from langchain import hub
from .agent.build_agent import create_agent
from .agent.build_tool import tavily_tool, python_repl
from .agent.build_agent_node import agent_node
from .agent.build_router import router
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START
import json
from langgraph.managed.is_last_step import RemainingSteps
from langchain.agents import AgentExecutor, create_react_agent, load_tools
from langchain_core.tools import BaseTool
from langchain_community.tools import BraveSearch,DuckDuckGoSearchResults
from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper


class AgentState(TypedDict):
    # 添加operator.add注解，相当于每次把消息列表加起来。变相的追加而已。
    messages: Annotated[Sequence[BaseMessage], operator.add]
    sender: str
    remaining_steps: RemainingSteps

class AgentModel:
    def __init__(self):
        self.llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        arxiv_tool = ArxivQueryRun(max_results=5, doc_content_chars_max=4000)

        self.research_agent = create_agent(
            self.llm,
            # load_tools(["arxiv"]),
            [arxiv_tool],
            # [tool_search],
            system_message="你应该提供准确的真实的论文供Researcher使用。",
        )

        # 创建查询节点，指定对应的agent   functools.partial是会生成一个函数，函数为agent_node，指定参数agent和name
        self.research_node = functools.partial(agent_node, agent=self.research_agent, name="Researcher")

        # 定义工具列表
        self.tools = [arxiv_tool, python_repl]

        # 创建工具节点
        self.tool_node = ToolNode(self.tools)

        # 创建状态图实例
        self.workflow = StateGraph(AgentState)

        # 添加搜索节点
        self.workflow.add_node("Researcher", self.research_node)

        # 添加工具调用节点
        self.workflow.add_node("call_tool", self.tool_node)

        # 添加起始边
        self.workflow.add_edge(START, "Researcher")
        self.workflow.add_conditional_edges(
            "Researcher",
            router,
            {"other_agent": "Researcher", "call_tool": "call_tool", "__end__": END},
        )
        # 添加条件边，工具调用结束后，需要返回到哪里。
        self.workflow.add_conditional_edges(
            source="call_tool",
            # 每个代理节点更新'sender'字段
            # 工具调用节点不更新，这意味着
            # 该边将路由回调用工具的原始代理
            path=lambda x: x["sender"],  # 发送方是谁，就返回到哪里

            path_map={  # 根据path进行路由，防止sender和具体的节点名字不一样的情况
                "Researcher": "Researcher",
                # "chart_generator": "chart_generator",
            },
        )

        # 编译工作流图
        self.graph = self.workflow.compile()

        # 将生成的图片保存到文件
        graph_png = self.graph.get_graph().draw_mermaid_png()
        with open("build_graph.png", "wb") as f:
            f.write(graph_png)

    async def find_paper(self, find_field):

        # print(paper_name)
        print(find_field)
        # 事件流

        events = self.graph.stream(
            {
                "messages": [
                    HumanMessage(
                        content=find_field+", Research papers in this domain must be both authentic and closely"
                        " aligned with user needs. The task is considered complete "
                        "once such papers are identified. If user don't provide a specific domain, "
                        "please inform them of the purpose of this agent and complete the task promptly."
                    )
                ],
            },
            # 图中最多执行的步骤数
            {"recursion_limit": 150},
        )
        for s in events:
            print(s)
            text = ""
            if 'Researcher' in s.keys():
                text = s['Researcher']['messages'][0].content

            if 'call_tool' in s.keys():
                text = s['call_tool']['messages'][0].content

            yield str(text)




    def analysis_paper(self, paper_content):

        # print(paper_name)
        print(paper_content)
        # 事件流

        events = self.graph.stream(
            {
                "messages": [
                    HumanMessage(
                        content="analysis"+paper_content['title']+
                        "Here is the abstract:"+paper_content['abstract']+
                                " Once the analysis is completed, the task is completed."
                    )
                ],
            },
            # 图中最多执行的步骤数
            {"recursion_limit": 150},
        )
            # 打印事件流中的每个状态
        
        for s in events:
            # print(s)
            if 'Researcher' in s.keys():
                text = s['call_tool']['messages'][0].content
            if 'call_tool' in s.keys():
                text = s['call_tool']['messages'][0].content
            yield str(text)
    

    async def analysis_full_paper(self, full_text):
        
        # 事件流

        events = self.graph.stream(
            {
                "messages": [
                    HumanMessage(
                        content="analysis this paper,"
                        "here is the full text:"+full_text+
                                " Once the analysis is completed, the task is completed."
                    )
                ],
            },
            # 图中最多执行的步骤数
            {"recursion_limit": 15},
        )
        text = ""
        for s in events:
            # print(s)
            if 'Researcher' in s.keys():
                text = s['Researcher']['messages'][0].content
            if 'call_tool' in s.keys():
                text = s['call_tool']['messages'][0].content
            yield str(text)

