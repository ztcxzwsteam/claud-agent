import os
from langchain_core.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

@tool
def web_search(query: str) -> str:
    """
    使用 Tavily 进行实时联网搜索，获取最新的行业动态、实时云产品信息、对比分析等。
    当用户问到实时资讯（例如最新的折扣、新发布的产品、竞争对手对比、最新市场趋势）或向量数据库和知识图谱中没有的信息时，使用此工具。
    """
    try:
        # 确保 TAVILY_API_KEY 存在于环境变量中
        if not os.getenv("TAVILY_API_KEY"):
            return "错误：未配置 TAVILY_API_KEY，无法进行联网搜索。"
            
        search = TavilySearchResults(max_results=3)
        results = search.invoke(query)
        if not results:
            return "未检索到相关联网搜索结果。"
            
        formatted_results = []
        for i, res in enumerate(results):
            url = res.get("url", "Unknown Source")
            content = res.get("content", "").strip()
            formatted_results.append(f"【联网来源 {i+1}: {url}】\n{content}")
            
        return "\n\n".join(formatted_results)
    except Exception as e:
        return f"进行联网搜索时发生错误: {str(e)}"
