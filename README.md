# ROX 01 Diagnostic Tool

> **Fully autonomous, open-source diagnostic platform for ROX 01 Chinese vehicles**
> 
> No dealer needed. Complete firmware analysis, live diagnostics, DTC clearing, firmware updates, app installation, and ECU resets—all via Codex-powered agentic automation.

## 🎯 Features

✅ **Firmware Extraction** — Direct from vehicle via ENET cable (OBD-II)  
✅ **Live Data Streaming** — Real-time engine, EV, sensor data  
✅ **DTC Reading & Clearing** — Full fault code management  
✅ **Firmware Updates** — Safe, verified ECU programming  
✅ **ECU Reset** — Factory reset or soft reset  
✅ **App Management** — Install/remove vehicle apps  
✅ **Agentic Automation** — Codex-powered autonomous operation  
✅ **100% Open Source** — No cloud lock-in, no licensing  

## ⚡ Quick Start

### Prerequisites
- Windows 10/11
- Python 3.9+
- ENET cable (USB to CAN/OBD-II) or standard CAN interface
- ROX 01 vehicle with OBD port

### Installation (One Command)

```powershell
# Run setup script
.\windows-setup.ps1

# Verify installation
python rox_diagnostic.py --version
```

### Usage Examples

```bash
# Extract firmware from vehicle
python rox_diagnostic.py firmware extract

# Read live data
python rox_diagnostic.py live-data

# Read fault codes
python rox_diagnostic.py read-faults

# Clear all faults
python rox_diagnostic.py clear-faults

# Update firmware (with safety checks)
python rox_diagnostic.py firmware update new_firmware.bin

# Reset ECU
python rox_diagnostic.py reset --type full
```

## 📁 Project Structure

```
roxdiagnostic/
├── firmware/
│   ├── extraction/          # Firmware extraction scripts
│   └── samples/             # Sample firmware files
├── implementation/
│   ├── rox_diagnostic.py           # Main CLI tool
│   ├── rox_diagnostic_core.py      # Core diagnostics library
│   └── protocol.py                 # ROX 01 UDS protocol
├── analysis/
│   ├── codex_orchestrator.py       # Codex agentic automation
│   └── firmware_analyzer.py        # Firmware analysis
├── testing/
│   ├── test_diagnostics.py         # Unit tests
│   └── mock_ecu.py                 # Mock ECU for testing
├── docs/
│   ├── ARCHITECTURE.md
│   ├── PROTOCOL.md
│   ├── API.md
│   └── SAFETY.md
├── windows-setup.ps1               # Windows setup script
├── .codex-config.json              # Codex configuration
└── LICENSE (MIT)
```

## 🏗 Architecture

```
Windows PC
    ↓
[ENET Cable / USB-CAN]
    ↓
ROX 01 Vehicle (OBD-II Port)
    ↓
ECU (UDS Protocol)
    ├─ Live Data
    ├─ DTC Management
    ├─ Firmware Storage
    └─ App Partition
```

## 📊 Supported Operations

| Operation | Status | Notes |
|-----------|--------|-------|
| Firmware Extraction | ✅ | Direct from ECU |
| Live Data | ✅ | 50+ parameters |
| DTC Read | ✅ | Full fault codes |
| DTC Clear | ✅ | Safe with backup |
| Firmware Update | ✅ | Verified & reversible |
| ECU Reset | ✅ | Hard/soft/factory |
| App Install | 🔄 | If ECU supports |
| Remote Diagnostics | 🔄 | WebUI coming soon |

## ⚠️ Legal & Safety

**You must:**
- ✅ Own the vehicle or have explicit permission
- ✅ Keep original firmware backup
- ✅ Understand risks of ECU modification
- ✅ Not use for illegal purposes
- ✅ Accept full liability

See [docs/SAFETY.md](docs/SAFETY.md) for full details.

## 📚 Documentation

- [Getting Started](docs/GETTING_STARTED.md)
- [Architecture & Design](docs/ARCHITECTURE.md)
- [ROX 01 Protocol Specification](docs/PROTOCOL.md)
- [API Reference](docs/API.md)
- [Safety Guidelines](docs/SAFETY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤖 Codex Agentic Automation

This tool uses **OpenAI Codex** for autonomous:
- Firmware analysis & code lifting
- Protocol extraction from binaries
- Test generation
- Documentation generation

```bash
python analysis/codex_orchestrator.py firmware.bin
```

## 📦 Installation Methods

### Method 1: Quick Setup (Recommended)
```powershell
.\windows-setup.ps1
```

### Method 2: Manual Python Setup
```bash
pip install python-can pyserial fastapi pydantic click
```

### Method 3: Docker
```bash
docker-compose up -d
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest testing/ -v

# Test with mock ECU
python testing/test_diagnostics.py

# Test firmware extraction
python testing/test_protocol.py
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

MIT License - See [LICENSE](LICENSE)

## ⚡ Status

- [x] Firmware extraction
- [x] Live data diagnostics
- [x] DTC management
- [x] ECU reset
- [ ] Firmware update (in testing)
- [ ] App installation
- [ ] Web UI
- [ ] Mobile app

## 💬 Support

- 📖 [Read the docs](docs/)
- 🐛 [Report issues](https://github.com/FtYadu/roxdiagnostic/issues)
- 💡 [Discussions](https://github.com/FtYadu/roxdiagnostic/discussions)

---

**Built with ❤️ for independent vehicle ownership**
