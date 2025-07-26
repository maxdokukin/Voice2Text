# wake_word_vosk.py

import os
import sys
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

WAKE_PHRASE = "jarvis"

def audio_callback(indata, frames, time, status):
    """Push raw mic data (int16 PCM) into the queue."""
    if status:
        print(f"⚠️ Audio status: {status}", file=sys.stderr)
    audio_q.put(bytes(indata))

def main(model_path: str, device: int = None):
    if not os.path.isdir(model_path):
        print(f"Model not found at {model_path}", file=sys.stderr)
        sys.exit(1)

    # 1. Load Vosk model
    model = Model(model_path)
    sample_rate = 16000
    recognizer = KaldiRecognizer(model, sample_rate)

    # 2. Prepare audio stream
    global audio_q
    audio_q = queue.Queue()
    stream = sd.RawInputStream(
        samplerate=sample_rate,
        blocksize=8000,
        dtype='int16',
        channels=1,
        device=device,            # None = default input
        callback=audio_callback
    )

    print(f"🎙️ Listening for “{WAKE_PHRASE}” (Ctrl‑C to quit)…")
    with stream:
        try:
            while True:
                data = audio_q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if WAKE_PHRASE in text.lower():
                        print(f"🔔 Detected wake‑phrase at {result.get('result', [{}])[0].get('end', 0):.2f}s")
                # (You can also inspect recognizer.PartialResult() if you want lower latency.)
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")

if __name__ == "__main__":
    # pass the path to your unzipped Vosk model here
    MODEL_PATH = "model/vosk-model-en-us-0.22"
    # optionally, find your mic device index with `sd.query_devices()`
    main(MODEL_PATH)
