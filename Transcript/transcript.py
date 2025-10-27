from multiprocessing.synchronize import Event as EventObject

import os
import subprocess

import cppimport

def use_whisper_cpp(transcript_flag: EventObject):
    WHISPER_CPP_DIR = "./whisper.cpp"
    subprocess.Popen()