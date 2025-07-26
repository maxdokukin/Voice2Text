import os
import sys
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Path to the unzipped Vosk model directory
# MODEL_PATH = "model/vosk-model-small-en-us-0.15"
MODEL_PATH = "model/vosk-model-en-us-0.22"

if not os.path.isdir(MODEL_PATH):
    print(f"Please download the model and unzip it to {MODEL_PATH}", file=sys.stderr)
    sys.exit(1)

# 1. Load the Vosk model
model = Model(MODEL_PATH)
sample_rate = 16000
recognizer = KaldiRecognizer(model, sample_rate)

# 2. Thread‑safe queue & audio callback
audio_q = queue.Queue()
def audio_callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Audio status: {status}", file=sys.stderr)
    # Wrap the CFFI buffer in bytes() so Vosk gets a proper bytes object
    audio_q.put(bytes(indata))

# 3. Start the microphone stream
with sd.RawInputStream(samplerate=sample_rate,
                       blocksize=8000,
                       dtype='int16',
                       channels=1,
                       callback=audio_callback):
    print("🎙️  Listening (Ctrl‑C to stop)…")
    try:
        while True:
            data = audio_q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                print(f"🗣️  You said: {result.get('text','')}")
            else:
                # You can inspect partial results if you like:
                # partial = json.loads(recognizer.PartialResult())
                # print(f"...{partial.get('partial','')}")
                pass

    except KeyboardInterrupt:
        print("\n🛑  Stopped by user")
