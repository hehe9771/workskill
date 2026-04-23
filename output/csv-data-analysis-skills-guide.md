# CSV 数据分析技能 - 最佳实践指南

## 安装信息

三个技能已安装到本项目 `.agents/skills/` 目录下：

| 技能 | 安装路径 | 定位 |
|------|----------|------|
| **csv-processor** | `.agents/skills/csv-processor/` | CSV 文件解析、转换、清洗、统计 |
| **pandas-data-analysis** | `.agents/skills/pandas-data-analysis/` | Pandas 全流程数据分析与可视化 |
| **data-analysis** | `.agents/skills/data-analysis/` | 高管级数据分析、SaaS 指标、投资者报告 |

### 依赖安装

```bash
# csv-processor + pandas-data-analysis 基础依赖
pip install pandas numpy openpyxl chardet

# pandas-data-analysis 可视化依赖
pip install matplotlib seaborn

# data-analysis 完整依赖（高管级报告）
pip install plotly altair streamlit polars duckdb pdfplumber python-pptx
```

---

## 技能一览 - 适用场景选择

```
你有一个 CSV 文件，想要做什么？
│
├── 快速查看结构、清洗、合并 → csv-processor
│
├── 深入分析、分组聚合、画图 → pandas-data-analysis
│
└── 给老板/投资人看的报告和仪表盘 → data-analysis
```

---

## 一、csv-processor（CSV 处理器）

### 核心能力

- 自动检测分隔符（逗号、Tab、分号、管道符）
- 自动处理编码（UTF-8、Latin-1、Windows-1252）
- 数据清洗（去重、缺失值、空格、格式标准化）
- 基础统计（sum、avg、min、max、count）
- 合并、拆分、透视

### 场景 1：快速查看 CSV 结构和质量

**提示词：**
```
帮我分析 data/sales.csv 的数据结构和质量，包括：
1. 列名、数据类型、行数
2. 每列的缺失值比例
3. 是否有重复行
4. 数值列的基础统计
```

**命令链：**
```python
import pandas as pd

df = pd.read_csv('data/sales.csv')
print(f"形状: {df.shape}")
print(f"\n数据类型:\n{df.dtypes}")
print(f"\n缺失值:\n{(df.isnull().sum() / len(df) * 100).round(1)}%")
print(f"\n重复行: {df.duplicated().sum()}")
print(f"\n数值统计:\n{df.describe()}")
```

### 场景 2：清洗并合并多个 CSV

**提示词：**
```
把 data/ 目录下所有 CSV 文件合并为一个文件，执行以下清洗：
1. 去除重复行
2. 删除 email 列为空的行
3. 将所有文本列去除首尾空格
4. 将日期列统一为 YYYY-MM-DD 格式
输出到 output/merged_clean.csv
```

**命令链：**
```python
import pandas as pd
from pathlib import Path

# 批量读取
files = list(Path('data').glob('*.csv'))
dfs = [pd.read_csv(f) for f in files]
df = pd.concat(dfs, ignore_index=True)

# 清洗
df = df.drop_duplicates()
df = df.dropna(subset=['email'])
for col in df.select_dtypes(include='object').columns:
    df[col] = df[col].str.strip()
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

df.to_csv('output/merged_clean.csv', index=False)
print(f"合并完成: {len(df)} 行")
```

### 场景 3：编码问题自动检测修复

**提示词：**
```
data/legacy_export.csv 打开是乱码，帮我：
1. 自动检测文件编码
2. 用正确的编码读取
3. 转存为 UTF-8 编码
```

**命令链：**
```python
import pandas as pd
import chardet

with open('data/legacy_export.csv', 'rb') as f:
    result = chardet.detect(f.read(10000))
print(f"检测到编码: {result['encoding']} (置信度: {result['confidence']:.0%})")

df = pd.read_csv('data/legacy_export.csv', encoding=result['encoding'])
df.to_csv('output/legacy_utf8.csv', encoding='utf-8', index=False)
```

### 场景 4：大文件分块处理

**提示词：**
```
data/huge_log.csv 有 500 万行，内存不够。帮我：
1. 分块读取（每次 10000 行）
2. 只保留 status='error' 的行
3. 只保留 timestamp, module, message 三列
4. 输出到 output/errors_only.csv
```

**命令链：**
```python
import pandas as pd

chunks = []
for chunk in pd.read_csv('data/huge_log.csv', chunksize=10000):
    filtered = chunk[chunk['status'] == 'error'][['timestamp', 'module', 'message']]
    chunks.append(filtered)

result = pd.concat(chunks, ignore_index=True)
result.to_csv('output/errors_only.csv', index=False)
print(f"错误记录: {len(result)} 行")
```

---

## 二、pandas-data-analysis（Pandas 数据分析）

### 核心能力

- DataFrame 高级操作（索引、切片、布尔筛选）
- 数据清洗与转换（缺失值、去重、类型转换、自定义函数）
- 分组聚合（GroupBy、透视表、窗口函数）
- 可视化（Matplotlib + Seaborn）

### 场景 1：销售数据探索性分析（EDA）

**提示词：**
```
对 data/sales_2024.csv 做完整的探索性分析：
1. 数据概览（行列数、类型、缺失值）
2. 按月汇总销售额趋势
3. 按产品类别的销售占比
4. 销售额的分布和异常值检测
5. 各维度之间的相关性
生成分析报告并配图，保存到 output/
```

**命令链：**
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data/sales_2024.csv', parse_dates=['order_date'])

# 1. 概览
print(df.info())
print(df.describe(include='all'))

# 2. 月度趋势
monthly = df.groupby(df['order_date'].dt.to_period('M'))['amount'].sum()
monthly.plot(kind='line', figsize=(10, 5), title='月度销售趋势')
plt.savefig('output/monthly_trend.png', dpi=150, bbox_inches='tight')
plt.close()

# 3. 类别占比
category_sales = df.groupby('category')['amount'].sum().sort_values(ascending=False)
category_sales.plot(kind='bar', figsize=(10, 5), title='分类别销售额')
plt.savefig('output/category_sales.png', dpi=150, bbox_inches='tight')
plt.close()

# 4. 分布 + 异常值
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
df['amount'].hist(bins=50, ax=axes[0])
axes[0].set_title('销售额分布')
df.boxplot(column='amount', by='category', ax=axes[1])
axes[1].set_title('各类别销售额箱线图')
plt.savefig('output/distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# 5. 相关性
corr = df.select_dtypes(include='number').corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', center=0)
plt.savefig('output/correlation.png', dpi=150, bbox_inches='tight')
plt.close()
```

### 场景 2：RFM 客户分群

**提示词：**
```
用 data/transactions.csv 做 RFM 客户分析：
- R(Recency): 距最近一次购买的天数
- F(Frequency): 购买次数
- M(Monetary): 总消费金额
按 R/F/M 各分 5 档，标记客户等级（高价值/流失风险/新客户等）
输出分群结果到 output/rfm_segments.csv
```

**命令链：**
```python
import pandas as pd
from datetime import datetime

df = pd.read_csv('data/transactions.csv', parse_dates=['purchase_date'])
now = df['purchase_date'].max() + pd.Timedelta(days=1)

rfm = df.groupby('customer_id').agg({
    'purchase_date': lambda x: (now - x.max()).days,
    'order_id': 'nunique',
    'amount': 'sum'
}).rename(columns={
    'purchase_date': 'recency',
    'order_id': 'frequency',
    'amount': 'monetary'
})

# 分档打分（1-5）
rfm['R'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1])
rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
rfm['M'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5])
rfm['RFM_Score'] = rfm['R'].astype(str) + rfm['F'].astype(str) + rfm['M'].astype(str)

# 客户分群
def segment(row):
    if int(row['R']) >= 4 and int(row['F']) >= 4:
        return '高价值客户'
    elif int(row['R']) >= 4 and int(row['F']) <= 2:
        return '新客户'
    elif int(row['R']) <= 2 and int(row['F']) >= 3:
        return '流失风险'
    elif int(row['R']) <= 2 and int(row['F']) <= 2:
        return '已流失'
    else:
        return '一般客户'

rfm['segment'] = rfm.apply(segment, axis=1)
rfm.to_csv('output/rfm_segments.csv')
print(rfm['segment'].value_counts())
```

### 场景 3：时间序列移动平均 + 异常检测

**提示词：**
```
分析 data/daily_metrics.csv 的时间序列：
1. 计算 7 日和 30 日移动平均
2. 用 IQR 方法检测异常值
3. 标注异常点并画趋势图
```

**命令链：**
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/daily_metrics.csv', parse_dates=['date'])
df = df.sort_values('date')

# 移动平均
df['ma_7'] = df['value'].rolling(7, min_periods=1).mean()
df['ma_30'] = df['value'].rolling(30, min_periods=1).mean()

# IQR 异常检测
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1
df['is_anomaly'] = (df['value'] < Q1 - 1.5*IQR) | (df['value'] > Q3 + 1.5*IQR)

# 画图
fig, ax = plt.subplots(figsize=(14, 6))
ax.plot(df['date'], df['value'], alpha=0.4, label='原始值')
ax.plot(df['date'], df['ma_7'], label='7日均线', linewidth=2)
ax.plot(df['date'], df['ma_30'], label='30日均线', linewidth=2)
anomalies = df[df['is_anomaly']]
ax.scatter(anomalies['date'], anomalies['value'], color='red', s=50, label='异常点', zorder=5)
ax.legend()
ax.set_title('时间序列分析 - 移动平均与异常检测')
plt.savefig('output/timeseries_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

print(f"检测到 {len(anomalies)} 个异常点")
```

---

## 三、data-analysis（高管级数据分析）

### 核心能力

- 万能数据加载（CSV/Excel/JSON/Parquet/PDF/PPTX）
- SaaS 核心指标计算（MRR/ARR/LTV/CAC/Churn/NRR）
- 队列留存分析（Cohort Retention）
- McKinsey 风格可视化（Plotly 交互图表）
- Streamlit 仪表盘
- 投资者汇报用图表

### 场景 1：SaaS 指标一键计算

**提示词：**
```
用 data/subscriptions.csv 计算以下 SaaS 核心指标：
- MRR 及月环比增长率
- ARR
- 客户流失率
- LTV、CAC、LTV:CAC 比率
- CAC 回收期
- 净收入留存率 (NRR)
用 McKinsey 风格图表展示结果
```

**命令链：**
```python
import pandas as pd
import plotly.graph_objects as go

df = pd.read_csv('data/subscriptions.csv', parse_dates=['date'])

# MRR 计算
mrr_by_month = df[df['status'] == 'active'].groupby(
    df['date'].dt.to_period('M')
)['mrr'].sum()

current_mrr = mrr_by_month.iloc[-1]
arr = current_mrr * 12
mrr_growth = mrr_by_month.pct_change().iloc[-1]

# 流失率
churned = df[df['status'] == 'churned']['mrr'].sum()
total = df['mrr'].sum()
churn_rate = churned / total

# LTV / CAC
arpu = df.groupby('customer_id')['mrr'].mean().mean()
avg_lifespan = 1 / churn_rate if churn_rate > 0 else 36
ltv = arpu * avg_lifespan

sales_marketing = df['sales_cost'].sum() + df['marketing_cost'].sum()
new_customers = df[df['is_new']]['customer_id'].nunique()
cac = sales_marketing / new_customers if new_customers > 0 else 0

# 输出
print(f"MRR: ${current_mrr:,.0f}")
print(f"ARR: ${arr:,.0f}")
print(f"MRR 月增长: {mrr_growth:.1%}")
print(f"流失率: {churn_rate:.1%}")
print(f"LTV: ${ltv:,.0f}")
print(f"CAC: ${cac:,.0f}")
print(f"LTV:CAC = {ltv/cac:.1f}x")

# McKinsey 风格 MRR 趋势图
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=[str(p) for p in mrr_by_month.index],
    y=mrr_by_month.values,
    mode='lines+markers',
    line=dict(color='#003366', width=3),
    marker=dict(size=8)
))
fig.update_layout(
    title=dict(
        text=f"<b>MRR 月环比增长 {mrr_growth:.1%}，超额完成目标</b>",
        font=dict(size=18, family="Georgia")
    ),
    plot_bgcolor='white',
    yaxis=dict(tickformat="$,.0f", gridcolor='#E0E0E0'),
    xaxis=dict(showgrid=False)
)
fig.write_html('output/mrr_trend.html')
fig.write_image('output/mrr_trend.png', scale=2)
```

### 场景 2：队列留存分析热力图

**提示词：**
```
用 data/user_activity.csv 做队列留存分析：
1. 按注册月份分队列
2. 计算每个队列在注册后 0-12 个月的留存率
3. 生成热力图，用蓝色色系
4. 输出到 output/cohort_heatmap.html
```

**命令链：**
```python
import pandas as pd
import plotly.express as px

df = pd.read_csv('data/user_activity.csv', parse_dates=['signup_date', 'activity_date'])

# 队列分配
df['cohort'] = df.groupby('customer_id')['signup_date'].transform('min').dt.to_period('M')
df['activity_month'] = df['activity_date'].dt.to_period('M')
df['cohort_age'] = (df['activity_month'] - df['cohort']).apply(lambda x: x.n)

# 留存矩阵
cohort_data = df.groupby(['cohort', 'cohort_age'])['customer_id'].nunique().reset_index()
matrix = cohort_data.pivot(index='cohort', columns='cohort_age', values='customer_id')
cohort_sizes = matrix.iloc[:, 0]
retention = matrix.divide(cohort_sizes, axis=0) * 100

# 热力图
fig = px.imshow(
    retention.values,
    labels=dict(x="注册后月数", y="队列", color="留存率 %"),
    x=[str(c) for c in retention.columns],
    y=[str(c) for c in retention.index],
    color_continuous_scale='Blues',
    aspect='auto'
)

# 添加文字标注
for i, row in enumerate(retention.values):
    for j, val in enumerate(row):
        if not pd.isna(val):
            fig.add_annotation(
                x=j, y=i,
                text=f"{val:.0f}%",
                showarrow=False,
                font=dict(color='white' if val > 50 else 'black', size=10)
            )

fig.update_layout(
    title=dict(
        text="<b>90天留存率从72%提升至85%</b>",
        font=dict(size=18, family="Georgia")
    )
)
fig.write_html('output/cohort_heatmap.html')
```

### 场景 3：Streamlit 仪表盘快速搭建

**提示词：**
```
用 data/business_metrics.csv 搭建一个 Streamlit 高管仪表盘：
- 顶部 4 个 KPI 卡片（MRR/ARR/LTV:CAC/流失率）
- 中间 MRR 趋势折线图
- 底部队列留存热力图
- 左侧边栏支持日期范围筛选
用 McKinsey 蓝色主题
```

**命令链：**
```bash
# 1. 创建项目结构
mkdir -p dashboard/.streamlit dashboard/components dashboard/data

# 2. 创建配置
cat > dashboard/.streamlit/config.toml << 'EOF'
[theme]
primaryColor = "#003366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F5F5F5"
textColor = "#333333"
font = "sans serif"

[server]
maxUploadSize = 200

[browser]
gatherUsageStats = false
EOF

# 3. 创建依赖文件
cat > dashboard/requirements.txt << 'EOF'
streamlit>=1.28.0
pandas>=2.0.0
plotly>=5.18.0
openpyxl>=3.1.0
EOF

# 4. 安装依赖
pip install -r dashboard/requirements.txt

# 5. 启动（创建 app.py 后）
streamlit run dashboard/app.py
```

### 场景 4：多格式数据源合并分析

**提示词：**
```
我有三个不同格式的数据源：
- data/quarterly_report.pdf （PDF 表格）
- data/sales_detail.xlsx （Excel 多 Sheet）
- data/api_export.json （JSON）

帮我：
1. 从每个文件中提取数据
2. 按 customer_id 关联合并
3. 计算合并后的关键指标
4. 输出合并数据到 output/unified_data.csv
```

**命令链：**
```python
import pandas as pd
import pdfplumber

# 1. PDF 表格提取
all_tables = []
with pdfplumber.open('data/quarterly_report.pdf') as pdf:
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table and len(table) > 1:
                df_pdf = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df_pdf)
df_pdf = pd.concat(all_tables, ignore_index=True) if all_tables else pd.DataFrame()

# 2. Excel 多 Sheet
xls = pd.ExcelFile('data/sales_detail.xlsx', engine='openpyxl')
df_excel = pd.concat(
    [pd.read_excel(xls, sheet_name=s) for s in xls.sheet_names],
    ignore_index=True
)

# 3. JSON
df_json = pd.read_json('data/api_export.json')

# 4. 合并
merged = df_excel.merge(df_json, on='customer_id', how='left')
if not df_pdf.empty:
    merged = merged.merge(df_pdf, on='customer_id', how='left')

merged.to_csv('output/unified_data.csv', index=False)
print(f"合并完成: {len(merged)} 行, {len(merged.columns)} 列")
```

---

## 技能组合使用 - 端到端工作流

### 完整数据分析流程

```
步骤 1 (csv-processor)    → 数据清洗、编码修复、合并
步骤 2 (pandas-data-analysis) → EDA、分组聚合、可视化
步骤 3 (data-analysis)    → 高管报告、仪表盘、投资者图表
```

**提示词（一步到位）：**
```
对 data/ 目录下的所有 CSV 文件执行完整数据分析流程：
1. 合并所有文件，自动检测编码，清洗去重
2. 做探索性分析：数据概览、分布、相关性、异常值
3. 按业务维度分组计算 KPI
4. 生成 McKinsey 风格的分析报告图表
5. 所有输出保存到 output/ 目录
```

---

## 常用提示词模板

### 数据质量检查
```
对 {文件路径} 做数据质量评估，检查：缺失值比例、重复行、异常值、数据类型是否正确、唯一值分布
```

### 对比分析
```
对比 {文件A} 和 {文件B} 的差异：
- 新增了哪些行/列
- 哪些值发生了变化
- 统计差异汇总
```

### 自动报告生成
```
读取 {文件路径}，生成 Markdown 格式的数据分析报告，包含：
1. 数据集概览表
2. 关键指标汇总
3. 趋势分析（如有时间维度）
4. 发现与建议
保存到 output/report.md
```

### 性能优化（大数据集）
```
{文件路径} 有 {N} 百万行，请用 Polars 替代 Pandas 进行分析：
1. 延迟加载 (lazy evaluation)
2. 只读取需要的列
3. 用 Int32/Category 等紧凑类型节省内存
4. 分块处理后合并结果
```

---

## McKinsey 图表标题规范

| 错误（描述性） | 正确（行动性） |
|----------------|----------------|
| "季度收入" | "Q4 收入超目标 23%" |
| "客户获取成本" | "CAC 降低 40%，获客质量不变" |
| "队列分析" | "90 天留存率从 72% 提升至 85%" |
| "市场规模" | "TAM 42 亿，SAM 路径清晰" |

## 配色方案

```python
EXECUTIVE_COLORS = {
    'primary': '#003366',    # 深蓝（主色）
    'accent': '#0066CC',     # 亮蓝
    'positive': '#2E7D32',   # 绿色（正向）
    'negative': '#C62828',   # 红色（负向）
    'neutral': '#757575',    # 灰色
}
```
