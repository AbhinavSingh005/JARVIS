import sounddevice as sd
import vosk
import queue
import sys
import json
import threading
from pathlib import Path

def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


BASE_DIR = get_base_dir()


MODEL_PATH = BASE_DIR / "vosk-model-small-en-us-0.15"

if not MODEL_PATH.exists():
    MODEL_PATH = Path("C:\\Users\\abhinav singh\\Downloads\\vosk-model-small-en-us-0.15\\vosk-model-small-en-us-0.15")

print("Loading speech model...")
model = vosk.Model(str(MODEL_PATH))
print("Speech model loaded.")

q = queue.Queue()
stop_listening_flag = threading.Event()


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))


def clean_text(text: str) -> str:
    text = text.lower().strip()

    wake_words = [
        "jarvis",
        "hey jarvis",
        "ok jarvis"
    ]

    for w in wake_words:
        text = text.replace(w, "")

    text = text.strip()

    return text


def record_voice(prompt="🎙 Listening..."):
    print(prompt)

    rec = vosk.KaldiRecognizer(model, 16000)

    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):

        while not stop_listening_flag.is_set():

            try:
                data = q.get(timeout=0.1)
            except queue.Empty:
                continue

            if rec.AcceptWaveform(data):

                result = json.loads(rec.Result())
                text = result.get("text", "")

                text = clean_text(text)

                if text:
                    print("👤 You:", text)
                    return text

    return ""


def stop_listening():
    stop_listening_flag.set()


def start_listening():
    stop_listening_flag.clear()