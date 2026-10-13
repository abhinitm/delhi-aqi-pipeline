#!/bin/bash
# Runs the whole pipeline once: load data, then check it.

cd /Users/abhinitmehndiratta/projects/delhi-aqi-pipeline || exit 1

echo "===== Run started: $(date) ====="
/usr/bin/python3 src/load_aqi.py
/usr/bin/python3 src/check_quality.py
echo "===== Run finished: $(date) ====="
echo ""