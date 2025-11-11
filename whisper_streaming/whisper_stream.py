from multiprocessing.synchronize import Event as EventObject
from multiprocessing import shared_memory

import numpy as np

from faster_whisper import WhisperModel

import global_constants as gc
from eaxtension import LogE

import simpleaudio as sa


def use_transcript(
    speech_data_shm_name: str,
    transcript_enable_flag: EventObject,
    transcript_complete_flag: EventObject,
    transcript_loading_complete_flag: EventObject,
    transcript_processing_flag: EventObject,
    loading_complete_flag: EventObject):

    PROCESS_NAME = "[whisper stream]"
    
    model = WhisperModel("small", device="cpu", compute_type="int8")

    LogE.g(PROCESS_NAME, "process is started")

    # Get speech data from shm
    speech_data_shm = shared_memory.SharedMemory(name=speech_data_shm_name)
    speech_data = np.ndarray(shape=gc.audio.SAMPLING_RATE * gc.vad.RECORDING_LIMIT,
                             dtype=gc.audio.NDARRAY_DTYPE,
                             buffer=speech_data_shm.buf)

    transcript_loading_complete_flag.set()

    write_shm = 0

    while not loading_complete_flag.is_set():
        pass

    while True:
        # if the recording of speech data has been completed
        if transcript_enable_flag.is_set():
            transcript_processing_flag.set()
            LogE.d(PROCESS_NAME, "transcription start")
            if write_shm:
                np.save("shm.npy", speech_data)
                LogE.g(PROCESS_NAME, "shm.txt was written.")
                write_shm = 0
            
            LogE.d(PROCESS_NAME, "transcribing")
            segments, info = model.transcribe(
                (speech_data.astype(np.float32)/32767),
                beam_size=5,
                language="ko",
                vad_filter=True,
                initial_prompt="This audio is about the request that user speaks to voice assistant speaker."
            )
            LogE.d(PROCESS_NAME, "transcription complete")

            speech_text = ""
            for segment in segments:
                speech_text += segment.text + " "

            if not speech_text == "":   
                # Write script as a txt file
                with open("./trans.txt", "w", encoding="utf-8") as f:
                    f.write(speech_text)
                    LogE.g("The file was written by 'whisper_stream.py'", str(speech_text))
                transcript_complete_flag.set()
            else:
                LogE.g(PROCESS_NAME, "transcripted text is empty")
                audio_file = "./sry.wav"
                wav_obj = sa.WaveObject.from_wave_file(audio_file)
                play_obj = wav_obj.play()
                play_obj.wait_done()
                pass
                # 잘 알아듣지 못했어요. 어쩌구 저쩌구
                # send query로 갈게 아니라 위의 문장 재생하고 다시 vad로 돌려야 함.
                 
            transcript_processing_flag.clear()
            transcript_enable_flag.clear()