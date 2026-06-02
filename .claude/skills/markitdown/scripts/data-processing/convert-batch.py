"""
Batch document-to-Markdown conversion using markitdown Docker container.

Usage:
    python convert-batch.py <source_directory>

Environment Variables:
    MARKITDOWN_CONTAINER  - Container name (default: markitdown-convert)
    MARKITDOWN_IMAGE      - Docker image (default: markitdown-mcp:latest)
    CONVERSION_TIMEOUT    - Per-file timeout in seconds (default: 120)
    MARKITDOWN_PORT       - HTTP port for container (default: 8765)

Output:
    For each document.pdf -> document.pdf.md (adjacent to original)
    Archive files (zip/rar) -> extracted and converted internally
"""

import os
import sys
import re
import subprocess
import shutil
import zipfile
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# Configuration from environment (no hardcoding)
CONTAINER = os.environ.get('MARKITDOWN_CONTAINER', 'markitdown-convert')
IMAGE = os.environ.get('MARKITDOWN_IMAGE', 'markitdown-mcp:latest')
TIMEOUT = int(os.environ.get('CONVERSION_TIMEOUT', '120'))
PORT = os.environ.get('MARKITDOWN_PORT', '8765')

CONVERTIBLE = {'pdf', 'docx', 'pptx', 'xlsx', 'doc', 'ppt', 'xls', 'jpg', 'png', 'jpeg'}
ARCHIVE_TYPES = {'zip', 'rar'}
CONTAINER_PREFIX = '/workdir'


def docker_exec(cmd, timeout_override=None):
    """Execute command inside Docker container with proper encoding."""
    t = timeout_override or TIMEOUT
    try:
        r = subprocess.run(
            ['docker', 'exec', CONTAINER, 'sh', '-c', cmd],
            capture_output=True, text=True, timeout=t,
            encoding='utf-8', errors='replace'
        )
        return r
    except subprocess.TimeoutExpired:
        return None


def convert_file_by_path(project_name, relative_path):
    """Convert a file using its relative path within the project directory."""
    safe_project = project_name.replace("'", "'\\''")
    safe_path = relative_path.replace("'", "'\\''")
    # Use forward slashes for container path
    container_path = safe_path.replace('\\', '/')
    cmd = f'markitdown "/workdir/{safe_project}/{container_path}" 2>/dev/null'

    r = docker_exec(cmd)
    if r is None:
        return None, 'timeout'
    if r.stdout and len(r.stdout.strip()) > 50:
        return r.stdout, None
    return None, 'empty_output'


def extract_and_convert_archive_with_path(project_name, archive_rel_path, project_path):
    """Extract archive at given relative path and convert all internal documents."""
    safe_project = project_name.replace("'", "'\\''")
    safe_archive = archive_rel_path.replace("'", "'\\''")
    container_archive = safe_archive.replace('\\', '/')

    archive_dir = os.path.dirname(archive_rel_path)
    archive_name = os.path.basename(archive_rel_path)
    safe_name = archive_name.replace("'", "'\\''")

    # Build cd path - handle subdirectories
    if archive_dir:
        safe_dir = archive_dir.replace("'", "'\\''").replace('\\', '/')
        cd_cmd = f'cd "/workdir/{safe_project}/{safe_dir}"'
    else:
        cd_cmd = f'cd "/workdir/{safe_project}"'

    cmd = (
        f'{cd_cmd} && '
        f'rm -rf "{safe_name}_extracted" && '
        f'mkdir -p "{safe_name}_extracted" && '
        f'cd "{safe_name}_extracted" && '
        f'unzip -o "../{safe_name}" 2>/dev/null || '
        f'7z x "../{safe_name}" -y 2>/dev/null; '
        f'count=0; '
        f'for f in $(find . -type f); do '
        f'ext="${{f##*.}}"; '
        f'case "$ext" in '
        f'pdf|docx|pptx|xlsx|doc|xls|jpg|png|jpeg|ppt) '
        f'result=$(markitdown "$f" 2>/dev/null); '
        f'if [ -n "$result" ] && [ $(echo "$result" | wc -c) -gt 50 ]; then '
        f'echo "$result" > "${{f}}.md"; '
        f'count=$((count+1)); '
        f'fi ;; '
        f'esac; '
        f'done; '
        f'echo "converted: $count"'
    )

    r = docker_exec(cmd, timeout_override=300)
    if r and r.stdout:
        return r.stdout.strip()
    return 'conversion failed'


def convert_single_file(project_name, filename):
    """Convert a single file using markitdown CLI inside container."""
    return convert_file_by_path(project_name, filename)


def extract_and_convert_archive(source_dir, project_name, archive_name):
    """Extract archive in container and convert all internal documents."""
    safe_project = project_name.replace("'", "'\\''")
    safe_file = archive_name.replace("'", "'\\''")

    cmd = (
        f'cd "/workdir/{safe_project}" && '
        f'rm -rf "{safe_file}_extracted" && '
        f'mkdir -p "{safe_file}_extracted" && '
        f'cd "{safe_file}_extracted" && '
        f'unzip -o "../{safe_file}" 2>/dev/null || '
        f'7z x "../{safe_file}" -y 2>/dev/null; '
        f'count=0; '
        f'for f in $(find . -type f); do '
        f'ext="${{f##*.}}"; '
        f'case "$ext" in '
        f'pdf|docx|pptx|xlsx|doc|xls|jpg|png|jpeg|ppt) '
        f'result=$(markitdown "$f" 2>/dev/null); '
        f'if [ -n "$result" ] && [ $(echo "$result" | wc -c) -gt 50 ]; then '
        f'echo "$result" > "${{f}}.md"; '
        f'count=$((count+1)); '
        f'fi ;; '
        f'esac; '
        f'done; '
        f'echo "converted: $count"'
    )

    r = docker_exec(cmd, timeout_override=300)
    if r and r.stdout:
        return r.stdout.strip()
    return 'conversion failed'


def process_directory(source_dir):
    """Process all files in source directory tree, recursively scanning subdirectories."""
    converted = 0
    failed = 0
    skipped = 0
    archives = 0
    failures = []

    # Check if source_dir is a leaf directory (files directly in it)
    # or a parent of project directories
    has_subdirs = any(
        os.path.isdir(os.path.join(source_dir, d))
        for d in os.listdir(source_dir)
    )

    if not has_subdirs:
        # Flat directory - process files directly
        project_dirs = [(os.path.basename(source_dir), source_dir)]
    else:
        # Parent directory with project subdirectories
        project_dirs = [
            (d, os.path.join(source_dir, d))
            for d in sorted(os.listdir(source_dir))
            if os.path.isdir(os.path.join(source_dir, d))
        ]

    for project_name, project_path in project_dirs:
        print(f'\n[{project_name}]')

        # Use os.walk to recursively find all files
        for root, dirs, files in os.walk(project_path):
            # Skip _extracted directories (already handled or empty)
            dirs[:] = [d for d in dirs if not d.endswith('_extracted')]

            for filename in sorted(files):
                filepath = os.path.join(root, filename)
                if not os.path.isfile(filepath):
                    continue

                ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

                # Handle archives
                if ext in ARCHIVE_TYPES:
                    archives += 1
                    # Compute relative path from project_path for container
                    rel_dir = os.path.relpath(root, project_path)
                    if rel_dir == '.':
                        archive_rel = filename
                    else:
                        archive_rel = os.path.join(rel_dir, filename)
                    result = extract_and_convert_archive_with_path(project_name, archive_rel, project_path)
                    print(f'  Archive: {archive_rel} -> {result}')
                    continue

                # Skip non-convertible types
                if ext not in CONVERTIBLE:
                    skipped += 1
                    continue

                # Check if already converted
                md_path = filepath + '.md'
                if os.path.exists(md_path) and os.path.getsize(md_path) > 0:
                    skipped += 1
                    continue

                # Compute relative path from project_path for container command
                rel_dir = os.path.relpath(root, project_path)
                if rel_dir == '.':
                    container_path = filename
                else:
                    container_path = os.path.join(rel_dir, filename)

                result, error = convert_file_by_path(project_name, container_path)
                if result:
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(result)
                    converted += 1
                    rel_display = container_path.replace('\\', '/')
                    print(f'  OK: {rel_display}')
                else:
                    failed += 1
                    reason = error if error else 'unknown'
                    failures.append(f'{project_name}/{container_path} ({reason})')
                    rel_display = container_path.replace('\\', '/')
                    print(f'  FAIL: {rel_display} ({reason})')

    # Write failure report
    report_path = os.path.join(source_dir, 'conversion-report.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f'=== Conversion Report ===\n')
        f.write(f'Success: {converted}\n')
        f.write(f'Failed: {failed}\n')
        f.write(f'Skipped: {skipped}\n')
        f.write(f'Archives: {archives}\n')
        if failures:
            f.write(f'\n=== Failed Files ===\n')
            for fail in failures:
                f.write(f'  {fail}\n')

    print(f'\n=== Conversion Complete ===')
    print(f'Success: {converted}')
    print(f'Failed: {failed}')
    print(f'Skipped: {skipped}')
    print(f'Archives: {archives}')
    print(f'Report: {report_path}')

    return converted, failed, skipped, archives


def ensure_container_running(source_dir):
    """Ensure the markitdown Docker container is running with correct volume mount."""
    # Check if container is running
    r = subprocess.run(
        ['docker', 'ps', '--filter', f'name={CONTAINER}', '--format', '{{.Names}}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )

    if CONTAINER in r.stdout:
        print(f'Container {CONTAINER} is running.')
        return True

    # Clean up stopped container
    subprocess.run(['docker', 'rm', '-f', CONTAINER], capture_output=True)

    # Resolve source dir to Linux-style path for Docker
    abs_source = os.path.abspath(source_dir)
    # Convert Windows path to Docker path
    if sys.platform == 'win32':
        # D:\path -> /d/path
        docker_path = '/' + abs_source[0].lower() + abs_source[2:].replace('\\', '/')
    else:
        docker_path = abs_source

    print(f'Starting container: {CONTAINER}')
    print(f'Mount: {docker_path} -> {CONTAINER_PREFIX}')

    r = subprocess.run(
        ['docker', 'run', '-d', '-p', f'{PORT}:8765',
         '-v', f'{docker_path}:{CONTAINER_PREFIX}',
         '--name', CONTAINER, IMAGE],
        capture_output=True, text=True, encoding='utf-8', errors='replace'
    )

    if r.returncode != 0:
        print(f'ERROR: Failed to start container: {r.stderr}')
        return False

    # Wait for container to be ready
    import time
    time.sleep(5)

    # Verify
    r = docker_exec('echo ready')
    if r and 'ready' in r.stdout:
        print('Container is ready.')
        return True
    else:
        print('WARNING: Container started but may not be ready.')
        return True


def main():
    if len(sys.argv) < 2:
        print('Usage: python convert-batch.py <source_directory>')
        print('Environment variables:')
        print('  MARKITDOWN_CONTAINER  - Container name (default: markitdown-convert)')
        print('  MARKITDOWN_IMAGE      - Docker image (default: markitdown-mcp:latest)')
        print('  CONVERSION_TIMEOUT    - Per-file timeout in seconds (default: 120)')
        sys.exit(1)

    source_dir = sys.argv[1]
    if not os.path.isdir(source_dir):
        print(f'ERROR: Source directory does not exist: {source_dir}')
        sys.exit(1)

    print('=' * 60)
    print('markitdown Batch Conversion')
    print('=' * 60)
    print(f'Source: {source_dir}')
    print(f'Container: {CONTAINER}')
    print(f'Image: {IMAGE}')
    print(f'Timeout: {TIMEOUT}s')

    if not ensure_container_running(source_dir):
        print('ERROR: Cannot start Docker container.')
        sys.exit(1)

    process_directory(source_dir)


if __name__ == '__main__':
    main()
