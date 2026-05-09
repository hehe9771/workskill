---
name: bfdata
description: 跨平台数据备份技能，备份指定目录为压缩归档，支持 OSS 云端存储。零硬编码，全环境变量驱动，支持 Windows/macOS/Linux。
version: 1.0.0
source: project-init
---

# bfdata Skill

## Skill 目标

自动化多源数据备份流程：

1. **环境初始化** — 生成 .env 和配置文件模板
2. **多源备份** — 将多个指定目录压缩为单个归档
3. **OSS 上传** — 可选上传到阿里云 OSS
4. **完整性验证** — 校验归档文件有效性

## 前置要求

- Python 3.10+ 可用
- 7-Zip 或 tar 可用（至少其一）
- (可选) 阿里云 OSS 凭证
- (可选) oss2 Python 库 或 Node.js + oss-helper.js

## 执行流程

### Phase 1: 环境初始化

```bash
bash scripts/setup/init-env.sh
```

1. 从模板生成 `.env` 文件（`assets/static/.env.tmpl` → `assets/static/.env`）
2. 从模板生成备份配置文件（`assets/configs/backup-config.tmpl` → `assets/configs/backup-config.json`）
3. 提示用户编辑配置

### Phase 2: 配置备份源

编辑 `assets/static/.env`：

```bash
# 指定备份源路径（JSON 数组）
BFDATA_SOURCES=["D:/mydoc/vibekanban/.vibe-kanban-workspaces","D:/mydoc/k8s-uat","D:/mydoc/proxy","D:/mydoc/qianzhiji"]

# 输出目录
BFDATA_OUTPUT_DIR=D:/mydoc/backup

# 可选：OSS 配置
OSS_ENDPOINT=your-oss-endpoint
OSS_ACCESS_KEY_ID=your-key
OSS_ACCESS_KEY_SECRET=your-secret
OSS_BUCKET=your-bucket
```

### Phase 3: 执行备份

```bash
python scripts/data-processing/bfdata.py
```

流程：
1. 加载环境变量（`.env` 或 `BFDATA_ENV_PATH` 指定路径）
2. 加载备份配置（JSON 或 `BFDATA_CONFIG_PATH` 指定路径）
3. 合并配置源和环境变量中的源路径
4. 验证所有源路径（过滤不存在的路径，防止路径遍历）
5. 检测可用压缩工具（7z > tar）
6. 创建压缩归档
7. 可选上传到 OSS
8. 根据清理策略处理本地归档

### Phase 4: 验证备份

```bash
bash scripts/validation/validate-backup.sh [归档路径]
```

- 不指定路径时自动查找最新归档
- 检查文件存在性、大小、可解压性

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BFDATA_SOURCES` | `[]` | 备份源路径，JSON 数组或逗号分隔 |
| `BFDATA_OUTPUT_DIR` | `<skill_root>/../backup` | 输出目录 |
| `BFDATA_COMPRESS_CMD` | `auto` | 压缩工具：7z / tar / auto |
| `BFDATA_ENV_PATH` | `<skill_root>/assets/static/.env` | 环境变量文件路径 |
| `BFDATA_CONFIG_PATH` | `<skill_root>/assets/configs/backup-config.json` | 备份配置文件路径 |
| `BFDATA_OSS_KEY_PREFIX` | `bfdata` | OSS 存储路径前缀 |
| `BFDATA_OSS_HELPER` | `<project_root>/config/oss-helper.js` | OSS helper 脚本路径 |
| `BFDATA_CLEANUP` | `keep_on_upload_fail` | 清理策略 |
| `BFDATA_PYTHON` | `python` | Python 可执行文件路径 |
| `OSS_ENDPOINT` | — | OSS 端点（可选） |
| `OSS_ACCESS_KEY_ID` | — | OSS AccessKey（可选） |
| `OSS_ACCESS_KEY_SECRET` | — | OSS Secret（可选） |
| `OSS_BUCKET` | — | OSS 存储桶（可选） |

## 依赖文件

| 文件 | 用途 |
|------|------|
| `scripts/data-processing/bfdata.py` | 核心备份脚本 |
| `scripts/setup/init-env.sh` | 环境初始化 |
| `scripts/validation/validate-backup.sh` | 备份验证 |
| `assets/static/.env.tmpl` | 环境变量模板 |
| `assets/configs/backup-config.tmpl` | 备份配置模板 |

## 输出产物

| 产物 | 位置 |
|------|------|
| 压缩归档 | `<BFDATA_OUTPUT_DIR>/bfdata-backup-YYYYMMDD_HHMMSS.{7z,tar.gz}` |
| 日志 | 标准输出 |

## 成功标准

1. `.env` 文件从模板生成成功
2. 所有指定的备份源路径被正确识别（不存在的路径被警告但不阻断）
3. 压缩归档创建成功，文件非空
4. (若配置 OSS) 上传成功或明确报错并保留本地归档
5. 验证脚本确认归档可解压
