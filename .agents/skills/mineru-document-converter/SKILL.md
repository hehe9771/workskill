---
name: mineru-document-converter
description: Use this skill when the user wants to convert documents (PDF, images, scanned documents) to Markdown format using MinerU 3.0 Docker deployment. Supports single file and batch conversion. Covers PDF to MD, image to MD, OCR extraction, table recognition, and formula parsing.
---

# MinerU 3.0 Document to Markdown Conversion

## Overview

MinerU 3.0 is a high-performance document parsing tool deployed via Docker, supporting:
- **PDF to Markdown**: Text, tables, formulas, images extraction
- **OCR Support**: Scanned documents, image-based PDFs
- **VLM Model**: Uses MinerU2.5-Pro-1.2B for hybrid processing
- **GPU Acceleration**: CUDA 12.9+ required (tested with CUDA 13.2)

## Environment Check

Before using, verify the setup:

```bash
# Check NVIDIA driver (must be 570+ for CUDA 12.9+)
nvidia-smi

# Check MinerU Docker image exists
docker images | grep mineru

# Expected: mineru:3.0 (~34.6GB)
```

## Directory Structure

```
mineru/
├── Dockerfile          # Official Docker build file
├── compose.yaml        # Docker Compose configuration
├── data/               # Input files directory
├── output/             # Output results directory
└── models_tmp/         # Cached models (optional)
```

## Single File Conversion

### Basic Usage

```bash
# Convert PDF to Markdown
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/path/to/input:/input" \
  -v "D:/path/to/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input/file.pdf -o /output -l ch"
```

### Parameters Explained

| Parameter | Description | Values |
|-----------|-------------|--------|
| `-p, --path` | Input file or directory path | Required |
| `-o, --output` | Output directory | Required |
| `-l, --lang` | Document language | `ch` (Chinese), `en` (English), `ch_server`, `ch_lite`, etc. |
| `-m, --method` | Parsing method | `auto` (default), `txt`, `ocr` |
| `-b, --backend` | Processing backend | `pipeline`, `vlm-transformers`, `vlm-sglang-engine`, `vlm-sglang-client` |
| `-f, --formula` | Enable formula parsing | `true` (default), `false` |
| `-t, --table` | Enable table parsing | `true` (default), `false` |
| `-s, --start` | Starting page (0-indexed) | Integer |
| `-e, --end` | Ending page (0-indexed) | Integer |

### Example: Chinese Document with OCR

```bash
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/mydoc/workskill/mineru/data:/input" \
  -v "D:/mydoc/workskill/mineru/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input/document.pdf -o /output -l ch -m ocr"
```

### Example: English Academic Paper

```bash
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/papers:/input" \
  -v "D:/papers/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input/paper.pdf -o /output -l en -f true -t true"
```

### Example: Specific Page Range

```bash
# Convert pages 5-20 (0-indexed, so pages 6-21)
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/book:/input" \
  -v "D:/book/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input/book.pdf -o /output -l ch -s 4 -e 19"
```

## Batch Conversion

### Convert All Files in Directory

```bash
# Place all PDFs in the input directory
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/batch/input:/input" \
  -v "D:/batch/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input -o /output -l ch"
```

### Batch with Mixed Languages

```bash
# Process directory with mixed Chinese and English documents
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/documents:/input" \
  -v "D:/documents/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input -o /output"  # Auto-detect language
```

### Batch Image Files (JPG/PNG)

```bash
# Convert image files to Markdown
docker run --rm \
  --gpus all \
  --shm-size 32g \
  --ipc=host \
  --entrypoint "bash" \
  -v "D:/images:/input" \
  -v "D:/images/output:/output" \
  mineru:3.0 \
  -c "mineru -p /input -o /output -l ch -m ocr"
```

## Output Structure

After conversion, output directory contains:

```
output/
└── filename/
    └── hybrid_auto/        # or auto/ for pipeline backend
        ├── filename.md             # Main Markdown output
        ├── filename_content_list.json    # Content structure
        ├── filename_content_list_v2.json # Enhanced content list
        ├── filename_layout.pdf         # Layout visualization
        ├── filename_middle.json        # Intermediate results
        ├── filename_model.json         # Model output details
        ├── filename_origin.pdf         # Original PDF copy
        └── images/                     # Extracted images
            ├── hash1.jpg
            ├── hash2.jpg
            └── ...
```

## Supported Input Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based and scanned |
| Images | `.png`, `.jpg`, `.jpeg` | Single or multiple |
| Scanned Documents | Any image-based PDF | Use `-m ocr` |

## Performance Notes

- **Cold Start**: First run takes ~60 seconds for model loading
- **Processing Speed**: ~5-6 seconds per page (4060 Ti GPU)
- **Memory Usage**: ~2.2GB VRAM for 1.2B model
- **Concurrent Processing**: Supports window-based batch processing

## Troubleshooting

### CUDA Version Mismatch

```
Error: cuda>=12.9, please update your driver
```

**Solution**: Update NVIDIA driver to 570+ (current: 596.21 with CUDA 13.2)

### Path Not Found in Container

```
Error: Path '/input/file.pdf' does not exist
```

**Solution**: Use Windows-style path in volume mount:
```bash
-v "D:/path/to/files:/input"  # Not -v /d/path/to/files:/input
```

### Out of Memory

```
Error: CUDA out of memory
```

**Solution**: Reduce batch size or add GPU memory limit:
```bash
# In compose.yaml, add:
# --gpu-memory-utilization 0.5
```

### Model Download Issues

If models need to be re-downloaded (network issues):
```bash
# Models are embedded in the image
# Verify with:
docker run --rm --entrypoint "bash" mineru:3.0 -c "ls /root/.cache/modelscope/hub/models/OpenDataLab/"
```

## Docker Compose Services

For persistent services (API, WebUI, Router):

```bash
# Start API service
docker compose -f compose.yaml --profile api up -d

# Start Gradio WebUI
docker compose -f compose.yaml --profile gradio up -d

# Start OpenAI-compatible server
docker compose -f compose.yaml --profile openai-server up -d

# Start Router (aggregates workers)
docker compose -f compose.yaml --profile router up -d

# Stop all services
docker compose -f compose.yaml down
```

## Quick Reference Commands

| Task | Command |
|------|---------|
| Single PDF | `mineru -p /input/file.pdf -o /output -l ch` |
| Directory batch | `mineru -p /input -o /output -l ch` |
| OCR mode | `mineru -p /input -o /output -l ch -m ocr` |
| Page range | `mineru -p /input -o /output -l ch -s 0 -e 9` |
| No formulas | `mineru -p /input -o /output -l ch -f false` |
| No tables | `mineru -p /input -o /output -l ch -t false` |
| English docs | `mineru -p /input -o /output -l en` |
