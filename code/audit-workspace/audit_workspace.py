"""
审计部 Workspace 原型 - 碳硅协同审计系统

架构：
- 数据收集专员 Agent：收集财务数据、行业基准
- 财务分析师 Agent：分析财报、识别异常
- 合规检查员 Agent：核对法规、识别合规风险
- 报告生成员 Agent：生成审计报告
- 审计经理（人类）：审核、决策

流程：
人类下达审计目标 → Agent 集群协作 → 人类审核关键节点 → 输出审计报告
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from datetime import datetime
from pathlib import Path


# ============================================================
# 基础数据结构
# ============================================================

class RiskLevel(Enum):
    LOW = "低风险"
    MEDIUM = "中风险"
    HIGH = "高风险"
    CRITICAL = "严重风险"


@dataclass
class AuditFinding:
    """审计发现"""
    id: str
    category: str  # 财务/合规/运营
    description: str
    risk_level: RiskLevel
    evidence: List[str]
    recommendation: str


@dataclass
class FinancialMetric:
    """财务指标"""
    name: str
    value: float
    industry_avg: float
    deviation: float  # 偏离度
    flag: Optional[str] = None  # 异常标记


# ============================================================
# Agent 基类
# ============================================================

class BaseAgent:
    """Agent 基类 - 模拟 AI Agent 行为"""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.history: List[Dict] = []

    def think(self, task: str, context: Dict) -> Dict:
        """思考过程（模拟 LLM 推理）"""
        raise NotImplementedError

    def execute(self, task: str, context: Dict) -> Dict:
        """执行任务"""
        print(f"\n[{self.name}] 正在处理: {task}")
        result = self.think(task, context)
        self.history.append({
            "task": task,
            "context": context,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        return result


# ============================================================
# 四个专业 Agent
# ============================================================

class DataCollectorAgent(BaseAgent):
    """数据收集专员 - 负责收集被审计单位信息"""

    def __init__(self):
        super().__init__("数据小助手", "数据收集专员")

    def think(self, task: str, context: Dict) -> Dict:
        """模拟数据收集过程"""
        company_name = context.get("company_name", "目标公司")

        # 模拟收集的数据（实际应调用 API/数据库）
        return {
            "company_info": {
                "name": company_name,
                "industry": "制造业",
                "revenue": 5_000_000_000,  # 50亿
                "employees": 3500
            },
            "financial_data": {
                "revenue": 5_000_000_000,
                "cost_of_goods_sold": 3_200_000_000,
                "operating_expenses": 800_000_000,
                "net_income": 450_000_000,
                "total_assets": 8_000_000_000,
                "total_liabilities": 4_500_000_000,
                "cash": 600_000_000,
                "receivables": 1_200_000_000,
                "inventory": 900_000_000
            },
            "industry_benchmarks": {
                "gross_margin_avg": 0.35,
                "operating_margin_avg": 0.12,
                "current_ratio_avg": 1.8,
                "debt_to_equity_avg": 0.8,
                "inventory_turnover_avg": 8.0
            }
        }


class FinancialAnalystAgent(BaseAgent):
    """财务分析师 - 分析财报数据，识别异常"""

    def __init__(self):
        super().__init__("财析君", "财务分析师")

    def think(self, task: str, context: Dict) -> Dict:
        """分析财务数据"""
        fin_data = context.get("financial_data", {})
        benchmarks = context.get("industry_benchmarks", {})

        # 计算关键指标
        revenue = fin_data.get("revenue", 0)
        cogs = fin_data.get("cost_of_goods_sold", 0)
        opex = fin_data.get("operating_expenses", 0)
        net_income = fin_data.get("net_income", 0)
        total_assets = fin_data.get("total_assets", 0)
        total_liabilities = fin_data.get("total_liabilities", 0)
        cash = fin_data.get("cash", 0)
        receivables = fin_data.get("receivables", 0)
        inventory = fin_data.get("inventory", 0)

        # 财务比率
        gross_margin = (revenue - cogs) / revenue if revenue else 0
        operating_margin = (revenue - cogs - opex) / revenue if revenue else 0
        current_ratio = (cash + receivables + inventory) / (total_liabilities * 0.4) if total_liabilities else 0
        debt_to_equity = total_liabilities / (total_assets - total_liabilities) if (total_assets - total_liabilities) else 0
        inventory_turnover = cogs / inventory if inventory else 0

        # 与行业对比
        metrics = [
            FinancialMetric("毛利率", gross_margin, benchmarks.get("gross_margin_avg", 0.35),
                          (gross_margin - benchmarks.get("gross_margin_avg", 0.35)) / benchmarks.get("gross_margin_avg", 0.35)),
            FinancialMetric("营业利润率", operating_margin, benchmarks.get("operating_margin_avg", 0.12),
                          (operating_margin - benchmarks.get("operating_margin_avg", 0.12)) / benchmarks.get("operating_margin_avg", 0.12)),
            FinancialMetric("流动比率", current_ratio, benchmarks.get("current_ratio_avg", 1.8),
                          (current_ratio - benchmarks.get("current_ratio_avg", 1.8)) / benchmarks.get("current_ratio_avg", 1.8)),
            FinancialMetric("资产负债率", debt_to_equity, benchmarks.get("debt_to_equity_avg", 0.8),
                          (debt_to_equity - benchmarks.get("debt_to_equity_avg", 0.8)) / benchmarks.get("debt_to_equity_avg", 0.8)),
            FinancialMetric("存货周转率", inventory_turnover, benchmarks.get("inventory_turnover_avg", 8.0),
                          (inventory_turnover - benchmarks.get("inventory_turnover_avg", 8.0)) / benchmarks.get("inventory_turnover_avg", 8.0)),
        ]

        # 识别异常（偏离度 > 20%）
        findings = []
        for m in metrics:
            if abs(m.deviation) > 0.2:
                flag = "偏高" if m.deviation > 0 else "偏低"
                m.flag = flag
                findings.append(AuditFinding(
                    id=f"FIN-{len(findings)+1:03d}",
                    category="财务",
                    description=f"{m.name}{flag}：{m.value:.2%}（行业均值：{m.industry_avg:.2%}，偏离：{m.deviation:.1%}）",
                    risk_level=RiskLevel.HIGH if abs(m.deviation) > 0.4 else RiskLevel.MEDIUM,
                    evidence=[f"{m.name}计算明细", "行业对标数据"],
                    recommendation=f"需进一步核查{m.name}异常原因，确认是否存在会计处理不当或经营风险"
                ))

        return {
            "metrics": [{"name": m.name, "value": m.value, "industry_avg": m.industry_avg,
                        "deviation": m.deviation, "flag": m.flag} for m in metrics],
            "findings": findings,
            "analysis_summary": f"共识别 {len(findings)} 项财务异常指标"
        }


class ComplianceCheckerAgent(BaseAgent):
    """合规检查员 - 核对法规要求"""

    def __init__(self):
        super().__init__("合规卫士", "合规检查员")

    def think(self, task: str, context: Dict) -> Dict:
        """检查合规性"""
        findings = []

        # 模拟合规检查项
        compliance_checks = [
            {
                "item": "收入确认时点",
                "standard": "企业会计准则第14号——收入",
                "status": "需关注",
                "detail": "存在大额期末收入确认，需核实是否符合控制权转移条件"
            },
            {
                "item": "关联交易披露",
                "standard": "企业会计准则第36号——关联方披露",
                "status": "合规",
                "detail": "关联交易已充分披露"
            },
            {
                "item": "存货跌价准备",
                "standard": "企业会计准则第1号——存货",
                "status": "需关注",
                "detail": "存货周转率偏低，需评估跌价准备计提是否充分"
            },
            {
                "item": "信息披露完整性",
                "standard": "上市公司信息披露管理办法",
                "status": "合规",
                "detail": "定期报告披露完整"
            }
        ]

        for check in compliance_checks:
            if check["status"] == "需关注":
                findings.append(AuditFinding(
                    id=f"COMP-{len(findings)+1:03d}",
                    category="合规",
                    description=f"{check['item']}：{check['detail']}",
                    risk_level=RiskLevel.MEDIUM,
                    evidence=[f"检查依据：{check['standard']}"],
                    recommendation=f"建议获取相关支持性文件，核实{check['item']}的合规性"
                ))

        return {
            "checks": compliance_checks,
            "findings": findings,
            "summary": f"完成 {len(compliance_checks)} 项合规检查，发现 {len(findings)} 项需关注事项"
        }


class ReportGeneratorAgent(BaseAgent):
    """报告生成员 - 汇总审计发现，生成报告"""

    def __init__(self):
        super().__init__("报告能手", "报告生成员")

    def think(self, task: str, context: Dict) -> Dict:
        """生成审计报告"""
        all_findings = context.get("findings", [])

        # 按风险等级排序
        risk_order = {RiskLevel.CRITICAL: 0, RiskLevel.HIGH: 1, RiskLevel.MEDIUM: 2, RiskLevel.LOW: 3}
        sorted_findings = sorted(all_findings, key=lambda f: risk_order.get(f.risk_level, 4))

        # 生成报告结构
        report = {
            "title": "审计报告",
            "company": context.get("company_name", "目标公司"),
            "audit_period": "2025年度",
            "generated_at": datetime.now().isoformat(),
            "executive_summary": f"本次审计共发现 {len(sorted_findings)} 项问题，"
                               f"其中高风险 {sum(1 for f in sorted_findings if f.risk_level == RiskLevel.HIGH)} 项，"
                               f"中风险 {sum(1 for f in sorted_findings if f.risk_level == RiskLevel.MEDIUM)} 项。",
            "findings": [
                {
                    "id": f.id,
                    "category": f.category,
                    "description": f.description,
                    "risk_level": f.risk_level.value,
                    "recommendation": f.recommendation
                }
                for f in sorted_findings
            ],
            "conclusion": "建议管理层针对上述发现制定整改计划，并在下一季度末完成整改。",
            "status": "待审计经理审核"
        }

        return report


# ============================================================
# 审计经理（人类角色）
# ============================================================

class AuditManager:
    """审计经理 - 人类角色，负责审核和决策"""

    def __init__(self, name: str = "张经理"):
        self.name = name

    def review(self, findings: List[AuditFinding], report: Dict) -> Dict:
        """审核 Agent 输出，做最终决策"""
        print(f"\n{'='*60}")
        print(f"[{self.name}] 正在审核审计发现...")
        print(f"{'='*60}")

        # 模拟人类审核逻辑
        high_risk_count = sum(1 for f in findings if f.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL])

        decision = {
            "approved": high_risk_count <= 3,  # 高风险超过3项需进一步调查
            "comments": "重点关注财务指标异常，建议增加实质性测试程序" if high_risk_count > 0 else "审计发现可控，同意出具报告",
            "next_steps": [
                "与被审计单位管理层沟通审计发现",
                "获取异常项目的支持性证据",
                "评估是否需要扩大审计范围"
            ] if high_risk_count > 2 else [
                "完成审计底稿整理",
                "出具正式审计报告"
            ],
            "reviewer": self.name,
            "review_time": datetime.now().isoformat()
        }

        return decision


# ============================================================
# Workspace 编排器
# ============================================================

class AuditWorkspace:
    """审计 Workspace - 协调多 Agent 协作"""

    def __init__(self):
        # 初始化 Agent 团队
        self.data_collector = DataCollectorAgent()
        self.financial_analyst = FinancialAnalystAgent()
        self.compliance_checker = ComplianceCheckerAgent()
        self.report_generator = ReportGeneratorAgent()
        self.audit_manager = AuditManager()

        print("="*60)
        print("审计 Workspace 启动")
        print("="*60)
        print(f"Agent 团队已就位：")
        print(f"  - {self.data_collector.name} ({self.data_collector.role})")
        print(f"  - {self.financial_analyst.name} ({self.financial_analyst.role})")
        print(f"  - {self.compliance_checker.name} ({self.compliance_checker.role})")
        print(f"  - {self.report_generator.name} ({self.report_generator.role})")
        print(f"人类角色：")
        print(f"  - {self.audit_manager.name} (审计经理)")
        print("="*60)

    def execute_audit(self, company_name: str) -> Dict:
        """执行审计任务 - 完整工作流"""

        print(f"\n[审计任务] 审计目标：对 {company_name} 进行年度审计")
        print("-"*60)

        # Step 1: 数据收集
        print("\n【阶段1】数据收集")
        data_result = self.data_collector.execute(
            f"收集 {company_name} 的财务数据和行业基准",
            {"company_name": company_name}
        )

        # Step 2: 财务分析
        print("\n【阶段2】财务分析")
        fin_result = self.financial_analyst.execute(
            "分析财务数据，识别异常指标",
            {
                "financial_data": data_result["financial_data"],
                "industry_benchmarks": data_result["industry_benchmarks"]
            }
        )

        # Step 3: 合规检查
        print("\n【阶段3】合规检查")
        comp_result = self.compliance_checker.execute(
            "核对会计准则和监管要求",
            {"company_info": data_result["company_info"]}
        )

        # Step 4: 人类审核点 1 - 审核审计发现
        print("\n【人类审核点】审计经理审核审计发现")
        all_findings = fin_result["findings"] + comp_result["findings"]
        print(f"共发现 {len(all_findings)} 项问题，提交审计经理审核...")

        # Step 5: 报告生成
        print("\n【阶段4】报告生成")
        report_result = self.report_generator.execute(
            "生成审计报告",
            {
                "company_name": company_name,
                "findings": all_findings
            }
        )

        # Step 6: 人类审核点 2 - 最终决策
        print("\n【人类审核点】审计经理最终审核")
        decision = self.audit_manager.review(all_findings, report_result)

        # 汇总结果
        final_result = {
            "audit_target": company_name,
            "data_collection": data_result,
            "financial_analysis": fin_result,
            "compliance_check": comp_result,
            "audit_report": report_result,
            "manager_decision": decision,
            "status": "审计完成" if decision["approved"] else "需进一步调查"
        }

        return final_result


# ============================================================
# 主程序
# ============================================================

def main():
    """演示审计 Workspace 工作流"""

    # 重定向输出到文件（解决 Windows 编码问题）
    import sys
    import io

    output_file = Path(__file__).parent / "output.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        # 保存原始 stdout
        original_stdout = sys.stdout
        sys.stdout = f

        try:
            _run_demo()
        finally:
            sys.stdout = original_stdout

    print(f"输出已保存到: {output_file}")


def _run_demo():
    """实际演示逻辑"""
    # 创建 Workspace
    workspace = AuditWorkspace()

    # 执行审计
    result = workspace.execute_audit("示例制造有限公司")

    # 输出最终结果
    print("\n" + "="*60)
    print("[审计结果] 审计结果摘要")
    print("="*60)
    print(f"审计状态：{result['status']}")
    print(f"审计发现：{len(result['financial_analysis']['findings']) + len(result['compliance_check']['findings'])} 项")
    print(f"审计经理决策：{'同意出具报告' if result['manager_decision']['approved'] else '需进一步调查'}")
    print(f"下一步行动：{', '.join(result['manager_decision']['next_steps'])}")
    print("="*60)


if __name__ == "__main__":
    main()
