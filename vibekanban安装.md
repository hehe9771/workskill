# Vibe Kanban 安装指南与踩坑记录

## 版本信息

- **安装版本**: 0.1.39 (GitHub Release: v0.1.39-20260331145823)
- **安装日期**: 2026-04-01
- **系统环境**: Windows 11 Pro, Node.js v24.11.1

---

## 踩坑记录

### 1. 版本号格式差异

**问题**: GitHub Release 版本号与 npm 版本号格式不同。

- GitHub Release: `v0.1.39-20260331145823` (带时间戳)
- npm 发布版本: `0.1.39` (纯数字)

**影响**: 直接用 GitHub tag 名称查询 npm 会找不到对应版本。

```bash
# npm 上看到的版本列表
npm view vibe-kanban versions --json
# 最新版本: 0.1.36 (可能滞后于 GitHub Release)
```

---

### 2. GitHub SSH 安装失败

**问题**: 通过 npm 直接从 GitHub 安装需要 SSH 权限。

```bash
npm install -g "BloopAI/vibe-kanban#v0.1.39-20260331145823"
# 错误: git@github.com: Permission denied (publickey)
```

**解决**: 使用 HTTPS 方式下载 release 文件，而非 git clone。

---

### 3. 网络下载不稳定

**问题**: GitHub 文件下载经常超时或连接重置。

```bash
curl -L -o file.tar.gz "https://github.com/..."
# 错误: (56) OpenSSL SSL_read: Connection was reset, errno 10054
# 错误: (28) Failed to connect to github.com port 443 after 21050 ms: Timed out
```

**解决**: 使用 PowerShell 的 `Invoke-WebRequest`，稳定性更好。

```powershell
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/...' -OutFile 'file.tgz' -TimeoutSec 300"
```

---

### 4. Release 文件结构混淆

**问题**: GitHub Release 上有多个文件，需要区分用途。

| 文件名 | 大小 | 内容 |
|--------|------|------|
| `vibe-kanban-0.1.39.tgz` | ~14KB | **仅 CLI 包装器**，不含二进制 |
| `vibe-kanban-v0.1.39-...zip` | ~24MB | Assets 资源文件（图片、SVG等） |
| `Vibe.Kanban_0.1.39_x64-setup.exe` | ~50MB | Windows 桌面安装程序 |
| `Vibe-Kanban-0.1.39-x86_64.msi` | ~50MB | Windows MSI 安装包 |

**关键发现**:
- `tgz` 文件只包含 `package/bin/cli.js`, `package/package.json`, `package/README.md`
- **实际二进制文件不打包在 npm 包中**，而是运行时从 CDN 自动下载

---

### 5. 本地构建需要 Rust 环境

**问题**: 源码 tarball (~60MB) 包含完整的 Rust + TypeScript 项目，需要本地构建。

```bash
# 检查 Rust 环境
rustc --version  # 未安装
cargo --version  # 未安装
```

**构建依赖**:
- Rust 工具链 (cargo, rustc)
- pnpm >= 8
- Node.js >= 20

**解决**: 如果没有 Rust 环境，直接使用预构建的 npm 包，CLI 会自动下载二进制。

---

### 6. 二进制运行时下载机制

**关键理解**: vibe-kanban 的二进制文件是在首次运行时自动下载的。

```javascript
// CLI 源码中的配置
var R2_BASE_URL = "https://npm-cdn.vibekanban.com";
var BINARY_TAG = "v0.1.39-20260331145823";

// 下载路径
~/.vibe-kanban/bin/v0.1.39-20260331145823/windows-x64/
```

首次运行时，CLI 会:
1. 检查本地缓存 `~/.vibe-kanban/bin/`
2. 从 CDN 下载 manifest.json 获取版本信息
3. 下载对应平台的二进制 zip 文件
4. 解压并执行

---

## 正确的安装流程

### 方法一: 从 GitHub Release 下载 npm 包（推荐）

```bash
# 1. 下载 npm 包 (tgz 文件)
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/BloopAI/vibe-kanban/releases/download/v0.1.39-20260331145823/vibe-kanban-0.1.39.tgz' -OutFile 'vibe-kanban-0.1.39.tgz' -TimeoutSec 300"

# 2. 本地安装
npm install -g vibe-kanban-0.1.39.tgz

# 3. 验证安装
npm list -g vibe-kanban
vibe-kanban --version

# 4. 清理临时文件
rm vibe-kanban-0.1.39.tgz
```

### 方法二: 等待 npm 同步后直接安装

```bash
# 当 npm 版本同步后
npm install -g vibe-kanban@latest
```

### 方法三: 安装桌面应用（Windows）

```powershell
# 下载 Windows 安装程序
Invoke-WebRequest -Uri 'https://github.com/BloopAI/vibe-kanban/releases/download/v0.1.39-20260331145823/Vibe.Kanban_0.1.39_x64-setup.exe' -OutFile 'vibe-kanban-setup.exe'

# 运行安装
.\vibe-kanban-setup.exe
```

---

## 验证安装

```bash
# 查看版本
vibe-kanban --version
# 输出: vibe-kanban/0.1.39 win32-x64 node-v24.11.1

# 查看全局安装位置
npm list -g vibe-kanban
# 输出: C:\Users\...\npm\node_modules\vibe-kanban@0.1.39

# 首次运行会自动下载二进制
vibe-kanban
# 会显示: Downloading vibe-kanban...
```

---

## 常见问题排查

### Q: 运行时报下载失败

检查网络是否能访问 `npm-cdn.vibekanban.com`:

```bash
curl -I "https://npm-cdn.vibekanban.com/binaries/manifest.json"
```

### Q: 版本号不匹配

GitHub Release 版本可能领先于 npm，这是正常的发布流程:
1. GitHub Release 先发布
2. CI/CD 流程同步到 npm (可能有延迟)

### Q: Windows ARM64 支持

检测系统架构:

```bash
# 查看处理器架构
echo $PROCESSOR_ARCHITECTURE
# 或
node -e "console.log(process.arch)"
```

---

## 参考链接

- GitHub Release: https://github.com/BloopAI/vibe-kanban/releases
- npm 包: https://www.npmjs.com/package/vibe-kanban
- CDN 域名: https://npm-cdn.vibekanban.com