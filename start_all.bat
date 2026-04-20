@echo off
chcp 65001 > nul
echo ========================================
echo 正在启动后端服务（Conda 虚拟环境）
echo ========================================
start "后端服务" cmd /k "cd /d %~dp0backend && deactivate && conda activate lty && python main.py"

timeout /t 2 /nobreak > nul

echo ========================================
echo 正在启动前端服务
echo ========================================
start "前端服务" cmd /k "cd /d %~dp0frontend && npm run serve"


:: 等待前端服务启动完成（可根据你电脑速度调整秒数）
timeout /t 8 /nobreak > nul

echo ========================================
echo 前后端服务已全部启动！
echo ========================================
echo 正在自动打开浏览器：http://localhost:8080
start http://localhost:8080
pause