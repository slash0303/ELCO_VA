import onnxruntime
onnxruntime.set_default_logger_severity(3)

from multiprocessing import Event, shared_memory, Process

import numpy as np

import global_constants as gc
from eaxtension import LogE

from audio.audio_stream import use_audio_stream
from VAD.voice_detection import use_vad_based_recording
from whisper_streaming.whisper_stream import use_transcript
from Llm.llm_send_query import use_ai_response

if __name__ == "__main__":

    # loading complete flags
    # transcript(faster-whisper)
    transcript_loading_complete_event = Event()
    transcript_loading_complete_event.clear()

    # transcripting flag
    transcript_processing_event = Event()
    transcript_processing_event.clear()

    # llm response generating flag
    llm_response_generating_event = Event()
    llm_response_generating_event.clear()

    # Audio stream process
    audio_stream_enable_event = Event()
    audio_stream_enable_event.set()

    # Flag for frame management of vad based recording.
    vad_stream_read_event = Event()
    vad_stream_read_event.clear()

    # TODO: ready 이벤트들 만들기(초기 실행 때 다 준비 되면 일제히 작업 수행하도록 만들기)

    audio_stream_shm = shared_memory.SharedMemory(create=True, 
                                                  size=np.zeros(gc.audio.FRAMES_PER_BUFFER, 
                                                                dtype=gc.audio.NDARRAY_DTYPE).nbytes,
                                                  name="audio_stream")

    Process(target=use_audio_stream, 
            args=(audio_stream_enable_event, 
                  audio_stream_shm.name,
                  vad_stream_read_event)).start()

    # VAD process
    speech_record_complete_event = Event()
    speech_record_complete_event.clear()

    speech_data_shm = shared_memory.SharedMemory(create=True,
                                                 size=np.zeros(gc.audio.SAMPLING_RATE * gc.vad.RECORDING_LIMIT, 
                                                               dtype=gc.audio.NDARRAY_DTYPE).nbytes,
                                                 name="speech_data")

    Process(target=use_vad_based_recording,
            args=(audio_stream_shm.name,
                  speech_data_shm.name,
                  speech_record_complete_event,
                  vad_stream_read_event,
                  transcript_loading_complete_event,
                  transcript_processing_event,
                  llm_response_generating_event)).start()
    
    # transcript process
    transcript_complete_event = Event()
    transcript_complete_event.clear()

    Process(target=use_transcript,
            args=(speech_data_shm.name,
                  speech_record_complete_event,
                  transcript_complete_event,
                  transcript_loading_complete_event,
                  transcript_processing_event)).start()
    
    # llm response process
    llm_response_created_event = Event()
    llm_response_created_event.clear()
    llm_start_send_query_event = Event()
    llm_start_send_query_event.clear()

    Process(target=use_ai_response,
            args=(transcript_complete_event,
                  llm_response_generating_event,
                  llm_response_created_event)).start()