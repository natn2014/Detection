# New Blink and Status Features + DI/DO Check Functions

## New Features Added

### 1. Blink Functionality
- **Simple Logic Sequences**: Added checkbox "Blink Mode (ON/OFF every 1 sec)" in the sequence dialog
- **Multi-Step Sequences**: Added support for `DO2(BLINK):10s` action format
- Blinks at 1-second intervals (ON for 1s, OFF for 1s, repeat)
- Works with duration for timed blink or infinite blink (duration = 0) until trigger goes off

### 2. Enhanced Sequence Status Display
Added a new "Sequence Status" panel that shows:
- **Current Sequence** (blue text): Shows currently running sequences
- **Next Step** (orange/yellow text): Shows what step will execute next in multi-step sequences
- **Completed Sequences** (green text): Shows sequences that have completed execution
- **Next Sequence** (yellow text with dark background): Shows the next sequence waiting to be triggered

### 3. DI/DO Channel Check Functions
Added comprehensive functions to check the state of individual DI/DO channels:

#### Programmatic Functions:
- `check_di_channel(channel)`: Check if a specific DI channel (1-8) is ON or OFF
- `get_all_di_states()`: Get a dictionary of all DI channel states
- `check_do_channel(channel)`: Check if a specific DO channel (1-8) is ON or OFF  
- `get_all_do_states()`: Get a dictionary of all DO channel states

#### UI Features:
- **"Check DI States" button**: Logs all DI channel states to the event log
- **"Check DO States" button**: Logs all DO channel states to the event log
- **Right-click context menus**: 
  - Right-click any DI channel to check its individual state
  - Right-click any DO channel to check its state or toggle it manually for testing

#### Error Handling:
- Validates channel numbers (must be 1-8)
- Handles relay connection errors gracefully
- Logs appropriate error messages for debugging

## Usage Examples

### Simple Logic with Blink
1. Create a new sequence
2. Select "Simple Logic"
3. Configure: DI1 -> DO2 with 10 second duration
4. Check "Blink Mode (ON/OFF every 1 sec)"
5. Result: When DI1 is triggered, DO2 will blink (ON/OFF every 1 sec) for 10 seconds

### Multi-Step with Blink
```
DI1->DO2(ON):2s
DI2->DO3(BLINK):5s
WAIT:2s
DI3->DO3(OFF)
```

### Status Display Behavior
- **Current Sequence**: Shows "Sequence #0: Simple Logic - DO2" when a simple sequence is active
- **Next Step**: Shows "Sequence #1: DI2->DO3(BLINK):5s" for the next step in multi-step sequences
- **Completed**: Shows "Sequence #1: Multi-Step Completed" when sequences finish
- **Next Sequence**: Shows the first enabled sequence that will be triggered next

## Configuration Changes
The sequence configuration now stores:
- `blink_mode`: Boolean flag for simple sequences
- Blink actions are supported in multi-step sequence text format

## Technical Implementation
- `blink_timers`: Tracks active blink operations with toggle timing
- `blink_states`: Tracks current ON/OFF state for each blink operation
- `update_sequence_status_display()`: Updates the status panel every 250ms
- Blink operations toggle every 1000ms (1 second)
- All blink timers are properly cleaned up when sequences are disabled or application closes

## Color Coding
- **Blue**: Current active sequences
- **Orange/Yellow**: Next steps to execute
- **Green**: Completed sequences  
- **Yellow with dark background**: Next sequence ready to trigger
- **Gray**: No activity/None state
