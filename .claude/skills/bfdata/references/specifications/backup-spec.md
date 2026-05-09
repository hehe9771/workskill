# 备份技术规范

## 备份格式

### 7z 格式
- 压缩级别: 5（平衡速度和体积）
- 支持 Windows 长路径
- 保留文件权限和属性

### tar.gz 格式
- 作为 7z 不可用时的备选
- 跨平台兼容性更好
- 压缩率略低于 7z

## 路径处理规范

### 跨平台路径解析

所有路径通过以下顺序解析：

1. **环境变量展开**: `os.path.expandvars()` 处理 `$VAR` / `%VAR%`
2. **用户目录展开**: `os.path.expanduser()` 处理 `~`
3. **绝对化**: `Path.resolve()` 转换为绝对路径
4. **遍历检查**: 拒绝包含 `..` 的路径

### 平台差异

| 平台 | 环境变量 | 路径分隔符 |
|------|----------|-----------|
| Windows | `%TEMP%`, `%APPDATA%`, `%USERPROFILE%` | `\` 或 `/` |
| macOS/Linux | `$HOME`, `$TMPDIR` | `/` |

### 推荐写法

```bash
# 使用环境变量（跨平台兼容）
${USERPROFILE}/.claude        # Windows
${HOME}/.claude               # macOS/Linux

# 使用绝对路径
D:/mydoc/workspace            # Windows
/home/user/workspace          # Linux
/Users/user/workspace         # macOS
```

## 安全规范

### 路径安全

- 禁止路径遍历（`..` 检查）
- 禁止符号链接跟随
- 所有路径在操作前进行 `resolve()` 规范化

### 凭证安全

- OSS 凭证存储在 `.env` 文件
- `.env` 文件必须加入 `.gitignore`
- 禁止在日志或错误消息中打印凭证
- 错误消息中仅显示变量名，不显示值

## 压缩策略

### 选择逻辑

```
if 7z available → use 7z (better compression)
elif tar available → use tar.gz (universal compatibility)
else → error (no compression tool available)
```

### 超时限制

- 单次压缩操作: 3600 秒
- 单次 OSS 上传: 600 秒

## OSS 上传规范

### 认证方式

1. 优先使用 Python `oss2` 库
2. 回退到 `oss-helper.js`（Node.js）
3. 两者都不可用时，仅保留本地归档

### 命名约定

```
<前缀>/bfdata-backup-YYYYMMDD_HHMMMSS.{7z,tar.gz}
```

默认前缀: `bfdata`

### 清理策略

| 策略 | 行为 |
|------|------|
| `remove_on_upload_success` | OSS 上传成功后删除本地归档 |
| `keep_on_upload_fail` | OSS 上传失败时保留本地归档（默认） |

## 错误处理

所有错误必须：

1. 输出到 stderr
2. 包含明确的 `[ERROR]` 或 `[WARN]` 前缀
3. 提供可操作的恢复建议
4. 不静默吞异常
