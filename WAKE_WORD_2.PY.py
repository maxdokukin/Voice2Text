# wake_word_snowboy.py

import sys
import signal
from snowboy import snowboydecoder

MODEL = "model/jarvis.umdl"
SENSITIVITY = 0.8  # Snowboy’s Jarvis model uses two sensitivities; here we’ll just use one

def detected_callback():
    print("🔔 Wake‑word detected!")

if __name__ == "__main__":
    # handle Ctrl‑C cleanly
    def signal_handler(sig, frame):
        detector.terminate()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # instantiate detector
    detector = snowboydecoder.HotwordDetector(
        MODEL,
        sensitivity=[SENSITIVITY, SENSITIVITY],
        apply_frontend=True  # recommended for universal models
    )

    print("🎙️  Listening for ‘Jarvis’ (Ctrl‑C to quit)…")
    detector.start(
        detected_callback=detected_callback,
        interrupt_check=lambda: False,
        sleep_time=0.03
    )
