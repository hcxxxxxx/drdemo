#!/usr/bin/env python
"""DeepResearch Agent 主运行脚本。"""

import logging
import os
from backend.api.main import run_server
from backend.utils.config import validate_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('deep_research_agent.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数，启动API服务器。"""
    try:
        # 验证配置
        validate_config()
        
        # 启动服务器
        logger.info("正在启动 DeepResearch Agent...")
        run_server()
    except Exception as e:
        logger.error(f"启动失败: {str(e)}", exc_info=True)
        exit(1)

if __name__ == "__main__":
    main() 