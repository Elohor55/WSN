"""
bridge.py — RFC2217 bridge between two Wokwi ESP32 simulations
---------------------------------------------------------------
Board A  <--RFC2217:5001-->  [this script]  <--RFC2217:5002-->  Board B

Install dependency first:
    pip install pyserial

Run AFTER both Wokwi simulations are already started:
    python bridge.py

Requires Python 3.6+
"""

import threading
import time
import sys

try:
    import serial
    from serial.rfc2217 import Serial as Rfc2217Serial
except ImportError:
    print("[bridge] ERROR: pyserial not found. Run:  pip install pyserial")
    sys.exit(1)

BOARD_A_URL  = "rfc2217://localhost:5001"
BOARD_B_URL  = "rfc2217://localhost:5002"
BAUD         = 115200
RETRY_DELAY  = 2
BUF_SIZE     = 256


def connect_with_retry(name: str, url: str) -> serial.Serial:
    while True:
        try:
            s = serial.serial_for_url(url, baudrate=BAUD, timeout=0.1)
            print(f"[bridge] Connected to {name}  ({url})")
            return s
        except Exception as e:
            print(f"[bridge] Waiting for {name}... ({e})")
            time.sleep(RETRY_DELAY)


def forward(src_name: str, src: serial.Serial,
            dst_name: str, dst: serial.Serial):
    while True:
        try:
            data = src.read(BUF_SIZE)
            if not data:
                continue
            # Debug: decode frames [ 0xAA | state ]
            i = 0
            while i < len(data) - 1:
                if data[i] == 0xAA:
                    print(f"[bridge] {src_name} → {dst_name}  "
                          f"state=0b{data[i+1]:03b}")
                    i += 2
                else:
                    i += 1
            dst.write(data)
        except Exception as e:
            print(f"[bridge] Error on {src_name}: {e}")
            break


def main():
    print("=" * 55)
    print("  Wokwi RFC2217 Bridge")
    print("  Board A :5001  <-->  Board B :5002")
    print("  Start both Wokwi simulations first, then run this.")
    print("  Press Ctrl+C to stop.")
    print("=" * 55)

    port_a = connect_with_retry("Board A", BOARD_A_URL)
    port_b = connect_with_retry("Board B", BOARD_B_URL)

    print("[bridge] Both boards connected — forwarding traffic.\n")

    t1 = threading.Thread(target=forward,
                          args=("Board A", port_a, "Board B", port_b),
                          daemon=True)
    t2 = threading.Thread(target=forward,
                          args=("Board B", port_b, "Board A", port_a),
                          daemon=True)
    t1.start()
    t2.start()

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\n[bridge] Stopped by user.")
    finally:
        port_a.close()
        port_b.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
