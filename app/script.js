/**
 * DeepResearch Agent 前端脚本
 */

// DOM 元素
const researchForm = document.getElementById('researchForm');
const researchTopicInput = document.getElementById('researchTopic');
const researchDepthInput = document.getElementById('researchDepth');
const maxSourcesInput = document.getElementById('maxSources');
const startResearchBtn = document.getElementById('startResearchBtn');

const researchProgress = document.getElementById('researchProgress');
const progressTopic = document.getElementById('progressTopic');
const progressBar = document.getElementById('progressBar');
const currentStep = document.getElementById('currentStep');
const newResearchBtn = document.getElementById('newResearchBtn');

const researchResults = document.getElementById('researchResults');
const reportTopic = document.getElementById('reportTopic');
const reportSummary = document.getElementById('reportSummary');
const keyFindings = document.getElementById('keyFindings');
const detailedAnalysis = document.getElementById('detailedAnalysis');
const researchSteps = document.getElementById('researchSteps');
const sources = document.getElementById('sources');
const newResearchBtnEnd = document.getElementById('newResearchBtnEnd');

const errorCard = document.getElementById('errorCard');
const errorMessage = document.getElementById('errorMessage');
const newResearchBtnError = document.getElementById('newResearchBtnError');

// 全局变量
let activeResearchId = null;
let pollingTimer = null;

// API 路径
const API_BASE_URL = window.location.origin;
const START_RESEARCH_URL = `${API_BASE_URL}/api/research/start`;
const GET_STATUS_URL = `${API_BASE_URL}/api/research/status/`;

/**
 * 将Markdown文本转换为HTML
 * @param {string} markdown - Markdown格式的文本
 * @return {string} - 转换后的HTML
 */
function markdownToHtml(markdown) {
    if (!markdown) return '';
    
    // 替换标题
    markdown = markdown.replace(/^### (.*$)/gm, '<h5>$1</h5>');
    markdown = markdown.replace(/^## (.*$)/gm, '<h4>$1</h4>');
    markdown = markdown.replace(/^# (.*$)/gm, '<h3>$1</h3>');
    
    // 替换粗体和斜体
    markdown = markdown.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    markdown = markdown.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // 替换列表
    markdown = markdown.replace(/^\d+\.\s+(.*$)/gm, '<li>$1</li>');
    markdown = markdown.replace(/^-\s+(.*$)/gm, '<li>$1</li>');
    
    // 替换换行符
    markdown = markdown.replace(/\n/g, '<br>');
    
    return markdown;
}

/**
 * 初始化页面
 */
function init() {
    researchForm.addEventListener('submit', handleSubmitResearch);
    newResearchBtn.addEventListener('click', resetResearch);
    newResearchBtnEnd.addEventListener('click', resetResearch);
    newResearchBtnError.addEventListener('click', resetResearch);
}

/**
 * 处理研究表单提交
 * @param {Event} event - 表单提交事件
 */
async function handleSubmitResearch(event) {
    event.preventDefault();

    // 获取表单数据
    const topic = researchTopicInput.value.trim();
    const depth = parseInt(researchDepthInput.value);
    const maxSources = parseInt(maxSourcesInput.value);

    if (!topic) {
        showError('请输入研究主题');
        return;
    }

    // 显示加载状态
    startResearchBtn.disabled = true;
    startResearchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 正在启动...';

    try {
        // 调用API启动研究
        const response = await fetch(START_RESEARCH_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic,
                depth,
                max_sources: maxSources
            })
        });

        if (!response.ok) {
            throw new Error(`API错误: ${response.status}`);
        }

        const data = await response.json();
        activeResearchId = data.research_id;

        // 显示进度界面
        showProgressView(topic);

        // 开始轮询研究状态
        startPolling();

    } catch (error) {
        console.error('启动研究失败:', error);
        showError(`启动研究失败: ${error.message}`);
        
        // 重置按钮状态
        startResearchBtn.disabled = false;
        startResearchBtn.innerHTML = '<i class="bi bi-play-fill me-2"></i>开始研究';
    }
}

/**
 * 开始轮询研究状态
 */
function startPolling() {
    if (!activeResearchId) return;

    // 每2秒轮询一次
    pollingTimer = setInterval(async () => {
        try {
            const status = await fetchResearchStatus(activeResearchId);
            updateProgressView(status);

            // 如果研究完成或失败，停止轮询
            if (status.status === 'completed' || status.status === 'failed') {
                stopPolling();
                
                if (status.status === 'completed') {
                    showResults(status);
                } else if (status.status === 'failed') {
                    showError(`研究失败: ${status.error || '未知错误'}`);
                }
            }
        } catch (error) {
            console.error('获取研究状态失败:', error);
            stopPolling();
            showError(`获取研究状态失败: ${error.message}`);
        }
    }, 2000);
}

/**
 * 停止轮询
 */
function stopPolling() {
    if (pollingTimer) {
        clearInterval(pollingTimer);
        pollingTimer = null;
    }
}

/**
 * 获取研究状态
 * @param {string} researchId - 研究ID
 * @returns {Promise<Object>} - 研究状态对象
 */
async function fetchResearchStatus(researchId) {
    const response = await fetch(`${GET_STATUS_URL}${researchId}`);
    
    if (!response.ok) {
        throw new Error(`API错误: ${response.status}`);
    }
    
    return await response.json();
}

/**
 * 显示进度视图
 * @param {string} topic - 研究主题
 */
function showProgressView(topic) {
    // 隐藏其他视图
    researchForm.closest('.card').classList.add('d-none');
    researchResults.classList.add('d-none');
    errorCard.classList.add('d-none');
    
    // 显示进度视图
    researchProgress.classList.remove('d-none');
    progressTopic.textContent = topic;
    updateProgress(0, "初始化中...");
}

/**
 * 更新进度视图
 * @param {Object} status - 研究状态对象
 */
function updateProgressView(status) {
    const progressPercentage = Math.round(status.progress * 100);
    updateProgress(progressPercentage, status.current_step);
    
    // 研究完成时启用新建研究按钮
    if (status.status === 'completed' || status.status === 'failed') {
        newResearchBtn.disabled = false;
    }
}

/**
 * 更新进度条和当前步骤
 * @param {number} percentage - 进度百分比
 * @param {string} step - 当前步骤描述
 */
function updateProgress(percentage, step) {
    progressBar.style.width = `${percentage}%`;
    progressBar.setAttribute('aria-valuenow', percentage);
    progressBar.textContent = `${percentage}%`;
    currentStep.textContent = step;
}

/**
 * 显示研究结果
 * @param {Object} status - 包含报告的研究状态对象
 */
function showResults(status) {
    if (!status.report) return;
    
    // 隐藏其他视图
    researchProgress.classList.add('d-none');
    errorCard.classList.add('d-none');
    
    // 显示结果视图
    researchResults.classList.remove('d-none');
    
    // 填充报告内容
    reportTopic.textContent = status.report.topic;
    reportSummary.innerHTML = markdownToHtml(status.report.summary);
    
    // 填充关键发现
    keyFindings.innerHTML = '';
    status.report.key_findings.forEach(finding => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = markdownToHtml(finding);
        keyFindings.appendChild(li);
    });
    
    // 填充详细分析，转换Markdown为HTML
    detailedAnalysis.innerHTML = markdownToHtml(status.report.detailed_analysis);
    
    // 填充研究步骤
    researchSteps.innerHTML = '';
    status.report.analysis_steps.forEach((step, index) => {
        const stepId = `step-${index}`;
        const headingId = `heading-${index}`;
        const collapseId = `collapse-${index}`;
        
        researchSteps.innerHTML += `
            <div class="accordion-item">
                <h2 class="accordion-header" id="${headingId}">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                        ${step.question}
                    </button>
                </h2>
                <div id="${collapseId}" class="accordion-collapse collapse" aria-labelledby="${headingId}" 
                     data-bs-parent="#researchSteps">
                    <div class="accordion-body">
                        <p>${markdownToHtml(step.answer)}</p>
                        <p class="mt-2 text-muted small">
                            <strong>来源:</strong> ${step.sources.length > 0 ? step.sources.join(', ') : '无特定来源'}
                        </p>
                    </div>
                </div>
            </div>
        `;
    });
    
    // 填充信息来源
    sources.innerHTML = '';
    status.report.sources.forEach(source => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        // 显示标题（如果存在）或URL
        const linkText = source.title && source.title !== '' ? source.title : source.url;
        li.innerHTML = `<a href="${source.url}" target="_blank">${linkText}</a>`;
        sources.appendChild(li);
    });
}

/**
 * 显示错误信息
 * @param {string} message - 错误消息
 */
function showError(message) {
    // 隐藏其他视图
    researchProgress.classList.add('d-none');
    researchResults.classList.add('d-none');
    
    // 显示错误视图
    errorCard.classList.remove('d-none');
    errorMessage.textContent = message;
}

/**
 * 重置研究，返回到初始视图
 */
function resetResearch() {
    // 停止轮询
    stopPolling();
    
    // 重置全局变量
    activeResearchId = null;
    
    // 重置表单按钮
    startResearchBtn.disabled = false;
    startResearchBtn.innerHTML = '<i class="bi bi-play-fill me-2"></i>开始研究';
    
    // 显示初始视图
    researchForm.closest('.card').classList.remove('d-none');
    researchProgress.classList.add('d-none');
    researchResults.classList.add('d-none');
    errorCard.classList.add('d-none');
}

// 页面加载时初始化
document.addEventListener('DOMContentLoaded', init); 