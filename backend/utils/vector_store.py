"""向量存储模块，提供文本嵌入和相似度搜索功能。"""

import os
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
from sentence_transformers import SentenceTransformer
import faiss

from ..models.schemas import SearchResult

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """向量存储类，提供文本嵌入和相似度搜索功能。"""
    
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """初始化向量存储。
        
        Args:
            model_name: 要使用的SentenceTransformer模型名称
        """
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.documents = []
        self.urls = []
        self.titles = []  # 添加标题存储
        self.initialize_index()
        
    def initialize_index(self):
        """初始化FAISS索引。"""
        self.index = faiss.IndexFlatL2(self.dimension)
        
    def add_documents(self, search_results: List[SearchResult]):
        """将搜索结果添加到向量存储中。
        
        Args:
            search_results: 搜索结果列表
        """
        if not search_results:
            logger.warning("没有搜索结果可添加到向量存储")
            return
            
        logger.info(f"向向量存储添加 {len(search_results)} 个文档")
        
        # 提取可用的文档内容
        docs = []
        urls = []
        titles = []  # 添加标题列表
        
        for result in search_results:
            if result.content:
                docs.append(result.content)
                urls.append(result.url)
                titles.append(result.title)  # 存储标题
                
        # 没有有效的文档内容，直接返回
        if not docs:
            logger.warning("没有包含内容的有效文档")
            return
                
        # 计算文档的嵌入向量
        embeddings = self.model.encode(docs)
        
        # 添加到FAISS索引
        self.index.add(np.array(embeddings).astype('float32'))
        
        # 存储文档、URL和标题
        self.documents.extend(docs)
        self.urls.extend(urls)
        self.titles.extend(titles)  # 存储标题
        
        logger.info(f"成功添加 {len(docs)} 个文档到向量存储")
        
    def search(self, query: str, k: int = 5) -> List[Dict[str, str]]:
        """搜索与查询最相似的文档。
        
        Args:
            query: 查询文本
            k: 返回的结果数量
            
        Returns:
            包含文档内容、URL和标题的字典列表
        """
        if not self.documents:
            logger.warning("向量存储为空，无法执行搜索")
            return []
            
        # 限制k不超过文档总数
        k = min(k, len(self.documents))
        
        # 计算查询的嵌入向量
        query_embedding = self.model.encode([query])
        
        # 搜索最相似的文档
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    "content": self.documents[idx],
                    "url": self.urls[idx],
                    "title": self.titles[idx] if idx < len(self.titles) else "",  # 返回标题
                    "distance": float(distances[0][i])
                })
                
        logger.info(f"为查询 '{query}' 找到 {len(results)} 个相似文档")
        return results 