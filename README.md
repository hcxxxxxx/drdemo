# DeepResearch Agent

一个模拟OpenAI的DeepResearch功能的AI代理演示。该代理能够根据用户提供的研究主题，自动检索、分析并整合互联网信息，生成一份包含详细分析和可靠来源的综合报告。

## 功能特点

- 🔍 **智能检索**：基于用户查询自动生成搜索策略，从互联网获取最相关的信息
- 📊 **深度分析**：使用多步骤推理分析和综合获取的信息
- 📝 **报告生成**：自动生成结构化的研究报告，包含来源引用
- 🔄 **反馈机制**：基于中间结果调整搜索和分析策略

## 技术栈

- FastAPI - Web服务框架
- Langchain - 构建LLM应用程序的框架
- OpenAI API - 提供LLM能力
- FAISS - 向量相似度搜索
- DuckDuckGo Search API - 网络搜索功能

## 快速开始

1. 克隆仓库
   ```
   git clone https://github.com/hcxxxxxx/drdemo.git
   cd drdemo
   ```

2. 创建虚拟环境并安装依赖
   ```
   conda create --name drdemo python=3.8
   conda activate drdemo
   pip install -r requirements.txt
   ```

3. 配置环境变量
   ```
   cp .env.example .env
   # 编辑.env文件，添加必要的API密钥
   ```

4. 启动服务
   ```
   uvicorn backend.api.main:app --reload
   ```

5. 访问Web界面
   浏览器打开 http://localhost:8000

## 系统架构

```
drdemo/
├── app/                 # 前端界面
├── backend/             # 后端服务
│   ├── api/             # API端点定义
│   ├── core/            # 核心业务逻辑
│   ├── models/          # 数据模型定义
│   └── utils/           # 工具函数
└── data/                # 数据存储
```

## 许可证

MIT 