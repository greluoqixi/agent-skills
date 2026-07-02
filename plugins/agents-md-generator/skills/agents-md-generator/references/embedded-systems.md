# Embedded & Engineering Systems Domain Guide

## CPS Layered Architecture

Embedded projects follow a four-layer Cyber-Physical Systems (CPS) model:

```
+----------------------------+
|    Application Layer       |  Control algorithms, sensor fusion, user logic
|  (control loops, FSM,     |
|   protocol stacks)         |
+----------------------------+
|  Middleware / RTOS Layer   |  Task scheduling, IPC, timers, synchronization
|  (FreeRTOS, Zephyr,       |
|   ThreadX, bare-metal)     |
+----------------------------+
|  HAL / Driver Layer        |  Register-level abstraction, peripheral drivers
|  (MCU SDK, CMSIS,         |
|   vendor HAL, own HAL)     |
+----------------------------+
|    Hardware Layer           |  MCU/MPU, memory, peripherals (SPI/I2C/CAN)
|  (datasheet, schematic,   |
|   PCB)                     |
+----------------------------+
```

Document each layer's responsibilities and the interfaces (API contracts) between adjacent layers.

## Hardware Context Documentation

Every embedded CLAUDE.md must document the hardware environment:

### MCU / MPU Specification
- Model: `STM32G474RET6`, `ESP32-S3`, `RP2040`, etc.
- Architecture: ARM Cortex-M4 (with FPU), RISC-V 32-bit, Xtensa LX7
- Clock speed: 170 MHz (max), 240 MHz (with PLL)
- Core features: FPU, DSP instructions, TrustZone, cache

### Memory Layout
- Flash: 512 KB (application + bootloader partition)
- RAM: 128 KB (96 KB SRAM1 + 32 KB SRAM2)
- Stack size per task: 1024 words (document per-task allocation)
- Heap: configurable in FreeRTOSConfig.h / startup file

### Peripherals
| Peripheral | Bus | IRQ Priority | Usage |
|------------|-----|-------------|-------|
| SPI1 | APB2 | 5 | IMU data |
| I2C2 | APB1 | 6 | Temperature sensor |
| CAN1 | APB1 | 4 | Motor commands |
| ADC1_IN1 | -- | 7 | Current sense |
| TIM2_CH1 | APB1 | 8 | PWM generation |

### Toolchain
- Compiler: `arm-none-eabi-gcc` 12.2, `-mcpu=cortex-m4 -mfloat-abi=hard`
- Cross-compilation prefix: `arm-none-eabi-`
- Linker script: `ldscripts/{mcu}.ld`
- Debug probe: J-Link / ST-Link / Black Magic Probe / OpenOCD config

## RTOS Configuration

### FreeRTOS (FreeRTOSConfig.h)
Key settings to document:
```c
#define configTICK_RATE_HZ          1000    // 1 ms tick
#define configMAX_PRIORITIES        10
#define configTOTAL_HEAP_SIZE       (32 * 1024)  // 32 KB heap
#define configMINIMAL_STACK_SIZE    128     // words
```

Task table:

| Task Name | Priority | Stack (words) | Period | Purpose |
|-----------|----------|---------------|--------|---------|
| ControlTask | 8 | 512 | 1 kHz | Motor control loop |
| SensorTask | 6 | 256 | 100 Hz | Read and filter sensors |
| CommTask | 4 | 384 | event | CAN/UART communication |

### Zephyr (prj.conf + device tree)
Key Kconfig settings:
```kconfig
CONFIG_SYS_CLOCK_TICKS_PER_SEC=1000
CONFIG_MAIN_STACK_SIZE=4096
CONFIG_HEAP_MEM_POOL_SIZE=16384
CONFIG_CAN=y
```

Device tree considerations:
- Pin muxing via `&{peripheral}` node aliases
- Clock configuration in `dts/bindings/`
- Flash partitions for bootloader + application + settings storage

### ISR Policy
- Minimum ISR latency: document maximum disabled-interrupt time
- Nested interrupts: priority grouping (group 4 bits for preemption, 0 for sub)
- Deferred processing: ISR sets event flag, task handles the work
- Banned in ISRs: blocking calls, printf, malloc/free

## Safety & Compliance

### MISRA-C Rules
Document the deviation process and which rules are enforced:
- Mandatory: Rule 10.1 (integer type conversions), Rule 14.3 (controlling expressions)
- Required: Rule 8.6 (symbol visibility), Rule 16.1 (switch statements)
- Deviated: list each deviation with rationale and review approval

### SIL Level Documentation
| Component | SIL | Standard | Mitigation |
|-----------|-----|----------|------------|
| Brake control | SIL 2 | IEC 61508 | Dual-channel, diagnostics |
| Motor driver | SIL 1 | IEC 61508 | Current monitoring |
| Communication | QM | -- | CRC-32 on CAN frames |

### Banned APIs
```c
// NEVER use these in production code:
malloc() / free() / realloc()     // Use static pools instead
printf() / sprintf()              // Use RTT / semihosting for debug only
assert()                          // Use custom error handler
alloca()                          // Stack overflow risk
memcpy() with runtime length      // Use checked copy
```

### Memory Safety
- Stack depth analysis: static analysis per task (TaskLord, `-fstack-usage`)
- DMA alignment: buffers must be word-aligned and in DMA-capable memory
- Volatile: use `volatile` for memory-mapped registers and ISR-shared variables
- Double-checked locking: banned unless memory barrier guarantees are clear

## Build & Flash

### Build
```bash
# CMake with toolchain file
cmake -B build -DCMAKE_TOOLCHAIN_FILE=arm-gcc-toolchain.cmake -DCMAKE_BUILD_TYPE=Release
cmake --build build

# PlatformIO
pio run -e {environment}
pio test -e {environment}

# Zephyr
west build -b {board} app/ -- -DCONF_FILE=prj.prod.conf
```

### Flash
```bash
# OpenOCD
openocd -f interface/stlink.cfg -f target/stm32g4x.cfg -c "program build/app.elf verify reset exit"

# J-Link
JLinkExe -device STM32G474RE -if SWD -speed 4000 -autoconnect 1 -CommanderScript flash.jlink

# STM32CubeProgrammer
STM32_Programmer_CLI -c port=SWD -w build/app.hex 0x08000000
```

### Debug Probe Configuration
| Probe | Interface | Speed | SWO |
|-------|-----------|-------|-----|
| ST-Link/V3 | SWD | 4 MHz | yes (UART) |
| J-Link EDU | SWD | 4 MHz | yes (pin 5) |
| Black Magic Probe | SWD + UART | 4 MHz | no |

## Dual-Layer AGENTS.md Strategy

When a project contains both hardware-near and algorithm-near code at significant scale, split documentation into two AGENTS.md files:

### Root AGENTS.md (hardware context)
- MCU specs, memory map, peripheral list
- Toolchain and cross-compilation setup
- Flash and debug instructions
- Safety and compliance rules
- RTOS configuration

### Algorithm subdirectory AGENTS.md (domain context)
- Control theory (PID gains, filter design, state estimation)
- Signal processing (FFT, sample rates, windowing)
- Sensor fusion algorithm and calibration
- Protocol logic and state machines

This split keeps hardware noise out of algorithm documentation and vice versa. The algorithm AGENTS.md is free to discuss numerical methods and control theory without needing to prefix every file path with hardware details.
