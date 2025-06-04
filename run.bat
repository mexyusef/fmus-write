@echo off
set PROJECT_DIR=%~dp0
set PYTHONPATH=%PROJECT_DIR%;%PYTHONPATH%
python -m writegui.main %*
