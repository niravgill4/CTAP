import os
import re

translations = {
    # System & Generic
    '加载中...': 'Loading...',
    '暂无数据': 'No data',
    '提示': 'Notice',
    '取消': 'Cancel',
    '确定': 'Confirm',
    '返回主页': 'Home',
    '返回首页': 'Home',
    '等待': 'Waiting',
    '已完成': 'Complete',
    '进行中': 'In Progress',
    '未知': 'Unknown',
    '无': 'None',
    '错误': 'Error',
    '刷新': 'Refresh',
    '关闭': 'Close',

    # Process.vue
    '刷新图谱': 'Refresh',
    '退出全屏': 'Exit Full Screen',
    '全屏显示': 'Full Screen',
    '构建失败': 'Build Failed',
    '图谱构建中': 'Building Map',
    '本体生成中': 'Generating Ontology',
    '初始化中': 'Initializing',
    '项目初始化失败': 'Project Init Failed',
    '加载项目失败': 'Load Project Failed',
    '启动图谱构建失败': 'Build Start Failed',
    '处理中...': 'Processing...',
    '未找到当前项目': 'Project Not Found',
    '准备上传文档...': 'Preparing documents...',
    '上传文件以启动构建': 'Upload files to start',
    '正在上传文件并分析文档...': 'Uploading and analyzing docs...',
    '正在启动图谱构建...': 'Starting map build...',
    '图谱构建任务已启动...': 'Map build started...',
    '创建模拟失败:': 'Simulation create failed:',
    '环境搭建功能开发中...': 'Environment setup in dev...',

    # Step1
    '本体生成': 'Ontology Generation',
    '生成中': 'Generating',
    '实体节点': 'Subject Nodes',
    '关系边': 'Relationships',
    'SCHEMA类型': 'SCHEMA Types',
    '图谱构建已完成，请进入下一步进行模拟环境搭建': 'Knowledge map build complete. Proceed to next step.',
    '创建中...': 'Creating...',
    '进入环境搭建 ➝': 'Enter Setup ➝',
    'LLM分析文档内容与模拟需求，提取出现实种子，自动生成合适的本体结构': 'Extracts seeds to automatically generate clinical ontology.',
    '基于生成的本体，将文档自动分块后调用 Zep 构建知识图谱，提取实体和关系，并形成时序记忆与社区摘要': 'Builds the knowledge graph extracting entities, relationships, memories.',
    '正在分析文档...': 'Analyzing documents...',
    '图谱构建': 'GraphRAG Build',
    '构建完成': 'Build Complete',
    
    # Step2
    '模拟实例': 'Simulation Instance',
    '生成 Agent 人设': 'Patient Agent Generation',
    '生成双平台模拟配置': 'Trial Configuration',
    '新建simulation实例，拉取模拟世界参数模版': 'Create simulation instance, fetch parameter templates',
    '查询图谱，提取患者实体构建Agent数字分身，赋予人口统计学、社交属性和预设人设': 'Query graph for clinical entities, spawn Agent digital twins with traits.',
    'LLM读取日程与人设，为每位Agent生成双平台（Twitter/Reddit）的发帖频率、活跃时间段及偏好事件配置': 'LLM reads schedules, configures platform activity and behavior parameters.',
    '等待中': 'Waiting',

    # Step3
    '平台进度': 'Platform Status',
    '回合': 'ROUND',
    '已用时间': 'Elapsed Time',
    '动作数': 'ACTS',
    '可用动作': 'Available Actions',
    '发帖': 'Post',
    '点赞': 'Like',
    '转发': 'Repost',
    '引用': 'Quote',
    '关注': 'Follow',
    '闲置': 'Idle',
    '评论': 'Comment',
    '踩': 'Dislike',
    '搜索': 'Search',
    '看趋势': 'Trend',
    '屏蔽': 'Mute',
    '发布帖子': 'Created post',
    '点赞帖子': 'Liked post',
    '转发了': 'Reposted',
    '关注了': 'Followed',
    '搜索了': 'Searched',
    '查看了热搜': 'Viewed trends',
    '屏蔽了': 'Muted',
    '刷新了': 'Refreshed',
    '评论了': 'Commented on',
    '踩了': 'Disliked',
    
    # Step4
    '报告生成': 'Report Generation',
    '基于模拟产生的数万条Agent交互日志，由分析Agent开始进行多维度的报告反思与撰写': 'Analysis Agent synthesizes the logs into a multi-dimensional attrition report.',
    '诊断报告': 'Diagnostics Report',
    '执行进度': 'Progress',
    '耗时': 'Time Taken',
    '字数': 'Word Count',
    '尚未生成报告...': 'Generating Report...',
    '导出 PDF': 'Export PDF',
    
    # HistoryDatabase
    '没有找到相关的历史记录': 'No records found',
    '选择项目查看详情': 'Select project for details',
    '暂无文件': 'No files',
    '模拟需求': 'Trial Objective',
    '支撑文档': 'Supporting Documents',
    '图谱数据异常': 'Graph data invalid',
    '没有找到该时间点的日志记录': 'No log found at this timestamp',
    
    # Layout and View Overrides
    'MIROFISH': 'CTAP',
    'Powered by MiroFish': 'Powered by Clinical Trial Attrition Predictor',
    'MiroFish 自动规划推演现实': 'System schedules trial reality for',
    '图谱': 'Graph',
    '双栏': 'Split View',
    '工作台': 'Workbench',
    '深度互动': 'Master Dashboard',
    '环境搭建': 'Environment Setup',
    '开始模拟': 'Start Simulation',
    '图谱数据加载成功': 'Graph data loaded successfully',
    '图谱加载失败': 'Graph loading failed',
    '开启图谱实时Refresh (30s)': 'Enable recurring map refresh (30s)',
    '停止图谱实时Refresh': 'Stop map refresh',
    '进入深度互动': 'Open Master Dashboard',
    '个体链接与交互图谱': 'Entity Interaction Graph',
    '小时，每轮代表现实': 'hours, each round represents',
    '分钟时间流逝': 'minutes elapsed',
}

def translate_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    for ch, en in translations.items():
        content = content.replace(ch, en)
        
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Translated: {filepath}")

def main():
    base_dir = r"C:\Users\Nirav\.vscode\projects\MiroFish\frontend\src"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(('.vue', '.js')):
                translate_file(os.path.join(root, file))

if __name__ == "__main__":
    main()
