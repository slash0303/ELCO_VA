from pygrabber.dshow_graph import FilterGraph

devices = FilterGraph().get_input_devices()
for i, name in enumerate(devices):
    print(f"Camera {i}: {name}")

import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(i, info.get('name'), info.get('maxInputChannels'))