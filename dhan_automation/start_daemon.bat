@echo off
title IMLT Live WS Daemon — shakhan32
color 0A
echo.
echo  ============================================
echo   IMLT LIVE WS DAEMON — DhanHQ WebSocket
echo   Run this at 09:00 AM before market opens
echo  ============================================
echo.
cd /d %~dp0
python live_ws_daemon.py
echo.
echo  Daemon stopped. Press any key to close.
pause
