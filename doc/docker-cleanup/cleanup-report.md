# Docker 空间清理报告

- 日期：2026-09-14
- 环境：Windows 11 / Docker Desktop（containerd image store, WSL2 backend）
- 存档：本目录下 `images-before.txt`、`containers-before.txt`、`volumes-before.txt`、`system-df-before.txt`

## 结果总览

| 项目 | 清理前 | 清理后 | 变化 |
|---|---|---|---|
| Images | 163.7GB / 319 个 | 73.3GB / 33 个 | -90.4GB，286 个旧版删除 |
| Build Cache | 79.7GB / 2476 条 | 0B | 全清 |
| Volumes | 3.5GB / 25 个 | 374MB / 5 个 | 20 个遗留卷删除 |
| **docker_data.vhdx（宿主机）** | **186 GB** | **86.7 GB** | **释放 99.3 GB** |

## 执行过程

1. **存档**：清理前全量清单落盘。
2. **镜像清理**：业务仓库（migration-system 214 个版本等）各保留最新 1 个，分 8 批共删 283 个；另删 OpenMetadata 2.0.0 旧版、pet-disease-api 旧版、neo4j 旧 tag 等 7 个引用 + 悬空层 272MB。全部 0 错误。
3. **Build Cache**：直接 prune 报 0B —— 根因是 containerd image store 下镜像层与 cache 共享 blob，`docker system df` 重复计数（163.7+79.7=243GB > vhdx 186GB）。镜像删除解除引用后 `docker buildx prune --builder desktop-linux -af` 成功全清。
4. **Volume**：用户确认保守方案，删 18 个匿名卷 + 2 个空命名卷；保留 `mysaas_postgres_data`、`ntest-data`、`ntest-logs` 及运行中容器的 2 个卷。
5. **VHDX 收缩**：优雅停容器 → 退 Docker Desktop → `wsl --shutdown` → diskpart（UAC 提权）attach readonly + compact vdisk → 186GB → 86.7GB。
6. **恢复**：Docker Desktop 重启，redis/mysql 容器已拉起（数据卷无损）。

## 保留清单（业务项目最新版）

- harbor.nbmarket.cn:8001/hubdocker/migration-system:2.3.136
- harbor.nbmarket.cn:8001/hubdocker/om-ingestion-neo4j:2.0.1-r21
- harbor.nbmarket.cn:8001/hubdocker/wasp:20260911-f602887
- harbor.nbmarket.cn:8001/hubdocker/canal-server-sync:v1.1.7-r10
- harbor.nbmarket.cn:8001/hubdocker/om-bridge:1.0-r25
- harbor.nbmarket.cn:8001/hubdocker/etl-extract:2.1
- 及基础/服务镜像：pytorch×2、nvidia/cuda×2、node×2、python:3.11-slim、alpine、postgres、redis、mysql、neo4j 系、elasticsearch、kafka、canal、clickhouse、OpenMetadata 2.0.1 全家桶、semantica、pet-asr-cuda、pet-sound-to-texts、pet-disease-api、opensaas-wasp-dev、om-fuseki-rdf、rdflib-baseline

## 注意事项

- 当前 `docker system df` 显示 Images RECLAIMABLE 65%（48GB）是口径问题：未被容器运行但属于保留范围的服务/基础镜像均被计为"可回收"，**不代表还能再删 48GB**。
- 未来旧版本镜像积累后可复用本报告 Phase 3 的分批删除模式；Build Cache 用 `docker buildx prune --builder desktop-linux -af`（注意显式指定 builder）。
- 收缩 vhdx 的 diskpart 脚本：`compact-vdisk.txt`（本目录）。
