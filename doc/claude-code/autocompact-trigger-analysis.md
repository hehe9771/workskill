# Claude Code auto-compact 触发机制分析与 80% 触发实现方案

> 分析日期：2026-09-10
> 分析对象：Claude Code CLI v2.1.223（npm 安装，`bin/claude.exe` Bun 编译二进制）
> 环境背景：DashScope 第三方 relay（`ANTHROPIC_BASE_URL=https://dashscope.aliyuncs.com/apps/anthropic`），模型 `ZHIPU/GLM-5.3-Flash[1M]`
> 触发场景：k8s-uat 项目会话「星图修改」上下文超过 90%（HUD 显示 91%），auto-compact 一直不触发
> 性质：**仅分析**，未做任何配置修改

---

## 一、问题根因：为什么超过 90% 不触发 compact

### 1.1 一句话根因

**auto-compact 的触发线不是"90%"，而是「窗口 − 固定 33k reserve」。1M 窗口下触发线 = 967,000 tokens（96.7%）。出问题的会话峰值只有 925,573 tokens（92.6%），离触发线还差 41k，所以没触发是代码的正确行为** ——是预期错了，不是功能坏了。

### 1.2 触发公式（二进制逆向得出）

```js
// claude.exe v2.1.223 提取的判定链
lin(model) = kwo(Jwe(model))
Jwe = window − min(maxOutputTokens, 20000)   // usable：1M − 20k = 980k
kwo = usable − 13000                          // 触发线：967k
```

- reserve（20k 输出预留 + 13k 缓冲）是**固定值，不随窗口缩放**
- 200k 窗口时触发在 167k（83.5%）；换 1M 窗口，触发点漂移到 967k（96.7%）
- 二进制内置模型表印证：`claude-sonnet-5 → default: 967000`

### 1.3 证据链

**① 出问题会话定位**（HUD 缓存 + sha256 双重确认）

会话 `C:\Users\wuyan\.claude\projects\D--mydoc-k8s-uat\ff2e2c95-0a5d-47b7-b9f8-2eff864f50be.jsonl`（session 名「星图修改」）：

```
used_percentage: 91, context_window_size: 1000000
usage: input 578 + cache_read 911,488 ≈ 912k tokens
峰值 925,573 tokens = 92.6%
transcript 中唯一一次 compact = 手动 /compact（2026-09-09 22:37 本地时间）
```

HUD 缓存键 = sha256(transcript 绝对路径)（Windows 反斜杠形式），缓存位于
`~/.claude/plugins/claude-hud/context-cache/<hash>.json`。

**② 窗口解析**

```js
function Fb(e){ return /\[1m\]/i.test(e) }   // 大小写不敏感，[1M] 命中 → 窗口 1,000,000
```

**③ "更早压缩"路径双重关闭**

代码里有两条压缩路径，提前介入的 precompute/reactive compact 被锁死：

- Statsig gate `tengu_sepia_moth` 默认 `false`
- `precomputeCompactionEnabled` 默认 `false`（`Wbr(){return!1}`）

本环境（DashScope 第三方 relay + `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`）拿不到实验开关 → 只剩 96.7% 的经典阈值一条路。相关锁：`hasAttemptedReactiveCompact`（失败一次不再重试）、`precomputed_compact_swap`、3 连快速回填 thrashing trip。

### 1.4 为什么"看起来像坏了"（三个叠加因素）

| 因素 | 说明 |
|---|---|
| `[1M]` 后缀放大分母 | 窗口按 1M 计，而 reserve 不缩放，触发点从 ~83% 漂移到 96.7% |
| GLM 后端"太能装" | DashScope 真的能吃下 925k 不报错，`model_context_window_exceeded` 一次没出现，没有任何错误逼人注意 |
| HUD 不提示余量 | HUD 直读 client 算出的 used_percentage，没显示"离触发还差 41k"；HUD 内置预测（buffer 0.165 ≈ 83.5% 触发）按 200k 经验调的，1M 下严重失真 |

### 1.5 附带发现

- `settings.json` 顶层的 `"CLAUDE_MODEL": "qwen3.7-plus[1M]"` 是无效位置（model 应在 `env` 块下），疑似遗留配置
- 二进制里有现成的调整口子（见第二节）

---

## 二、如何实现 80% 触发（方案对比分析）

### 2.1 默认参数回顾

```
usable = 1M − 20k = 980,000
默认触发线 = usable − 13,000 = 967,000（96.7%）
目标：触发在 800,000（1M 窗口的 80%）
```

### 2.2 五条路径对比

| 路径 | 机制 | 能否实现 | 评价 |
|---|---|---|---|
| **A. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`** | 直接覆盖触发百分比 | ✅ **精确实现** | **推荐**，为比例触发而生 |
| B. `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | 改窗口分母 | ⚠️ 绕路实现 | 触发线仍 = window−33k，且 HUD 分母跟着变，口径失真 |
| C. `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | 改未知模型默认窗口 | ❌ 被 `[1M]` 拦死 | `UKp()` 里 `Fb(e)` 先命中 `[1M]` 直接返回 1e6，**该 env 永远读不到**；除非去掉 `[1M]` 后缀 |
| D. hooks 外挂监控 | 监控 usage 触发压缩 | ❌ 不可行 | 无 hook 能向运行中 CLI 注入 /compact；PreCompact 只是通知不是触发器 |
| E. 去掉模型名 `[1M]` 后缀 | 窗口回落 200k | ⚠️ 触发 83.5% | 容量缩水 5 倍，除非为省配额否则不值 |

### 2.3 路径 A 的精确数学

代码链：`rws()` 读 env → `testPctOverride` → `kwo()`：

```js
if(n>0 && n<=100) return Math.min(Math.floor(usable × n/100), usable−13000)
```

| 目标 | 设定值 | 实际触发线 |
|---|---|---|
| usable 的 80% | `80` | **784,000**（= 1M 窗口的 78.4%） |
| **1M 窗口的 80%（800k）** | **`81.633`** | **≈800,000**（980000×0.81633→floor） |

> 注意：80% 的分母是谁要先定义——`80` 触发在 HUD 显示 78.4% 处，`81.633` 才是 HUD 显示 80% 时触发。

### 2.4 路径 A 关键行为细节

1. **实时读取**：`rws()` 每次判定时读 `process.env`，无缓存 → 启动前设好即可，已运行会话不受影响
2. **生效面一致**：classic 触发（lin）、预压缩（Yvs）、CLI 状态分级（warn 764k / compact 784k）全部前移；**HUD 显示不变**（分母仍是 1M），会在 HUD 78.4%/80% 处看到 compact 发生
3. **非法值静默回退**：parseFloat 宽松（`"80abc"`=80），但 0、负数、>100、非数字 → 无报错静默回到 967k。⚠️ 踩坑点
4. **设置位置**：`~/.claude/settings.json` 的 `env` 块。⚠️ 已知坑：若 daemon 用 `--settings` 文件启动，`--settings` 不继承 settings.json 的 env → 必须写进那个文件
5. **命名风险**：变量在代码里叫 `testPctOverride`（测试钩子语义），上游无兼容承诺，**升级 CLI 版本后需复查**（v2.1.223 实证存在）

### 2.5 路径 B 补充说明（`CLAUDE_CODE_AUTO_COMPACT_WINDOW`）

它是 `/config` 交互式设置 "Select auto-compact window" 的 env 前置，优先级 env > settings，来源枚举：`env / settings / unknown-model / model-default / auto`。官方警告："Overriding auto may result in high token usage, especially when resuming long sessions."

- 要触发 800k → 需设 window = 833,000（800k + 33k），此时 HUD 分母也变 833k，触发时 HUD 显示 96% —— 显示口径失真
- 若设成 <200k 会撞 `Uhe=200000` 禁用线（`window < Uhe → 永不触发`）

### 2.6 降到 80% 触发的副作用

- **单轮成本省 ~14%**：91% 时每轮 cache_read ~912k tokens → 78% 时 ~784k，对 DashScope 配额/延迟直接受益
- **压缩更频繁**：按「星图修改」增速（手动 compact 后一天涨回 925k），大约每天多压 1 次，每次都是一场有损摘要
- **thrashing 风险**：若单个工具结果 >180k，3 turns 内回填到线、连续 3 轮 → 触发 "Autocompact is thrashing... use /clear" 警告；大文件读取场景需留意
- blocked 层（默认 977k）不动，最后 3k 的保险丝保留

---

## 三、结论

**根因**：1M 窗口 + 固定 33k reserve → 触发线 967k（96.7%），会话峰值 925.6k（92.6%）从未越过，行为正确，预期错误。

**若要 80% 触发**（推荐路径 A，未实施）：
- 设 `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=81.633`（HUD 显示 80% 时触发，即 800k）
- 或 `=80`（usable 口径，784k，HUD 显示 78.4% 时触发）
- 写进 `~/.claude/settings.json` 的 `env` 块（daemon `--settings` 场景写进对应文件），新会话生效
- 升级 CLI 后需复查该变量是否仍存在

---

## 附：诊断工具链（可复用）

| 工具 | 用法 |
|---|---|
| claude-hud 缓存 | `~/.claude/plugins/claude-hud/context-cache/<sha256(transcript_path)>.json`（Windows 反斜杠路径），含 used_percentage / context_window_size / 真实 usage |
| used_percentage 口径 | `(input + cache_creation + cache_read) / window × 100`，client 自己算，HUD 直读 stdin |
| 二进制函数提取 | `grep -a -o -E 'function <name>\(.{0,N}' bin/claude.exe`（Bun 编译，JS 明文嵌入） |
| 相关 env | `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`（百分比）、`CLAUDE_CODE_AUTO_COMPACT_WINDOW`（窗口）、`CLAUDE_CODE_MAX_CONTEXT_TOKENS`（被 `[1M]` 拦截）、`DISABLE_AUTO_COMPACT`（关闭） |
| transcript 定位 | `~/.claude/projects/<项目路径转义>/<session-id>.jsonl`，注意 grep 搜索串会被记进 transcript 造成自污染，用精确模式（如 `"isCompactSummary":true`） |
