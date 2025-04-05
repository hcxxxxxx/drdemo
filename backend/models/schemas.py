"""系统中使用的Pydantic数据模型。"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ResearchRequest(BaseModel):
    """用户研究请求模型。"""
    topic: str = Field(..., description="研究主题或问题")
    depth: int = Field(3, description="研究深度级别（1-5）")
    max_sources: int = Field(10, description="最大信息源数量")
    academic_only: bool = Field(False, description="是否仅搜索学术资源")
    
class SearchResult(BaseModel):
    """搜索结果模型。"""
    title: str
    url: str
    snippet: str
    content: Optional[str] = None
    
class AnalysisStep(BaseModel):
    """分析步骤模型。"""
    question: str
    answer: str
    sources: List[str] = []
    
class ResearchReport(BaseModel):
    """研究报告模型。"""
    topic: str
    summary: str
    key_findings: List[str]
    detailed_analysis: str
    sources: List[Dict[str, str]]
    analysis_steps: List[AnalysisStep] = []
    created_at: datetime = Field(default_factory=datetime.now)
    
class ResearchStatus(BaseModel):
    """研究状态模型。"""
    id: str
    topic: str
    status: str = "in_progress"  # 'in_progress', 'completed', 'failed'
    progress: float = 0.0
    current_step: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    report: Optional[ResearchReport] = None
    error: Optional[str] = None 