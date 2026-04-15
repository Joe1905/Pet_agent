@echo off
title Claude Code Loader - MiniMax


set PS_EXE=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe


if not exist "%PS_EXE%" (
    echo [错误] 找不到 PowerShell，请检查路径: %PS_EXE%
    pause
    exit /b
)

"%PS_EXE%" -NoExit -Command ^
  "$env:ANTHROPIC_BASE_URL='https://api.ppio.com/anthropic';" ^
  "$env:ANTHROPIC_API_KEY='sk_983TfnF4AtX1UcpbID3jacNjaNB-8T6ze0ogSZvZ22E';" ^
  "$env:ANTHROPIC_AUTH_TOKEN='sk_983TfnF4AtX1UcpbID3jacNjaNB-8T6ze0ogSZvZ22E';" ^
  "$env:ANTHROPIC_MODEL='minimax/minimax-m2.7-highspeed';" ^
  "$env:ANTHROPIC_SMALL_FAST_MODEL='minimax/minimax-m2.7-highspeed';" ^
  "Write-Host '--------------------------------------------------' -ForegroundColor Cyan;" ^
  "Write-Host '✅ 环境变量载入成功 (PPIO - MiniMax)' -ForegroundColor Green;" ^
  "Write-Host '🚀 正在启动 Claude Code...' -ForegroundColor Yellow;" ^
  "Write-Host '--------------------------------------------------' -ForegroundColor Cyan;" ^
  "claude"

pause