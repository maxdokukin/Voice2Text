import sys
import os
import signal
import threading
import serial
from pocketsphinx import LiveSpeech

# Wake word model directory
MODEL_DIR = os.path.expanduser(
    "/Users/xewe/Documents/Programming/Python/Voice2Text/model/cmusphinx-en-us-5.2"
)
# Keyword to detect
KEYPHRASE = "jarvis"

# Serial config (same as reference)
SERIAL_PORT = "/dev/cu.usbmodem101"
BAUDRATE = 115200

# Commands to send (same as reference)
CMD1 = "$led turn_on\n$led set_rgb 0 255 255\n$led set_brightness 255\n"
CMD2 = "$led turn_off\n"

# 1. Open serial port
def open_serial():
    try:
        s = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
        print(f"🔌 Serial port open at {SERIAL_PORT} @ {BAUDRATE} baud")
        return s
    except Exception as e:
        print(f"Could not open serial port {SERIAL_PORT}: {e}", file=sys.stderr)
        sys.exit(1)

ser = open_serial()

# Send functions

def send_cmd1_and_schedule_cmd2():
    """Send CMD1 immediately, then schedule CMD2 2s later."""
    try:
        ser.write(CMD1.encode("utf-8"))
        print(f"➡️ Sent: {CMD1.strip()}")
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

# Detection callback

def detected_callback():
    print("🔔 Wake‑word detected!")
    send_cmd1_and_schedule_cmd2()

# Configure keyword spotting with pocketsphinx
speech = LiveSpeech(
    verbose=False,
    sampling_rate=16000,
    buffer_size=2048,
    no_search=False,
    full_utt=False,
    hmm=MODEL_DIR,
    keyphrase=KEYPHRASE,
    kws_threshold=1e-20
)

# 2. Handle Ctrl‑C cleanly
def signal_handler(sig, frame):
    if ser and ser.is_open:
        ser.close()
    print("\n🛑 Exiting...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 3. Start listening loop
print(
    f"🎙️ Listening for ‘{KEYPHRASE.capitalize()}’ (Ctrl‑C to quit)…\n"
)
for phrase in speech:
    text = str(phrase).strip().lower()
    if text == KEYPHRASE:
        detected_callback()
