# -*- coding: utf-8 -*-
"""
储能/发电业务分析看板 - Streamlit Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="储能/发电业务分析看板",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = '#003366'
SECONDARY = '#0066CC'
PALETTE = ['#003366', '#0066CC', '#2E7D32', '#0097A7', '#F57C00',
           '#7B1FA2', '#C62828', '#757575', '#FFB300', '#4CAF50']

st.markdown("""
<style>
    .kpi-card {
        background: white;
        border-left: 4px solid #003366;
        padding: 18px 24px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        text-align: center;
    }
    .kpi-label { font-size: 13px; color: #757575; letter-spacing: 0.5px; }
    .kpi-value { font-size: 28px; font-weight: bold; color: #003366; margin: 4px 0; }
    .kpi-sub { font-size: 12px; color: #9E9E9E; }
    .section-header {
        border-bottom: 2px solid #003366;
        padding-bottom: 8px;
        margin-bottom: 16px;
        margin-top: 8px;
    }
    .stApp { background: #F8F9FA; }
</style>
""", unsafe_allow_html=True)


def make_exec_layout(fig, title_text):
    fig.update_layout(
        title=dict(text="<b>{}</b>".format(title_text),
                    font=dict(size=14, family="Arial", color=PRIMARY), x=0),
        font=dict(family="Arial", size=11),
        plot_bgcolor='white', paper_bgcolor='white',
        xaxis=dict(showgrid=False, showline=True, linecolor='black', linewidth=0.5),
        yaxis=dict(showgrid=True, gridcolor='#E0E0E0', showline=True, linecolor='black', linewidth=0.5),
        margin=dict(l=60, r=30, t=40, b=40),
    )
    return fig


def show_kpi(col, label, value, sub):
    col.markdown(
        '<div class="kpi-card">'
        '<div class="kpi-label">{}</div>'
        '<div class="kpi-value">{}</div>'
        '<div class="kpi-sub">{}</div>'
        '</div>'.format(label, value, sub),
        unsafe_allow_html=True
    )


@st.cache_data
def load_data():
    parquet_path = Path(__file__).parent / "output" / "processed_data.parquet"
    if not parquet_path.exists():
        st.error("未找到处理数据，请先运行 process_data.py")
        st.stop()
    return pd.read_parquet(parquet_path)


df = load_data()

# ===================== 侧边栏筛选 =====================
st.sidebar.header("筛选条件")

all_bl = sorted(df["业务条线"].unique())
selected_bl = st.sidebar.multiselect("业务条线", all_bl, default=all_bl)

all_lm = sorted(df["租赁模式"].unique())
selected_lm = st.sidebar.multiselect("租赁模式", all_lm, default=all_lm)

all_fp = sorted(df["资金用途类型"].unique())
selected_fp = st.sidebar.multiselect("资金用途类型", all_fp, default=all_fp)

all_li = sorted(df["租赁物类型"].unique())
selected_li = st.sidebar.multiselect("租赁物类型", all_li, default=all_li)

valid_years = sorted(df["年份"].dropna().unique())
yr_min = int(min(valid_years))
yr_max = int(max(valid_years))
selected_yr = st.sidebar.slider("年份范围", yr_min, yr_max, (yr_min, yr_max))

all_prov = sorted(df["省份"].unique())
selected_prov = st.sidebar.multiselect("省份", all_prov, default=all_prov)

# 应用筛选
mask = (
    df["业务条线"].isin(selected_bl)
    & df["租赁模式"].isin(selected_lm)
    & df["资金用途类型"].isin(selected_fp)
    & df["租赁物类型"].isin(selected_li)
    & df["年份"].between(selected_yr[0], selected_yr[1])
    & df["省份"].isin(selected_prov)
)
df_f = df[mask].copy()

# ===================== 空数据保护 =====================
if len(df_f) == 0:
    st.warning(
        "当前筛选条件下没有匹配数据，请调整筛选条件。\n\n"
        "**当前筛选**：业务条线={} | 租赁模式={} | 资金用途={} | 租赁物={} | 年份={}-{} | 省份={}"
        .format(
            ", ".join(selected_bl) if selected_bl else "无",
            ", ".join(selected_lm) if selected_lm else "无",
            ", ".join(selected_fp) if selected_fp else "无",
            ", ".join(selected_li) if selected_li else "无",
            selected_yr[0], selected_yr[1],
            ", ".join(selected_prov) if selected_prov else "无",
        )
    )
    # 显示原始明细表（全部数据）
    st.info("以下为全部数据供参考：")
    display_cols = [
        "项目编号", "项目名称", "业务条线", "业务类型", "租赁模式",
        "资金用途类型", "租赁物类型", "省份", "部门名称",
        "客户经理名称", "客户名称", "项目金额", "年份",
    ]
    st.dataframe(df[display_cols], use_container_width=True, height=600)
    st.stop()

# ===================== KPI 卡片 =====================
st.markdown('<div class="section-header"><h2 style="color:#003366;font-size:22px;">核心指标概览</h2></div>', unsafe_allow_html=True)

total_projects = len(df)
total_amount = df["项目金额"].sum()
avg_amount = df["项目金额"].mean()
filtered_count = len(df_f)
filtered_amount = df_f["项目金额"].sum()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
show_kpi(kpi1, "项目总数", "{:,} 个".format(total_projects), "储能/发电业务全部项目")
show_kpi(kpi2, "总金额", "¥{:.0f} 万".format(total_amount / 10000),
         "平均 ¥{:.0f} 万".format(avg_amount / 10000))
show_kpi(kpi3, "筛选金额", "¥{:.0f} 万".format(filtered_amount / 10000),
         "筛选项目 {} 个".format(filtered_count))
show_kpi(kpi4, "当前筛选占比", "{:.1%}".format(filtered_count / total_projects),
         "金额占比 {:.1%}".format(filtered_amount / total_amount if total_amount > 0 else 0))

# ===================== 业务维度分析 =====================
st.markdown('<div class="section-header"><h2 style="color:#003366;font-size:22px;">业务维度分析</h2></div>', unsafe_allow_html=True)

# 业务条线
grp_bl = df_f.groupby("业务条线")["项目金额"].sum().sort_values()
fig_bl = px.bar(
    x=grp_bl.values / 10000, y=grp_bl.index, orientation='h',
    color=grp_bl.values, color_continuous_scale=[PRIMARY, SECONDARY],
)
fig_bl = make_exec_layout(fig_bl, "各业务条线项目总金额 (万元)")
fig_bl.update_xaxes(title="金额 (万元)")
fig_bl.update_layout(showlegend=False, coloraxis_showscale=False)

# 业务类型
grp_bt = df_f.groupby("业务类型")["项目金额"].sum()
fig_bt = px.pie(
    values=grp_bt.values, names=grp_bt.index, hole=0.5,
    color_discrete_sequence=PALETTE,
)
fig_bt.update_layout(
    title=dict(text="<b>业务类型资金构成</b>", font=dict(size=14, family="Arial", color=PRIMARY), x=0.5),
    font=dict(family="Arial", size=11),
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=20, r=20, t=40, b=20),
)

# 资金用途类型 - 双轴图
grp_fp = df_f.groupby("资金用途类型").agg(
    count=("项目ID", "count"), amount=("项目金额", "sum")
).reset_index()
fig_fp = go.Figure()
fig_fp.add_trace(go.Bar(
    x=grp_fp["资金用途类型"], y=grp_fp["count"],
    name="项目数量", marker_color=PRIMARY, yaxis="y",
))
fig_fp.add_trace(go.Bar(
    x=grp_fp["资金用途类型"], y=grp_fp["amount"] / 10000,
    name="金额(万元)", marker_color=SECONDARY, yaxis="y2",
))
fig_fp.update_layout(
    title=dict(text="<b>资金用途类型: 项目数与金额对比</b>",
               font=dict(size=14, family="Arial", color=PRIMARY), x=0),
    font=dict(family="Arial", size=11),
    plot_bgcolor='white', paper_bgcolor='white',
    yaxis=dict(title="项目数量", showgrid=True, gridcolor='#E0E0E0'),
    yaxis2=dict(title="金额(万元)", overlaying='y', side='right', showgrid=False),
    legend=dict(orientation='h', y=1.12, x=0),
    margin=dict(l=60, r=60, t=40, b=40),
    bargap=0.15,
)

# 租赁模式
grp_mode = df_f.groupby("租赁模式")["项目金额"].sum()
fig_mode = px.pie(
    values=grp_mode.values, names=grp_mode.index,
    color_discrete_sequence=PALETTE[:3],
)
fig_mode.update_layout(
    title=dict(text="<b>租赁模式资金占比</b>", font=dict(size=14, family="Arial", color=PRIMARY), x=0.5),
    font=dict(family="Arial", size=11),
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=20, r=20, t=40, b=20),
)

col_a, col_b = st.columns(2)
with col_a:
    st.plotly_chart(fig_bl, use_container_width=True)
with col_b:
    st.plotly_chart(fig_bt, use_container_width=True)

col_c, col_d = st.columns(2)
with col_c:
    st.plotly_chart(fig_fp, use_container_width=True)
with col_d:
    st.plotly_chart(fig_mode, use_container_width=True)

# ===================== 租赁物维度分析 =====================
st.markdown('<div class="section-header"><h2 style="color:#003366;font-size:22px;">租赁物维度分析</h2></div>', unsafe_allow_html=True)

grp_li_bl = df_f.groupby(["租赁物类型", "业务条线"])["项目金额"].sum().unstack(fill_value=0)
fig_li = px.bar(
    grp_li_bl.T, barmode='stack',
    color_discrete_sequence=PALETTE,
)
fig_li = make_exec_layout(fig_li, "各业务条线按租赁物类型金额构成")
fig_li.update_yaxes(title="金额 (万元)")

grp_li = df_f.groupby("租赁物类型")["项目金额"].sum()
fig_li_pie = px.pie(
    values=grp_li.values, names=grp_li.index, hole=0.5,
    color_discrete_sequence=PALETTE,
)
fig_li_pie.update_layout(
    title=dict(text="<b>租赁物类型资金占比</b>", font=dict(size=14, family="Arial", color=PRIMARY), x=0.5),
    font=dict(family="Arial", size=11),
    plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=20, r=20, t=40, b=20),
)

col_e, col_f = st.columns(2)
with col_e:
    st.plotly_chart(fig_li, use_container_width=True)
with col_f:
    st.plotly_chart(fig_li_pie, use_container_width=True)

# ===================== 组织与地域分析 =====================
st.markdown('<div class="section-header"><h2 style="color:#003366;font-size:22px;">组织与地域分析</h2></div>', unsafe_allow_html=True)

grp_prov = df_f.groupby("省份")["项目金额"].sum().sort_values(ascending=False).head(15)
fig_prov = px.bar(
    x=grp_prov.values / 10000, y=grp_prov.index, orientation='h',
    color=grp_prov.values, color_continuous_scale=[PRIMARY, SECONDARY],
)
fig_prov = make_exec_layout(fig_prov, "省份项目金额 TOP15 (万元)")
fig_prov.update_layout(showlegend=False, coloraxis_showscale=False)

grp_dept = df_f.groupby("部门名称")["项目金额"].sum().sort_values(ascending=False)
fig_dept = px.bar(
    x=grp_dept.index, y=grp_dept.values / 10000,
    color=grp_dept.values, color_continuous_scale=[PRIMARY, SECONDARY],
)
fig_dept = make_exec_layout(fig_dept, "部门项目金额分布 (万元)")
fig_dept.update_xaxes(title="")
fig_dept.update_layout(showlegend=False, coloraxis_showscale=False, xaxis_tickangle=-30)

grp_mgr = df_f.groupby("客户经理名称").agg(
    count=("项目ID", "count"), amount=("项目金额", "sum")
).sort_values("amount", ascending=False).head(10)
fig_mgr = px.bar(
    x=grp_mgr["amount"] / 10000, y=grp_mgr.index, orientation='h',
    color=grp_mgr["amount"] / 10000, color_continuous_scale=[PRIMARY, SECONDARY],
)
fig_mgr = make_exec_layout(fig_mgr, "客户经理业绩 TOP10 (万元)")
fig_mgr.update_layout(showlegend=False, coloraxis_showscale=False)

grp_cust = df_f.groupby("客户名称").agg(
    count=("项目ID", "count"), amount=("项目金额", "sum")
).sort_values("amount", ascending=False).head(10)
fig_cust = px.bar(
    x=grp_cust["amount"] / 10000, y=grp_cust.index, orientation='h',
    color=grp_cust["amount"] / 10000, color_continuous_scale=[PRIMARY, SECONDARY],
)
fig_cust = make_exec_layout(fig_cust, "客户集中度 TOP10 (万元)")
fig_cust.update_layout(showlegend=False, coloraxis_showscale=False)

col_g, col_h = st.columns(2)
with col_g:
    st.plotly_chart(fig_prov, use_container_width=True)
with col_h:
    st.plotly_chart(fig_dept, use_container_width=True)

col_i, col_j = st.columns(2)
with col_i:
    st.plotly_chart(fig_mgr, use_container_width=True)
with col_j:
    st.plotly_chart(fig_cust, use_container_width=True)

# ===================== 时间与金额分析 =====================
st.markdown('<div class="section-header"><h2 style="color:#003366;font-size:22px;">时间与金额分析</h2></div>', unsafe_allow_html=True)

grp_yr = df_f.groupby("年份").agg(
    count=("项目ID", "count"), amount=("项目金额", "sum")
).reset_index()
fig_yr = go.Figure()
fig_yr.add_trace(go.Bar(
    x=grp_yr["年份"], y=grp_yr["count"],
    name="项目数量", marker_color=PRIMARY, yaxis="y",
))
fig_yr.add_trace(go.Scatter(
    x=grp_yr["年份"], y=grp_yr["amount"] / 10000,
    name="金额(万元)", mode='lines+markers',
    line=dict(color=SECONDARY, width=3), marker=dict(size=8),
    yaxis="y2",
))
fig_yr.update_layout(
    title=dict(text="<b>项目数量与金额年度趋势</b>", font=dict(size=14, family="Arial", color=PRIMARY), x=0),
    font=dict(family="Arial", size=11),
    plot_bgcolor='white', paper_bgcolor='white',
    yaxis=dict(title="项目数量", showgrid=True, gridcolor='#E0E0E0'),
    yaxis2=dict(title="金额(万元)", overlaying='y', side='right', showgrid=False),
    legend=dict(orientation='h', y=1.12, x=0),
    margin=dict(l=60, r=60, t=40, b=40),
)

bucket_order = ["50万以下", "50-200万", "200-500万", "500万-1000万", "1000万-5000万", "5000万以上", "未知"]
grp_bucket = df_f["金额区间"].value_counts().reindex(bucket_order).dropna()
fig_bucket = go.Figure(go.Waterfall(
    orientation="v",
    measure=["relative"] * len(grp_bucket),
    x=grp_bucket.index,
    y=grp_bucket.values,
    text=grp_bucket.values.astype(str) + "个项目",
    textposition="outside",
    connector=dict(line=dict(color="rgb(63, 63, 63)")),
    increasing=dict(marker=dict(color=PRIMARY)),
))
fig_bucket.update_layout(
    title=dict(text="<b>项目金额区间分布</b>", font=dict(size=14, family="Arial", color=PRIMARY), x=0),
    font=dict(family="Arial", size=11),
    plot_bgcolor='white', paper_bgcolor='white',
    showlegend=False,
    margin=dict(l=60, r=30, t=40, b=40),
    yaxis=dict(title="项目数量", showgrid=True, gridcolor='#E0E0E0'),
)

col_k, col_l = st.columns(2)
with col_k:
    st.plotly_chart(fig_yr, use_container_width=True)
with col_l:
    st.plotly_chart(fig_bucket, use_container_width=True)

# ===================== 明细数据表 =====================
st.markdown('<div class="section-header"><h2 style="color:#003366;font-size:22px;">明细数据</h2></div>', unsafe_allow_html=True)

display_cols = [
    "项目编号", "项目名称", "业务条线", "业务类型", "租赁模式",
    "资金用途类型", "租赁物类型", "省份", "部门名称",
    "客户经理名称", "客户名称", "项目金额", "年份",
]

df_display = df_f[display_cols].sort_values("项目金额", ascending=False).reset_index(drop=True)
st.dataframe(df_display, use_container_width=True, height=400)

csv_data = df_display.to_csv(index=False, encoding='utf-8-sig')
st.download_button(
    label="下载当前筛选数据 (CSV)",
    data=csv_data,
    file_name="energy_business_filtered.csv",
    mime="text/csv",
)
