# Poka-Yoke Table Control - Visual Guide

## Application Window Overview

**6-Tab Interface for Production Line Control**

```
╔══════════════════════════════════════════════════════════════════════════════╗
║              Poka-Yoke Table Control System - Production Monitoring          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ [Monitor] [Job Change] [Machine Data] [Alarm] [Manual] [Graph]              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  Tab 1: MONITOR - Real-time Production Control (Horizontal Layout)          ║
║  ════════════════════════════════════════════════════════════════════        ║
║                                                                              ║
║  ┌─ TABLE 1 ────────────┬─ TABLE 2 ────────────┬─ TABLE 3 ────────────┐    ║
║  │                      │                      │                      │    ║
║  │ Step │BOX│STA│ Status │ Step │BOX│STA│ Status │ Step │BOX│STA│ Status│    ║
║  │──────┼───┼────┼───────│──────┼───┼────┼───────│──────┼───┼────┼───────│    ║
║  │  1   │ 1 │ ✓  │  OK   │  1   │ 2 │ ⊙  │ WAIT  │  1   │ 0 │  │ SKIP  │    ║
║  │  2   │ 2 │ ✓  │  OK   │  2   │ 3 │ ⊙  │ WAIT  │  2   │ 0 │  │ SKIP  │    ║
║  │  3   │ 3 │ ⊙  │ WAIT  │  3   │ 1 │ ⊙  │ WAIT  │  3   │ 0 │  │ SKIP  │    ║
║  │  4   │ 0 │    │ SKIP  │  4   │ 0 │    │ SKIP  │  4   │ 0 │  │ SKIP  │    ║
║  │ ... (remaining steps 5-20 shown as 0 SKIP)                   │    ║
║  │                      │                      │                      │    ║
║  │ Cycle Time: 00:02:35 │ Cycle Time: 00:03:12 │ Cycle Time: --:--:-- │    ║
║  │ Cycles: 47 pcs       │ Cycles: 42 pcs       │ Cycles: 0 pcs        │    ║
║  │ Avg Time: 00:02:41   │ Avg Time: 00:03:08   │ Avg Time: --:--:--   │    ║
║  │                      │                      │                      │    ║
║  │ [Start] [Stop] [Reset]│ [Start] [Stop] [Reset]│ [Start] [Stop] [Reset]│    ║
║  └──────────────────────┴──────────────────────┴──────────────────────┘    ║
║                                                                              ║
║  ┌─ TABLE 4 ────────────────────────────────────────────────────────────┐  ║
║  │                                                                        │  ║
║  │ Step │BOX│STA│ Status │                                               │  ║
║  │──────┼───┼────┼────────                                               │  ║
║  │  1   │ 1 │ ✓  │  OK   │                                               │  ║
║  │  2   │ 2 │ ✓  │  OK   │                                               │  ║
║  │  3   │ 3 │ ⊙  │ WAIT  │                                               │  ║
║  │  ... │   │    │       │                                               │  ║
║  │                                                                        │  ║
║  │ Cycle Time: 00:02:45 │                                                │  ║
║  │ Cycles: 53 pcs       │                                                │  ║
║  │ Avg Time: 00:02:38   │                                                │  ║
║  │                                                                        │  ║
║  │ [Start] [Stop] [Reset]│                                               │  ║
║  └────────────────────────────────────────────────────────────────────────┘  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

---

## Tab 2: JOB CHANGE - Save and Load Production Jobs

```
╔══════════════════════════════════════════════════════════════╗
║  JOB CHANGE TAB - Job Templates                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Save Current Job                                            ║
║  ──────────────────                                          ║
║  Job Name: [___________________]                             ║
║  [Save Job Model]                                            ║
║                                                              ║
║  OR                                                          ║
║                                                              ║
║  Load Existing Job                                           ║
║  ──────────────────                                          ║
║  Select Job: [Product A         ▼]  ← Dropdown list          ║
║              [Product B        ]                             ║
║              [Test Job        ]                              ║
║              [Emergency Sequence]                            ║
║  [Load Job Model]                                            ║
║                                                              ║
║  Current Job Status:                                         ║
║  ┌────────────────────────────────────────────────────┐      ║
║  │ Table 1: 3 steps configured ✓                      │      ║
║  │ Table 2: 3 steps configured ✓                      │      ║
║  │ Table 3: Not configured                            │      ║
║  │ Table 4: 2 steps configured ✓                      │      ║
║  └────────────────────────────────────────────────────┘      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Tab 3: MACHINE DATA - Alarm Configuration

```
╔══════════════════════════════════════════════════════════════╗
║  MACHINE DATA TAB - Alarm Setup                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Unexpected DI Detection & Alarm Configuration               ║
║                                                              ║
║  Table 1 (192.168.1.200)                                     ║
║  ┌────────────────────────────────────────────────────┐      ║
║  │ [✓] Enable Unexpected DI Detection                 │      ║
║  │                                                    │      ║
║  │ Alarm Output Channel:  [DO 8  ▼]                   │      ║
║  │                        [DO 1]                      │      ║
║  │                        [DO 2]                      │      ║
║  │                        [DO 3 through 8]            │      ║
║  │                                                    │      ║
║  │ Description: Send alarm signal to channel DO8      │      ║
║  │              when unexpected DI is detected        │      ║
║  └────────────────────────────────────────────────────┘      ║
║                                                              ║
║  Table 2 (192.168.1.201)                                     ║
║  ┌────────────────────────────────────────────────────┐      ║
║  │ [✓] Enable Unexpected DI Detection                 │      ║
║  │ Alarm Output Channel:  [DO 8  ▼]                   │      ║
║  └────────────────────────────────────────────────────┘      ║
║                                                              ║
║  Table 3 (192.168.1.202)                                     ║
║  ┌────────────────────────────────────────────────────┐      ║
║  │ [ ] Enable Unexpected DI Detection                 │      ║
║  │ Alarm Output Channel:  [DO 1  ▼]                   │      ║
║  └────────────────────────────────────────────────────┘      ║
║                                                              ║
║  Table 4 (192.168.1.203)                                     ║
║  ┌────────────────────────────────────────────────────┐      ║
║  │ [✓] Enable Unexpected DI Detection                 │      ║
║  │ Alarm Output Channel:  [DO 7  ▼]                   │      ║
║  └────────────────────────────────────────────────────┘      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Tab 4: ALARM - Status Monitoring and Reset (Horizontal Layout)

```
╔══════════════════════════════════════════════════════════════╗
║  ALARM TAB - 4 Relay Units (Horizontal)                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌─ Table 1 ─────┬─ Table 2 ─────┬─ Table 3 ─────┬─ Table 4 ─────┐
║  │               │               │               │               │
║  │ Status:       │ Status:       │ Status:       │ Status:       │
║  │ No Alarm ✓    │ ALARM! ✗      │ No Alarm ✓    │ No Alarm ✓    │
║  │ (green)       │ (red)         │ (green)       │ (green)       │
║  │               │               │               │               │
║  │ DO8: OFF      │ DO8: ON ●     │ DO1: OFF      │ DO7: OFF      │
║  │               │               │               │               │
║  │               │ [Reset Alarm] │               │               │
║  │ [Reset Alarm] │ (requires     │ [Reset Alarm] │ [Reset Alarm] │
║  │               │  password)    │               │               │
║  │               │               │               │               │
║  └───────────────┴───────────────┴───────────────┴───────────────┘
║                                                              ║
║  When [Reset Alarm] is clicked on an active alarm:           ║
║  ┌────────────────────────────────────────────────────┐      ║
║  │     Enter Alarm Reset Password                     │      ║
║  │     (4-digit numeric code)                         │      ║
║  │                                                    │      ║
║  │     ╔═══════════════════════════════════════════╗  │      ║
║  │     ║                                           ║  │      ║
║  │     ║  Display: [*][*][*][*]                    ║  │      ║
║  │     ║                                           ║  │      ║
║  │     ║  ┌─────────────────────────────────────┐  ║  │      ║
║  │     ║  │ [1] [2] [3]                         │  ║  │      ║
║  │     ║  │ [4] [5] [6]                         │  ║  │      ║
║  │     ║  │ [7] [8] [9]                         │  ║  │      ║
║  │     ║  │ [Clear] [0] [Backspace]             │  ║  │      ║
║  │     ║  │                                     │  ║  │      ║
║  │     ║  │        [OK]  [Cancel]               │  ║  │      ║
║  │     ║  └─────────────────────────────────────┘  ║  │      ║
║  │     ║                                           ║  │      ║
║  │     ╚═══════════════════════════════════════════╝  │      ║
║  │                                                    │      ║
║  │  Password: 5435 (default)                          │      ║ 
║  │  Clears all 4 relay alarm states on success        │      ║
║  └────────────────────────────────────────────────────┘      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Tab 5: MANUAL - Direct Relay Control

```
╔══════════════════════════════════════════════════════════════╗
║  MANUAL TAB - Individual Relay Control (Horizontal)         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  ┌─ Table 1 ──────┬─ Table 2 ──────┬─ Table 3 ──────┬─ Table 4 ───┐
║  │ Connected ✓    │ Connected ✓    │ Disconnected ✗ │ Connected ✓ │
║  │                │                │                │             │
║  │ Inputs (DI)    │ Inputs (DI)    │ Inputs (DI)    │ Inputs (DI) │
║  │ ┌────────────┐ │ ┌────────────┐ │ ┌────────────┐ │ ┌──────────┐│
║  │ │ DI1: OFF   │ │ │ DI1: ON ●  │ │ │ DI1: OFF   │ │ │DI1: ON●  ││
║  │ │ DI2: OFF   │ │ │ DI2: OFF   │ │ │ DI2: OFF   │ │ │DI2: OFF  ││
║  │ │ DI3: ON ●  │ │ │ DI3: ON ●  │ │ │ DI3: OFF   │ │ │DI3: OFF  ││
║  │ │ DI4-8: OFF │ │ │ DI4-8: OFF │ │ │ DI4-8: OFF │ │ │DI4-8:OFF ││
║  │ └────────────┘ │ └────────────┘ │ └────────────┘ │ └──────────┘│
║  │                │                │                │             │
║  │ Outputs (DO)   │ Outputs (DO)   │ Outputs (DO)   │ Outputs(DO) │
║  │ ┌────────────┐ │ ┌────────────┐ │ ┌────────────┐ │ ┌──────────┐│
║  │ │ [DO1] [DO2]│ │ │ [DO1] [DO2]│ │ │ [DO1] [DO2]│ │ │[DO1][DO2]││
║  │ │ [DO3] [DO4]│ │ │ [DO3] [DO4]│ │ │ [DO3] [DO4]│ │ │[DO3][DO4]││
║  │ │ [DO5] [DO6]│ │ │ [DO5] [DO6]│ │ │ [DO5] [DO6]│ │ │[DO5][DO6]││
║  │ │ [DO7] [DO8]│ │ │ [DO7] [DO8]│ │ │ [DO7] [DO8]│ │ │[DO7][DO8]││
║  │ └────────────┘ │ └────────────┘ │ └────────────┘ │ └──────────┘│
║  │                │                │                │             │
║  │ Status:        │ Status:        │ Status:        │ Status:     │
║  │ DO1: OFF       │ DO1: OFF       │ (unavailable)  │ DO1: ON●    │
║  │ DO2: ON ●      │ DO2: ON ●      │                │ DO2: OFF    │
║  │ DO3-8: OFF     │ DO3-8: OFF     │                │ DO3-8: OFF  │
║  │                │                │                │             │
║  └────────────────┴────────────────┴────────────────┴─────────────┘
║                                                              ║
║  Click buttons to toggle DO output (only when connected)    ║
║  Green button = Output ON                                   ║
║  Gray button = Output OFF                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Tab 6: GRAPH - Real-Time Performance Analytics

```
╔══════════════════════════════════════════════════════════════╗
║  GRAPH TAB - Cycle Time Trends                               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Cycle Time Performance Over Time                            ║
║  (X-axis: Clock time, Y-axis: Duration in seconds)           ║
║                                                              ║
║  360 ┤                                                       ║
║      │                          ▲                            ║
║  300 ┤                       ▲  │  ▲                         ║
║      │                    ▲  │  │  │  ▲                      ║
║  240 ┤  ▲  ▲           ▲  │  │  │  │  │  ▲ ▲                 ║
║      │  │  │         ▲ │  │  │  │  │  │  │ │                 ║
║  180 ┤  │  │  ▲    ▲ │ │  │  │  │  │  │  │ │  ▲              ║
║      │  │  │  │    │ │ │  │  │  │  │  │  │ │  │              ║
║  120 ┤  │  │  │  ▲ │ │ │  │  │  │  │  │  │ │  │  ▲ ▲ ▲       ║
║      │  │  │  │  │ │ │ │  │  │  │  │  │  │ │  │  │ │ │       ║
║   60 ┤  │  │  │  │ │ │ │  │  │  │  │  │  │ │  │  │ │ │  ▲    ║ 
║      │  │  │  │  │ │ │ │  │  │  │  │  │  │ │  │  │ │ │  │    ║
║    0 └──┴──┴──┴──┴─┴─┴─┴──┴──┴──┴──┴──┴──┴─┴──┴──┴─┴─┴──┴──►
║      10:00 10:30 11:00 11:30 12:00 12:30 13:00 13:30 14:00   ║
║      ────  ────  ────  ────  ────  ────  ────  ────  ────    ║
║                                                              ║
║  Legend:                                                     ║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━     ║
║  ─ Red ──────── Table 1                                      ║
║  ─ Teal ─────── Table 2                                      ║
║  ─ Blue ─────── Table 3                                      ║
║  ─ Salmon ───── Table 4                                      ║
║                                                              ║
║  Statistics:                                                 ║
║  ┌────────────────┬────────────────┬────────────────┐        ║
║  │ Table 1        │ Table 2        │ Table 3        │        ║
║  │ Min: 00:02:15  │ Min: 00:02:45  │ Min: --:--:--  │        ║
║  │ Max: 00:04:12  │ Max: 00:04:30  │ Max: --:--:--  │        ║
║  │ Avg: 00:02:41  │ Avg: 00:03:08  │ Avg: --:--:--  │        ║
║  └────────────────┴────────────────┴────────────────┘        ║
║                                                              ║
║  ┌────────────────────────────────────────────────────┐      ║
║  │ Table 4                                            │      ║
║  │ Min: 00:02:30  Max: 00:03:45  Avg: 00:02:38        │      ║
║  └────────────────────────────────────────────────────┘      ║
║                                                              ║
║  [Clear Graph]  [Export Data (CSV)]  [Refresh]               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Cycle Time Tracking Flowchart

```
START SEQUENCE
       │
       ▼
Step 1 → SIGNAL (Send DO)
       │
       ▼
   Start Timer ◄────── cycle_start_time recorded
       │
       ├─ Step 2 → Execute
       ├─ Step 3 → Execute
       ├─ ...
       │
       ▼
Last Step → OK (Completed)
       │
       ▼
   Stop Timer
   elapsed_time = current_time - cycle_start_time
   cycle_count++
   total_cycle_time += elapsed_time
   average_time = total_cycle_time / cycle_count
       │
       ▼
Display:
  • Cycle Time: elapsed_time (HH:MM:SS in black)
  • Cycles: cycle_count (blue "pcs")
  • Avg Time: average_time (dark green)
  • Graph: Add point (timestamp, duration)
       │
       ▼
Auto-Restart or Wait for Next Cycle
```

---

## Sequence Execution Step States

```
┌─ SIGNAL State ─┐
│ DO signal sent │
│ Relay activated│
└────────────────┘
         │
         ▼
┌─ WAIT State ──────┐
│ Waiting for DI=ON │
│ Monitor DI status │
└───────────────────┘
         │
         ▼
┌─ WAIT_OFF State ──┐
│ Waiting for DI=OFF│
│ Monitor DI status │
└───────────────────┘
         │
         ▼
┌─ OFF State ───────┐
│ DO signal removed │
│ Relay deactivated │
└───────────────────┘
         │
         ▼
┌─ OK State ────────┐
│ Step completed    │
│ Proceed to next   │
└───────────────────┘
```

---

## Data Files Structure

```json
job_sequences.json - Saved Jobs
────────────────────────────────
[
  {
    "job_name": "Product A",
    "created_at": "2025-12-17T10:30:00",
    "relay_sequences": {
      "192.168.1.200": [1, 2, 3, 0, 0, ...],  // Table 1 BOX numbers
      "192.168.1.201": [2, 3, 1, 0, 0, ...],  // Table 2 BOX numbers
      "192.168.1.202": [0, 0, 0, 0, 0, ...],  // Table 3 (not configured)
      "192.168.1.203": [1, 2, 0, 0, 0, ...]   // Table 4 BOX numbers
    }
  }
]

alarm_config.json - Alarm Settings
───────────────────────────────────
{
  "192.168.1.200": {
    "relay_id": "192.168.1.200",
    "do_channel": 8,
    "enabled": true
  },
  "192.168.1.201": {
    "relay_id": "192.168.1.201",
    "do_channel": 8,
    "enabled": true
  },
  ...
}
```

---

## Color Coding Summary

```
METRIC              COLOR               FORMAT
─────────────────────────────────────────────────────
Cycle Time          Black               HH:MM:SS
Cycle Count         Blue                N pcs
Average Time        Dark Green (#006600) HH:MM:SS
Status: OK          Green               ✓
Status: WAIT        Yellow              ⊙
Status: SIGNAL      Cyan                ↻
Status: ERROR       Red                 ✗
Status: SKIP        Gray                -
Button: Active      Green (#4CAF50)     
Button: Reset       Default gray        
Alarm: Active       Red                 ✗
Alarm: Inactive     Green               ✓
```

---

## File System Structure

```
/home/jetson/dev/modbus-relay-control/
├── app_pokayoke.py                   ← Main application (1500+ lines)
├── relay_client.py                   ← Modbus TCP/IP client
├── requirements.txt                  ← Dependencies (PySide6, matplotlib)
├── USER_MANUAL.md                    ← User documentation
├── README.md                         ← Project overview
├── VISUAL_GUIDE.md                   ← This file (visual reference)
├── job_sequences.json                ← Saved jobs (auto-created)
├── alarm_config.json                 ← Alarm settings (auto-created)
└── relay_sequences.json              ← Relay configuration
```

---

## Performance Metrics

```
METRIC                  VALUE
────────────────────────────────────
Polling Interval        500ms per relay
UI Update Rate          100ms (cycle timer)
Graph Redraw            On cycle completion
Max Relays              4 (easily scalable)
Max Steps per Relay     20
DI/DO Channels          8 each per relay
Supported Job Templates Unlimited
Memory (Baseline)       ~50-100MB (with GUI)
CPU Usage (Idle)        <2%
CPU Usage (Active)      ~5-10%
```
Want to...                  Location to Edit
─────────────────────────   ──────────────────────────
Add relay boards        →   RELAY_CONFIGS
Change polling rate     →   UPDATE_INTERVAL
Increase channels       →   NUM_INPUTS, NUM_OUTPUTS
Extend timeout          →   timeout in SequenceExecutor
Add new action type     →   StepEditorDialog.action_type
Change UI colors        →   setStyleSheet() calls
Add delay action        →   StepAction class
Enable logging          →   Add to execution methods
```

---

**This visual guide complements the detailed documentation in:**
- **QUICK_START.md** - Step-by-step instructions
- **SMART_SEQUENCES_README.md** - Complete reference
- **IMPLEMENTATION_COMPLETE.md** - Architecture overview
