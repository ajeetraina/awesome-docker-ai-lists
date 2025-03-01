#!/bin/bash

# This script combines and runs the GitHub crawler

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set"
    echo "Please set it with: export GITHUB_TOKEN=your_github_token"
    exit 1
fi

# Combine the crawler script parts
cat github_crawler.py github_crawler_part2.py > crawler_combined.py

# Parse arguments
DRY_RUN=""
DAYS=7
LIMIT=20

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN="--dry-run"
            ;;
        --days)
            shift
            DAYS="$1"
            ;;
        --limit)
            shift
            LIMIT="$1"
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: ./run_crawler.sh [--dry-run] [--days N] [--limit N]"
            exit 1
            ;;
    esac
    shift
done

# Run the crawler
python crawler_combined.py --days "$DAYS" --limit "$LIMIT" $DRY_RUN

# Clean up
rm crawler_combined.py
