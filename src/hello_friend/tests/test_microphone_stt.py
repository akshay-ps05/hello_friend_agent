import os
import tempfile
import wave

import numpy as np
import sounddevice as sd
import riva.client
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("NVIDIA_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "NVIDIA_API_KEY is not set. "
        "Check your .env file."
    )

SAMPLE_RATE = 16000
SECONDS = 5

API_KEY = os.getenv(
    "NVIDIA_API_KEY"
)

if not API_KEY:

    raise RuntimeError(
        "NVIDIA_API_KEY is not set."
    )


print("Recording...")

audio = sd.rec(
    int(
        SAMPLE_RATE
        * SECONDS
    ),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
)

sd.wait()

print("Recording complete.")


with tempfile.NamedTemporaryFile(
    suffix=".wav",
    delete=False,
) as tmp:

    wav_path = tmp.name


with wave.open(
    wav_path,
    "wb",
) as wav:

    wav.setnchannels(1)

    wav.setsampwidth(2)

    wav.setframerate(
        SAMPLE_RATE
    )

    wav.writeframes(
        audio.tobytes()
    )


print(
    "WAV:",
    wav_path,
)


auth = riva.client.Auth(
    use_ssl=True,

    uri="grpc.nvcf.nvidia.com:443",

    metadata_args=[
        (
            "function-id",
            "b702f636-f60c-4a3d-a6f4-f3568c13bd7d",
        ),
        (
            "authorization",
            f"Bearer {API_KEY}",
        ),
    ],
)


asr = riva.client.ASRService(
    auth
)


with open(
    wav_path,
    "rb",
) as f:

    data = f.read()


config = riva.client.RecognitionConfig(
    language_code="en",
    max_alternatives=1,
    enable_automatic_punctuation=True,
)


response = asr.offline_recognize(
    data,
    config,
)


print("\n========== RESULT ==========")

for result in response.results:

    if result.alternatives:

        print(
            result.alternatives[0].transcript
        )

print("============================")