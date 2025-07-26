from TTS.api import TTS

# List available models
print(TTS.list_models())

# Load a pretrained model (e.g. “tts_models/en/vctk/vits”)
tts = TTS(model_name="tts_models/en/vctk/vits", progress_bar=False, gpu=False)

# Synthesize to file
tts.tts_to_file(text="Hello, world!", speaker_wav=None, language="en", file_path="output.wav")
