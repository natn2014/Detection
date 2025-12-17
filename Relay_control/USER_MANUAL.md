# Poka-Yoke Table Control - User Manual

## Overview
The **Poka-Yoke Table Control** is a production-line automation system designed to manage 4 independent relay units via Modbus TCP/IP communication. It provides real-time monitoring, sequence execution, alarm management, and performance analytics.

## System Requirements
- **Python:** 3.10+
- **OS:** Linux (tested on Jetson Nano)
- **Network:** TCP/IP connection to 4 relay units at:
  - 192.168.1.200 (Table 1)
  - 192.168.1.201 (Table 2)
  - 192.168.1.202 (Table 3)
  - 192.168.1.203 (Table 4)

## Installation

### 1. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app_pokayoke.py
```

## Main Features

### 1. **Monitor Tab** - Real-time Sequence Control
- **4 Independent Tables** - One table for each relay unit
- **Step Configuration** - Define up to 20 steps per sequence (BOX 0-8, where 0 = skip)
- **Status Display** - Real-time step status with color coding:
  - 🟩 **OK** = Step completed successfully (green)
  - 🟨 **WAIT** = Waiting for DI signal (yellow)
  - 🟦 **SIGNAL** = DO signal sent (light blue)
  - 🟥 **ERROR** = Step failed (red)
  - ⬜ **SKIP** = Step not configured (gray)
- **Cycle Metrics:**
  - Cycle Time: Duration from Step 1 start to last step completion (HH:MM:SS)
  - Cycles: Counter of completed cycles (pcs)
  - Avg: Average cycle time across all cycles (dark green)
- **Control Buttons:**
  - **Start** - Begin sequence execution (turns green when active)
  - **Stop** - Stop current sequence (turns red when active)
  - **Reset** - Clear all configuration and metrics

### 2. **Job Change Tab** - Sequence Templates
Save and load pre-configured job sequences for different production runs.

**To Save a Job:**
1. Configure all 4 tables with your step sequences
2. Enter a job name (e.g., "Product A V1")
3. Click **"Save Job Model"**
4. Saved to: `job_sequences.json`

**To Load a Job:**
1. Select job from dropdown list
2. Click **"Load Job Model"**
3. All 4 tables update automatically

### 3. **Machine Data Tab** - Alarm Configuration
Configure unexpected DI detection and alarm triggering per relay.

**Settings:**
- **Enabled** - Activate alarm detection for this relay
- **Alarm DO** - Which output channel (1-8) to activate on alarm
  - Set to 0 to disable alarm
  - Alarm remains ON until manually reset

**How It Works:**
- If a DI signal appears when NOT expected (outside current step), alarm triggers
- Configured DO channel turns ON and stays ON until reset
- Automatically switches to Alarm tab when triggered

### 4. **Alarm Tab** - Alarm Management
Password-protected alarm reset interface.

**To Reset an Alarm:**
1. Click **"Reset Alarm"** button under triggered relay
2. Numeric keypad dialog appears
3. Enter password: **5435**
4. Click **OK** to reset
5. Alarm DO turns OFF, status returns to "No Alarm"

**Visual Indicators:**
- 🟩 Green text "No Alarm" = Safe
- 🟥 Red text "Alarm Active" = Action needed

### 5. **Manual Tab** - Direct Relay Control
Test and troubleshoot individual relay channels manually.

**Per Relay Display:**
- **Connection Status** - Connected ✓ or Disconnected ✗
- **Digital Inputs (DI)** - Monitor all 8 input states in real-time
- **Relay Control** - Click buttons (CH1-CH8) to toggle outputs
- **Relay Status** - Visual feedback of all 8 output states

**All 4 tables displayed horizontally for easy comparison**

### 6. **Graph Tab** - Performance Analytics
Real-time visualization of cycle time trends across all 4 tables.

**Features:**
- **Line Plot** - Each table has unique color (Red, Teal, Blue, Salmon)
- **X-axis** - Actual clock time (HH:MM:SS format)
- **Y-axis** - Cycle time in seconds
- **Markers** - Individual cycle completion points
- **Legend** - Color-coded table identification
- **Clear Graph** - Reset all history

**Use For:**
- Identify performance variations
- Detect bottlenecks
- Compare table efficiency
- Track improvements over time

## Step Sequence Definition

### Understanding BOX Numbers
- **BOX 0** = Skip this step (not used in sequence)
- **BOX 1-8** = Relay channel to use for this step

### Execution Flow (per step)
1. **SIGNAL** - Send DO command to configured BOX
2. **WAIT** - Wait for corresponding DI to turn ON
3. **WAIT_OFF** - Wait for DI to turn OFF before next step
4. **OFF** - Turn off DO signal
5. **OK** - Step completed successfully

### Example 3-Step Sequence
```
Step 1: BOX 1 (Signal → Wait for DI1 ON → Wait for DI1 OFF → Turn off DO1)
Step 2: BOX 2 (Signal → Wait for DI2 ON → Wait for DI2 OFF → Turn off DO2)
Step 3: BOX 3 (Signal → Wait for DI3 ON → Wait for DI3 OFF → Turn off DO3)
Steps 4-20: BOX 0 (Skipped)

Cycle Time: Measured from Step 1 execution through Step 3 completion
```

## Color Coding Reference

### Status Indicators
| Color | Status | Meaning |
|-------|--------|---------|
| 🟩 Green | OK | Step completed |
| 🟨 Yellow | WAIT/WAIT_OFF | Waiting for signal |
| 🟦 Light Blue | SIGNAL | Signal sent |
| 🟥 Red | ERROR | Failed/Alarm |
| ⬜ Gray | SKIP | Not configured |

### Text Colors
| Color | Element | Meaning |
|-------|---------|---------|
| Blue | Cycles Counter | Number of completed cycles |
| Dark Green | Avg Time | Average cycle duration |
| Red | Alarm Status | Active alarm condition |
| Green | Normal Status | No alarm active |

## Workflow Example

### Starting Production
1. **Monitor Tab** → Select job from dropdown or configure manually
2. **Machine Data Tab** → Set alarm DO channel (e.g., DO 8)
3. **Monitor Tab** → Click **"Start"** to begin sequence
4. Watch cycle times and metrics update in real-time

### During Production
- **Visual feedback** shows each step status
- **Real-time cycle timer** displays elapsed time
- **Cycle counter** increments automatically on completion
- **Graph** plots all cycle times for trend analysis

### Handling Alarms
1. **Unexpected DI detected** → Auto-switches to Alarm tab
2. **Status shows red "Alarm Active"** with problem DI number
3. Click **"Reset Alarm"** → Enter password (5435)
4. Alarm DO turns OFF, system ready to resume

### Troubleshooting
1. **Manual Tab** → Check DI/DO connection status
2. **Click CH buttons** → Test relay outputs manually
3. **Monitor DI indicators** → Verify input signals
4. **Check Machine Data** → Verify alarm configuration

## Data Storage

### Saved Files
- **job_sequences.json** - All saved job templates
- **alarm_config.json** - Per-relay alarm configuration
- **relay_sequences.json** - Relay definitions (auto-loaded)

### Data Persistence
- Jobs and settings persist between application restarts
- Cycle counters reset when "Reset" button clicked
- Graph data clears when "Clear Graph" clicked or on app restart

## Technical Details

### Modbus Communication
- **Protocol:** Modbus TCP/IP
- **Port:** 4196
- **Polling Interval:** 500ms (configurable via UPDATE_INTERVAL env var)
- **Per Relay:** 8 DI channels, 8 DO channels

### Threading Model
- **Polling Thread** - Per relay, updates DI/DO status continuously
- **Executor Thread** - Per relay, executes step sequences
- **Qt Timer** - Updates cycle time display (100ms interval)
- **All thread-safe** with proper locking

### Update Environment Variable
```bash
export UPDATE_INTERVAL=1000  # Change polling to 1 second
python app_pokayoke.py
```

## Tips & Best Practices

✅ **Do:**
- Configure 1-3 steps initially, test, then expand
- Use same BOX number across tables only if coordinated
- Save job templates before major configuration changes
- Monitor Graph tab during initial production runs
- Reset metrics between different product runs

❌ **Don't:**
- Set multiple relays to trigger same BOX simultaneously (without coordination)
- Leave Alarm DO channel set to 0 if using alarm detection
- Forget to test manual controls before automation
- Run sequences without DI signals properly connected

## Support

### Common Issues

**"Disconnected ✗" on Manual Tab**
- Check network connection to relay (ping 192.168.1.200)
- Verify relay power and Modbus enabled
- Check port 4196 accessibility

**Cycle counter not incrementing**
- Verify steps 1 through last configured step complete with "OK" status
- Check DI/DO connections
- Ensure timeout values configured in relay

**Alarm not triggering**
- Check "Enabled" checkbox in Machine Data tab
- Verify Alarm DO channel is 1-8 (not 0)
- Test with Manual tab to ensure DO works

**Graph shows only points, no lines**
- Run at least 2 complete cycles to see trend
- Check that cycle times are recording

---

**Version:** 1.0  
**Last Updated:** December 2025  
**Tested On:** Jetson Nano with Python 3.10+
