from melo.api import TTS

from multiprocessing.synchronize import Event as EventObject
from multiprocessing import Process, Queue, Event

from eaxtension import LogE

import playsound

# def use_tts_model(tts_text_queue: Queue, 
#                   tts_flag: EventObject, 
#                 #   part_generating_complete_flag: EventObject,
#                   tts_id: str, speaker_ids, speed):
#     model = TTS(language='KR', device="cpu")
    
#     while True:
#         if tts_flag.is_set():
#             tts_text = tts_text_queue.get()
#             LogE.d("[tts model]", tts_text)
#             model.tts_to_file(tts_text, speaker_ids['KR'], f"./voices/{tts_id}.wav", speed=speed)
#             tts_flag.clear()

def use_generate_voice(llm_response_generated_flag: EventObject,
                       tts_loading_complete_flag: EventObject,
                       tts_generating_flag: EventObject,
                       tts_generated_flag: EventObject):
    PROCESS_NAME = "[tts generate voice]"
    LogE.g(PROCESS_NAME, "process started.")

    speed = 1.5
    device = "cpu"

    # cosyvoice = CosyVoice2('./CosyVoice/pretrained_models/CosyVoice2-0.5B', load_jit=False, load_trt=False, load_vllm=False, fp16=False)
    # prompt_speech_16k = load_wav('./voice_prompt.wav', 16000)
    llm_response = ""
    tts_loading_complete_flag.set()
    LogE.d(PROCESS_NAME, "loading complete")

    queues = []
    flags = []
    # part_generating_complete_flags = []

    model = TTS(language='KR', device=device)
    speaker_ids = model.hps.data.spk2id

    for i in range(6):
        queues.append(Queue())
        flags.append(Event())
        # part_generating_complete_flags.append(Event())
        Process(name=str(i),
                args=(queues[i], flags[i], i, speaker_ids, speed)).start()
    
    while True:
        if llm_response_generated_flag.is_set():
            LogE.d(PROCESS_NAME, "tts generating")
            tts_generating_flag.set()
            with open("./response.txt", "r", encoding="utf-8") as f:
                llm_response = f.read()

            audio_file = "./voices/out.wav"

            model = TTS(language='KR', device="cpu")
            model.tts_to_file(llm_response, speaker_ids['KR'], audio_file, speed=speed)

            # prompt_speech_16k_text = "Unfortunately, the device that's keeping you alive is also killing."
            # for i, j in enumerate(cosyvoice.inference_zero_shot(prompt_speech_16k_text, llm_response, prompt_speech_16k, stream=False)):
            #     torchaudio.save('zero_shot_{}.wav'.format(i), j['tts_speech'], cosyvoice.sample_rate)
            # tts = gtts.gTTS(text=llm_response, lang="ko")
            # tts.save("generated_voice.mp3")
            
            # llm_response_splited = llm_response.split("|")
            # if len(llm_response_splited) <= 6:
            #     for i, llm_response in enumerate(llm_response_splited):
            #         queues[i].put(llm_response)
            #         flags[i].set()
            #         # Process(name="response",
            #         #         args=(llm_response, i, model, speaker_ids, speed)).start()
            # else:
            #     pass
            #     LogE.E(PROCESS_NAME, "Prompt is too Long!")
            #     # output_path = 'kr.wav' 

            #     # model.tts_to_file(llm_response, speaker_ids['KR'], output_path, speed=speed)
            #     # LogE.g(PROCESS_NAME, "zero_shot_{i}.wav file was created.")
            # complete_flag = False
            # while not complete_flag:
            #     complete_flag = False
            #     for i in range(6):
            #         complete_flag = complete_flag and flags[i].is_set()
            #         lst = [i if flag.is_set() else 0 for i, flag in enumerate(flags)]
            #         print(f"{lst} tts generating...", end="\r")

            LogE.d(PROCESS_NAME, "Speaking")
            playsound.playsound(audio_file)
            print(end="\r")

            tts_generated_flag.set()
            tts_generating_flag.clear()
            llm_response_generated_flag.clear()