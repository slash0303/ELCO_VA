import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from multiprocessing import Event, shared_memory, Process, Queue

import numpy as np

import global_constants as gc
from eaxtension import LogE

from flag_management.load import use_load_management
# from flag_management.enable import use_enable_management
from audio.audio_stream import use_audio_stream
from VAD.voice_detection import use_vad_based_recording
from whisper_streaming.whisper_stream import use_transcript
from Llm.llm_send_query import use_ai_response
from Llm.weatherapi import weather_update_loop
from voice_generation.generate_voice import use_generate_voice
from Gaze.gazing import use_gaze
from Display.convert_emoji import use_convert_emoji

PROCESS_NAME = "[MAIN]"

if __name__ == "__main__":
	
	LogE.g(PROCESS_NAME, "program started.")
	# audio stream flags
	# Audio stream process
	audio_stream_enable_event = Event()
	audio_stream_enable_event.set()
	# Flag for frame management of vad based recording.
	vad_stream_read_enable_event = Event()
	vad_stream_read_enable_event.clear()
	# ========================================

	# vad based recording flags
	# VAD process
	speech_record_complete_event = Event()
	speech_record_complete_event.clear()
	vad_enable_event = Event() 
	vad_enable_event.clear()
	# ========================================

	# transcript flags
	# loading complete flags
	transcript_loading_complete_event = Event()
	transcript_loading_complete_event.clear()
	# transcripting flag
	transcript_processing_event = Event()
	transcript_processing_event.clear()
	# transcript process
	transcript_complete_event = Event()
	transcript_complete_event.clear()
	# =========================================

	# llm flags
	# llm response generating flag
	llm_response_generating_event = Event()
	llm_response_generating_event.clear()
	# llm response process
	llm_response_generated_event = Event()
	llm_response_generated_event.clear()
	# =========================================

	# tts flags
	tts_loading_complete_event = Event()
	tts_loading_complete_event.clear()
	tts_generating_event = Event()
	tts_generating_event.clear()
	tts_generated_event = Event()
	tts_generated_event.clear()
	# =========================================

	# gaze flags
	gaze_loading_complete_event = Event()
	gaze_loading_complete_event.clear()
	gaze_enable_event = Event()
	gaze_enable_event.clear()
	gazing_event = Event()
	gazing_event.clear()
	# =========================================

	# loading management flags
	loading_complete_event = Event()
	loading_complete_event.clear()
	# =========================================

	# convert emoji flags
	convert_emoji_enable_flag = Event()
	convert_emoji_enable_flag.clear()
	convert_emoji_processing_flag = Event()
	convert_emoji_processing_flag.clear()
	convert_emoji_complete_flag = Event()
	convert_emoji_complete_flag.clear()
	#==========================================

	LogE.g(PROCESS_NAME, "flags all set")

	Process(target=weather_update_loop, args=(3600,)).start()  # 1시간 간격

	Process(target=use_load_management,
			args=(transcript_loading_complete_event,
		 			tts_loading_complete_event,
					gaze_loading_complete_event,
					loading_complete_event)).start()
	LogE.d(PROCESS_NAME, "load manager setted")


	Process(target=use_gaze,
		 	args=(gaze_loading_complete_event,
		  			gaze_enable_event,
					gazing_event)).start()
	LogE.d(PROCESS_NAME, "gaze setted.")


	audio_stream_shm = shared_memory.SharedMemory(create=True, 
													size=np.zeros(gc.audio.FRAMES_PER_BUFFER, 
																dtype=gc.audio.NDARRAY_DTYPE).nbytes,
													name="audio_stream")

	Process(target=use_audio_stream, 
			args=(audio_stream_enable_event, 
					audio_stream_shm.name,
					vad_stream_read_enable_event)).start()
	LogE.d(PROCESS_NAME, "audio stream setted")


	speech_data_shm = shared_memory.SharedMemory(create=True,
													size=np.zeros(gc.audio.SAMPLING_RATE * gc.vad.RECORDING_LIMIT, 
																dtype=gc.audio.NDARRAY_DTYPE).nbytes,
													name="speech_data")

	Process(target=use_vad_based_recording,
			args=(audio_stream_shm.name,
					speech_data_shm.name,
					speech_record_complete_event,
					vad_stream_read_enable_event,
					transcript_processing_event,
					llm_response_generating_event,
					tts_generating_event,
					loading_complete_event,
					gazing_event,
					gaze_enable_event,
					convert_emoji_processing_flag)).start()


	Process(target=use_transcript,
			args=(speech_data_shm.name,
					speech_record_complete_event,
					transcript_complete_event,
					transcript_loading_complete_event,
					transcript_processing_event,
					loading_complete_event)).start()


	emoji_queue = Queue()

	Process(target=use_ai_response,
			args=(transcript_complete_event,
					llm_response_generating_event,
					llm_response_generated_event,
					convert_emoji_enable_flag,
					emoji_queue)).start()

	Process(target=use_generate_voice,
			args=(llm_response_generated_event,
					tts_loading_complete_event,
					tts_generating_event,
					tts_generated_event,
					loading_complete_event)).start()

	Process(target=use_convert_emoji,
		 args=(convert_emoji_enable_flag,
		 		convert_emoji_processing_flag,
				convert_emoji_complete_flag,
				emoji_queue)).start()