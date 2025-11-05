from multiprocessing import shared_memory
from multiprocessing.synchronize import Event as EventObject

from enum import Enum
import random as r
import time as t

import numpy as np
from silero_vad import load_silero_vad
import torch
from scipy.io.wavfile import write

import global_constants as gc
import common.time_utilies as time_util

from eaxtension import LogE

SAV_WAV_DEBUGGING = True

class DetectionState(Enum):
    deactivate = 0
    speech = 1
    pause = 2

def use_vad_based_recording(audio_stream_shm_name: str,
                            speech_data_shm_name: str,
                            speech_record_complete_flag: EventObject,
                            vad_stream_read_flag: EventObject,
                            transcript_loading_complete_flag: EventObject,
                            trascript_processing_flag: EventObject,
                            llm_response_generating_flag: EventObject,
                            tts_loading_complete_flag: EventObject,
                            tts_generating_flag: EventObject):
    
    wrt = 1

    PROCESS_NAME = "[vad_based_recording]"

    LogE.g(PROCESS_NAME, "process is started")
    
    # Access to shared memory
    # Audio stream
    audio_data_shm = shared_memory.SharedMemory(name=audio_stream_shm_name)
    audio_data_ndarr = np.ndarray(gc.audio.FRAMES_PER_BUFFER, 
                                  dtype=gc.audio.NDARRAY_DTYPE, 
                                  buffer=audio_data_shm.buf)
    # Recorded speech data
    speech_data_shm = shared_memory.SharedMemory(name=speech_data_shm_name)
    speech_data_ndarr = np.ndarray(gc.audio.SAMPLING_RATE * gc.vad.RECORDING_LIMIT,
                                   dtype=gc.audio.NDARRAY_DTYPE,
                                   buffer=speech_data_shm.buf)

    # Load VAD Model
    vad_model = load_silero_vad(onnx=gc.vad.USE_ONNX)
    
    # Flags
    detection_state = DetectionState(0)
    
    # Timers
    # Counting 'speech' duration if it's over SPEECH_LIMIT or not.
    speech_time = time_util.TimeChecker(gc.vad.SPEECH_LIMIT, print_log=True)
    # Counting Maintaining duration before switch the mode to 'pause'.
    speech_maintain_time = time_util.TimeChecker(gc.vad.MAINTAIN_LIMIT)
    # Counting 'pause' duration before terminate recording session.
    pause_time = time_util.TimeChecker(gc.vad.PAUSE_LIMIT)
    # Counting duration of whole recording session. If the duration over the RECORDING_LIMIT, the session will close.
    recording_time = time_util.TimeChecker(gc.vad.RECORDING_LIMIT)

    # Speech data storing arrays.
    speech_raw = []

    while (not transcript_loading_complete_flag.is_set()) or (not tts_loading_complete_flag.is_set()):
        pass

    LogE.g(PROCESS_NAME, "voice detection started.")
    dot = 1
    # Main loop
    while True:
        if not (trascript_processing_flag.is_set() or llm_response_generating_flag.is_set() or tts_generating_flag.is_set()):
            # Get audio data from shared memory.
            audio_data_tensor = torch.from_numpy(audio_data_ndarr) 

            # Get activity detetction probabilty
            speech_prob = vad_model(audio_data_tensor, 
                                    gc.audio.SAMPLING_RATE).item()

            # Evaluate the probability
            if speech_prob >= gc.vad.ACTIVATE_THRESHOLD:
                # If voice was detected by the model
                if detection_state.name == "deactivate":
                    # initialize the session
                    # initialize the storing arrays
                    speech_raw = []
                    # Start timers(initializing)
                    time_util.start_timers([speech_time, speech_maintain_time, pause_time, recording_time])
                    pause_time.pause()
                elif detection_state.name == "pause":
                    # resume the session to 'speech'
                    # restart the timers.
                    pause_time.restart()
                    pause_time.pause()
                    speech_time.resume()
                    speech_maintain_time.restart()
                    LogE.d("resume", speech_time.get_time())
                elif detection_state.name == "speech":
                    # When the user starts mumbling
                    speech_maintain_time.restart()
                # If the probability is over threshold, should update the state to speech always.
                detection_state = DetectionState.speech
            else:
                # If the voice wasn't detected by the model
                if speech_maintain_time.is_over():
                    if detection_state.name == "speech":
                        # Start/Pause the timers
                        speech_time.pause()
                        pause_time.resume()
                        # Change the flag to 'pause'
                        detection_state = DetectionState.pause
                        LogE.d("pause", pause_time.get_time())
                    else:
                        # Maintain the state as 'pause'
                        LogE.p("pausing", pause_time.get_time(), gc.vad.PAUSE_LIMIT)
                        pass
                else:
                    if detection_state.name == "speech":
                        LogE.p("speech maintaining", speech_maintain_time.get_time(), gc.vad.MAINTAIN_LIMIT)
                    else:
                        print(f"listening{'.' * (dot%3)}", end="\r")
                        if dot <= 30:
                            dot += 1
                        else: 
                            dot = 0

            # Capture speech frames and store in arrays.
            if detection_state.name != "deactivate" and (not vad_stream_read_flag.is_set()):
                # speech_data.append(audio_data_tensor)
                speech_raw.append(audio_data_ndarr.astype(np.int16))
                vad_stream_read_flag.set()
            
            # Check time over 
            if recording_time.is_over() or (detection_state.name != "deactivate" and (speech_time.is_over() or pause_time.is_over())):
                # Clear time checker and reset the state.
                detection_state = DetectionState.deactivate
                if recording_time.is_over():
                    # Indicate recording time over
                    LogE.d(PROCESS_NAME, "timeover")
                time_util.clear_timers([speech_time, speech_maintain_time, pause_time, recording_time])
               
                # Serialize speech data array
                speech_raw = np.concatenate(speech_raw, axis=0).astype(np.int16)
                
                # Sav speech data to wav file
                if SAV_WAV_DEBUGGING:
                    name = int(r.random()*100)
                    write(f'./audio_files/{name}.wav', gc.audio.SAMPLING_RATE, speech_raw)
                    LogE.d(PROCESS_NAME, f"'{name}.wav' was created in 'audio_files' directory.")
                
                # padding 0 to match the size of ndarray between data and shm.
                pad_size = speech_data_ndarr.size - speech_raw.size
                LogE.d("speech_raw", pad_size)
                if pad_size > 0:
                    speech_raw = np.pad(speech_raw, (0, pad_size), "constant", constant_values=0)
                np.copyto(speech_data_ndarr, speech_raw)
                
                speech_record_complete_flag.set()
                
                if wrt == 1:
                    wrt = 0
                    np.save("./raw_vad.npy", speech_raw)
                    np.save("./shm_vad.npy", speech_data_ndarr)
                
                # Clear speech data array
                speech_raw = []
            else:
                pass