# Docker 空间清理过程实录

> 结果速览见同目录 [cleanup-report.md](cleanup-report.md)；本文记录完整操作过程、踩坑排查与可复用命令。
> 环境：Windows 11 / Docker Desktop 4.x / WSL2 / containerd image store

## 1. 背景与目标

Docker 占用过大，目标：

1. 同一个项目只保留最新镜像
2. 保留用作打包基础的基础镜像（pytorch/nvidia-cuda/node/python 等）
3. 释放宿主机磁盘空间

## 2. 现状盘点（只读命令）

```powershell
docker system df                     # 总览：Images 163.7GB / Build Cache 79.7GB / Volumes 3.5GB
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}\t{{.CreatedSince}}"
docker ps -a                         # 仅 2 个容器在跑（redis/mysql dev）
docker buildx ls                     # 发现 builder 实例（后面踩坑的关键）
Get-ChildItem "$env:LOCALAPPDATA\Docker\wsl" -Recurse -Filter *.vhdx
```

关键数据：

- 319 个镜像仅 2 个在用；**migration-system 一个仓库 214 个版本 tag**（每天多次构建），om-ingestion-neo4j 21 个、wasp 19 个
- 宿主机真实占用 `docker_data.vhdx` = **186GB**
- 疑点：Images 163.7 + Cache 79.7 + Volumes 3.5 = **243GB > vhdx 186GB**（当时未解，后来成为破案线索）

## 3. 计划与执行顺序

原计划：存档 → 清 cache → 清旧版镜像 → 清未用镜像 → 清 volume → 收缩 vhdx。
实际执行中 cache 一步受挫，**顺序修正为：先删镜像、最后清 cache**（原因见 §5）。

每一步原则：先只读生成清单 → 过目/确认 → 分批删除 → 验证。大批量操作（删 283 个镜像）按 40 个/批分批执行，避免一次删除太多卡死。

### Phase 1 存档

```powershell
mkdir doc\docker-cleanup
docker images --format "..." > images-before.txt    # 另存 containers/volumes/system-df
```

### Phase 3 业务旧版镜像分批删除

按 `CreatedAt` 排序，每仓库保留最新 1 个，生成 `images-to-delete-phase3.txt`（283 条）：

```powershell
# 生成清单（CreatedAt 是定宽字符串，直接字符串排序即可，不要转 [datetime]）
docker images $repo --format "{{.CreatedAt}}|{{.Tag}}" | Sort-Object -Descending

# 分批删除，每批 40 个；stderr 单独落文件防 PowerShell 5.1 NativeCommandError
& docker rmi @ids 2>"$env:TEMP\p3-b1-err.txt" | Select-String "^Untagged:" | Measure-Object
```

8 批 × 40 个，283/283 成功、0 错误。另删 OpenMetadata 2.0.0 旧版、pet-disease-api 旧版、neo4j 旧 tag 等 7 个引用。

### Phase 5 Volume（先确认再删）

`docker system df -v` 列出 25 个卷及 LINKS 数。**不用 `docker volume prune`**（会连保留卷一起删），按名字精确 `rm`：

```powershell
$targets = docker volume ls -q | Where-Object { $keep -notcontains $_ }
& docker volume rm @targets    # 20 个匿名/空卷删除；在用卷 docker 自动拒绝，双保险
```

### Phase 6 收缩 VHDX（Windows 特有：删镜像后 vhdx 不会自动缩小）

```powershell
docker stop <容器>                                    # 1. 优雅停容器
Get-Process "Docker Desktop","com.docker.backend" | Stop-Process -Force   # 2. 退 Docker Desktop
wsl --shutdown                                        # 3. WSL 完全停机（vhdx 句柄才能释放）
```

diskpart 需要管理员权限；脚本文件必须 ASCII 编码（UTF-8 BOM 会解析失败）：

```
# compact-vdisk.txt
select vdisk file="C:\Users\<user>\AppData\Local\Docker\wsl\disk\docker_data.vhdx"
attach vdisk readonly
compact vdisk
detach vdisk
```

```powershell
Start-Process diskpart -ArgumentList "/s","compact-vdisk.txt" -Verb RunAs   # 4. UAC 提权执行
# 5. 轮询 Get-Process diskpart 等待结束，结果：186GB → 86.7GB
Start-Process "Docker Desktop"                        # 6. 重启后 docker start 容器
```

## 4. 恢复与验证

- `docker ps`：redis/mysql 容器 Up，数据卷无损
- `docker system df`：Images 73.3GB/33 个、Cache 0、Volumes 374MB/5 个
- vhdx：186GB → **86.7GB**（宿主机释放 99.3GB）

## 5. 踩坑与根因（本次最有价值的部分）

### 坑 1：build cache 79.7GB 删不掉（prune 报 0B）

现象与排查链：

1. `docker builder prune -f --filter until=168h` 只删 42MB
2. `docker builder prune -af --keep-storage 40GB` → **Total: 0B**
3. `docker buildx ls` 发现**两个 builder**：`default` 与 `desktop-linux*`（当前选中）—— 排除选错 builder
4. `docker buildx du --builder default` 为空，79.7GB 都在 desktop-linux；显式 `--builder desktop-linux` prune 依然 0B
5. `docker info` 看到 `driver-type: io.containerd.snapshotter.v1` → **根因确认**

**根因**：Docker Desktop 开启 containerd image store 后，镜像层与 build cache 共享同一 content store 的 blob。`docker system df` 把这些 blob 在 Images 和 Build Cache 两类里**重复计数**（163.7+79.7=243GB > vhdx 186GB 的疑点对上了）。被镜像引用的 blob prune 释放不了 → 一条记录都删不掉。

**解法**：先删镜像（解除 blob 引用）→ 再 `docker buildx prune --builder desktop-linux -af` → 一次全清成功（79.7GB → 0）。

### 坑 2：`--filter until=...` 对 shared 缓存条目无效

`buildx du` 中带 `*` 的条目是 shared，按时间过滤删不动；不要依赖时间过滤做批量 cache 清理。

### 坑 3：PowerShell 5.1 调 docker 的两个小坑

- docker 的 `CreatedAt`（`2026-09-13 10:24:15 +0800 CST`）无法被 `[datetime]` 转换 → 用定宽字符串直接排序
- native 命令的 `2>&1` 会产生 NativeCommandError 包装 → stderr 重定向到文件再读

### 口径提醒：清理后 RECLAIMABLE 65% 不是还能删 48GB

容器未运行但属于保留范围的服务/基础镜像，全部被计为 RECLAIMABLE。这是统计口径，不是可回收空间。

## 6. 可复用命令速查

| 场景 | 命令 |
|---|---|
| 按仓库列版本数与名义大小 | `docker images --format "{{.Repository}}\t{{.Size}}"` 后 PowerShell 分组求和 |
| 每仓库保留最新 | 按 CreatedAt 字符串排序，留首个，其余 `docker rmi`（分批 ≤40） |
| 全清构建缓存 | `docker buildx prune --builder desktop-linux -af`（**显式指定 builder**） |
| 精确删卷 | `docker volume rm <name>`（勿用 prune） |
| 收缩 vhdx | 停容器 → 退 Docker → `wsl --shutdown` → diskpart compact（UAC）→ 重启 |
| 清理后验证 | `docker system df` + `Get-Item <vhdx>` 文件大小对比 |
