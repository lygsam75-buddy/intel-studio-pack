@echo off
chcp 65001 >nul
title ComfyUI Intel Arc XPU (B580 12G profile)
setlocal

rem ============================================================
rem  B580 12G replacement launcher for ComfyUI Intel Arc Studio Pack
rem  Drop this file into the pack root (the folder that contains ComfyUI\).
rem  Differences vs the stock launcher (measured on B580 11.6 GiB,
rem  2026-11-23, see README_B580.md):
rem    1. --disable-pinned-memory  REAL switch. The stock OMNIXPU_PIN_MEMORY
rem       env var is consumed by NOTHING in the engine (verified by grep +
rem       runtime probe). Without this flag the cudaHostRegister crash path
rem       stays open (upstream #16804 / #16846).
rem    2. --reserve-vram 2  (stock 5 is a B70 value; on 11.6 GiB it costs
rem       ~20% end-to-end. 4 is the fallback if the OS fights for VRAM.)
rem    3. --enable-dynamic-vram  mandatory here: without it every prompt
rem       reloads the whole model chain (+74% steady state).
rem  Keep this file pure ASCII + CRLF.
rem ============================================================

set "ROOT=%~dp0"
set "PY=%ROOT%python_embeded\python.exe"
set "COMFY=%ROOT%ComfyUI"

if not exist "%PY%" (
    echo [X] python_embeded\python.exe not found - please unzip the full pack
    pause
    exit /b 1
)

rem ---- XPU environment ----
set OMNIXPU_ENABLE=1
rem  OMNIXPU_PIN_MEMORY kept for compatibility only - it is a no-op.
rem  The effective gate is --disable-pinned-memory below.
set OMNIXPU_PIN_MEMORY=0
set PYTHONIOENCODING=utf-8

rem ---- B580 12G profile (measured 2026-11-23) ----
rem  --reserve-vram 2         : 2G reserved for OS/display on an 11.6G card
rem  --cache-classic          : stop reloading the text encoder each round
rem  --disable-pinned-memory  : closes the cudaHostRegister crash path
rem  --enable-dynamic-vram    : streaming load; without it every prompt
rem                              reloads all models (loads=4 per run, +74%)
rem  fallback if unstable     : raise --reserve-vram to 4
rem  fallback on DEVICE_LOST  : remove --enable-dynamic-vram (slow but safe)

echo ============================================================
echo  ComfyUI Intel Arc XPU - B580 12G profile
echo  python : %PY%
echo  url    : http://127.0.0.1:8188
echo  args   : --reserve-vram 2 --cache-classic --disable-pinned-memory --enable-dynamic-vram
echo ============================================================
echo.

cd /d "%COMFY%"
"%PY%" main.py --listen 127.0.0.1 --port 8188 --reserve-vram 2 --cache-classic --disable-pinned-memory --enable-dynamic-vram

echo.
echo [exited] press any key to close
pause >nul
