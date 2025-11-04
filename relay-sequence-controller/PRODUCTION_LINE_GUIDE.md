# Production Line Relay Sequence Controller

## New Production Line Concept

This system has been redesigned specifically for manufacturing and production line control where:

- **DI (Digital Input)** = Sensors detecting parts, positions, operations, and feedback
- **DO (Digital Output)** = Actuators, machines, and devices performing operations  
- **Sequence Control** = Based on real sensor feedback and part detection
- **Error Handling** = Skip processes when wrong conditions are detected

## Station Operation Types

### 1. **Part Detection & Process**
- **Part Sensor (DI)**: Detects when a part arrives at the station
- **Process Device (DO)**: Performs the manufacturing operation
- **Feedback Sensor (DI)**: Confirms operation completed successfully
- **Skip Sensor (DI)**: Error condition to skip processing
- **Timeout**: Maximum time allowed for operation
- **Duration**: Fixed operation time (0 = wait for feedback)

**Example**: Drilling Station
- Part detected on DI1 → Start drill on DO2 → Wait for drill completion on DI3
- If error sensor DI4 active → Skip drilling process

### 2. **Sequential Operation**
- Chain multiple operations based on sensor feedback
- Each step waits for confirmation before proceeding
- Built-in error recovery and timeout handling

**Example**: Assembly Station
- Clamp part (DO1) → Wait clamp confirm (DI2) → Start assembly (DO3) → Wait complete (DI4)

### 3. **Conditional Process**
- Branch operations based on quality checks or part types
- Route parts to different processes based on sensor input

**Example**: Quality Control
- Inspect part (DO5) → Check pass/fail sensors (DI6/DI7) → Route to appropriate output

### 4. **Safety Interlock**
- Emergency stop and safety monitoring
- Immediate shutdown on safety violations
- Blink warning devices

## Production Line Sequence Format

### Advanced Sensor-Based Steps:
```
PART_DI1->CLAMP_DO1:2s                    # Part detected → Clamp for 2 seconds
CLAMP_FEEDBACK_DI2->DRILL_DO2:5s          # Clamp confirmed → Drill for 5 seconds  
DRILL_FEEDBACK_DI3->UNCLAMP_DO1(OFF)      # Drill complete → Release clamp
UNCLAMP_FEEDBACK_DI4->TRANSFER_DO3:3s     # Unclamp confirmed → Transfer part
TRANSFER_COMPLETE_DI5->STATION_READY_DO4(OFF)  # Transfer done → Reset station
```

### Error Handling:
```
PART_DI1->PROCESS_DO2->FEEDBACK_DI3|SKIP_DI4:15s    # Process or skip on error
ERROR_DI7->ALARM_DO8(BLINK):10s                     # Error alarm
ESTOP_DI8(OFF)->EMERGENCY_STOP                      # Emergency stop
```

### Multi-Station Coordination:
```
STATION1_DI1->PROCESS1_DO1->FEEDBACK_DI2->TRANSFER_DO3
STATION2_DI4->PROCESS2_DO2->FEEDBACK_DI5->COMPLETE_DO4
```

## Key Features

### **Sensor Feedback Control**
- Operations wait for actual sensor confirmation
- No blind timing - everything based on real feedback
- Built-in timeout protection

### **Error Recovery** 
- Skip sensors prevent processing defective parts
- Automatic retry and error logging
- Safety interlocks with immediate response

### **Production Flow**
- Part tracking through stations
- Automatic handoff between processes
- Quality control branching

### **Real-Time Status**
- Current station operations display
- Next process step preview  
- Completed operations tracking (green)
- Error conditions highlighted

## Usage Examples

### Simple Manufacturing Station:
1. Create "Station Operation" sequence
2. Set Part Detection Sensor = DI1 (proximity sensor)
3. Set Process Device = DO2 (pneumatic drill)
4. Set Feedback Sensor = DI3 (drill position sensor)
5. Set Skip Sensor = DI4 (part defect sensor)
6. Set timeout = 15 seconds, duration = 0 (wait for feedback)

### Complete Production Line:
1. Create "Production Line Sequence" 
2. Define multi-station workflow with sensor handoffs
3. Include error handling and quality checks
4. Set proper timeouts and safety interlocks

### Benefits:
- **Reliable**: Based on actual sensor feedback, not blind timing
- **Safe**: Built-in timeouts and error handling
- **Flexible**: Easy to reconfigure for different products
- **Traceable**: Complete logging of all operations and errors
- **Efficient**: No wasted cycles, parts flow smoothly through line
