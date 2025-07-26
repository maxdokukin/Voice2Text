# silero.py

import ssl
import os
import torch
torch.set_num_threads(12)

import numpy as np
import sounddevice as sd
import queue

# 0. If you haven’t already: pin NumPy to 1.x in your venv:
#    pip install "numpy<2.0.0"

# Workaround for any SSL cert issues
ssl._create_default_https_context = ssl._create_unverified_context

# Path to your local clone of snakers4/silero-models
REPO_PATH = os.path.expanduser("~/Downloads/silero-models")

# 1. Load Silero STT (xxsmall) from the local repo
device = torch.device("cpu")
model, decoder, utils = torch.hub.load(
    repo_or_dir=REPO_PATH,
    model="silero_stt",
    language="en",
    device=device,
    source="local"
)

# We only need the prepare_model_input util
# (it takes a list of torch.Tensor audio chunks)
*_, prepare_model_input = utils

# 2. Audio queue and callback
audio_q = queue.Queue()
def audio_callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Audio status: {status}")
    # grab mono channel
    audio_q.put(indata[:, 0].copy())

def main():
    # 3. Open Stream: 16 kHz, mono, blocks of 8000 samples (~0.5 s)
    stream = sd.InputStream(
        samplerate=16_000,
        blocksize=8_000,
        channels=1,
        dtype="float32",
        callback=audio_callback
    )
    with stream:
        print("🎙️  Listening (Ctrl‑C to stop)…")
        buffer = np.zeros(0, dtype=np.float32)

        while True:
            # 4. Get next chunk and append to buffer
            chunk = audio_q.get()
            buffer = np.concatenate((buffer, chunk))

            # 5. When we have ≥1 s of audio, transcribe it
            while len(buffer) >= 16_000:
                frame, buffer = buffer[:16_000], buffer[16_000:]

                # 6. Convert to torch.Tensor (shape [16000]) and pack into a batch
                wav_tensor = torch.from_numpy(frame).float()
                inp = prepare_model_input([wav_tensor], device=device)

                # 7. Inference + decode
                out = model(inp)             # list of logits tensors
                text = decoder(out[0]).strip()
                if text:
                    print(f"🗣️  You said: {text}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑  Stopped by user")
