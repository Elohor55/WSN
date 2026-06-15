# Two-ESP32 Wokwi Split Simulation — Setup Guide

## Folder structure

```
board_A/
  diagram.json      ← left ESP32 (buttons 1-2-3, LEDs driven by Board B)
  wokwi.toml        ← points to COM3 (your end of the virtual pair)

board_B/
  diagram.json      ← right ESP32 (buttons 4-5-6, LEDs driven by Board A)
  wokwi.toml        ← points to COM4 (other end of the virtual pair)

SIMULATION.ino      ← identical sketch flashed to both boards
```

---

## Step 1 — Install a virtual COM port pair (com0com)

1. Download **com0com** (null-modem emulator):  
   https://sourceforge.net/projects/com0com/
2. Run the installer and open the **Setup** utility.
3. Create one pair, e.g. **COM3 ↔ COM4**.  
   (Tick *"use Ports class"* so they appear in Device Manager as real COM ports.)
4. Confirm both ports appear in Device Manager → Ports (COM & LPT).

---

## Step 2 — Open two VS Code windows

Open `board_A/` as the workspace in one VS Code window and  
`board_B/` in a second VS Code window.

Each folder must contain:
- `diagram.json`
- `wokwi.toml`
- A `build/` subfolder with the compiled `.bin` and `.elf`  
  (both windows share the same compiled output — see Step 3).

---

## Step 3 — Compile once, symlink (or copy) to both build folders

Compile `SIMULATION.ino` with **Arduino IDE** or **arduino-cli**:

```
arduino-cli compile --fqbn esp32:esp32:esp32 SIMULATION.ino \
  --output-dir build/
```

Then copy (or symlink) the `build/` folder into both `board_A/` and `board_B/`.

---

## Step 4 — Update COM port names in wokwi.toml

Edit `board_A/wokwi.toml` → set `"serial:COM3"` to your actual port A.  
Edit `board_B/wokwi.toml` → set `"serial:COM4"` to your actual port B.

---

## Step 5 — Start both simulations

In each VS Code window press **F1 → "Wokwi: Start Simulator"** (or the play button).  
Start Board A first, then Board B within a few seconds so the virtual link is live on both ends before either board begins transmitting.

---

## How it works

| | Board A | Board B |
|---|---|---|
| **Buttons** | btn1 (red), btn2 (green), btn3 (blue) | btn4 (red), btn5 (green), btn6 (blue) |
| **LEDs driven** | led1/led2/led3 (show Board B's buttons) | led1b/led2b/led3b (show Board A's buttons) |
| **Indicator** | GPIO 14 — white LED, always ON | GPIO 14 — white LED, always ON |
| **Link UART** | Serial2 → COM3 | Serial2 → COM4 |
| **Debug** | Serial → $serialMonitor | Serial → $serialMonitor |

### Protocol
Each board sends a 2-byte frame whenever its button state changes:

```
[ 0xAA ] [ state ]
           bit 0 = button 1 (or 4)
           bit 1 = button 2 (or 5)
           bit 2 = button 3 (or 6)
```

---

## Hardware note (real boards)

GPIO 16 = RX2 and GPIO 17 = TX2 on ESP32 DevKit C v4.  
These are the same pins used for `led1`/`led2` in the original diagram.  
This is fine in simulation (Wokwi handles the multiplexing), but on real  
hardware you should remap Serial2 to unused pins, e.g.:

```cpp
Serial2.begin(115200, SERIAL_8N1, 21, 22); // RX=GPIO21, TX=GPIO22
```
and wire accordingly.
