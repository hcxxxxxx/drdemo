"""研究引擎核心模块，协调整个研究过程。"""

import asyncio
import uuid
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..utils.search import SearchTool
from ..utils.vector_store import VectorStore
from ..utils.llm import LLMTool
from ..models.schemas import (
    ResearchRequest, 
    SearchResult, 
    AnalysisStep, 
    ResearchReport, 
    ResearchStatus
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchEngine:
    """研究引擎类，协调整个研究过程。"""
    
    def __init__(self):
        """初始化研究引擎。"""
        self.search_tool = SearchTool()
        self.vector_store = VectorStore()
        self.llm_tool = LLMTool()
        self.active_researches = {}  # 存储进行中的研究状态
        
    async def start_research(self, request: ResearchRequest) -> str:
        """启动新的研究过程。
        
        Args:
            request: 研究请求
            
        Returns:
            研究ID
        """
        # 生成唯一的研究ID
        research_id = str(uuid.uuid4())
        
        # 创建研究状态
        status = ResearchStatus(
            id=research_id,
            topic=request.topic,
            status="in_progress",
            progress=0.0,
            current_step="初始化研究流程"
        )
        
        # 存储研究状态
        self.active_researches[research_id] = status
        
        # 在后台启动研究过程
        asyncio.create_task(self._conduct_research(research_id, request))
        
        return research_id
    
    def get_research_status(self, research_id: str) -> Optional[ResearchStatus]:
        """获取研究状态。
        
        Args:
            research_id: 研究ID
            
        Returns:
            研究状态，如果不存在则返回None
        """
        return self.active_researches.get(research_id)
    
    async def _conduct_research(self, research_id: str, request: ResearchRequest):
        """执行研究过程。
        
        Args:
            research_id: 研究ID
            request: 研究请求
        """
        try:
            # 更新状态
            self._update_status(research_id, "生成搜索查询", 0.1)
            
            # 步骤1: 生成初始搜索查询
            search_queries = self.llm_tool.generate_search_queries(
                request.topic, 
                num_queries=3
            )
            
            # 步骤2: 执行初始搜索
            self._update_status(research_id, "执行网络搜索", 0.2)
            all_search_results = []
            
            for query in search_queries:
                search_results = self.search_tool.search(query)
                all_search_results.extend(search_results)
            
            # 步骤3: 丰富搜索结果
            self._update_status(research_id, "获取网页内容", 0.3)
            enriched_results = await self.search_tool.enrich_search_results(all_search_results)
            
            # 步骤4: 添加到向量存储
            self._update_status(research_id, "向量化内容", 0.4)
            self.vector_store.add_documents(enriched_results)
            
            # 步骤5: 生成初步分析
            self._update_status(research_id, "初步分析", 0.5)
            initial_question = f"请简要总结关于'{request.topic}'的基本情况和主要观点。"
            
            # 从向量存储中检索相关内容
            relevant_docs = self.vector_store.search(initial_question, k=3)
            
            # 如果没有足够的相关文档，执行额外搜索
            if len(relevant_docs) < 2:
                self._update_status(research_id, "执行额外初步搜索", 0.55)
                extra_query = f"{request.topic} 概述 主要观点"
                extra_search_results = self.search_tool.search(extra_query)
                enriched_extra = await self.search_tool.enrich_search_results(extra_search_results)
                self.vector_store.add_documents(enriched_extra)
                # 重新检索
                relevant_docs = self.vector_store.search(initial_question, k=3)
            
            # 检查内容质量
            content_quality = sum([len(doc["content"].strip()) for doc in relevant_docs])
            if content_quality < 1000:  # 如果总内容少于1000字符，再次尝试不同的搜索
                self._update_status(research_id, "尝试备选搜索策略", 0.56)
                backup_queries = [
                    f"{request.topic} 详解",
                    f"{request.topic} 最新进展",
                    f"什么是 {request.topic}"
                ]
                for query in backup_queries:
                    backup_results = self.search_tool.search(query)
                    enriched_backup = await self.search_tool.enrich_search_results(backup_results)
                    self.vector_store.add_documents(enriched_backup)
                
                # 最后一次尝试检索
                relevant_docs = self.vector_store.search(initial_question, k=5)  # 增加到前5个结果
            
            # 确保至少有一些内容
            if not relevant_docs:
                logger.warning(f"无法获取到关于 '{request.topic}' 的相关内容")
                # 创建一个虚拟文档
                relevant_docs = [{
                    "content": f"这是关于'{request.topic}'的研究。我们将利用大语言模型的知识来生成分析。",
                    "url": "https://example.com/no-results"
                }]
            
            combined_content = "\n\n".join([doc["content"] for doc in relevant_docs])
            
            # 分析内容
            initial_analysis = self.llm_tool.analyze_content(combined_content, initial_question)
            
            # 记录初步分析步骤
            analysis_steps = [
                AnalysisStep(
                    question=initial_question,
                    answer=initial_analysis,
                    sources=[doc["url"] for doc in relevant_docs]
                )
            ]
            
            # 步骤6: 生成深入研究问题
            self._update_status(research_id, "生成深入研究问题", 0.6)
            research_questions = self.llm_tool.generate_research_questions(
                request.topic, 
                initial_analysis,
                num_questions=request.depth
            )
            
            # 步骤7: 回答每个深入问题
            self._update_status(research_id, "进行深入分析", 0.7)
            
            for i, question in enumerate(research_questions):
                # 更新状态以显示当前问题进度
                progress = 0.7 + (i / len(research_questions) * 0.2)
                self._update_status(
                    research_id, 
                    f"分析问题 {i+1}/{len(research_questions)}: {question[:50]}...", 
                    progress
                )
                
                # 从向量存储中检索相关内容
                relevant_docs = self.vector_store.search(question, k=3)
                
                # 如果相关文档不足，执行额外搜索
                if len(relevant_docs) < 2 or sum([len(doc["content"].strip()) for doc in relevant_docs]) < 800:
                    self._update_status(research_id, f"为问题 {i+1} 执行额外搜索", progress)
                    
                    # 尝试几种不同的搜索查询变体
                    search_variants = [
                        question,
                        f"{question} {request.topic}",
                        " ".join(question.split()[:5]) + f" {request.topic}"  # 问题的前几个词 + 主题
                    ]
                    
                    for variant in search_variants:
                        extra_search_results = self.search_tool.search(variant)
                        enriched_extra = await self.search_tool.enrich_search_results(extra_search_results)
                        if enriched_extra:  # 如果找到了内容
                            self.vector_store.add_documents(enriched_extra)
                            break  # 找到内容后停止尝试其他变体
                    
                    # 重新检索
                    relevant_docs = self.vector_store.search(question, k=4)  # 增加结果数
                
                # 确保至少有一些内容
                if not relevant_docs or sum([len(doc["content"].strip()) for doc in relevant_docs]) < 300:
                    # 使用备用内容，告诉LLM使用自己的知识回答
                    logger.warning(f"无法获取到关于问题 '{question}' 的足够相关内容")
                    relevant_docs = [{
                        "content": f"请使用你的知识和理解，回答关于'{request.topic}'的以下问题：{question}",
                        "url": "https://example.com/internal-knowledge"
                    }]
                
                combined_content = "\n\n".join([doc["content"] for doc in relevant_docs])
                
                # 分析内容
                answer = self.llm_tool.analyze_content(combined_content, question)
                
                # 记录分析步骤
                analysis_steps.append(
                    AnalysisStep(
                        question=question,
                        answer=answer,
                        sources=[doc["url"] for doc in relevant_docs]
                    )
                )
            
            # 步骤8: 生成最终报告
            self._update_status(research_id, "生成研究报告", 0.9)
            
            # 将分析步骤转换为适合报告生成的格式
            research_findings = [
                {
                    "question": step.question,
                    "answer": step.answer,
                    "sources": step.sources
                }
                for step in analysis_steps
            ]
            
            report_data = self.llm_tool.generate_report(request.topic, research_findings)
            
            # 创建最终报告
            report = ResearchReport(
                topic=request.topic,
                summary=report_data["summary"],
                key_findings=report_data["key_findings"],
                detailed_analysis=report_data["detailed_analysis"],
                sources=report_data["sources"],
                analysis_steps=analysis_steps,
                created_at=datetime.now()
            )
            
            # 完成研究
            self._update_status(
                research_id, 
                "研究完成", 
                1.0, 
                status="completed", 
                report=report
            )
            
        except Exception as e:
            logger.error(f"研究过程出错: {str(e)}", exc_info=True)
            # 更新状态为失败
            self._update_status(
                research_id, 
                f"研究失败: {str(e)}", 
                0.0, 
                status="failed", 
                error=str(e)
            )
    
    def _update_status(self, research_id: str, current_step: str, progress: float, 
                      status: str = "in_progress", report: Optional[ResearchReport] = None,
                      error: Optional[str] = None):
        """更新研究状态。
        
        Args:
            research_id: 研究ID
            current_step: 当前步骤
            progress: 进度 (0-1)
            status: 状态 ('in_progress', 'completed', 'failed')
            report: 研究报告
            error: 错误信息
        """
        if research_id in self.active_researches:
            research_status = self.active_researches[research_id]
            research_status.current_step = current_step
            research_status.progress = progress
            research_status.status = status
            
            if status == "completed":
                research_status.completed_at = datetime.now()
                research_status.report = report
            
            if error:
                research_status.error = error
                
            logger.info(f"研究 {research_id} 更新: {current_step} (进度: {progress:.0%})")
        else:
            logger.warning(f"尝试更新不存在的研究ID: {research_id}") 