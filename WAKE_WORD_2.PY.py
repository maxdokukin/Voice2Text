# wake_word_serial.py

import sys
import signal
import threading
import serial
from snowboy import snowboydecoder
import subprocess

MODEL = "model/jarvis.umdl"
SENSITIVITY = 0.5
SERIAL_PORT = "/dev/cu.usbmodem101"
BAUDRATE = 115200

# Commands to send
CMD1 = "$led turn_on\n$led set_rgb 0 255 255\n$led set_brightness 255\n"
CMD2 = "$led turn_off\n"

def send_cmd1_and_schedule_cmd2():
    """Send CMD1 immediately, then schedule CMD2 2s later."""
    try:
        threading.Thread(
            target=subprocess.run,
            args=(["afplay", "t2v/output_male.wav"],),
            daemon=True
        ).start()
        ser.write(CMD1.encode("utf-8"))
        print(f"➡️ Sent: {CMD1.strip()}")
        # schedule CMD2 in 2 seconds without blocking
        threading.Timer(2.0, send_cmd2).start()
    except Exception as e:
        print(f"❗️ Failed to write CMD1: {e}")

def send_cmd2():
    """Send CMD2."""
    try:
        ser.write(CMD2.encode("utf-8"))
        print(f"➡️ Sent: {CMD2.strip()}")
    except Exception as e:
        print(f"❗️ Failed to write CMD2: {e}")

def detected_callback():
    print("🔔 Wake‑word detected!")
    # fire-and-forget background sequence
    send_cmd1_and_schedule_cmd2()

if __name__ == "__main__":
    # 1. Open serial port
    try:
        ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    except Exception as e:
        print(f"Could not open serial port {SERIAL_PORT}: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Handle Ctrl‑C cleanly
    def signal_handler(sig, frame):
        detector.terminate()
        ser.close()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # 3. Initialize Snowboy detector
    detector = snowboydecoder.HotwordDetector(
        MODEL,
        sensitivity=[SENSITIVITY, SENSITIVITY],
        apply_frontend=True
    )

    print(
        f"🎙️ Listening for ‘Jarvis’ (Ctrl‑C to quit)…\n"
        f"🔌 Serial port open at {SERIAL_PORT} @ {BAUDRATE} baud"
    )
    detector.start(
        detected_callback=detected_callback,
        interrupt_check=lambda: False,
        sleep_time=0.03
    )
