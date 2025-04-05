"""配置模块，负责加载环境变量和其他设置。"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 加载.env文件
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

# OpenAI API设置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_MODEL = os.getenv("OPENAI_API_MODEL", "gpt-4o-mini")

# 检索设置
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "10"))
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", "4000"))

# 学术搜索设置
ACADEMIC_SEARCH_ENABLED = os.getenv("ACADEMIC_SEARCH_ENABLED", "True").lower() in ["true", "1", "yes"]
# 学术网站列表
ACADEMIC_SITES = [
    "arxiv.org",           # arXiv预印本
    "scholar.google.com",  # 谷歌学术
    "ieee.org",            # IEEE
    "acm.org",             # ACM
    "springer.com",        # Springer
    "sciencedirect.com",   # Science Direct
    "nature.com",          # Nature
    "science.org",         # Science
    "ncbi.nlm.nih.gov",    # PubMed
    "researchgate.net",    # ResearchGate
    "semanticscholar.org", # Semantic Scholar
    "dl.acm.org",          # ACM数字图书馆
    "ieeexplore.ieee.org", # IEEE Xplore
    "jstor.org",           # JSTOR
    "ssrn.com",            # SSRN
    "pnas.org",            # PNAS
    "aps.org",             # 美国物理学会
    "wiley.com",           # Wiley
    "tandfonline.com",     # Taylor & Francis
    "oup.com",             # Oxford University Press
    "cell.com",            # Cell
    "cnki.net",            # 中国知网
    "wanfangdata.com.cn",  # 万方数据
    "aclweb.org",          # ACL
    "neurips.cc",          # NeurIPS
    "mlr.press",           # JMLR
    "mdpi.com",            # MDPI
    "frontiersin.org",     # Frontiers
    "elsevier.com",        # Elsevier
    "biorxiv.org",         # bioRxiv
]

# Web服务设置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# 确保必要的环境变量存在
def validate_config():
    """验证必要的配置是否存在。"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY 环境变量未设置！请在.env文件中配置。") 
    if not OPENAI_API_BASE_URL:
        raise ValueError("OPENAI_API_BASE_URL 环境变量未设置！请在.env文件中配置。") 