"""LLM工具模块，提供与大型语言模型的交互功能。"""

import os
from typing import List, Dict, Any, Optional
import logging
import openai
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

from ..utils.config import OPENAI_API_KEY, OPENAI_API_MODEL, OPENAI_API_BASE_URL

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置OpenAI
openai.api_key = OPENAI_API_KEY
openai.base_url = OPENAI_API_BASE_URL

class LLMTool:
    """LLM工具类，提供与大型语言模型的交互功能。"""
    
    def __init__(self, model_name=OPENAI_API_MODEL):
        """初始化LLM工具。
        
        Args:
            model_name: 要使用的OpenAI模型名称
        """
        self.model_name = model_name
        self.chat_model = ChatOpenAI(model_name=model_name, openai_api_key=OPENAI_API_KEY, base_url=OPENAI_API_BASE_URL)
        
    def generate_search_queries(self, topic: str, num_queries: int = 3, academic_search: bool = False) -> List[str]:
        """生成搜索查询。
        
        Args:
            topic: 研究主题
            num_queries: 生成的查询数量
            academic_search: 是否为学术搜索
            
        Returns:
            生成的搜索查询列表
        """
        logger.info(f"为主题 '{topic}' 生成搜索查询")
        
        if academic_search:
            system_prompt = """
            你是一个专业的学术研究助手。给定一个研究主题，你的任务是生成能够找到高质量学术论文和资源的搜索查询。
            这些查询将用于在学术数据库和论文来源（如arXiv、IEEE、ACM、Springer等）中搜索相关研究。
            查询应该包含适合学术搜索的术语和关键字，能够返回高质量的研究论文、会议论文、期刊文章等。
            """
            
            user_prompt = f"""
            请为研究主题 "{topic}" 生成 {num_queries} 个可用于学术搜索引擎的查询。
            这些查询将用于查找与该主题相关的学术论文、研究报告和科学文献。
            
            请确保查询：
            1. 使用学术术语和关键字
            2. 专注于发现研究论文、会议论文、期刊文章等
            3. 覆盖主题的不同方面
            4. 避免使用非学术性的术语
            5. 使用英文（因为大多数学术数据库以英文为主）
            
            仅输出查询字符串，每行一个，不要包含任何标号或额外解释。
            """
        else:
            system_prompt = """
            你是一个专业的研究助手。给定一个研究主题，你的任务是生成能够找到相关信息的搜索查询。
            这些查询将用于在搜索引擎中搜索相关信息。查询应该能够返回全面且多样的信息。
            """
            
            user_prompt = f"""
            请为研究主题 "{topic}" 生成 {num_queries} 个搜索查询。
            这些查询将用于查找与该主题相关的信息。
            
            请确保查询：
            1. 使用明确的关键词
            2. 涵盖主题的不同方面
            3. 能够返回高质量的信息
            
            仅输出查询字符串，每行一个，不要包含任何标号或额外解释。
            """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.chat_model(messages)
        
        # 解析响应，获取查询列表
        queries = [
            line.strip() for line in response.content.strip().split("\n")
            if line.strip()
        ]
        
        # 确保我们有足够的查询
        if len(queries) < num_queries:
            # 如果生成的查询数量不足，添加一些基本查询
            if academic_search:
                default_queries = [
                    f"{topic} research papers",
                    f"{topic} scientific review",
                    f"latest research on {topic}"
                ]
            else:
                default_queries = [
                    topic,
                    f"{topic} 概述",
                    f"{topic} 最新进展"
                ]
            queries.extend(default_queries[:num_queries - len(queries)])
        
        # 只返回请求的数量
        queries = queries[:num_queries]
        
        logger.info(f"生成的搜索查询: {', '.join(queries)}")
        return queries
    
    def analyze_content(self, content: str, question: str) -> str:
        """分析内容，回答特定问题。
        
        Args:
            content: 要分析的内容
            question: 要回答的问题
            
        Returns:
            生成的回答
        """
        logger.info(f"分析内容以回答问题: {question}")
        
        # 检查内容是否足够
        if not content or len(content.strip()) < 100:
            logger.warning(f"为问题 '{question}' 提供的内容不足")
            content = f"虽然没有足够的原始内容，但我将尝试回答关于 '{question}' 的问题。"
        
        system_prompt = """
        你是一个专业的研究分析师。我将给你一些从互联网上获取的相关内容和一个问题。
        请根据提供的内容回答问题。如果内容中没有足够的信息来回答问题，请不要说"抱歉，您没有提供相关内容"，
        而是使用你自己的知识提供信息丰富的回答，同时说明你是基于自己的知识而不是提供的内容回答的。
        回答应该客观、基于事实、有洞察力，并且尽可能有用。
        """
        
        user_prompt = f"""
        问题: {question}
        
        基于以下内容回答:
        
        {content}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.chat_model(messages)
        return response.content
    
    def generate_research_questions(self, topic: str, initial_findings: str, 
                                   num_questions: int = 3) -> List[str]:
        """生成深入研究问题。
        
        Args:
            topic: 研究主题
            initial_findings: 初步研究发现
            num_questions: 生成的问题数量
            
        Returns:
            生成的研究问题列表
        """
        logger.info(f"为主题 '{topic}' 生成深入研究问题")
        
        system_prompt = """
        你是一个专业的研究方法专家。我将给你一个研究主题和一些初步发现。
        请生成深入的研究问题，以引导进一步的研究。这些问题应该帮助揭示更深层次的见解、挑战初步假设、探索不同视角，
        并填补知识空白。每个问题都应该是具体的、有思考性的，并且可以通过进一步的信息搜集来回答。
        """
        
        user_prompt = f"""
        研究主题: {topic}
        
        初步发现:
        {initial_findings}
        
        请基于以上信息，生成 {num_questions} 个深入的研究问题，以指导进一步的研究和分析。
        这些问题应该帮助我们获得更全面、更深入的理解。
        
        格式: 每行一个问题，不要包含数字或标点符号前缀。
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.chat_model(messages)
        
        # 解析返回的问题
        questions = [q.strip() for q in response.content.split('\n') if q.strip()]
        
        logger.info(f"生成了 {len(questions)} 个研究问题")
        return questions[:num_questions]  # 确保返回的问题数量不超过要求
    
    def generate_report(self, topic: str, research_findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """根据研究发现生成最终报告。
        
        Args:
            topic: 研究主题
            research_findings: 研究发现列表
            
        Returns:
            包含报告各部分的字典
        """
        # 构建系统提示
        system_prompt = """你是一个专业的研究报告生成助手。你会分析研究发现，并生成高质量、结构化的研究报告。
        报告应当客观、详实，具有科学性和可读性。确保内容逻辑连贯，观点明确，避免重复冗余。"""
        
        # 构建用户提示
        findings_text = ""
        for i, finding in enumerate(research_findings):
            findings_text += f"问题 {i+1}: {finding['question']}\n"
            findings_text += f"回答: {finding['answer']}\n"
            findings_text += f"来源: {', '.join(finding['sources'])}\n\n"
        
        user_prompt = f"""
        我需要一份关于"{topic}"的研究报告。

        研究发现:
        {findings_text}
        
        请生成一份结构化的研究报告，包括以下部分:
        1. 摘要 - 简要概述研究内容和主要发现（200-300字）
        2. 关键发现 - 列出3-5个最重要的发现点，每点一段话
        3. 详细分析 - 深入分析研究主题，整合所有发现，应包含事实、数据和具体例子
        
        对于详细分析部分:
        - 使用明确的章节标题（例如 # 标题）
        - 使用有序列表（1. 2. 3.）来组织内容，确保序号连续不重复
        - 避免内容重复，整合相似观点
        - 合理分段，每段聚焦一个明确的要点
        
        确保报告内容全面、有逻辑性，并且信息丰富。如果研究发现不足，请使用你的知识补充相关内容。
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.chat_model(messages)
        
        # 从响应中提取报告部分
        content = response.content
        
        # 简单解析报告内容（实际应用中可能需要更复杂的解析）
        summary = ""
        key_findings = []
        detailed_analysis = ""
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if "摘要" in line or "总结" in line:
                current_section = "summary"
                continue
            elif "关键发现" in line or "主要发现" in line:
                current_section = "key_findings"
                continue
            elif "详细分析" in line or "分析" in line:
                current_section = "detailed_analysis"
                continue
                
            if current_section == "summary":
                summary += line + " "
            elif current_section == "key_findings":
                if line.startswith("- ") or line.startswith("* ") or (len(line) > 2 and line[0].isdigit() and line[1] == "."):
                    key_findings.append(line.lstrip("- *0123456789. "))
                else:
                    # 如果已经有关键发现且当前行不是新的项目符号，将其附加到最后一个发现
                    if key_findings:
                        key_findings[-1] += " " + line
            elif current_section == "detailed_analysis":
                detailed_analysis += line + "\n"
        
        # 确保至少有一些关键发现
        if not key_findings:
            # 从内容中提取一些关键句子作为关键发现
            sentences = content.split('。')
            key_findings = [s.strip() + '。' for s in sentences[:3] if len(s.strip()) > 10]
        
        # 如果找不到明确的摘要或分析，使用内容的前半部分作为摘要，后半部分作为分析
        if not summary:
            content_parts = content.split("\n\n")
            if len(content_parts) >= 2:
                summary = content_parts[0].strip()
        
        if not detailed_analysis:
            if summary:
                # 使用除摘要外的所有内容作为详细分析
                detailed_analysis = content.replace(summary, "").strip()
            else:
                # 如果没有识别出摘要，将整个内容作为详细分析
                detailed_analysis = content
        
        # 整理源引用
        sources = []
        for finding in research_findings:
            if 'sources' in finding and finding['sources']:
                for source in finding['sources']:
                    if source not in [s.get('url', '') for s in sources] and 'example.com' not in source:
                        # 使用SearchTool中获取的标题，如果没有则使用默认标题
                        title = f"关于 {topic} 的资料"
                        if len(sources) > 0:
                            title += f" {len(sources) + 1}"
                        sources.append({"url": source, "title": title})
        
        return {
            "summary": summary.strip(),
            "key_findings": key_findings,
            "detailed_analysis": detailed_analysis.strip(),
            "sources": sources
        } 