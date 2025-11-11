from multiprocessing.synchronize import Event as EventObject
from multiprocessing import Queue

from Display.emoji_to_bmp import trasfer_HW

def use_convert_emoji(convert_emoji_enable_flag: EventObject,
                      convert_emoji_processing_flag: EventObject,
                      convert_emoji_complete_flag: EventObject,
                      emoji_queue: Queue):
    while True:
        if convert_emoji_enable_flag.is_set():
            convert_emoji_processing_flag.set()
            
            emoji = emoji_queue.get()
            if emoji != None:
                trasfer_HW(emoji)
            
            convert_emoji_processing_flag.clear()
            convert_emoji_complete_flag.set()
            convert_emoji_enable_flag.clear()