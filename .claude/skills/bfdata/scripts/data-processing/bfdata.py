#!/usr/bin/env python3
"""
bfdata.py - 跨平台数据备份脚本

从 .env 和 backup-config 读取配置，备份指定目录为 7z/tar 归档，
可选上传到 OSS。零硬编码，全环境变量驱动。
"""

import os
import sys
import json
import shutil
import subprocess
import tarfile
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Literal

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# 路径推断：从脚本自身位置推导技能根目录，支持跨平台
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent.parent

# 默认配置文件路径（相对技能根目录）
DEFAULT_ENV_PATH = SKILL_ROOT / "assets" / "static" / ".env"
DEFAULT_CONFIG_PATH = SKILL_ROOT / "assets" / "configs" / "backup-config.json"

# ---------------------------------------------------------------------------
# 加载配置
# ---------------------------------------------------------------------------

def load_env():
    """加载环境变量，优先使用 BFDATA_ENV_PATH 环境变量指定的路径。"""
    env_path = os.environ.get("BFDATA_ENV_PATH")
    if env_path and Path(env_path).exists():
        load_dotenv(env_path, override=True)
    elif DEFAULT_ENV_PATH.exists():
        load_dotenv(DEFAULT_ENV_PATH, override=True)

def load_backup_config():
    """加载备份配置 JSON。"""
    config_path = os.environ.get("BFDATA_CONFIG_PATH", str(DEFAULT_CONFIG_PATH))
    if not Path(config_path).exists():
        print(f"[WARN] 备份配置文件不存在: {config_path}，使用默认配置", file=sys.stderr)
        return {"sources": [], "compress_cmd": "auto"}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] 配置文件 JSON 格式错误: {e}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def find_executable(name: str) -> Optional[str]:
    """在 PATH 中查找可执行文件。"""
    path = shutil.which(name)
    if path:
        return path
    # Windows: 尝试 .exe 后缀
    if sys.platform == "win32":
        path = shutil.which(f"{name}.exe")
        if path:
            return path
    return None

VALID_COMPRESSORS: Tuple[str, ...] = ("7z", "tar")

def get_compressor() -> Literal["7z", "tar"]:
    """根据可用工具自动选择压缩命令。"""
    cfg_cmd = os.environ.get("BFDATA_COMPRESS_CMD", "auto")
    if cfg_cmd != "auto":
        if cfg_cmd not in VALID_COMPRESSORS:
            print(f"[ERROR] 不支持的压缩工具: {cfg_cmd}，可选: {', '.join(VALID_COMPRESSORS)}", file=sys.stderr)
            sys.exit(1)
        exe = find_executable(cfg_cmd)
        if exe:
            return cfg_cmd
        print(f"[ERROR] 指定的压缩工具 '{cfg_cmd}' 不可用", file=sys.stderr)
        sys.exit(1)

    if find_executable("7z"):
        return "7z"
    if find_executable("tar"):
        return "tar"
    print("[ERROR] 未找到 7z 或 tar，请安装其中之一", file=sys.stderr)
    sys.exit(1)

def validate_paths(sources: List[str]) -> List[str]:
    """验证源路径，过滤不存在的路径，防止路径遍历攻击。"""
    valid = []
    for src in sources:
        # 在展开前检查原始路径中的遍历字符
        if ".." in src:
            print(f"[ERROR] 拒绝路径遍历尝试: {src}", file=sys.stderr)
            sys.exit(1)
        expanded = os.path.expandvars(os.path.expanduser(src))
        p = Path(expanded)
        if not p.exists():
            print(f"[WARN] 源路径不存在，跳过: {expanded}", file=sys.stderr)
            continue
        valid.append(str(p.resolve()))
    return valid

# ---------------------------------------------------------------------------
# 核心功能
# ---------------------------------------------------------------------------

def create_archive(compressor: Literal["7z", "tar"], sources: List[str], output_dir: str, timestamp: str) -> Optional[str]:
    """创建压缩包，返回归档文件路径。"""
    os.makedirs(output_dir, exist_ok=True)
    ext = "7z" if compressor == "7z" else "tar.gz"
    archive_name = f"bfdata-backup-{timestamp}.{ext}"
    archive_path = os.path.join(output_dir, archive_name)

    print(f"[INFO] 创建归档: {archive_name}")
    print(f"[INFO] 压缩工具: {compressor}")
    print(f"[INFO] 源数量: {len(sources)}")

    if compressor == "tar":
        return _create_tar(sources, archive_path)
    else:
        return _create_7z(sources, archive_path)

def _create_tar(sources: List[str], archive_path: str) -> Optional[str]:
    """使用 Python 内置 tarfile 模块创建归档（跨平台，无需 shell）。"""
    try:
        with tarfile.open(archive_path, "w:gz") as tar:
            for src in sources:
                src_path = Path(src)
                arcname = src_path.name
                print(f"[INFO] 添加: {src}")
                tar.add(src, arcname=arcname, recursive=True)
        print(f"[OK] 归档已创建: {archive_path}")
        return archive_path
    except (OSError, tarfile.TarError) as e:
        print(f"[ERROR] 压缩异常: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return None

def _create_7z(sources: List[str], archive_path: str) -> Optional[str]:
    """使用 7z 创建归档。"""
    exe = find_executable("7z")
    if not exe:
        print("[ERROR] 7z 可执行文件未找到", file=sys.stderr)
        return None
    cmd = [exe, "a", "-t7z", "-mx=5", archive_path] + sources
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        if result.returncode != 0:
            print(f"[ERROR] 压缩失败:\n{result.stderr}", file=sys.stderr)
            return None
        print(f"[OK] 归档已创建: {archive_path}")
        return archive_path
    except subprocess.TimeoutExpired:
        print("[ERROR] 压缩超时 (3600s)", file=sys.stderr)
        return None
    except OSError as e:
        print(f"[ERROR] 压缩异常: {e}", file=sys.stderr)
        return None

def upload_to_oss(archive_path: str, oss_key: str) -> bool:
    """上传归档文件到 OSS。"""
    required_vars = ["OSS_ENDPOINT", "OSS_ACCESS_KEY_ID", "OSS_ACCESS_KEY_SECRET", "OSS_BUCKET"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        print(f"[WARN] OSS 配置缺失，跳过上传: {', '.join(missing)}", file=sys.stderr)
        return False

    # 尝试使用 Python oss2 库
    try:
        import oss2
        auth = oss2.Auth(os.environ["OSS_ACCESS_KEY_ID"], os.environ["OSS_ACCESS_KEY_SECRET"])
        endpoint = os.environ["OSS_ENDPOINT"]
        # 如果 endpoint 没有 http(s):// 前缀，自动添加
        if not endpoint.startswith(("http://", "https://")):
            endpoint = f"https://{endpoint}"
        bucket = oss2.Bucket(auth, endpoint, os.environ["OSS_BUCKET"])

        file_size = os.path.getsize(archive_path)
        file_size_mb = round(file_size / (1024 * 1024), 1)
        print(f"[INFO] 上传到 OSS: {oss_key} ({file_size_mb} MB)")

        with open(archive_path, "rb") as f:
            bucket.put_object(oss_key, f)
        print(f"[OK] OSS 上传成功: {oss_key}")
        return True
    except ImportError:
        print("[WARN] oss2 库未安装，尝试使用 oss-helper.js", file=sys.stderr)
        return _upload_via_oss_helper(archive_path, oss_key)
    except OSError as e:
        print(f"[ERROR] OSS 上传失败: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

def _upload_via_oss_helper(archive_path: str, oss_key: str) -> bool:
    """通过 oss-helper.js 上传到 OSS。"""
    oss_helper = os.environ.get("BFDATA_OSS_HELPER", str(SKILL_ROOT.parent / "config" / "oss-helper.js"))
    if not Path(oss_helper).exists():
        print(f"[ERROR] OSS helper 不存在: {oss_helper}", file=sys.stderr)
        return False

    node = find_executable("node")
    if not node:
        print("[ERROR] Node.js 未安装，无法使用 OSS helper", file=sys.stderr)
        return False

    try:
        result = subprocess.run(
            [node, oss_helper, "upload", archive_path, oss_key],
            capture_output=True,
            text=True,
            timeout=600,
        )
        if result.returncode != 0:
            print(f"[ERROR] OSS helper 上传失败:\n{result.stderr}", file=sys.stderr)
            return False
        print(f"[OK] OSS helper 上传成功: {oss_key}")
        return True
    except (OSError, subprocess.TimeoutExpired) as e:
        print(f"[ERROR] OSS helper 异常: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return False

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    load_env()
    config = load_backup_config()

    # 确定压缩工具
    compressor = get_compressor()

    # 构建源路径列表
    sources = []
    # 1. 从配置文件读取
    cfg_sources = config.get("sources", [])
    sources.extend(cfg_sources)
    # 2. 从环境变量 BFDATA_SOURCES 读取（JSON 数组，逗号分隔字符串）
    env_sources = os.environ.get("BFDATA_SOURCES", "")
    if env_sources:
        try:
            sources.extend(json.loads(env_sources))
        except json.JSONDecodeError:
            sources.extend([s.strip() for s in env_sources.split(",")])

    if not sources:
        print("[ERROR] 没有配置任何备份源", file=sys.stderr)
        sys.exit(1)

    # 验证路径
    valid_sources = validate_paths(sources)
    if not valid_sources:
        print("[ERROR] 所有备份源路径均无效", file=sys.stderr)
        sys.exit(1)

    # 确定输出目录
    output_dir = os.environ.get("BFDATA_OUTPUT_DIR", str(SKILL_ROOT.parent / "backup"))

    # 生成时间戳 (UTC)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # 创建归档
    archive_path = create_archive(compressor, valid_sources, output_dir, timestamp)
    if not archive_path:
        print("[ERROR] 归档创建失败", file=sys.stderr)
        sys.exit(1)

    # 上传到 OSS
    oss_key_prefix = os.environ.get("BFDATA_OSS_KEY_PREFIX", "bfdata")
    oss_key = f"{oss_key_prefix}/bfdata-backup-{timestamp}.{'7z' if compressor == '7z' else 'tar.gz'}"
    upload_success = upload_to_oss(archive_path, oss_key)

    # 清理策略
    cleanup = os.environ.get("BFDATA_CLEANUP", "keep_on_upload_fail")
    if upload_success and cleanup == "remove_on_upload_success":
        print(f"[INFO] 清理本地归档: {archive_path}")
        os.remove(archive_path)
    elif not upload_success:
        print(f"[INFO] OSS 上传失败，保留本地归档: {archive_path}")

    print(f"[OK] 备份完成: {archive_path}")

if __name__ == "__main__":
    # Windows 控制台编码修复
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except AttributeError:
            pass  # stdout/stderr 被重定向到不支持 reconfigure 的对象
    main()
