#!/bin/bash
# 验证输出文件
# 该脚本验证处理流程的最终输出文件是否符合预期

set -e  # 遇到错误立即退出

if [ $# -ne 1 ]; then
    echo "用法: $0 <output_directory>"
    exit 1
fi

OUTPUT_DIR=$1

echo "正在验证输出文件: $OUTPUT_DIR"

# 检查输出目录是否存在
if [ ! -d "$OUTPUT_DIR" ]; then
    echo "错误: 输出目录不存在: $OUTPUT_DIR"
    exit 1
fi

# 检查是否存在markdown文件
MD_FILES=$(find "$OUTPUT_DIR" -name "*.md" -type f)

if [ -z "$MD_FILES" ]; then
    echo "错误: 在输出目录中未找到markdown文件"
    exit 1
else
    echo "找到markdown文件:"
    echo "$MD_FILES"
fi

# 检查每个markdown文件是否包含图表
CHART_COUNT=0
for md_file in $MD_FILES; do
    # 检查是否包含Mermaid代码块
    if grep -q "\`\`\`mermaid" "$md_file"; then
        MERMAID_BLOCKS=$(grep -c "\`\`\`mermaid" "$md_file")
        echo "文件 $md_file 包含 $MERMAID_BLOCKS 个Mermaid图表"
        CHART_COUNT=$((CHART_COUNT + MERMAID_BLOCKS))
    else
        echo "警告: 文件 $md_file 不包含Mermaid图表"
    fi

    # 验证markdown语法（简单检查）
    if [ "$(head -n 1 "$md_file" | grep -c "^# ")" -eq 0 ]; then
        echo "警告: 文件 $md_file 似乎不符合预期的markdown格式"
    fi
done

echo "总共找到 $CHART_COUNT 个图表"

# 检查是否有章节标题
TOTAL_CHAPTERS=0
for md_file in $MD_FILES; do
    # 计算二级标题的数量（通常代表章节）
    CHAPTERS=$(grep -c "^## " "$md_file")
    TOTAL_CHAPTERS=$((TOTAL_CHAPTERS + CHAPTERS))
done

echo "总共找到 $TOTAL_CHAPTERS 个章节标题"

if [ $TOTAL_CHAPTERS -gt 0 ] && [ $CHART_COUNT -gt 0 ]; then
    echo "输出验证成功：包含章节标题和图表"
else
    echo "警告: 输出可能不完整（章节数: $TOTAL_CHAPTERS, 图表数: $CHART_COUNT）"
fi

echo "输出验证完成"