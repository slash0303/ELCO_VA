from multiprocessing.synchronize import Event as EventObject

def set_enable_flag(enable_flag: list,
                    condition_flags: list):
    for condition_flag in condition_flags:
        if not condition_flag.is_set():
            enable_flag.clear()
    return enable_flag.set()

def use_enable_management(vad_enable_flag: EventObject,
                          vad_condition_flags: list,
                          gaze_enable_flag: EventObject,
                          gaze_condition_flags: list,
                          transcript_enable_flag: EventObject,
                          transcript_condition_flags: list, 
                          llm_enable_flag: EventObject,
                          llm_condition_flags: list,
                          tts_enable_flag: EventObject,
                          tts_condition_flags: list):
    
    while True:
        set_enable_flag(vad_enable_flag, vad_condition_flags)
        set_enable_flag(gaze_enable_flag, gaze_condition_flags)
        set_enable_flag(transcript_enable_flag, transcript_condition_flags)
        set_enable_flag(llm_enable_flag, llm_condition_flags)
        set_enable_flag(tts_enable_flag, tts_condition_flags)
