---
name: mineru-install
description: Use this skill when the user wants to install, deploy, or set up MinerU 3.0 via Docker. Covers Dockerfile build, NVIDIA driver requirements, model download, network issues in China, and troubleshooting. This skill captures the complete installation experience including all pitfalls and workarounds.
---

# MinerU 3.0 Docker Installation Guide

## Prerequisites

### 1. NVIDIA Driver (Critical)

MinerU 3.0 requires **CUDA 12.9+**. Check your current version:

```bash
nvidia-smi
```

If CUDA version < 12.9, you MUST update the driver first.

**Driver Update Process**:
1. Download latest Game Ready Driver from TechPowerUp or NVIDIA:
   - Latest (as of 2026-04-25): **596.21 WHQL** (CUDA 13.2)
   - Download URL format: `https://us.download.nvidia.com/Windows/{version}/{version}-desktop-win10-win11-64bit-international-dch-whql.exe`
2. Install silently:
   ```powershell
   Start-Process -FilePath "596.21-desktop-win10-win11-64bit-international-dch-whql.exe" -ArgumentList '-s','-noreboot' -Wait -Verb RunAs
   ```
3. Verify: `nvidia-smi` should show Driver Version: 596.21+ and CUDA Version: 13.2

### 2. Docker Desktop

- Docker Desktop must be installed and running
- WSL2 backend recommended for Windows

### 3. Disk Space

- Base image: ~25GB
- Models: ~10GB
- Final image: ~35GB
- **Minimum free space required: 50GB**

## Step-by-Step Installation

### Step 1: Create Project Directory

```bash
mkdir -p mineru && cd mineru
mkdir -p data output
```

### Step 2: Download Official Files

Due to GitHub access restrictions in China, use proxy mirrors:

```bash
# Download Dockerfile (China version with mirrored registries)
curl -sL "https://ghproxy.net/https://raw.githubusercontent.com/opendatalab/MinerU/master/docker/china/Dockerfile" -o Dockerfile

# Download compose.yaml
curl -sL "https://ghproxy.net/https://raw.githubusercontent.com/opendatalab/MinerU/master/docker/compose.yaml" -o compose.yaml
```

**Alternative proxies** (if one fails, try another):
- `https://ghproxy.net/`
- `https://ghproxy.org/`
- `https://gh-proxy.com/`
- `https://mirror.ghproxy.com/`

### Step 3: Configure Docker Registry Mirrors

Edit `~/.docker/daemon.json` to add Chinese mirrors:

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://docker.aichenkang.com",
    "https://hub.rat.dev"
  ]
}
```

**Then restart Docker Desktop** (right-click tray icon -> Restart).

### Step 4: Build Docker Image

```bash
cd mineru
docker build -t mineru:3.0 -f Dockerfile .
```

**Build Process Breakdown**:
1. Pull base image `vllm/vllm-openai:v0.11.2` from daocloud mirror (~25GB)
2. Install system packages (fonts, libgl)
3. Install MinerU Python package from Aliyun PyPI mirror
4. Download models via ModelScope:
   - PDF-Extract-Kit-1.0 (layout, OCR, formula models)
   - MinerU2.5-Pro-2604-1.2B (VLM model, ~2.15GB)
5. Set offline environment variables

**Expected build time**: 30-45 minutes (depends on network speed)

### Step 5: Verify Installation

```bash
# Check image exists
docker images | grep mineru
# Expected: mineru:3.0 ~34.6GB

# Test GPU access
docker run --rm --gpus all --entrypoint "bash" mineru:3.0 -c "nvidia-smi | head -5"

# Test basic conversion
echo "test" > data/test.txt  # Replace with actual PDF
docker run --rm --gpus all --shm-size 32g --ipc=host --entrypoint "bash" \
  -v "D:/path/to/mineru/data:/input" \
  -v "D:/path/to/mineru/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input/test.pdf -o /output -l ch"
```

## Known Issues and Workarounds

### Issue 1: GitHub Connection Timeout/Reset

**Symptoms**:
```
fatal: unable to access 'https://github.com/...': Connection timed out
curl: (35) OpenSSL SSL_connect: Connection was reset
```

**Solutions**:
1. Use GitHub proxy mirrors (see Step 2)
2. Try multiple proxy services
3. If all fail, manually create Dockerfile (see below)

### Issue 2: Docker Hub Pull Timeout

**Symptoms**:
```
Error response from daemon: Get "https://registry-1.docker.io/v2/": context deadline exceeded
```

**Solutions**:
1. Add registry mirrors to daemon.json (see Step 3)
2. Restart Docker Desktop after adding mirrors
3. Try direct pull: `docker pull docker.m.daocloud.io/vllm/vllm-openai:v0.11.2`

### Issue 3: vllm/vllm-openai Image Not Found

**Symptoms**:
```
manifest for docker.1ms.run/vllm/vllm-openai:v0.11.2 not found
官方仓库已删除该镜像
```

**Root cause**: The official vllm-openai repository was removed from Docker Hub.

**Solution**: Use the China Dockerfile which pulls from `docker.m.daocloud.io` mirror instead of Docker Hub directly.

### Issue 4: CUDA Version Mismatch

**Symptoms**:
```
nvidia-container-cli: requirement error: unsatisfied condition: cuda>=12.9
```

**Root cause**: NVIDIA driver too old (560.94 only supports CUDA 12.6).

**Solution**: Update driver to 570+ (see Prerequisites section 1).

### Issue 5: Model Download Fails (HuggingFace Access)

**Symptoms**:
```
huggingface_hub.errors.LocalEntryNotFoundError
Failed to resolve 'huggingface.co'
```

**Root cause**: Container cannot access HuggingFace from inside Docker.

**Solution**: The Dockerfile already sets `HF_ENDPOINT=https://hf-mirror.com` and downloads models during build. If rebuilding, ensure:
```dockerfile
RUN export HF_ENDPOINT=https://hf-mirror.com && /bin/bash -c "mineru-models-download -s modelscope -m all"
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV MINERU_MODEL_SOURCE=local
```

### Issue 6: Container Path Not Found

**Symptoms**:
```
Error: Invalid value for '-p' / '--path': Path '/input/test.pdf' does not exist
```

**Root cause**: Windows path format in volume mount.

**Solution**: Use Windows-style paths with quotes:
```bash
# WRONG
-v /d/mydoc/data:/input

# CORRECT
-v "D:/mydoc/data:/input"
```

### Issue 7: Docker Build "Dockerfile not found"

**Symptoms**:
```
ERROR: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory
```

**Root cause**: Working directory mismatch.

**Solution**: Run build from the directory containing Dockerfile:
```bash
cd /path/to/mineru
docker build -t mineru:3.0 -f Dockerfile .
```

### Issue 8: WSL Pin Memory Warning

**Symptoms**:
```
WARNING: Using 'pin_memory=False' as WSL is detected. This may slow down the performance.
```

**Impact**: Minor performance degradation (~10-15% slower).

**Solution**: Acceptable for most use cases. No fix needed.

## Manual Dockerfile (If Download Fails)

If you cannot download the official Dockerfile, create this file manually:

```dockerfile
# Use DaoCloud mirrored vllm image for China region
FROM docker.m.daocloud.io/vllm/vllm-openai:v0.11.2

# Install libgl for opencv support & Noto fonts for Chinese characters
RUN apt-get update && \
    apt-get install -y \
        fonts-noto-core \
        fonts-noto-cjk \
        fontconfig \
        libgl1 && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install mineru latest
RUN python3 -m pip install -U 'mineru[core]>=3.0.0' -i https://mirrors.aliyun.com/pypi/simple --break-system-packages && \
    python3 -m pip cache purge

# Download models and update the configuration file
RUN export HF_ENDPOINT=https://hf-mirror.com && /bin/bash -c "mineru-models-download -s modelscope -m all"

# Set offline mode environment variables
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV MINERU_MODEL_SOURCE=local

# Set the entry point
ENTRYPOINT ["/bin/bash", "-c", "export MINERU_MODEL_SOURCE=local && exec \"$@\"", "--"]
```

## Post-Installation Setup

### Create Working Directory Structure

```bash
mkdir -p mineru/{data,output}
```

### Test with Sample PDF

1. Copy a test PDF to `mineru/data/`
2. Run conversion:
```bash
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/mydoc/workskill/mineru/data:/input" \
  -v "D:/mydoc/workskill/mineru/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input/test.pdf -o /output -l ch"
```

3. Check output in `mineru/output/`

## Version Information

| Component | Version | Notes |
|-----------|---------|-------|
| MinerU | 3.0.0+ | `mineru[core]>=3.0.0` |
| VLM Model | MinerU2.5-Pro-2604-1.2B | ~2.15GB |
| Pipeline Models | PDF-Extract-Kit-1.0 | Layout, OCR, Formula |
| vLLM | 0.11.2 | Inference engine |
| CUDA | 12.9+ required | Tested with 13.2 |
| NVIDIA Driver | 570+ required | Tested with 596.21 |
| Base Image | vllm/vllm-openai:v0.11.2 | From daocloud mirror |

## Quick Installation Checklist

- [ ] NVIDIA driver 570+ (`nvidia-smi`)
- [ ] Docker Desktop running
- [ ] 50GB+ free disk space
- [ ] Registry mirrors configured in daemon.json
- [ ] Dockerfile downloaded (via proxy if needed)
- [ ] `docker build -t mineru:3.0 -f Dockerfile .` completed
- [ ] GPU access verified in container
- [ ] Test PDF conversion successful

## Maintenance

### Rebuild Image (When MinerU Updates)

```bash
cd mineru
# Update Dockerfile if new version available
docker build -t mineru:3.0 -f Dockerfile .
```

### Clean Up Old Images

```bash
# Remove unused images
docker image prune -a

# Remove specific old image
docker rmi mineru:old_tag
```

### Update NVIDIA Driver

1. Check for new driver on TechPowerUp or NVIDIA
2. Download and install silently (see Prerequisites)
3. Restart Docker Desktop
4. Verify: `nvidia-smi`
