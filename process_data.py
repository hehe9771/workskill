# -*- coding: utf-8 -*-
"""
储能/发电业务数据处理脚本
从项目主表.xlsx中过滤储能/发电业务，补全字段并归纳类型
"""
import pandas as pd
import numpy as np
import re
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "an" / "项目主表.xlsx"
OUTPUT_FILE = Path(__file__).parent / "output" / "processed_data.parquet"

# 省份编码映射
PROVINCE_CODE_MAP = {
    "110000": "北京", "120000": "天津", "130000": "河北", "140000": "山西",
    "150000": "内蒙古", "210000": "辽宁", "220000": "吉林", "230000": "黑龙江",
    "310000": "上海", "320000": "江苏", "330000": "浙江", "340000": "安徽",
    "350000": "福建", "360000": "江西", "370000": "山东", "410000": "河南",
    "420000": "湖北", "430000": "湖南", "440000": "广东", "450000": "广西",
    "460000": "海南", "500000": "重庆", "510000": "四川", "520000": "贵州",
    "530000": "云南", "540000": "西藏", "610000": "陕西", "620000": "甘肃",
    "630000": "青海", "640000": "宁夏", "650000": "新疆",
}

# 原始列名列表
COLUMNS = [
    "项目ID", "项目编号", "项目名称", "项目金额", "业务模式", "业务条线",
    "租赁模式", "项目状态", "客户ID", "客户名称", "客户经理ID", "客户经理名称",
    "部门ID", "部门名称", "机构ID", "机构名称", "项目资金用途", "国家", "省份",
    "市", "地区", "项目第一偿还来源", "项目第二偿还来源", "租赁物描述",
    "争议解决方式", "数据版本", "创建人", "创建时间", "最后修改人", "最后修改时间",
    "业务类型",
]


def load_raw_data(path):
    """加载原始Excel数据"""
    df = pd.read_excel(path, sheet_name="项目详情", engine="openpyxl")
    print(f"原始数据: {len(df)} 行, {len(df.columns)} 列")
    return df


def filter_energy_business(df):
    """过滤储能/发电业务线"""
    mask = df["业务条线"].str.contains("储能|发电", na=False)
    filtered = df[mask].copy()
    print(f"过滤后(储能/发电): {len(filtered)} 行")
    print(f"  业务条线分布: {filtered['业务条线'].value_counts().to_dict()}")
    return filtered


def fill_business_type(df):
    """补全业务类型字段"""
    conditions = [
        df["业务类型"].notna() & (df["业务类型"].str.strip() != ""),
        (df["业务条线"].str.contains("光伏|风电|储能", na=False))
        & (df["租赁模式"] == "直租")
        & df["机构名称"].str.contains("富鸿", na=False),
        (df["业务条线"].str.contains("光伏|风电|储能", na=False))
        & (df["租赁模式"] == "直租"),
        (df["业务条线"].str.contains("光伏|风电|储能", na=False))
        & (df["租赁模式"] == "回租"),
        df["机构名称"].str.contains("富鸿", na=False),
    ]
    choices = [
        df["业务类型"],
        "SILVER_LEASE",
        "自主开发类",
        "常规融资租赁",
        "同业资产交易",
    ]
    df["业务类型"] = np.select(conditions, choices, default="常规融资租赁")
    print(f"业务类型补全后: {df['业务类型'].value_counts().to_dict()}")
    return df


def categorize_fund_purpose(text):
    """将项目资金用途归类为5大类"""
    if pd.isna(text) or str(text).strip() == "":
        return "其他类"
    t = str(text).strip()

    # 优先级: 设备采购 > 工程建设 > 补充流动性 > 统筹安排 > 其他
    device_kw = [
        "设备采购", "购买设备", "支付设备", "采购款", "设备款",
        "购买光伏", "发电及配套设备", "购置", "配套设备",
        "购买电站设备", "光伏组件", "逆变器", "电池",
    ]
    construction_kw = [
        "电站建设", "EPC", "建设工程", "施工", "项目建设",
        "总包", "光伏建设", "风电建设", "基础设施",
        "改造", "扩建", "自来水厂", "城中村", "公共基础设施",
    ]
    liquidity_kw = [
        "补充流动资金", "补充流动", "补充承租人流动资金",
    ]
    arrangement_kw = [
        "财政", "政府安排", "统筹", "卫健委", "卫生医疗",
    ]

    # 1. 补充流动性（避免误匹配建设类）
    if any(kw in t for kw in liquidity_kw):
        return "补充流动性"

    # 2. 统筹安排
    if any(kw in t for kw in arrangement_kw):
        return "统筹安排类"

    # 3. 工程建设（优先级高于设备采购，如果同时涉及）
    has_construction = any(kw in t for kw in construction_kw)
    has_device = any(kw in t for kw in device_kw)

    if has_construction:
        return "工程建设类"
    if has_device:
        return "设备采购类"

    return "其他类"


def add_fund_purpose_type(df):
    """添加资金用途类型字段"""
    df["资金用途类型"] = df["项目资金用途"].apply(categorize_fund_purpose)
    print(f"资金用途类型: {df['资金用途类型'].value_counts().to_dict()}")
    return df


def categorize_lease_item(text):
    """将租赁物描述归类为5大类"""
    if pd.isna(text) or str(text).strip() == "":
        return "其他类"
    t = str(text).strip()

    # 优先级: 光伏 > 风电 > 储能 > 医疗 > 其他
    solar_kw = ["光伏", "太阳能"]
    wind_kw = ["风电", "风力", "风机", "风能"]
    storage_kw = ["储能"]
    medical_kw = ["医疗", "医院"]

    if any(kw in t for kw in solar_kw):
        return "光伏类"
    if any(kw in t for kw in wind_kw):
        return "风电类"
    if any(kw in t for kw in storage_kw):
        return "储能类"
    if any(kw in t for kw in medical_kw):
        return "医疗类"
    return "其他类"


def add_lease_item_type(df):
    """添加租赁物类型字段"""
    df["租赁物类型"] = df["租赁物描述"].apply(categorize_lease_item)
    print(f"租赁物类型: {df['租赁物类型'].value_counts().to_dict()}")
    return df


def add_derived_columns(df):
    """添加派生列：省份中文、年份、金额区间"""
    # 省份代码转中文（处理 float 类型如 330000.0）
    prov = pd.to_numeric(df["省份"], errors="coerce")
    prov_str = []
    for v in prov:
        if pd.isna(v):
            prov_str.append(None)
        else:
            s = str(int(v)).zfill(6)
            prov_str.append(s)
    prov_series = pd.Series(prov_str, index=df.index)
    df["省份"] = prov_series.map(PROVINCE_CODE_MAP).fillna("未知")

    # 提取年份
    df["创建时间"] = pd.to_datetime(df["创建时间"], errors="coerce")
    df["年份"] = df["创建时间"].dt.year

    # 项目金额转数值
    df["项目金额"] = pd.to_numeric(df["项目金额"], errors="coerce")

    # 金额区间
    def amount_bucket(amt):
        if pd.isna(amt):
            return "未知"
        if amt < 500_000:
            return "50万以下"
        elif amt < 2_000_000:
            return "50-200万"
        elif amt < 5_000_000:
            return "200-500万"
        elif amt < 10_000_000:
            return "500万-1000万"
        elif amt < 50_000_000:
            return "1000万-5000万"
        else:
            return "5000万以上"

    df["金额区间"] = df["项目金额"].apply(amount_bucket)
    print(f"金额区间: {df['金额区间'].value_counts().to_dict()}")
    return df


def process_all():
    """运行完整处理流程"""
    df = load_raw_data(INPUT_FILE)
    df = filter_energy_business(df)
    df = fill_business_type(df)
    df = add_fund_purpose_type(df)
    df = add_lease_item_type(df)
    df = add_derived_columns(df)

    # 导出
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_FILE, index=False)
    print(f"\n数据已导出: {OUTPUT_FILE}")
    print(f"最终数据: {len(df)} 行, {len(df.columns)} 列")
    return df


if __name__ == "__main__":
    process_all()
