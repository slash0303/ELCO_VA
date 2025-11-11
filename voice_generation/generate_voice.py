from melo.api import TTS

from multiprocessing.synchronize import Event as EventObject
# from multiprocessing import Process, Queue, Event

from eaxtension import LogE

import simpleaudio as sa

import os

def use_generate_voice(llm_response_generated_flag: EventObject,
                       tts_loading_complete_flag: EventObject,
                       tts_generating_flag: EventObject,
                       tts_generated_flag: EventObject,
                       loading_complete_flag: EventObject):
    
    PROCESS_NAME = "[tts generate voice]"
    LogE.g(PROCESS_NAME, "process started.")
    
    llm_response = ""

    # tts option values
    SPEED = 1.5
    DEVICE = "cpu"

    # load tts model
    model = TTS(language='KR', device=DEVICE)
    speaker_ids = model.hps.data.spk2id

    tts_loading_complete_flag.set()
    LogE.d(PROCESS_NAME, "loading complete")

    while not loading_complete_flag.is_set():
        pass

    while True:
        if llm_response_generated_flag.is_set():
            LogE.d(PROCESS_NAME, "tts generating")
            tts_generating_flag.set()
            
            # load response of model from 'response.txt' file
            with open("./response.txt", "r", encoding="utf-8") as f:
                llm_response = f.read()

            if "out.wav" in os.listdir("./voices"):
                os.remove("./voices/out.wav")

            # generate tts file
            audio_file = "./voices/out.wav"
            model.tts_to_file(llm_response, speaker_ids['KR'], audio_file, speed=SPEED)

            # play tts file
            LogE.d(PROCESS_NAME, "Speaking")
            # absolute_audio_path = os.path.abspath(audio_file)
            # playsound.playsound(audio_file)
            wav_obj = sa.WaveObject.from_wave_file(audio_file)
            play_obj = wav_obj.play()
            play_obj.wait_done()
            print(end="\r")

            tts_generated_flag.set()
            tts_generating_flag.clear()
            llm_response_generated_flag.clear()