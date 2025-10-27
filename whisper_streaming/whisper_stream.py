from multiprocessing.synchronize import Event as EventObject
from multiprocessing import shared_memory

import numpy as np

from faster_whisper import WhisperModel

import global_constants as gc
from eaxtension import LogE


def use_transcript(
    speech_data_shm_name: str,
    transcript_activate_flag: EventObject,
    transcript_complete_flag: EventObject,
    transcript_loading_complete_flag: EventObject,
    transcript_processing_flag: EventObject):
    PROCESS_NAME = "[whisper stream]"
    
    model = WhisperModel("small", device="cpu", compute_type="int8")

    LogE.g(PROCESS_NAME, "process is started")

    # LogE.d(PROCESS_NAME, "initializing whisper stream...")
    # # Create arguments instance for running whisper
    # parser = argparse.ArgumentParser()
    # add_shared_args(parser)
    # args = parser.parse_args()
    # LogE.d(PROCESS_NAME, f"selected transcription model: {args.backend}")

    # # Create asr and online instances.
    # # 'asr' instance includes 'faster-whisper' model.
    # # 'online' instance includes methods which can instruct actions to a model such as 'insert audio chunk'.
    # asr, online = asr_factory(args)
    # LogE.d(PROCESS_NAME, "initialization complete")

    # Get speech data from shm
    speech_data_shm = shared_memory.SharedMemory(name=speech_data_shm_name)
    speech_data = np.ndarray(shape=gc.audio.SAMPLING_RATE * gc.vad.RECORDING_LIMIT,
                             dtype=gc.audio.NDARRAY_DTYPE,
                             buffer=speech_data_shm.buf)
    
    # LogE.d(PROCESS_NAME, "warm up asr model...")
    # # Warm up the model because it's first transcription is too slow.
    # asr.transcribe(np.zeros(1, gc.audio.NDARRAY_DTYPE))
    # LogE.g(PROCESS_NAME, "warming up complete")

    transcript_loading_complete_flag.set()

    write_shm = 1

    while True:
        # if the recording of speech data has been completed
        if transcript_activate_flag.is_set():
            transcript_processing_flag.set()
            if write_shm:
                # with open("./shm.txt", "w", encoding="utf-8") as f:
                #     f.write(str(speech_data))
                np.save("shm.npy", speech_data)
                LogE.g(PROCESS_NAME, "shm.txt was written.")
                write_shm = 0
            
            LogE.d("transcription", "start")
            LogE.d(PROCESS_NAME, "transcribing")
            segments, info = model.transcribe(
                (speech_data.astype(np.float32)/32767),
                beam_size=5,
                language="ko",
                vad_filter=True,
                initial_prompt="This audio is about the request that user speaks to voice assistant speaker."
            )

            speech_text = ""
            for segment in segments:
                speech_text += segment.text + " "
                
            # # set speech data into the online instance.
            # LogE.d("set audio", speech_data.size)
            # speech_data.astype(np.float32)
            # # Start transcription
            # transcripted_speech = online.process_iter()
            # LogE.g("transcript", "completed")
            # Write script as a txt file
            with open("./trans.txt", "w", encoding="utf-8") as f:
                f.write(speech_text)
                LogE.g("The file was written by 'whisper_stream.py'", str(speech_text))
                transcript_processing_flag.clear()
                transcript_complete_flag.set()
                transcript_activate_flag.clear()