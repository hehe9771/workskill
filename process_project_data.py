"""项目主表1数据清洗与分析脚本"""
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

INPUT_PATH = os.path.join('an', '项目主表1.csv')
OUTPUT_PATH = os.path.join('output', '项目主表1_cleaned.csv')
REPORT_PATH = os.path.join('output', '项目主表1_report.txt')


def classify_rental(desc: str) -> str:
    """从租赁物描述提取租赁物类型（≤10类）"""
    if pd.isna(desc):
        return '未知'
    desc = str(desc)

    # 检查是否包含多种设备类型（综合类）
    has_pv = any(k in desc for k in ['光伏', '组件', '逆变器'])
    has_wind = any(k in desc for k in ['风力', '风电', '风机', '风场'])
    has_storage = '储能' in desc
    has_hydro = any(k in desc for k in ['水电', '水力', '水轮'])

    type_count = sum([has_pv, has_wind, has_storage, has_hydro])
    if type_count >= 2:
        return '综合能源设备'

    if has_pv:
        return '光伏设备'
    if has_wind:
        return '风电设备'
    if has_storage:
        return '储能设备'
    if has_hydro:
        return '水电设备'
    if any(k in desc for k in ['供热', '供暖', '供电供暖', '电供暖']):
        return '供热设备'
    if any(k in desc for k in ['车', '动力电池']):
        return '车辆设备'
    if any(k in desc for k in ['房地产', '不动产']):
        return '不动产'

    return '其他设备'


def classify_fund_usage(usage: str) -> str:
    """从项目资金用途提取项目资金类型（≤10类）"""
    if pd.isna(usage):
        return '未知'
    usage = str(usage)

    # 置换/偿还融资优先判断（较长描述中常包含多种用途）
    if any(k in usage for k in ['置换', '结清', '偿还贷款', '归还贷款', '偿还借款', '归还借款']):
        return '置换/偿还融资'
    if any(k in usage for k in ['补充流动', '补充现金', '经营周转', '补充企业', '补充承租人']):
        return '补充流动资金'
    if any(k in usage for k in ['收购', '受让', '并购']):
        return '资产收购'
    if 'EPC' in usage:
        return 'EPC款项'
    if any(k in usage for k in ['偿还', '归还']):
        return '偿还债务'
    if any(k in usage for k in ['采购', '购买', '购置', '采购款']):
        return '设备采购'
    if any(k in usage for k in ['建设', '施工', '建安', '开发']):
        return '项目建设'
    if any(k in usage for k in ['设备款', '设备价款']):
        return '设备采购'
    if any(k in usage for k in ['通道', '详见会议']):
        return '其他'

    return '其他'


# 业务条线 → 业务条线类型映射（11→合并到≤10类）
BUSINESS_LINE_MAP = {
    '新能源市场化-光伏': '光伏',
    '新能源股东-光伏': '光伏',
    '光伏发电': '光伏',
    '风力发电': '风电',
    '新能源股东-风电': '风电',
    '新能源市场化-风电': '风电',
    '储能业务': '储能',
    '新能源市场化水电': '水电',
    '水力发电': '水电',
    '能源类市场化-其他': '其他能源',
    '能源类股东-其他': '其他能源',
}


def process():
    """主处理流程"""
    logger.info("读取数据: %s", INPUT_PATH)
    df = pd.read_csv(INPUT_PATH)
    logger.info("原始数据: %d 行, %d 列", len(df), len(df.columns))

    # 1. 业务类型和业务属性缺失补全
    missing_biz_type = df['业务类型'].isna().sum()
    missing_biz_attr = df['业务属性'].isna().sum()
    df['业务类型'] = df['业务类型'].fillna('未知')
    df['业务属性'] = df['业务属性'].fillna('未知')
    logger.info("业务类型补全: %d 条缺失 → 填充为'未知'", missing_biz_type)
    logger.info("业务属性补全: %d 条缺失 → 填充为'未知'", missing_biz_attr)

    # 2. 租赁物描述 → 租赁物类型
    df['租赁物类型'] = df['租赁物描述'].apply(classify_rental)
    logger.info("租赁物类型分布:\n%s", df['租赁物类型'].value_counts().to_string())

    # 3. 项目资金用途 → 项目资金类型
    df['项目资金类型'] = df['项目资金用途'].apply(classify_fund_usage)
    logger.info("项目资金类型分布:\n%s", df['项目资金类型'].value_counts().to_string())

    # 4. 业务条线 → 业务条线类型
    df['业务条线类型'] = df['业务条线'].map(BUSINESS_LINE_MAP).fillna('其他能源')
    logger.info("业务条线类型分布:\n%s", df['业务条线类型'].value_counts().to_string())

    # 输出
    os.makedirs('output', exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
    logger.info("清洗后数据已保存: %s", OUTPUT_PATH)

    # 生成报告
    generate_report(df)
    return df


def generate_report(df: pd.DataFrame):
    """生成数据清洗报告"""
    lines = [
        "=" * 60,
        "项目主表1 数据清洗与分析报告",
        "=" * 60,
        f"\n总记录数: {len(df)}",
        f"总字段数: {len(df.columns)}",
        "\n--- 缺失值补全 ---",
        f"业务类型: 原缺失 {(df['业务类型'] == '未知').sum()} 条，已补全为'未知'",
        f"业务属性: 原缺失 {(df['业务属性'] == '未知').sum()} 条，已补全为'未知'",
        "\n--- 租赁物类型（从租赁物描述提取）---",
        df['租赁物类型'].value_counts().to_string(),
        "\n--- 项目资金类型（从项目资金用途提取）---",
        df['项目资金类型'].value_counts().to_string(),
        "\n--- 业务条线类型（从业务条线提取）---",
        df['业务条线类型'].value_counts().to_string(),
        "\n--- 业务类型分布 ---",
        df['业务类型'].value_counts().to_string(),
        "\n--- 业务属性分布 ---",
        df['业务属性'].value_counts().to_string(),
        "\n" + "=" * 60,
    ]
    report = '\n'.join(lines)
    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)
    logger.info("报告已保存: %s", REPORT_PATH)


if __name__ == '__main__':
    process()
