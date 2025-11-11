from multiprocessing.synchronize import Event as EventObject

def use_load_management(transcript_loading_complete_flag: EventObject,
                        tts_loading_complete_flag: EventObject,
                        gaze_loading_complete_flag: EventObject,
                        loading_complete_flag: EventObject):
    
    while True:
        if transcript_loading_complete_flag.is_set() and tts_loading_complete_flag.is_set() and gaze_loading_complete_flag.is_set():
            break
        print(f"Loading {transcript_loading_complete_flag.is_set()} {tts_loading_complete_flag.is_set()} {gaze_loading_complete_flag.is_set()}...", end="\r")
    
    loading_complete_flag.set()
    print("Loading complete")