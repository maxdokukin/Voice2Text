from TTS.api import TTS
import subprocess

# 1. Load the multi‑speaker VCTK model
tts = TTS(model_name="tts_models/en/vctk/vits", gpu=False)

# 2. See which speaker IDs are available
print("Available speakers:", tts.speakers)

# 3. Pick a male speaker ID.
#    Usually the first few IDs in VCTK are male voices; you can experiment.
male_speaker = tts.speakers[2]

# 4. Synthesize with that speaker
tts.tts_to_file(
    text="What's up",
    speaker=male_speaker,
    file_path="output_male.wav"
)

# 5. Play it
subprocess.run(["afplay", "output_male.wav"])
