"""
Simple activation phrase detector using Vosk.

Setup:
    create a python virtual environment and activate it:
        python3 -m venv venv
    pip install vosk sounddevice
    Download a small model from https://alphacephei.com/vosk/models
    (e.g. vosk-model-small-en-us-0.15), unzip it, and point MODEL_PATH at it.

Run:
    python3 voice_interface.py
"""

import json
import queue
import sys

import sounddevice as sd
from vosk import KaldiRecognizer, Model, SetLogLevel




INTENT_RULES = {
    "go_forward": ["forward", "ahead", "go", "move"],
    "turn": ["turn", "right", "left", "go", "move"],
    "transcribe": ["hear", "listen", "transcribe", "saying", "conversation"],
    "translate": ["understand" "translate", "language", "saying", "conversation"],
    "stop": ["stop"],
    "wave": ["hey", "hello", "hi", "whats up", "how are you"],
    "you're welcome": ["thank"]
}

KEYWORDS = [
    "forward",
    "ahead",
    "go",
    "move",
    "turn",
    "right",
    "left",
    "hear",
    "listen",
    "transcribe",
    "saying",
    "conversation",
    "understand",
    "translate",
    "language",
    "stop",
    "hey",
    "hello",
    "hi",
    "whats up",
    "how are you",
    "thank",
]

LANGUAGES = ["spanish", "french"]

def classify_intent(user_speech: str) -> str:
    detected_intent = "unknown_intent"
    detected_language = None
    done = False

    # Clean the input text
    cleaned_input = user_speech.lower().strip()
    # Check text against rules
    intent_scores = {}
    for intent, keywords in INTENT_RULES.items():
        for keyword in keywords:
            if keyword in cleaned_input:
                intent_scores[intent] = intent_scores.get(intent, 0) + 1

        if intent == "translate":
            for language in LANGUAGES:
                if language in cleaned_input:
                    intent_scores[intent] = intent_scores.get(intent, 0) + 1

    if len(intent_scores) != 0:
        detected_intent = max(intent_scores, key=intent_scores.get)
    print(intent_scores)
    return (detected_intent, intent_scores.get(detected_intent))





MODEL_PATH = "./models/vosk-model-small-en-us-0.15"
# MODEL_PATH = "./models/vosk-model-en-us-0.22"
WAKE_PHRASE = "scrappy"
SAMPLE_RATE = 16000

SetLogLevel(-1)  # silence Vosk's logging

audio_q: "queue.Queue[bytes]" = queue.Queue()
model = Model(MODEL_PATH)


def audio_callback(indata, frames, time_info, status):
    if status:
        print(status, file=sys.stderr)
    audio_q.put(bytes(indata))


def transcribe_until_silence(
    rec,
    sample_rate=SAMPLE_RATE,
    silence_timeout=1.0,   # seconds of silence after speech that ends the recording
    initial_timeout=2.0,   # give up if nobody starts talking within this long
    max_duration=10.0,     # hard cap on total length
):
    # """Read audio chunks from audio_q and return the transcribed text."""
    # Throw away audio that piled up before we started (e.g. the wake phrase).
    # while not audio_q.empty():
        # audio_q.get_nowait()

    # raw = [KEYWORDS, ["[unk]"]]
    # grammar = json.dumps([string for sublist in raw for string in sublist])

    # rec = KaldiRecognizer(model, sample_rate, grammar)  # full vocabulary, no grammar
    # rec = KaldiRecognizer(model, sample_rate)  # full vocabulary, no grammar


    parts = []
    elapsed = 0.0          # measured in seconds of audio processed
    last_speech = 0.0
    last_partial = ""
    heard_speech = False

    while elapsed < max_duration:
        try:
            data = audio_q.get(timeout=1.0)
        except queue.Empty:
            continue
        elapsed += len(data) / (sample_rate * 2)

        if rec.AcceptWaveform(data):
            text = json.loads(rec.Result()).get("text", "")
            if text:
                parts.append(text)
                heard_speech = True
                last_speech = elapsed
                last_partial = ""
        else:
            partial = json.loads(rec.PartialResult()).get("partial", "")
            # A changing partial means the person is still talking.
            if partial and partial != last_partial:
                heard_speech = True
                last_speech = elapsed
            last_partial = partial

        if heard_speech and elapsed - last_speech >= silence_timeout:
            break
        if not heard_speech and elapsed >= initial_timeout:
            break

    final = json.loads(rec.FinalResult()).get("text", "")
    if final:
        parts.append(final)

    return " ".join(parts).strip()



def on_wake(rec):
    print(">>> Wake phrase detected! <<<")
    transcription = transcribe_until_silence(rec)
    print(f"You said: '{transcription}'")
    print(f"Detected Command: [{classify_intent(transcription)}]")
    


def main():

    # restricting the grammar to the wake phrase (plus [unk] for everything
    # else) makes recognition faster and far more accurate for this use case.
    # grammar = json.dumps([WAKE_PHRASE, "[unk]"])
    # rec = KaldiRecognizer(model, SAMPLE_RATE, grammar)
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    print(f'Listening for "{WAKE_PHRASE}"... (Ctrl+C to quit)')

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=4000,
        dtype="int16",
        channels=1,
        callback=audio_callback,
    ):
        while True:
            final_text = ""
            partial_text = ""
            data = audio_q.get()
            if rec.AcceptWaveform(data):
                final_text = json.loads(rec.Result()).get("text", "")
            else:
                partial_text = json.loads(rec.PartialResult()).get("partial", "")
                print(f"You are saying: '{partial_text}'")

            if WAKE_PHRASE in partial_text:
                on_wake(rec)
                rec.Reset()  # clear state


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped.")