# Manual DI Control Feature - Quick Guide

## ✅ New Features Added

### Manual DI Control
You can now **manually control DI1 and DI2** to simulate hardware signals and trigger detection!

## How to Use

### 1. Manual DI Control Mode (Default)
When you start the app, it's in **Manual DI Control** mode:

**DI1 Control (Detection Trigger):**
- Click the "DI1: OFF (Click to Toggle)" button
- Button turns GREEN and shows "DI1: ON"
- **Detection automatically starts** (same as real hardware DI1 signal)
- Camera feeds show "DETECTION ACTIVE" overlay
- System log shows "DI1 ON - Detection mode activated"

**DI2 Control (Stop Signal):**
- Click the "DI2: OFF (Click to Toggle)" button  
- Button turns GREEN and shows "DI2: ON"
- **Stop signal activates** (same as real hardware DI2 signal)
- Works with detection logic for DO4/DO5 output

**Toggle back OFF:**
- Click the button again to turn it OFF
- Detection stops when DI1 goes OFF

### 2. Hardware DI Monitoring Mode
Click the **"Mode: Manual DI Control"** button to switch modes:

- Button changes to "Mode: Hardware DI Monitoring" (orange background)
- DI1/DI2 buttons become **read-only** (disabled)
- App now monitors **real hardware DI signals** from relay board
- Buttons show current hardware state
- Auto-updates every 2 seconds

Click again to switch back to Manual mode.

## Detection Logic

### When DI1 is ON (Manual or Hardware):
1. ✅ Detection mode **activates automatically**
2. ✅ Cameras send frames to inference engine
3. ✅ Object detection runs in real-time
4. ✅ Results displayed on screen and in log

### When DI1 is OFF:
1. Detection mode **deactivates**
2. Cameras show feed only (no detection)
3. Lower CPU/GPU usage

### Output Control (DO4/DO5):
- **Object detected in any camera** → DO5 ON
- **DI2 ON + No object detected** → DO4 ON
- **Other states** → Both OFF

## GUI Elements

### Manual Control Panel Layout:

```
┌─────────────────────────────────────┐
│ Digital Inputs (Manual):            │
├─────────────────────────────────────┤
│ [DI1: OFF]  [DI2: OFF]              │ ← Click to toggle
├─────────────────────────────────────┤
│ Digital Outputs:                    │
│ [DO4: OFF]  [DO5: OFF]              │ ← Manual DO control
├─────────────────────────────────────┤
│ All DI Status (DI1-DI8)             │ ← Monitor all inputs
│ All DO Status (DO1-DO8)             │ ← Monitor all outputs
├─────────────────────────────────────┤
│ Control Mode:                       │
│ [Mode: Manual DI Control]           │ ← Click to switch
│ [Refresh All Status]                │
└─────────────────────────────────────┘
```

## Testing Scenarios

### Test 1: Manual Detection Start/Stop
1. Start app (Manual mode by default)
2. Click "DI1: OFF" → Detection starts
3. Watch camera feeds show "DETECTION ACTIVE"
4. Check system log for activation message
5. Click "DI1: ON" again → Detection stops

### Test 2: Complete Detection Flow
1. Click DI1 to ON (start detection)
2. Wait for object detection (if cameras connected)
3. When object detected: Watch DO5 turn green
4. Click DI2 to ON
5. If no object: Watch DO4 turn green

### Test 3: Hardware Mode
1. Click "Mode" button to switch to Hardware
2. DI buttons become read-only
3. Connect relay board signals
4. Watch DI1/DI2 respond to hardware
5. Detection triggers on hardware DI1 signal

## Advantages

✅ **No hardware needed for testing** - Use manual buttons
✅ **Same behavior as hardware** - Triggers identical logic
✅ **Easy switching** - One button to toggle modes
✅ **Full visibility** - See all DI/DO states
✅ **Real-time updates** - Immediate feedback

## System Log Messages

When using manual control, you'll see:
```
[14:30:15] Manual DI1: ON - Detection activated
[14:30:20] DI1 ON - Detection mode activated
[14:30:25] Camera 1: 0 object(s) detected
[14:30:30] Manual DI2: ON - Stop signal active
[14:30:35] DO4 ON - No object detected (DI2 active)
```

## Keyboard Shortcuts (Future)
Currently click-based, keyboard shortcuts can be added:
- F1: Toggle DI1
- F2: Toggle DI2
- F3: Toggle Mode
- F4: Refresh Status

---

**The manual DI control works exactly like hardware signals - perfect for testing without relay board!**
