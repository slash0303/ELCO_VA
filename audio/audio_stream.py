from multiprocessing import shared_memory
from multiprocessing.synchronize import Event as EventObject

import pyaudio

import numpy as np

import global_constants as gc
from eaxtension import LogE

def use_audio_stream(get_audio_flag: EventObject,
                     audio_data_shm_name: shared_memory,
                     vad_stream_read: EventObject):
    PROCESS_NAME = "[audio stream]"

    LogE.g(PROCESS_NAME, "process is started")
    
    pa = pyaudio.PyAudio()

    stream = pa.open(channels=gc.audio.CHANNELS,
                     input=True,
                     format=gc.audio.FORMAT,
                     rate=gc.audio.SAMPLING_RATE,
                     frames_per_buffer=gc.audio.FRAMES_PER_BUFFER,
                     input_device_index=0)
    
    audio_data_mem = shared_memory.SharedMemory(name=audio_data_shm_name)
    audio_data_buf = np.ndarray(gc.audio.FRAMES_PER_BUFFER, 
                                dtype=gc.audio.NDARRAY_DTYPE, 
                                buffer=audio_data_mem.buf)

    while True:
        if get_audio_flag.is_set():
            audio_data = np.frombuffer(stream.read(gc.audio.FRAMES_PER_BUFFER), 
                                       dtype=np.int16)
            np.copyto(audio_data_buf, audio_data)
            vad_stream_read.clear()
        else:
            pass