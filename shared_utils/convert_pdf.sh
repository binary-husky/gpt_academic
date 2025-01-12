#!/bin/bash
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <path-to-pdf-file>"
    exit 1
fi

FILE_PATH=$(realpath "$1")

if [ ! -f "$FILE_PATH" ]; then
    echo "File not found: $FILE_PATH"
    exit 1
fi

conda activate mineru

if ! command -v magic-pdf &> /dev/null; then
    echo "magic-pdf could not be found in the current conda environment"
    exit 1
fi

magic-pdf pdf-command --pdf "$FILE_PATH" --inside_model true

if [ $? -eq 0 ]; then
    echo "PDF conversion successful"
else
    echo "PDF conversion failed"
    exit 1
fi
