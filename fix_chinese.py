import os
import re

translations = {
    # Backend Logging & Agent
    '开始规划报告大纲': 'Starting report outline planning',
    '大纲规划完成': 'Outline planning complete',
    '大纲已生成': 'Outline generated',
    '大纲已保存': 'Outline saved',
    '章节已保存': 'Section saved',
    '报告生成失败': 'Report generation failed',
    '覆盖包含主结果': 'Overwriting with main result',
    '主结果生成成功': 'Main result generated successfully',
    '阶段1: 规划大纲': 'Phase 1: Planning Outline',
    '模型不支持工具调用，降级为普通对话': 'Model does not support tools, degrading to chat',
    '生成大纲': 'Generate Outline',
    '生成章节': 'Generate Section',
    '汇总报告': 'Assemble Report',
    '开始提取事实与社区摘要': 'Extracting facts and community summary',
    '完成数据提取': 'Data extraction complete',
    '报告生成任务已取消': 'Report generation task cancelled',
    '分析完成': 'Analysis complete',
    '大纲数据异常': 'Outline data invalid',
    '章节数据异常': 'Section data invalid',
    '报告路径异常': 'Report path invalid',

    # Frontend Remnants
    '进入Master Dashboard': 'Open Master Dashboard',
    '进入 Step': 'Entering Step',
    '进入 Environment Setup': 'Enter Environment Setup',
    '进入 Configuration': 'Enter Configuration',
    '请进入下一步': 'Please proceed to next step',
    '图谱Loading...': 'Graph Loading...',
    '图谱Building...': 'Graph Building...',
    '加载图谱...': 'Loading graph...',
    '图谱数据加载成功': 'Graph data loaded successfully',
    '图谱加载失败': 'Graph loading failed',
    
    # Step4 UI specifics in screenshot
    '试验结果预测与人群反应': 'Trial Results & Cohort Response',
    '未来趋势与风险分析': 'Trajectory & Risk Analysis',
    '结构性建议与优化方向': 'Structural Recommendations',
    '本报告基于': 'This report is based on',
    '未来预测报告': 'Predictive Analysis Report',
    '内容生成完成': 'Content generated',
    '章节内容生成完成': 'Section content generated'
}

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    for ch, en in translations.items():
        content = content.replace(ch, en)
        
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Translated leftovers in: {filepath}")

def main():
    paths = [
        r"C:\Users\Nirav\.vscode\projects\MiroFish\frontend\src",
        r"C:\Users\Nirav\.vscode\projects\MiroFish\backend\app"
    ]
    for base_dir in paths:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith(('.vue', '.js', '.py')):
                    fix_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
