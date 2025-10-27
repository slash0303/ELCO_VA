from pyaudio import PyAudio, paInt16

def use_audio_stream():
    # Constants for stream
    CHANNELS = 1
    FORMAT = paInt16
    SAMPLING_RATE = 16000
    FRAMES_PER_BUFFER = 1024

    pa = PyAudio()

    pa_stream = pa.open(rate=SAMPLING_RATE,
                        format=FORMAT,
                        channels=CHANNELS,
                        input=True,
                        frames_per_buffer=FRAMES_PER_BUFFER)
    
    data = pa_stream.read(FRAMES_PER_BUFFER)