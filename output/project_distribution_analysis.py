"""
项目全维度分布分析
按租赁物类型、项目资金类型、客户经理名称、部门名称、省份、
业务属性、业务类型、业务条线、业务条线类型等维度分析项目数量分布
输出HTML报告
"""
import pandas as pd
import plotly.graph_objects as go
import os

COLORS = [
    '#003366', '#0066CC', '#66A3D2', '#FF6B35', '#2E7D32',
    '#C62828', '#757575', '#8E24AA', '#00897B', '#F9A825',
    '#5D4037', '#1565C0', '#AD1457', '#00695C', '#EF6C00',
    '#4527A0', '#E65100', '#1B5E20', '#0277BD', '#558B2F',
    '#6A1B9A', '#00838F', '#BF360C', '#33691E', '#01579B',
    '#4E342E', '#37474F', '#880E4F', '#1A237E', '#004D40',
]

PRIMARY = '#003366'


def load_data(filepath):
    """加载CSV数据，填充空值"""
    df = pd.read_csv(filepath, encoding='utf-8')
    fill_cols = ['省份', '业务属性', '业务类型', '客户经理名称',
                 '部门名称', '租赁物类型', '项目资金类型',
                 '业务条线', '业务条线类型']
    for col in fill_cols:
        if col in df.columns:
            df[col] = df[col].fillna('未知')
    return df


def fig_to_div(fig, chart_id):
    """将plotly figure转为HTML div（避免中文JS变量名问题）"""
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        div_id=chart_id,
        config={'responsive': True},
    )


def create_bar_chart(labels, values, title, x_label):
    """创建柱状图"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        marker_color=COLORS[:len(labels)],
        text=values, textposition='outside',
        textfont=dict(size=12),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        xaxis_title=x_label, yaxis_title="项目数量",
        font=dict(family="Microsoft YaHei", size=12),
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showline=True,
                   linecolor='black', tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0',
                   showline=True, linecolor='black'),
        margin=dict(l=60, r=40, t=60, b=120),
        height=500,
    )
    return fig


def create_pie_chart(labels, values, title):
    """创建饼图"""
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=COLORS[:len(labels)]),
        textinfo='label+percent+value',
        textfont=dict(size=11),
        hole=0.3,
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        font=dict(family="Microsoft YaHei", size=12),
        height=500,
        margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_h_bar(labels, values, title, x_label="项目数量"):
    """创建水平柱状图（最大值在上方）"""
    # 传入时已降序，反转使最大值在上方
    labels_r = list(reversed(labels))
    values_r = list(reversed(values))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values_r, y=labels_r,
        orientation='h', marker_color=PRIMARY,
        text=values_r, textposition='outside',
        textfont=dict(size=11),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        xaxis_title=x_label,
        font=dict(family="Microsoft YaHei", size=12),
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#E0E0E0',
                   showline=True, linecolor='black'),
        yaxis=dict(showgrid=False, showline=True, linecolor='black'),
        margin=dict(l=200, r=80, t=60, b=40),
        height=max(400, len(labels_r) * 30 + 100),
    )
    return fig


def build_summary_table(df, dimensions):
    """构建汇总统计表"""
    rows = []
    for dim in dimensions:
        col = dim['col']
        label = dim['label']
        counts = df[col].value_counts()
        rows.append({
            '分析维度': label,
            '分类数': len(counts),
            '最多类别': f"{counts.index[0]}（{counts.values[0]}个）",
            '最少类别': f"{counts.index[-1]}（{counts.values[-1]}个）",
            '项目总数': counts.sum(),
        })
    return pd.DataFrame(rows)


def generate_distribution_html(df, output_path):
    """生成项目分布分析HTML报告"""
    dimensions = [
        {'col': '业务条线类型', 'label': '业务条线类型'},
        {'col': '租赁物类型', 'label': '租赁物类型'},
        {'col': '项目资金类型', 'label': '项目资金类型'},
        {'col': '业务属性', 'label': '业务属性'},
        {'col': '业务类型', 'label': '业务类型'},
        {'col': '业务条线', 'label': '业务条线'},
        {'col': '部门名称', 'label': '部门名称'},
        {'col': '省份', 'label': '省份'},
        {'col': '客户经理名称', 'label': '客户经理名称'},
    ]

    total_projects = len(df)
    summary_df = build_summary_table(df, dimensions)
    unique_provinces = df['省份'].nunique()
    unique_managers = df['客户经理名称'].nunique()
    unique_depts = df['部门名称'].nunique()
    unique_biz_lines = df['业务条线类型'].nunique()

    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>项目全维度分布分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', sans-serif;
            background: #f5f7fa; margin: 0; padding: 0;
        }}
        .header {{
            background: linear-gradient(135deg, #003366, #0066CC);
            color: white; padding: 30px 40px;
        }}
        .header h1 {{ margin: 0; font-size: 28px; }}
        .header p {{ margin: 8px 0 0; opacity: 0.85; font-size: 14px; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px 40px; }}
        .kpi-row {{
            display: flex; gap: 20px; margin: 20px 0 30px; flex-wrap: wrap;
        }}
        .kpi-card {{
            flex: 1; min-width: 180px; background: white;
            border-radius: 10px; padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center;
        }}
        .kpi-card .value {{
            font-size: 32px; font-weight: bold; color: #003366;
        }}
        .kpi-card .label {{
            font-size: 13px; color: #757575; margin-top: 6px;
        }}
        .section {{
            background: white; border-radius: 10px;
            padding: 25px; margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}
        .section h2 {{
            color: #003366; border-bottom: 2px solid #003366;
            padding-bottom: 10px; margin-top: 0;
        }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #E0E0E0; }}
        th {{ background: #003366; color: white; font-weight: 600; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #e8f0fe; }}
        .chart-row {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .chart-half {{ flex: 1; min-width: 500px; }}
        .footer {{ text-align: center; padding: 20px; color: #757575; font-size: 12px; }}
    </style>
</head>
<body>
<div class="header">
    <h1>项目全维度分布分析报告</h1>
    <p>数据来源：项目主表 | 项目总数：{total_projects} 个 | 分析维度：{len(dimensions)} 个</p>
</div>
<div class="container">

    <div class="kpi-row">
        <div class="kpi-card"><div class="value">{total_projects}</div><div class="label">项目总数</div></div>
        <div class="kpi-card"><div class="value">{unique_provinces}</div><div class="label">覆盖省份数</div></div>
        <div class="kpi-card"><div class="value">{unique_managers}</div><div class="label">客户经理人数</div></div>
        <div class="kpi-card"><div class="value">{unique_depts}</div><div class="label">业务部门数</div></div>
        <div class="kpi-card"><div class="value">{unique_biz_lines}</div><div class="label">业务条线类型数</div></div>
    </div>

    <div class="section">
        <h2>各维度分布概览</h2>
        {summary_df.to_html(index=False, classes='', border=0)}
    </div>
""")

    # 逐维度图表
    chart_counter = 0
    for dim in dimensions:
        col = dim['col']
        label = dim['label']
        counts = df[col].value_counts()
        labels_list = counts.index.astype(str).tolist()
        values_list = counts.values.tolist()

        html_parts.append(f"""
    <div class="section">
        <h2>{label}分布分析（共{len(counts)}类）</h2>
        <div class="chart-row"><div class="chart-half">
""")
        # 柱状图
        if len(counts) <= 15:
            bar_fig = create_bar_chart(
                labels_list, values_list,
                f"按{label}分布的项目数量", label)
        else:
            bar_fig = create_h_bar(
                labels_list[:20], values_list[:20],
                f"按{label}分布的项目数量（Top20）")

        chart_counter += 1
        html_parts.append(fig_to_div(bar_fig, f"c{chart_counter}"))

        html_parts.append("</div><div class='chart-half'>")

        # 饼图
        pie_fig = create_pie_chart(
            labels_list, values_list, f"{label}占比分布")
        chart_counter += 1
        html_parts.append(fig_to_div(pie_fig, f"c{chart_counter}"))

        html_parts.append("</div></div>")

        # 明细表
        detail_df = pd.DataFrame({
            label: labels_list,
            '项目数量': values_list,
        })
        detail_df['占比'] = (
            detail_df['项目数量'] / detail_df['项目数量'].sum() * 100
        ).round(2).astype(str) + '%'
        html_parts.append(detail_df.to_html(
            index=False, classes='', border=0))
        html_parts.append("</div>")

    # 交叉分析1
    html_parts.append("""
    <div class="section">
        <h2>交叉分析：业务条线类型 × 租赁物类型</h2>
""")
    cross_tab = pd.crosstab(df['业务条线类型'], df['租赁物类型'])
    # 使用 go.Heatmap 替代 px.imshow，避免 numpy array 序列化问题
    heatmap_fig = go.Figure()
    heatmap_fig.add_trace(go.Heatmap(
        z=cross_tab.values.tolist(),
        x=cross_tab.columns.tolist(),
        y=cross_tab.index.tolist(),
        colorscale='Blues',
        text=[[str(v) for v in row] for row in cross_tab.values.tolist()],
        texttemplate='%{text}',
        textfont=dict(size=10),
        colorbar=dict(title='项目数量'),
    ))
    heatmap_fig.update_layout(
        title=dict(text="<b>业务条线类型与租赁物类型交叉分布</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        font=dict(family="Microsoft YaHei", size=12),
        height=500, margin=dict(l=120, r=40, t=60, b=100),
    )
    chart_counter += 1
    html_parts.append(fig_to_div(heatmap_fig, f"c{chart_counter}"))
    html_parts.append(cross_tab.to_html(classes='', border=0))
    html_parts.append("</div>")

    # 交叉分析2
    html_parts.append("""
    <div class="section">
        <h2>交叉分析：部门名称 × 业务条线类型</h2>
""")
    cross_tab2 = pd.crosstab(df['部门名称'], df['业务条线类型'])
    heatmap_fig2 = go.Figure()
    heatmap_fig2.add_trace(go.Heatmap(
        z=cross_tab2.values.tolist(),
        x=cross_tab2.columns.tolist(),
        y=cross_tab2.index.tolist(),
        colorscale='Greens',
        text=[[str(v) for v in row] for row in cross_tab2.values.tolist()],
        texttemplate='%{text}',
        textfont=dict(size=10),
        colorbar=dict(title='项目数量'),
    ))
    heatmap_fig2.update_layout(
        title=dict(text="<b>部门名称与业务条线类型交叉分布</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        font=dict(family="Microsoft YaHei", size=12),
        height=500, margin=dict(l=150, r=40, t=60, b=100),
    )
    chart_counter += 1
    html_parts.append(fig_to_div(heatmap_fig2, f"c{chart_counter}"))
    html_parts.append(cross_tab2.to_html(classes='', border=0))
    html_parts.append("</div>")

    html_parts.append("""
</div>
<div class="footer">
    项目全维度分布分析报告 | 数据分析自动生成
</div>
</body></html>
""")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(html_parts))
    print(f"报告已生成: {output_path}")


if __name__ == '__main__':
    data_path = os.path.join(
        os.path.dirname(__file__), '项目主表1_cleaned.csv')
    output_path = os.path.join(
        os.path.dirname(__file__), '项目全维度分布分析.html')
    df = load_data(data_path)
    generate_distribution_html(df, output_path)
