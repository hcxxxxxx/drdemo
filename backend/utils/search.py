"""网络搜索工具模块，提供从网络获取信息的功能。"""

import asyncio
import requests
import re
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import logging

from ..models.schemas import SearchResult
from ..utils.config import MAX_SEARCH_RESULTS, MAX_CONTENT_LENGTH, ACADEMIC_SITES

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SearchTool:
    """网络搜索工具类，提供从互联网获取信息的功能。"""
    
    def __init__(self):
        self.ddgs = DDGS()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search(self, query: str, max_results: int = MAX_SEARCH_RESULTS, academic_only: bool = False) -> List[SearchResult]:
        """执行网络搜索并返回结果。
        
        Args:
            query: 搜索查询
            max_results: 最大结果数量
            academic_only: 是否仅搜索学术资源
            
        Returns:
            搜索结果列表
        """
        try:
            if academic_only:
                # 通过添加学术站点限制和学术关键词增强查询
                logger.info(f"学术搜索查询: {query}")
                # 为查询添加一些学术相关词汇以增强学术性
                enhanced_query = f"{query} (paper OR research OR study OR journal OR conference OR proceedings)"
                
                # 构建学术站点搜索限制
                sites_query = " OR ".join([f"site:{site}" for site in ACADEMIC_SITES])
                academic_query = f"{enhanced_query} ({sites_query})"
                
                logger.info(f"增强的学术搜索查询: {academic_query}")
                results = self.ddgs.text(academic_query, max_results=max_results*2)  # 获取更多结果以便过滤
            else:
                logger.info(f"普通搜索查询: {query}")
                results = self.ddgs.text(query, max_results=max_results)
            
            search_results = []
            
            # 如果是学术搜索，过滤结果只包含学术网站
            for result in results:
                url = result.get("href", "")
                
                # 如果是学术搜索，检查URL是否来自学术网站
                if academic_only:
                    is_academic = False
                    for site in ACADEMIC_SITES:
                        if site in url:
                            is_academic = True
                            break
                    
                    if not is_academic:
                        continue
                
                search_results.append(SearchResult(
                    title=result.get("title", ""),
                    url=url,
                    snippet=result.get("body", "")
                ))
                
                # 如果已经收集了足够的结果，就停止
                if len(search_results) >= max_results:
                    break
            
            logger.info(f"获取到 {len(search_results)} 条{'学术' if academic_only else ''}搜索结果")
            return search_results
        except Exception as e:
            logger.error(f"搜索失败: {str(e)}")
            return []
    
    def get_webpage_content(self, url: str) -> Optional[Dict[str, str]]:
        """获取网页内容并提取文本与标题。"""
        try:
            logger.info(f"获取网页内容: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取页面标题
            title = soup.title.string.strip() if soup.title else ""
            
            # 移除脚本和样式元素
            for script in soup(["script", "style"]):
                script.extract()
            
            # 获取文本内容
            text = soup.get_text(separator='\n')
            
            # 清理文本：移除多余空行和空格
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # 限制内容长度
            if len(text) > MAX_CONTENT_LENGTH:
                text = text[:MAX_CONTENT_LENGTH] + "..."
                
            return {"content": text, "title": title}
        except Exception as e:
            logger.error(f"获取网页内容失败 {url}: {str(e)}")
            return None
    
    async def enrich_search_results(self, search_results: List[SearchResult]) -> List[SearchResult]:
        """异步获取每个搜索结果的完整网页内容。"""
        async def _get_content(result: SearchResult) -> SearchResult:
            content_data = self.get_webpage_content(result.url)
            if content_data:
                result.content = content_data["content"]
                # 如果网页有标题，则使用网页标题，否则保留搜索结果的标题
                if content_data["title"]:
                    result.title = content_data["title"]
            return result
        
        tasks = [asyncio.create_task(_get_content(result)) for result in search_results]
        enriched_results = await asyncio.gather(*tasks)
        
        # 过滤掉没有内容的结果
        return [result for result in enriched_results if result.content]
    
    def is_academic_url(self, url: str) -> bool:
        """检查URL是否来自学术网站。
        
        Args:
            url: 要检查的URL
            
        Returns:
            如果URL来自学术网站，则为True，否则为False
        """
        for site in ACADEMIC_SITES:
            if site in url:
                return True
        return False 