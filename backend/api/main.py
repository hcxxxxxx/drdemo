"""FastAPI 主应用程序。"""

import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import logging
from pathlib import Path

from ..core.research_engine import ResearchEngine
from ..models.schemas import ResearchRequest, ResearchStatus
from ..utils.config import validate_config, HOST, PORT

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 验证环境变量
try:
    validate_config()
except ValueError as e:
    logger.error(f"配置错误: {str(e)}")
    exit(1)

# 创建FastAPI应用
app = FastAPI(
    title="DeepResearch Agent API",
    description="一个模拟OpenAI的DeepResearch功能的AI代理",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建研究引擎实例
research_engine = ResearchEngine()

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = os.path.join(BASE_DIR, "app")

# 定义API路由
@app.get("/api")
async def api_root():
    """API根路径。"""
    return {"message": "DeepResearch Agent API"}

@app.post("/api/research/start", response_model=dict)
async def start_research(request: ResearchRequest):
    """启动新的研究。
    
    Args:
        request: 研究请求
        
    Returns:
        研究ID
    """
    try:
        research_id = await research_engine.start_research(request)
        return {"research_id": research_id}
    except Exception as e:
        logger.error(f"启动研究失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动研究失败: {str(e)}")

@app.get("/api/research/status/{research_id}", response_model=ResearchStatus)
async def get_research_status(research_id: str):
    """获取研究状态。
    
    Args:
        research_id: 研究ID
        
    Returns:
        研究状态
    """
    status = research_engine.get_research_status(research_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"找不到研究ID: {research_id}")
    return status

@app.get("/api/health")
async def health_check():
    """API健康检查。
    
    Returns:
        健康状态
    """
    return {"status": "healthy"}

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """全局异常处理程序。"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误: {str(exc)}"}
    )

# 挂载静态文件 - 注意：这必须放在API路由定义之后
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

# 捕获所有其他请求并提供index.html
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """提供前端页面。"""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Page not found")

def run_server():
    """启动API服务器。"""
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 