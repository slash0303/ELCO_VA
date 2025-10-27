import pyaudio
import numpy as np

class audio:
    CHANNELS = 1
    FORMAT = pyaudio.paInt16
    SAMPLING_RATE = 16000
    FRAMES_PER_BUFFER = 512
    NDARRAY_DTYPE = np.int16

class vad:
    SPEECH_LIMIT = 30
    PAUSE_LIMIT = 2
    RECORDING_LIMIT = 60
    MAINTAIN_LIMIT = 0.5
    
    USE_ONNX = True
    ACTIVATE_THRESHOLD = 0.3