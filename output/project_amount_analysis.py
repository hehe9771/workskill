"""
项目金额维度分析
按租赁物类型、项目资金类型、客户经理名称、部门名称、省份、
业务属性、业务类型、业务条线、业务条线类型等维度分析项目金额
输出HTML报告，金额统一使用万元
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
    """加载CSV数据"""
    df = pd.read_csv(filepath, encoding='utf-8')
    df['项目金额_万元'] = df['项目金额'] / 10000
    fill_cols = ['省份', '业务属性', '业务类型', '客户经理名称',
                 '部门名称', '租赁物类型', '项目资金类型',
                 '业务条线', '业务条线类型']
    for col in fill_cols:
        if col in df.columns:
            df[col] = df[col].fillna('未知')
    return df


def fmt_wan(val):
    """格式化万元显示"""
    if val >= 10000:
        return f"{val / 10000:.2f}亿元"
    return f"{val:.2f}万元"


def fig_to_div(fig, chart_id):
    """将plotly figure转为HTML div"""
    return fig.to_html(
        full_html=False,
        include_plotlyjs=False,
        div_id=chart_id,
        config={'responsive': True},
    )


def create_amount_bar(labels, values, title, x_label):
    """创建金额柱状图（降序排列）"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        marker_color=COLORS[:len(labels)],
        text=[fmt_wan(v) for v in values],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        xaxis_title=x_label, yaxis_title="金额(万元)",
        font=dict(family="Microsoft YaHei", size=12),
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showline=True,
                   linecolor='black', tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0',
                   showline=True, linecolor='black'),
        margin=dict(l=80, r=40, t=60, b=120),
        height=500,
    )
    return fig


def create_amount_pie(labels, values, title):
    """创建金额占比饼图"""
    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=COLORS[:len(labels)]),
        textinfo='label+percent',
        textfont=dict(size=11), hole=0.3,
        hovertemplate=(
            '%{label}<br>金额: %{value:,.2f}万元'
            '<br>占比: %{percent}<extra></extra>'
        ),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        font=dict(family="Microsoft YaHei", size=12),
        height=500, margin=dict(l=40, r=40, t=60, b=40),
    )
    return fig


def create_amount_h_bar(labels, values, title):
    """水平柱状图（最大值在上方）"""
    labels_r = list(reversed(labels))
    values_r = list(reversed(values))
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=values_r, y=labels_r,
        orientation='h', marker_color=PRIMARY,
        text=[fmt_wan(v) for v in values_r],
        textposition='outside',
        textfont=dict(size=10),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        xaxis_title="金额(万元)",
        font=dict(family="Microsoft YaHei", size=12),
        plot_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#E0E0E0',
                   showline=True, linecolor='black'),
        yaxis=dict(showgrid=False, showline=True, linecolor='black'),
        margin=dict(l=200, r=120, t=60, b=40),
        height=max(400, len(labels_r) * 30 + 100),
    )
    return fig


def create_avg_bar(labels, values, title, x_label):
    """创建平均金额柱状图"""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=labels, y=values,
        marker_color='#0066CC',
        text=[fmt_wan(v) for v in values],
        textposition='outside',
        textfont=dict(size=11),
    ))
    fig.update_layout(
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        xaxis_title=x_label, yaxis_title="平均金额(万元)",
        font=dict(family="Microsoft YaHei", size=12),
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showline=True,
                   linecolor='black', tickangle=-45),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0',
                   showline=True, linecolor='black'),
        margin=dict(l=80, r=40, t=60, b=120),
        height=500,
    )
    return fig


def build_amount_table(df, dimensions):
    """构建金额汇总表"""
    rows = []
    for dim in dimensions:
        col = dim['col']
        label = dim['label']
        grouped = df.groupby(col)['项目金额_万元']
        total = grouped.sum()
        count = grouped.count()
        avg = total / count
        top_cat = total.idxmax()
        rows.append({
            '分析维度': label,
            '分类数': len(total),
            '总金额(万元)': f"{total.sum():,.2f}",
            '金额最高类别': f"{top_cat}（{fmt_wan(total[top_cat])}）",
            '平均项目金额(万元)': f"{avg.mean():,.2f}",
        })
    return pd.DataFrame(rows)


def generate_amount_html(df, output_path):
    """生成项目金额维度分析HTML报告"""
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
    total_amount = df['项目金额_万元'].sum()
    avg_amount = df['项目金额_万元'].mean()
    max_amount = df['项目金额_万元'].max()
    min_amount = df['项目金额_万元'].min()
    median_amount = df['项目金额_万元'].median()
    summary_df = build_amount_table(df, dimensions)

    html_parts = []
    html_parts.append(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>项目金额维度分析报告</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', sans-serif;
            background: #f5f7fa; margin: 0; padding: 0;
        }}
        .header {{
            background: linear-gradient(135deg, #2E7D32, #00897B);
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
            font-size: 26px; font-weight: bold; color: #2E7D32;
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
            color: #2E7D32; border-bottom: 2px solid #2E7D32;
            padding-bottom: 10px; margin-top: 0;
        }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #E0E0E0; }}
        th {{ background: #2E7D32; color: white; font-weight: 600; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        tr:hover {{ background: #e8f5e9; }}
        .chart-row {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .chart-half {{ flex: 1; min-width: 500px; }}
        .footer {{ text-align: center; padding: 20px; color: #757575; font-size: 12px; }}
    </style>
</head>
<body>
<div class="header">
    <h1>项目金额维度分析报告</h1>
    <p>数据来源：项目主表 | 项目总数：{total_projects} 个 | 金额单位：万元</p>
</div>
<div class="container">

    <div class="kpi-row">
        <div class="kpi-card"><div class="value">{fmt_wan(total_amount)}</div><div class="label">项目总金额</div></div>
        <div class="kpi-card"><div class="value">{fmt_wan(avg_amount)}</div><div class="label">平均项目金额</div></div>
        <div class="kpi-card"><div class="value">{fmt_wan(median_amount)}</div><div class="label">中位数金额</div></div>
        <div class="kpi-card"><div class="value">{fmt_wan(max_amount)}</div><div class="label">最大项目金额</div></div>
        <div class="kpi-card"><div class="value">{fmt_wan(min_amount)}</div><div class="label">最小项目金额</div></div>
    </div>
""")

    chart_counter = 0

    # 金额分布直方图 + 金额区间
    html_parts.append('<div class="section"><h2>项目金额分布</h2>')
    # 手动分箱，避免 px.histogram 序列化问题
    amount_vals = df['项目金额_万元'].dropna().values.tolist()
    hist_fig = go.Figure()
    hist_fig.add_trace(go.Histogram(
        x=amount_vals,
        nbinsx=30,
        marker_color='#003366',
    ))
    hist_fig.update_layout(
        title=dict(text="<b>项目金额分布直方图</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        xaxis_title="项目金额(万元)", yaxis_title="项目数量",
        font=dict(family="Microsoft YaHei", size=12),
        plot_bgcolor='white',
        xaxis=dict(showgrid=False, showline=True, linecolor='black'),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0',
                   showline=True, linecolor='black'),
        height=400, margin=dict(l=60, r=40, t=60, b=60),
    )
    chart_counter += 1
    html_parts.append(fig_to_div(hist_fig, f"c{chart_counter}"))

    # 金额区间分析
    bins = [0, 500, 1000, 5000, 10000, 50000, 100000, float('inf')]
    labels_b = ['500万以下', '500-1000万', '1000-5000万',
                '0.5-1亿', '1-5亿', '5-10亿', '10亿以上']
    df['金额区间'] = pd.cut(
        df['项目金额_万元'], bins=bins, labels=labels_b, right=False)
    interval_counts = df['金额区间'].value_counts().reindex(labels_b).fillna(0)
    interval_amounts = df.groupby(
        '金额区间', observed=False)['项目金额_万元'].sum().reindex(labels_b).fillna(0)

    interval_fig = go.Figure()
    interval_fig.add_trace(go.Bar(
        x=labels_b, y=interval_counts.values.astype(int).tolist(),
        name='项目数量', marker_color='#003366',
        text=interval_counts.values.astype(int).tolist(),
        textposition='outside', yaxis='y',
    ))
    interval_fig.add_trace(go.Scatter(
        x=labels_b, y=interval_amounts.values.tolist(),
        name='金额合计(万元)', mode='lines+markers+text',
        line=dict(color='#C62828', width=3), marker=dict(size=8),
        text=[fmt_wan(v) for v in interval_amounts.values],
        textposition='top center', textfont=dict(size=10),
        yaxis='y2',
    ))
    interval_fig.update_layout(
        title=dict(text="<b>按金额区间分布的项目数量与金额</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        font=dict(family="Microsoft YaHei", size=12),
        plot_bgcolor='white',
        yaxis=dict(title="项目数量", showgrid=True, gridcolor='#E0E0E0'),
        yaxis2=dict(title="金额合计(万元)", overlaying='y', side='right'),
        legend=dict(x=0.02, y=0.98),
        height=500, margin=dict(l=80, r=80, t=60, b=80),
    )
    chart_counter += 1
    html_parts.append(fig_to_div(interval_fig, f"c{chart_counter}"))
    html_parts.append("</div>")

    # 汇总表
    html_parts.append(f"""
    <div class="section">
        <h2>各维度金额概览</h2>
        {summary_df.to_html(index=False, classes='', border=0)}
    </div>
""")

    # 逐维度图表
    for dim in dimensions:
        col = dim['col']
        label = dim['label']
        amount_sum = df.groupby(col)['项目金额_万元'].sum().sort_values(
            ascending=False)
        amount_count = df.groupby(col)['项目金额_万元'].count()

        sum_labels = amount_sum.index.astype(str).tolist()
        sum_values = amount_sum.values.tolist()

        # 计算平均金额（按总金额降序对齐）
        avg_series = (amount_sum / amount_count.reindex(
            amount_sum.index)).sort_values(ascending=False)
        avg_labels = avg_series.index.astype(str).tolist()
        avg_values = avg_series.values.tolist()

        html_parts.append(f"""
    <div class="section">
        <h2>{label}金额分析</h2>
        <div class="chart-row"><div class="chart-half">
""")
        # 总金额柱状图
        if len(amount_sum) <= 15:
            bar_fig = create_amount_bar(
                sum_labels, sum_values,
                f"按{label}的项目总金额", label)
        else:
            bar_fig = create_amount_h_bar(
                sum_labels[:20], sum_values[:20],
                f"按{label}的项目总金额（Top20）")

        chart_counter += 1
        html_parts.append(fig_to_div(bar_fig, f"c{chart_counter}"))
        html_parts.append("</div><div class='chart-half'>")

        # 金额占比饼图
        pie_fig = create_amount_pie(
            sum_labels, sum_values, f"{label}金额占比")
        chart_counter += 1
        html_parts.append(fig_to_div(pie_fig, f"c{chart_counter}"))
        html_parts.append("</div></div>")

        # 平均金额图
        if len(avg_series) <= 15:
            avg_fig = create_avg_bar(
                avg_labels, avg_values,
                f"按{label}的平均项目金额", label)
        else:
            avg_fig = create_amount_h_bar(
                avg_labels[:20], avg_values[:20],
                f"按{label}的平均项目金额（Top20）")

        chart_counter += 1
        html_parts.append(fig_to_div(avg_fig, f"c{chart_counter}"))

        # 明细表
        count_aligned = amount_count.reindex(amount_sum.index).values.tolist()
        avg_aligned = (amount_sum / amount_count.reindex(
            amount_sum.index)).values.tolist()
        detail_df = pd.DataFrame({
            label: sum_labels,
            '项目数量': count_aligned,
            '总金额(万元)': [f"{v:,.2f}" for v in sum_values],
            '平均金额(万元)': [f"{v:,.2f}" for v in avg_aligned],
            '金额占比': [
                f"{v / amount_sum.sum() * 100:.2f}%"
                for v in sum_values
            ],
        })
        html_parts.append(detail_df.to_html(
            index=False, classes='', border=0))
        html_parts.append("</div>")

    # 交叉分析
    html_parts.append("""
    <div class="section">
        <h2>交叉分析：部门名称 × 业务条线类型（金额维度）</h2>
""")
    cross_amount = df.pivot_table(
        values='项目金额_万元', index='部门名称',
        columns='业务条线类型', aggfunc='sum', fill_value=0,
    )
    # 使用 go.Heatmap 替代 px.imshow，避免 numpy array 序列化问题
    heatmap_fig = go.Figure()
    heatmap_fig.add_trace(go.Heatmap(
        z=cross_amount.values.tolist(),
        x=cross_amount.columns.tolist(),
        y=cross_amount.index.tolist(),
        colorscale='YlOrRd',
        text=[[f"{v:.0f}" for v in row] for row in cross_amount.values.tolist()],
        texttemplate='%{text}',
        textfont=dict(size=10),
        colorbar=dict(title='金额(万元)'),
    ))
    heatmap_fig.update_layout(
        title=dict(text="<b>部门 × 业务条线类型金额热力图(万元)</b>",
                   font=dict(size=16, family="Microsoft YaHei")),
        font=dict(family="Microsoft YaHei", size=12),
        height=500, margin=dict(l=150, r=40, t=60, b=100),
    )
    chart_counter += 1
    html_parts.append(fig_to_div(heatmap_fig, f"c{chart_counter}"))
    cross_display = cross_amount.applymap(lambda x: f"{x:,.2f}")
    html_parts.append(cross_display.to_html(classes='', border=0))
    html_parts.append("</div>")

    # Top10
    html_parts.append('<div class="section"><h2>Top10项目金额排名</h2>')
    top10 = df.nlargest(10, '项目金额_万元')[
        ['项目名称', '项目金额_万元', '业务条线类型', '部门名称',
         '客户经理名称', '省份', '租赁物类型']
    ].copy()
    top10['项目金额_万元'] = top10['项目金额_万元'].apply(
        lambda x: f"{x:,.2f}")
    top10.columns = ['项目名称', '金额(万元)', '业务条线类型',
                     '部门名称', '客户经理名称', '省份', '租赁物类型']
    html_parts.append(top10.to_html(index=False, classes='', border=0))
    html_parts.append("</div>")

    html_parts.append("""
</div>
<div class="footer">
    项目金额维度分析报告 | 金额单位：万元 | 数据分析自动生成
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
        os.path.dirname(__file__), '项目金额维度分析.html')
    df = load_data(data_path)
    generate_amount_html(df, output_path)
