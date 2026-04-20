#!/bin/bash

# 启动后端（conda 环境）
echo "=== 启动后端 Python ==="
cd backend
deactivate
conda activate lty
python main.py &

# 启动前端
echo "=== 启动前端 npm ==="
cd ../frontend
npm run serve &

wait