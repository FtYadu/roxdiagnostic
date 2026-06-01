# ROX 01 Diagnostic Tool - Windows Setup Script
# Run as Administrator

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ROX 01 DIAGNOSTIC TOOL - WINDOWS SETUP" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[*] Checking Python installation..." -ForegroundColor Yellow
if (!(python --version 2>&1 | Select-String "3.")) {
    Write-Host "[!] Python 3.9+ not found. Please install from https://www.python.org/" -ForegroundColor Red
    exit 1
}
Write-Host "[+] Python $(python --version) found" -ForegroundColor Green

# Install pip packages
Write-Host "[*] Installing Python dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install python-can==4.2.0 pyserial==3.5 fastapi==0.104.0 pydantic==2.4.0 click==8.1.7 requests==2.31.0 pyyaml==6.0 pytest==7.4.0
Write-Host "[+] Python dependencies installed" -ForegroundColor Green

# Create directories
Write-Host "[*] Creating project directories..." -ForegroundColor Yellow
$dirs = @(
    "firmware/extraction",
    "firmware/samples",
    "analysis/output",
    "testing/logs",
    "docs/images",
    "build/logs"
)
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}
Write-Host "[+] Directories created" -ForegroundColor Green

# Create configuration file
Write-Host "[*] Creating configuration file..." -ForegroundColor Yellow
$config = @{
    "project" = "rox-01-diagnostic"
    "can_interface" = "can0"
    "can_bitrate" = 500000
    "can_timeout" = 1.0
    "firmware_timeout" = 30
}
$config | ConvertTo-Json | Out-File -Path ".\config.json" -Force
Write-Host "[+] Configuration file created at ./config.json" -ForegroundColor Green

# Test imports
Write-Host "[*] Testing Python imports..." -ForegroundColor Yellow
python -c "import can, serial, fastapi, pydantic, click; print('[+] All imports successful')"
if ($?) {
    Write-Host "[+] Python environment ready" -ForegroundColor Green
} else {
    Write-Host "[!] Import test failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Connect ENET cable to vehicle" -ForegroundColor White
Write-Host "  2. Run: python implementation/rox_diagnostic.py --help" -ForegroundColor White
Write-Host "  3. Extract firmware: python implementation/rox_diagnostic.py firmware extract" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: ./docs/GETTING_STARTED.md" -ForegroundColor Cyan
