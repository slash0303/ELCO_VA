from silero_vad import VADIterator, load_silero_vad
from pyaudio import PyAudio, paInt16
from copy import deepcopy

import numpy as np
import torch

USE_ONNX = False
SAMPLING_RATE = 16000

def use_vad():
    # <pa>
    # Constants for stream
    CHANNELS = 1
    FORMAT = paInt16
    SAMPLING_RATE = 16000
    FRAMES_PER_BUFFER = 512

    pa = PyAudio()

    pa_stream = pa.open(rate=SAMPLING_RATE,
                        format=FORMAT,
                        channels=CHANNELS,
                        input=True,
                        frames_per_buffer=FRAMES_PER_BUFFER)
    
    vad_model = load_silero_vad(onnx=USE_ONNX, opset_version=16)
    vad_iterator = VADIterator(model=vad_model, sampling_rate=SAMPLING_RATE, threshold=0.3)
    
    while True:
        stream_data = pa_stream.read(FRAMES_PER_BUFFER)
        data = np.frombuffer(stream_data, dtype=np.int16)
        data_mut = deepcopy(data)
        data_mut = torch.from_numpy(data_mut)
        # print(len(data_mut))

        speech_dict = vad_iterator(data_mut, return_seconds=False)
        # print(data_mut)
        # print(speech_dict)
        speech_prob = vad_model(data_mut, SAMPLING_RATE).item()
        print("*" * int(speech_prob*10))
        # vad_iterator.reset_states()

if __name__ == "__main__":
    use_vad()