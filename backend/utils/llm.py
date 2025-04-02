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
        
    def generate_search_queries(self, research_topic: str, num_queries: int = 3) -> List[str]:
        """基于研究主题生成搜索查询。
        
        Args:
            research_topic: 研究主题
            num_queries: 生成的查询数量
            
        Returns:
            生成的搜索查询列表
        """
        logger.info(f"为主题 '{research_topic}' 生成搜索查询")
        
        system_prompt = """
        你是一个专业的研究助手。我将给你一个研究主题，请生成具体的搜索查询，以便从互联网获取相关信息。
        查询应该具体、有针对性，并覆盖主题的不同方面。每个查询都应该是一个完整的搜索词，不要包含引号或特殊格式。
        """
        
        user_prompt = f"""
        研究主题: {research_topic}
        
        请生成 {num_queries} 个不同的搜索查询，以获取关于这个主题的全面信息。确保查询覆盖该主题的不同方面和角度。
        
        格式: 每行一个查询，不要包含数字或标点符号前缀。
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.chat_model(messages)
        
        # 解析返回的查询
        queries = [q.strip() for q in response.content.split('\n') if q.strip()]
        
        logger.info(f"生成了 {len(queries)} 个搜索查询")
        return queries[:num_queries]  # 确保返回的查询数量不超过要求
    
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
        """生成研究报告。
        
        Args:
            topic: 研究主题
            research_findings: 研究发现列表，每个元素包含问题和答案
            
        Returns:
            生成的研究报告
        """
        logger.info(f"为主题 '{topic}' 生成研究报告")
        
        # 检查研究发现是否足够
        has_sufficient_content = True
        if not research_findings or len(research_findings) < 2:
            has_sufficient_content = False
            logger.warning(f"主题 '{topic}' 的研究发现不足")
        
        # 将研究发现格式化为字符串
        findings_text = ""
        for i, finding in enumerate(research_findings):
            findings_text += f"\n问题 {i+1}: {finding['question']}\n"
            findings_text += f"回答: {finding['answer']}\n"
            if 'sources' in finding and finding['sources']:
                findings_text += f"来源: {', '.join(finding['sources'])}\n"
        
        system_prompt = """
        你是一个专业的研究报告撰写专家。我将给你一个研究主题和一系列研究发现。
        请根据这些信息生成一份全面的研究报告，包括摘要、关键发现、详细分析和参考来源。
        报告应该客观、结构清晰、内容连贯，并清晰地呈现得到的洞察。
        
        如果研究发现中有"请使用你的知识"等提示，表示该部分缺乏外部来源的信息。
        在这种情况下，你应该:
        1. 使用你自己的知识填补空白
        2. 确保报告内容丰富、信息量大
        3. 尽量提供相关的数据点、例子和见解
        4. 避免说"内容不足"或"没有足够信息"等消极表述
        
        无论如何，请确保最终报告对用户有用、有见地，并展示对主题的深入理解。
        """
        
        user_prompt = f"""
        研究主题: {topic}
        
        研究发现:
        {findings_text}
        
        请生成一份结构化的研究报告，包括以下部分:
        1. 摘要 - 简要概述研究内容和主要发现（200-300字）
        2. 关键发现 - 列出3-5个最重要的发现点，每点一段话
        3. 详细分析 - 深入分析研究主题，整合所有发现，应包含事实、数据和具体例子
        
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
                detailed_analysis += line + " "
        
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
                        # 为每个来源添加标题
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