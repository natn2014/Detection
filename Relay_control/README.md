# Poka-Yoke Table Control System

A production-line automation control system for managing 4 independent relay units via Modbus TCP/IP communication with real-time monitoring, sequence execution, alarm management, and performance analytics.

## 🎯 Overview

**Poka-Yoke Table Control** is a PyQt6-based GUI application designed for industrial production environments. It enables:
- **Real-time control** of up to 4 relay units simultaneously
- **Step-based sequence execution** with 20 steps per unit
- **Intelligent alarm detection** for unexpected signals
- **Production metrics** tracking (cycle time, average time, cycle count)
- **Job template system** for repeatable production runs
- **Performance graphing** with real-time trend analysis

## ✨ Key Features

### 📊 Monitor Tab
- 4 independent control tables (horizontal layout)
- Up to 20 configurable steps per sequence
- Real-time status display with color-coded feedback
- Cycle time tracking (HH:MM:SS format)
- Cycle counter with automatic increment
- Average cycle time calculation
- Start/Stop/Reset controls with visual button states

### 💾 Job Change Tab
- Save current configurations as job templates
- Load pre-configured jobs instantly
- Support for unlimited job templates
- Persistent storage in `job_sequences.json`

### ⚙️ Machine Data Tab
- Per-relay alarm configuration
- Enable/disable unexpected DI detection
- Select alarm output channel (DO 1-8)
- Persistent storage in `alarm_config.json`

### 🚨 Alarm Tab
- Horizontal layout for all 4 relay alarm controls
- Real-time alarm status monitoring
- Password-protected reset (numeric keypad)
- Default password: **5435**
- Auto-switch on alarm trigger

### 🎮 Manual Tab
- Direct relay control for testing
- Real-time DI/DO monitoring
- Per-relay connection status
- Channel-by-channel control buttons
- Horizontal layout for side-by-side comparison

## 🚀 Installation

### 1. Clone Repository
```bash
cd /home/jetson/dev/modbus-relay-control
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python app_pokayoke.py
```

## 📱 Hardware Requirements

### Relay Units
- **Quantity:** 4 units (can be reduced by modifying config)
- **Protocol:** Modbus TCP/IP
- **Port:** 4196
- **Default IPs:** 192.168.1.200 - 192.168.1.203
- **I/O Per Unit:** 8 Digital Inputs (DI) + 8 Digital Outputs (DO)

### Network
- Stable Ethernet connection (1Gbps recommended)
- Devices on same subnet or properly routed

### Computing
- **CPU:** ARM or x86 (tested on Jetson Nano)
- **RAM:** 1GB minimum (2GB+ recommended)
- **Display:** Any resolution (1400x900+ recommended)

## 📖 Usage Guide

### Quick Start

1. **Configure Sequence**
   - Select Monitor tab
   - Choose BOX numbers (1-8) for each step
   - Set BOX to 0 to skip a step
   - Steps 4-20 can be left as 0

2. **Start Production**
   - Click **Start** button
   - Watch cycle metrics update in real-time
   - Monitor Graph tab for trends

3. **Save Job**
   - Go to Job Change tab
   - Enter job name
   - Click "Save Job Model"

4. **Load Job**
   - Go to Job Change tab
   - Select from dropdown
   - Click "Load Job Model"

### Sequence Execution Flow

Per step:
1. **SIGNAL** - Send DO command to configured BOX channel
2. **WAIT** - Wait for corresponding DI to turn ON
3. **WAIT_OFF** - Wait for DI to turn OFF
4. **OFF** - Turn off DO signal
5. **OK** - Step completed successfully

### Example: 3-Step Job
```
Step 1: BOX 1 → DI1 control on Table 1
Step 2: BOX 2 → DI2 control on Table 1
Step 3: BOX 3 → DI3 control on Table 1
Steps 4-20: BOX 0 (skipped)

Cycle Time: Measured from Step 1 start → Step 3 completion
Average: Sum of all cycle times ÷ Number of cycles
```

## 🎨 Color Reference

### Status Indicators
| Status | Color | Meaning |
|--------|-------|---------|
| OK | 🟩 Green | Step completed |
| WAIT/WAIT_OFF | 🟨 Yellow | Waiting for signal |
| SIGNAL | 🟦 Cyan | Signal sent |
| ERROR | 🟥 Red | Failed/Alarm |
| SKIP | ⬜ Gray | Not configured |

### Text Elements
| Element | Color | Meaning |
|---------|-------|---------|
| Cycles Counter | Blue | Number of completed cycles |
| Avg Time | Dark Green | Average duration |
| Alarm Status | Red | Active alarm |
| Normal Status | Green | No alarm |

## 📁 Project Structure

```
modbus-relay-control/
├── app_pokayoke.py              # Main application (1500+ lines)
├── relay_client.py              # Modbus client (socket-based)
├── requirements.txt             # Python dependencies
├── USER_MANUAL.md              # Detailed user guide
├── README.md                   # This file
├── job_sequences.json          # Saved jobs (auto-created)
├── alarm_config.json           # Alarm settings (auto-created)
└── relay_sequences.json        # Relay definitions
```

## ⚙️ Configuration

### Environment Variables
```bash
# Change polling interval (milliseconds)
export UPDATE_INTERVAL=1000
python app_pokayoke.py
```

### Modify Relay IPs
Edit `app_pokayoke.py` line ~37:
```python
RELAY_CONFIGS = [
    {'ip': '192.168.1.200', 'port': 4196, 'name': 'Table 1'},
    {'ip': '192.168.1.201', 'port': 4196, 'name': 'Table 2'},
    {'ip': '192.168.1.202', 'port': 4196, 'name': 'Table 3'},
    {'ip': '192.168.1.203', 'port': 4196, 'name': 'Table 4'},
]
```

## 🐛 Troubleshooting

### Cannot Connect to Relays
```bash
# Test connectivity
ping 192.168.1.200

# Check if port is open
nc -zv 192.168.1.200 4196

# Verify relay is powered and Modbus enabled
# Check relay status LEDs
```

### Cycle Time Not Recording
- Verify all steps 1→N complete with "OK" status
- Check DI/DO connections
- Review Manual tab for signal issues

### Alarm Not Triggering
- Confirm "Enabled" in Machine Data tab
- Set Alarm DO channel to 1-8 (not 0)
- Test DO with Manual tab first

### Graph Shows No Lines
- Need minimum 2 completed cycles
- Verify cycle completion occurs
- Check timestamp generation

## 📊 Architecture

### Threading Model
- **Polling Thread** (per relay) - 500ms DI/DO polling
- **Executor Thread** (per relay) - Step sequence execution
- **Qt Timer** - 100ms cycle time display updates
- **Main Thread** - Qt event loop & UI

### Signal Flow
```
Relay (via TCP) 
    ↓
RelayClient (socket)
    ↓
Polling Thread → DI/DO update signals
    ↓
Qt Signals → UI update
    ↓
StepSequenceExecutor → Execute next step
    ↓
RelayClient → Send command back to relay
```

## 📈 Performance Metrics

- **Polling Latency:** ~50-100ms per relay
- **UI Update Rate:** 100ms cycle timer
- **Graph Redraw:** On each cycle completion
- **Supported Relays:** 4 (easily scalable to 8+)

## 🔐 Security

### Default Credentials
- **Alarm Reset Password:** 5435 (numeric keypad)
- Modify in code if needed: search `"5435"` in `app_pokayoke.py`

### Network Security
- System assumes trusted network (industrial LAN)
- No encryption on Modbus communication
- For public networks, add VPN tunnel

## 📝 Data Files

### job_sequences.json
```json
[
  {
    "job_name": "Product A",
    "created_at": "2025-12-17T10:30:00",
    "relay_sequences": {
      "192.168.1.200": [1, 2, 3, 0, ...],
      "192.168.1.201": [2, 3, 1, 0, ...]
    }
  }
]
```

### alarm_config.json
```json
{
  "192.168.1.200": {
    "relay_id": "192.168.1.200",
    "do_channel": 8,
    "enabled": true
  }
}
```

## 🔄 Update Interval Configuration

Default: 500ms (polling from all 4 relays)

Adjust via environment variable:
```bash
export UPDATE_INTERVAL=1000  # 1 second
export UPDATE_INTERVAL=250   # 250ms (faster, more CPU)
python app_pokayoke.py
```

## 🤝 Contributing

For improvements or bug reports, document:
1. Issue description
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment (OS, Python version, relay firmware)

## 📄 License

Internal use only - Proprietary software

## 📞 Support

### Documentation
- See `USER_MANUAL.md` for detailed user guide
- Inline code comments explain complex logic
- README provides technical overview

### Testing Production Jobs
1. Start with 1-step sequences
2. Add steps incrementally
3. Test with Manual tab first
4. Verify all DI signals present
5. Monitor cycle times for anomalies

---

**Version:** 1.0  
**Last Updated:** December 2025  
**Platform:** Linux (Jetson Nano, x86)  
**Python:** 3.10+  
**Status:** Production Ready ✅

---

## 🔍 File Manifest

```
/home/jetson/dev/modbus-relay-control/
├── app_smart_sequences.py           ← Main application
├── relay_client.py                  ← Device communication  
├── relay_sequences.json             ← Example sequences
├── test_smart_sequences.py          ← Test suite
├── QUICK_START.md                   ← Quick start guide
├── SMART_SEQUENCES_README.md        ← Complete reference
├── IMPLEMENTATION_COMPLETE.md       ← Architecture overview
├── VISUAL_GUIDE.md                  ← Diagrams & flowcharts
└── README.md                        ← This index (you are here)
```

---

**Status**: ✅ COMPLETE  
**Version**: 1.0  
**Date**: December 16, 2025  
**Ready for**: Production use  

🚀 **Start here**: [QUICK_START.md](QUICK_START.md) or run `python app_smart_sequences.py`
