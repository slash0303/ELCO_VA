
from melo.api import TTS

# from multiprocessing.synchronize import Event as EventObject
# from multiprocessing import Process, Queue, Event

# from eaxtension import LogE

# import simpleaudio as sa

# import os

# tts option values
SPEED = 1.5
DEVICE = "cpu"

# load tts model
model = TTS(language='KR', device=DEVICE)
speaker_ids = model.hps.data.spk2id

while True:
    inp = input("prompt: ")
    if inp == "-1":
        break
    # generate tts file
    audio_file = f"a.wav"
    model.tts_to_file(inp, speaker_ids['KR'], audio_file, speed=SPEED)
