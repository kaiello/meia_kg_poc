# ==============================================================================
# MEIA Knowledge Graph POC - Automated Windows Setup Script
# Usage: powershell -ExecutionPolicy Bypass -File setup_windows.ps1
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "    MEIA Federated Tri-Graph POC - Automated Windows Environment Setup    " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Check Python installation
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = & python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python is not found in PATH." -ForegroundColor Red
    Write-Host "  Please install Python 3.10, 3.11, or 3.12 from python.org and ensure 'Add Python to PATH' is checked." -ForegroundColor Red
    exit 1
}

# 2. Virtual Environment Setup
Write-Host "[2/5] Configuring virtual environment (.venv)..." -ForegroundColor Yellow
if (-not (Test-Path ".venv")) {
    Write-Host "  Creating new virtual environment in .venv..." -ForegroundColor Gray
    python -m venv .venv
} else {
    Write-Host "  Existing .venv directory detected." -ForegroundColor Gray
}

$venvPython = ".\.venv\Scripts\python.exe"
$venvPip = ".\.venv\Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    Write-Host "  Fallback to global python executable..." -ForegroundColor Yellow
    $venvPython = "python"
    $venvPip = "pip"
}

# 3. Install Python Dependencies
Write-Host "[3/5] Installing/verifying required Python packages..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip --quiet
& $venvPip install -r requirements.txt --quiet
Write-Host "  Python dependencies successfully installed and verified." -ForegroundColor Green

# 4. Check & Pre-Warm Embedding Model
Write-Host "[4/5] Checking embedding model cache (BAAI/bge-large-en-v1.5)..." -ForegroundColor Yellow
$modelWarmCode = @"
import os
os.environ['HF_HUB_OFFLINE'] = '0'
try:
    from sentence_transformers import SentenceTransformer
    print('  Loading BAAI/bge-large-en-v1.5...')
    model = SentenceTransformer('BAAI/bge-large-en-v1.5')
    print('  [SUCCESS] Embedding model is cached and ready.')
except Exception as e:
    print(f'  [WARNING] Embedding model check encountered: {e}')
"@
& $venvPython -c $modelWarmCode

# 5. Check Local Ollama Engine (Optional / Recommended)
Write-Host "[5/5] Checking Ollama service..." -ForegroundColor Yellow
try {
    $ollamaCheck = & ollama --version 2>&1
    Write-Host "  Found Ollama: $ollamaCheck" -ForegroundColor Green
    
    # Check if recommended models exist
    $ollamaList = & ollama list 2>&1
    $modelsToCheck = @("qwen3-vl:8b-instruct", "gemma4:e4b", "hermes3:8b")
    $missingModels = @()
    foreach ($m in $modelsToCheck) {
        if ($ollamaList -notmatch $m) {
            $missingModels += $m
        }
    }
    
    if ($missingModels.Count -gt 0) {
        Write-Host "  Optional open-weight models not yet pulled: $($missingModels -join ', ')" -ForegroundColor Cyan
        Write-Host "  You can pull them anytime using:" -ForegroundColor Gray
        foreach ($m in $missingModels) {
            Write-Host "    ollama pull $m" -ForegroundColor Gray
        }
    } else {
        Write-Host "  All recommended open-weight models are installed!" -ForegroundColor Green
    }
} catch {
    Write-Host "  Ollama not detected in PATH. (The system will run in deterministic tri-graph mode or use cloud API keys)." -ForegroundColor Gray
    Write-Host "  To enable local LLM synthesis, install Ollama from https://ollama.com" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================================================" -ForegroundColor Green
Write-Host "  Setup Complete! MEIA Knowledge Graph POC is ready on this machine.    " -ForegroundColor Green
Write-Host "========================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "To start the interactive Web Visual Explorer:" -ForegroundColor Cyan
Write-Host "  & $venvPython -m src.web" -ForegroundColor White
Write-Host "Then open: http://127.0.0.1:8000" -ForegroundColor White
Write-Host ""
Write-Host "To run the automated verification test suite:" -ForegroundColor Cyan
Write-Host "  & $venvPython -m pytest tests/test_web_and_benchmark.py" -ForegroundColor White
Write-Host ""
