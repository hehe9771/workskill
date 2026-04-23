"""
项目主表数据清洗与多维度分析脚本
使用技能: csv-processor, pandas-data-analysis, data-analysis
输出: 项目全维度分析.html + 项目金融维度分析.html
"""
import os
import re
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# ==================== 配置 ====================
INPUT_FILE = os.path.join(os.path.dirname(__file__), "an", "项目主表.csv")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
PYTHON_ENV = r"C:\Users\wuyan\.conda\envs\picproject\python.exe"

# 金额显示单位：万元
WAN = 10000

# Executive 配色
EXEC_COLORS = {
    'primary': '#003366',
    'secondary': '#0066CC',
    'positive': '#2E7D32',
    'negative': '#C62828',
    'neutral': '#757575',
}

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==================== 省份代码映射 ====================
PROVINCE_CODE_MAP = {
    '11': '北京', '12': '天津', '13': '河北', '14': '山西', '15': '内蒙古',
    '21': '辽宁', '22': '吉林', '23': '黑龙江',
    '31': '上海', '32': '江苏', '33': '浙江', '34': '安徽', '35': '福建', '36': '江西', '37': '山东',
    '41': '河南', '42': '湖北', '43': '湖南', '44': '广东', '45': '广西', '46': '海南',
    '50': '重庆', '51': '四川', '52': '贵州', '53': '云南', '54': '西藏',
    '61': '陕西', '62': '甘肃', '63': '青海', '64': '宁夏', '65': '新疆',
}

# ==================== 业务条线规范化 ====================
BUSINESS_LINE_MAP = {
    '风力发电': '风电',
    '光伏发电': '光伏',
    '储能业务': '储能',
}

# ==================== 租赁物类型关键词 ====================
LEASE_ITEM_KEYWORDS = [
    ('储能', ['储能设备', '储能电站', '储能系统', '电池', '储能场站', '换电']),
    ('光伏', ['光伏', '太阳能', '光储']),
    ('风电', ['风电', '风机', '风电站']),
    ('物流车辆', ['冷藏车', '物流车', '商用车']),
]

# ==================== 项目资金类型关键词 ====================
FUND_USE_KEYWORDS = [
    ('设备采购', ['设备采购', '购置', '采购']),
    ('项目建设', ['项目建设', '电站建设', '建设', 'EPC总包', '施工']),
    ('偿还债务', ['结清', '偿还', '债权']),
    ('补充现金流', ['现金流', '经营']),
    ('其他', []),
]


def convert_province_code(code):
    """将6位行政区划代码转换为省份名称"""
    try:
        code_str = str(int(code))[:2]
        return PROVINCE_CODE_MAP.get(code_str, '未知')
    except (ValueError, TypeError):
        return '未知'


def normalize_business_line(value):
    """规范化业务条线"""
    if pd.isna(value) or not str(value).strip():
        return '未知'
    val = str(value).strip()
    return BUSINESS_LINE_MAP.get(val, val)


def extract_lease_type(description):
    """从租赁物描述提取租赁物类型"""
    if pd.isna(description) or not str(description).strip():
        return '未知'
    desc = str(description).lower()
    for type_name, keywords in LEASE_ITEM_KEYWORDS:
        if any(kw in desc for kw in keywords):
            return type_name
    return '其他'


def extract_fund_type(usage):
    """从项目资金用途提取资金类型"""
    if pd.isna(usage) or not str(usage).strip():
        return '未知'
    text = str(usage).lower()
    for type_name, keywords in FUND_USE_KEYWORDS:
        if keywords and any(kw in text for kw in keywords):
            return type_name
    return '其他'


def load_and_clean_data(file_path):
    """加载并清洗数据"""
    logger.info(f"读取CSV文件: {file_path}")

    # 尝试多种编码
    for encoding in ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"成功使用 {encoding} 编码读取，共 {len(df)} 行")
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("无法读取CSV文件，尝试所有编码均失败")

    # 省份字段转换
    logger.info("转换省份代码...")
    df['省份'] = df['省份'].apply(convert_province_code)

    # 缺失值补全
    logger.info("补全缺失值...")
    df['业务类型'] = df['业务类型'].fillna('未知').replace('', '未知')
    df['业务属性'] = df['业务属性'].fillna('未知').replace('', '未知')

    # 提取新字段
    logger.info("提取新字段...")
    df['租赁物类型'] = df['租赁物描述'].apply(extract_lease_type)
    df['项目资金类型'] = df['项目资金用途'].apply(extract_fund_type)
    df['业务条线类型'] = df['业务条线'].apply(normalize_business_line)

    # 金额转换为万元
    df['项目金额_万元'] = pd.to_numeric(df['项目金额'], errors='coerce') / WAN

    # 清理租赁利率字段
    df['租赁利率_数值'] = pd.to_numeric(df['租赁利率'], errors='coerce')

    logger.info(f"数据清洗完成，共 {len(df)} 行，{len(df.columns)} 列")
    return df


def create_html_report(figures, title, summary_cards, output_path):
    """生成HTML报告"""
    html_parts = []
    html_parts.append(f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #f5f7fa;
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, {EXEC_COLORS['primary']}, {EXEC_COLORS['secondary']});
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 8px 0 0;
            opacity: 0.8;
            font-size: 14px;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }}
        .card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .card .label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}
        .card .value {{
            font-size: 24px;
            font-weight: bold;
            color: {EXEC_COLORS['primary']};
        }}
        .chart-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
""")

    # 汇总卡片
    if summary_cards:
        html_parts.append('<div class="summary-cards">')
        for label, value in summary_cards:
            html_parts.append(f'''
            <div class="card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
            </div>
            ''')
        html_parts.append('</div>')

    # 图表
    for fig in figures:
        html_parts.append('<div class="chart-container">')
        html_parts.append(fig.to_html(full_html=False, include_plotlyjs=True))
        html_parts.append('</div>')

    html_parts.append('</body></html>')
    html_content = '\n'.join(html_parts)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    logger.info(f"报告已保存: {output_path}")


def format_wan(value):
    """格式化金额为万元显示"""
    if pd.isna(value):
        return '0.00'
    return f"{value:,.2f}"


def generate_amount_report(df):
    """生成项目全维度分析报告（金额维度）"""
    logger.info("生成项目全维度分析报告（金额维度）...")
    figures = []

    # 汇总卡片
    total_amount = df['项目金额_万元'].sum()
    avg_amount = df['项目金额_万元'].mean()
    max_amount = df['项目金额_万元'].max()
    total_projects = len(df)

    summary_cards = [
        ('项目总数', f"{total_projects} 个"),
        ('总金额', f"{format_wan(total_amount)} 万元"),
        ('平均金额', f"{format_wan(avg_amount)} 万元"),
        ('最大金额', f"{format_wan(max_amount)} 万元"),
    ]

    # 1. 金额Top10客户
    client_amount = df.groupby('客户名称')['项目金额_万元'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(
        client_amount, x='客户名称', y='项目金额_万元',
        title='项目金额 Top10 客户',
        color_discrete_sequence=[EXEC_COLORS['primary']]
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title='金额（万元）',
        xaxis_title='',
        plot_bgcolor='white',
    )
    fig.update_yaxes(tickformat=',.0f')
    figures.append(fig)

    # 2. 各省份金额分布
    province_amount = df.groupby('省份')['项目金额_万元'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(
        province_amount, x='省份', y='项目金额_万元',
        title='各省份项目金额分布',
        color_discrete_sequence=[EXEC_COLORS['secondary']]
    )
    fig.update_layout(
        yaxis_title='金额（万元）',
        xaxis_title='',
        plot_bgcolor='white',
    )
    fig.update_yaxes(tickformat=',.0f')
    figures.append(fig)

    # 3. 租赁物类型金额分布
    lease_amount = df.groupby('租赁物类型')['项目金额_万元'].sum().sort_values(ascending=False).reset_index()
    fig = px.pie(
        lease_amount, names='租赁物类型', values='项目金额_万元',
        title='租赁物类型金额分布',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    figures.append(fig)

    # 4. 项目资金类型金额分布
    fund_amount = df.groupby('项目资金类型')['项目金额_万元'].sum().sort_values(ascending=False).reset_index()
    fig = px.pie(
        fund_amount, names='项目资金类型', values='项目金额_万元',
        title='项目资金类型金额分布',
        color_discrete_sequence=px.colors.qualitative.Pastel1
    )
    figures.append(fig)

    # 5. 业务条线类型金额分布
    line_amount = df.groupby('业务条线类型')['项目金额_万元'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(
        line_amount, x='业务条线类型', y='项目金额_万元',
        title='业务条线类型金额分布',
        color_discrete_sequence=[EXEC_COLORS['primary']]
    )
    fig.update_layout(
        yaxis_title='金额（万元）',
        xaxis_title='',
        plot_bgcolor='white',
    )
    fig.update_yaxes(tickformat=',.0f')
    figures.append(fig)

    # 6. 部门金额排名
    dept_amount = df.groupby('部门名称')['项目金额_万元'].sum().sort_values(ascending=True).reset_index()
    fig = px.bar(
        dept_amount, x='项目金额_万元', y='部门名称', orientation='h',
        title='部门项目金额排名',
        color_discrete_sequence=[EXEC_COLORS['secondary']]
    )
    fig.update_layout(
        xaxis_title='金额（万元）',
        yaxis_title='',
        plot_bgcolor='white',
    )
    fig.update_xaxes(tickformat=',.0f')
    figures.append(fig)

    # 7. 业务属性金额分布
    attr_amount = df.groupby('业务属性')['项目金额_万元'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(
        attr_amount, x='业务属性', y='项目金额_万元',
        title='业务属性金额分布',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        yaxis_title='金额（万元）',
        xaxis_title='',
        plot_bgcolor='white',
    )
    fig.update_yaxes(tickformat=',.0f')
    figures.append(fig)

    # 8. 业务类型金额分布
    type_amount = df.groupby('业务类型')['项目金额_万元'].sum().sort_values(ascending=False).reset_index()
    fig = px.pie(
        type_amount, names='业务类型', values='项目金额_万元',
        title='业务类型金额分布',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    figures.append(fig)

    # 9. 客户经理金额Top10
    manager_amount = df.groupby('客户经理名称')['项目金额_万元'].sum().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(
        manager_amount, x='客户经理名称', y='项目金额_万元',
        title='客户经理项目金额 Top10',
        color_discrete_sequence=[EXEC_COLORS['primary']]
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title='金额（万元）',
        xaxis_title='',
        plot_bgcolor='white',
    )
    fig.update_yaxes(tickformat=',.0f')
    figures.append(fig)

    output_path = os.path.join(OUTPUT_DIR, "项目全维度分析.html")
    create_html_report(figures, "项目全维度分析报告（金额分析）", summary_cards, output_path)


def generate_count_report(df):
    """生成项目金融维度分析报告（个数维度）"""
    logger.info("生成项目金融维度分析报告（个数维度）...")
    figures = []

    # 汇总卡片
    total_projects = len(df)
    unique_clients = df['客户名称'].nunique()
    unique_managers = df['客户经理名称'].nunique()
    unique_depts = df['部门名称'].nunique()

    summary_cards = [
        ('项目总数', f"{total_projects} 个"),
        ('客户总数', f"{unique_clients} 个"),
        ('客户经理数', f"{unique_managers} 个"),
        ('部门数', f"{unique_depts} 个"),
    ]

    # 1. 各省份项目数量分布
    province_count = df.groupby('省份')['项目ID'].count().sort_values(ascending=False).reset_index()
    province_count.columns = ['省份', '项目数量']
    fig = px.bar(
        province_count, x='省份', y='项目数量',
        title='各省份项目数量分布',
        color_discrete_sequence=[EXEC_COLORS['primary']]
    )
    fig.update_layout(
        yaxis_title='项目数量',
        xaxis_title='',
        plot_bgcolor='white',
    )
    figures.append(fig)

    # 2. 租赁物类型项目数量分布
    lease_count = df.groupby('租赁物类型')['项目ID'].count().sort_values(ascending=False).reset_index()
    lease_count.columns = ['租赁物类型', '项目数量']
    fig = px.pie(
        lease_count, names='租赁物类型', values='项目数量',
        title='租赁物类型项目数量分布',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    figures.append(fig)

    # 3. 项目资金类型项目数量分布
    fund_count = df.groupby('项目资金类型')['项目ID'].count().sort_values(ascending=False).reset_index()
    fund_count.columns = ['项目资金类型', '项目数量']
    fig = px.pie(
        fund_count, names='项目资金类型', values='项目数量',
        title='项目资金类型项目数量分布',
        color_discrete_sequence=px.colors.qualitative.Pastel1
    )
    figures.append(fig)

    # 4. 业务条线类型项目数量分布
    line_count = df.groupby('业务条线类型')['项目ID'].count().sort_values(ascending=False).reset_index()
    line_count.columns = ['业务条线类型', '项目数量']
    fig = px.bar(
        line_count, x='业务条线类型', y='项目数量',
        title='业务条线类型项目数量分布',
        color_discrete_sequence=[EXEC_COLORS['secondary']]
    )
    fig.update_layout(
        yaxis_title='项目数量',
        xaxis_title='',
        plot_bgcolor='white',
    )
    figures.append(fig)

    # 5. 部门项目数量排名
    dept_count = df.groupby('部门名称')['项目ID'].count().sort_values(ascending=True).reset_index()
    dept_count.columns = ['部门名称', '项目数量']
    fig = px.bar(
        dept_count, x='项目数量', y='部门名称', orientation='h',
        title='部门项目数量排名',
        color_discrete_sequence=[EXEC_COLORS['primary']]
    )
    fig.update_layout(
        xaxis_title='项目数量',
        yaxis_title='',
        plot_bgcolor='white',
    )
    figures.append(fig)

    # 6. 业务属性项目数量分布
    attr_count = df.groupby('业务属性')['项目ID'].count().sort_values(ascending=False).reset_index()
    attr_count.columns = ['业务属性', '项目数量']
    fig = px.bar(
        attr_count, x='业务属性', y='项目数量',
        title='业务属性项目数量分布',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        yaxis_title='项目数量',
        xaxis_title='',
        plot_bgcolor='white',
    )
    figures.append(fig)

    # 7. 业务类型项目数量分布
    type_count = df.groupby('业务类型')['项目ID'].count().sort_values(ascending=False).reset_index()
    type_count.columns = ['业务类型', '项目数量']
    fig = px.pie(
        type_count, names='业务类型', values='项目数量',
        title='业务类型项目数量分布',
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    figures.append(fig)

    # 8. 客户经理项目数量Top10
    manager_count = df.groupby('客户经理名称')['项目ID'].count().sort_values(ascending=False).head(10).reset_index()
    manager_count.columns = ['客户经理名称', '项目数量']
    fig = px.bar(
        manager_count, x='客户经理名称', y='项目数量',
        title='客户经理项目数量 Top10',
        color_discrete_sequence=[EXEC_COLORS['secondary']]
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title='项目数量',
        xaxis_title='',
        plot_bgcolor='white',
    )
    figures.append(fig)

    # 9. 客户项目数量Top10
    client_count = df.groupby('客户名称')['项目ID'].count().sort_values(ascending=False).head(10).reset_index()
    client_count.columns = ['客户名称', '项目数量']
    fig = px.bar(
        client_count, x='客户名称', y='项目数量',
        title='客户项目数量 Top10',
        color_discrete_sequence=[EXEC_COLORS['primary']]
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        yaxis_title='项目数量',
        xaxis_title='',
        plot_bgcolor='white',
    )
    figures.append(fig)

    output_path = os.path.join(OUTPUT_DIR, "项目金融维度分析.html")
    create_html_report(figures, "项目金融维度分析报告（数量分析）", summary_cards, output_path)


def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("项目主表数据清洗与分析开始")
    logger.info("=" * 50)

    try:
        # Step 1: 加载和清洗数据
        df = load_and_clean_data(INPUT_FILE)

        # 打印字段提取统计
        logger.info(f"租赁物类型分布: {df['租赁物类型'].value_counts().to_dict()}")
        logger.info(f"项目资金类型分布: {df['项目资金类型'].value_counts().to_dict()}")
        logger.info(f"业务条线类型分布: {df['业务条线类型'].value_counts().to_dict()}")
        logger.info(f"省份分布: {df['省份'].value_counts().to_dict()}")

        # Step 2: 生成项目全维度分析（金额）
        generate_amount_report(df)

        # Step 3: 生成项目金融维度分析（个数）
        generate_count_report(df)

        logger.info("=" * 50)
        logger.info("分析完成！")
        logger.info(f"输出文件1: {os.path.join(OUTPUT_DIR, '项目全维度分析.html')}")
        logger.info(f"输出文件2: {os.path.join(OUTPUT_DIR, '项目金融维度分析.html')}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"分析过程中发生错误: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
