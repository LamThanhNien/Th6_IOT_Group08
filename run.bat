@echo off
chcp 65001 >nul
title Smart Classroom AIoT - System Runner
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
