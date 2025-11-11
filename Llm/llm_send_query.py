from multiprocessing.synchronize import Event as EventObject
from multiprocessing import Queue

from openai import OpenAI

from eaxtension import LogE

import keyboard

import time as t
import datetime

import emoji

# from Llm.weatherapi import use_weather_api

import json
import datetime
import os

def sys_prompt_replace(sys_prompt: str, json_file: str = "./weather_data.json"):
    """
    sys_prompt 안의 {content} 형태를 weather_data.json에서 읽은 값으로 치환
    """
    # JSON 파일 읽기
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = None

    # JSON에서 값 가져오기, 없으면 "None"
    if data is not None:
        temperature = data.get("temperature", "None")
        condition = data.get("weather_condition", "None")
        rain_type = data.get("rain_type", "None")
        rain_amount = data.get("rain_amount", "None")
    else:
        temperature = "None"
        condition = "None"
        rain_type = "None"
        rain_amount = "None"

    cur_time = datetime.datetime.now()

    # 치환용 dict
    sys_prompt_replace_dict = {
        "year": cur_time.year,
        "month": cur_time.month,
        "day": cur_time.day,
        "hour": cur_time.strftime("%H"),
        "min": cur_time.strftime("%M"),
        "temperature": temperature,
        "weather_condition": condition,
        "rain_type": rain_type,
        "rain_amount": rain_amount
    }

    # {content} 치환
    for key, value in sys_prompt_replace_dict.items():
        sys_prompt = sys_prompt.replace(f"{{{key}}}", str(value))

    return sys_prompt

 
def parse_emoji(response: str):
    return [char for char in response if char in emoji.EMOJI_DATA]

def use_ai_response(llm_enable_flag: EventObject,
                    # transcript_complete_flag: EventObject,
                    llm_response_generating_flag: EventObject,
                    llm_response_generated_flag: EventObject,
                    convert_emoji_enable_flag: EventObject,
                    emoji_queue: Queue):
    PROCESS_NAME = "[ai response]"
    LogE.g(PROCESS_NAME, "process started")

    client = OpenAI(base_url="http://localhost:1234/v1",
                    api_key="lm-studio")
    
    user_request_text = ""

    previous_request = "이전에 받은 요청이 존재하지 않습니다."
    previous_response = "이전에 생성 된 응답이 존재하지 않습니다."

    # load system prompt
    sys_prompt = ""
    with open("./sys_prompt.txt", "r", encoding="utf-8") as f:
        sys_prompt = f.read()

    sys_prompt_origin = sys_prompt[:]
    
    while True:
        if llm_enable_flag.is_set():
            sys_prompt = sys_prompt_origin[:]
            sys_prompt_replace(sys_prompt)
            
            # Set generating flag as True. it will pause all actions of processes.
            llm_response_generating_flag.set()
            LogE.d(PROCESS_NAME, "query sended")
            # open txt file which include transcripted request of user.
            with open("./trans.txt", "r", encoding="utf-8") as f:
                user_request_text = f.read()
            # Check transcripted text is empty
            if(user_request_text != "" and user_request_text != " "):
                # Send resquest to local llm server
                response = client.chat.completions.create(
                    model = 'qwen/qwen3-vl-4b',
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "assistant", "content": f"이전 요청: {previous_request}"},
                        {"role": "assistant", "content": f"이전 응답: {previous_response}"},
                        {"role": "user", "content": user_request_text}
                    ],
                    temperature=0.7,
                    max_tokens=512
                )
                LogE.d(PROCESS_NAME, f"response: {response}")
                # Write response as a file.
                emoji_list = parse_emoji(response.choices[0].message.content)
                if len(emoji_list) > 0:
                    emoji_queue.put(emoji_list[0])
                    convert_emoji_enable_flag.set()
                else:
                    LogE.e(PROCESS_NAME, "emoji not found.")
                with open("./response.txt", "w", encoding="utf-8") as f:
                    f.write(response.choices[0].message.content)
            else:
                with open("./response.txt", "w", encoding="utf-8") as f:
                    f.write("")
            LogE.d(PROCESS_NAME, "'response.txt' was written in root directory.")
            previous_request = user_request_text
            previous_response = response.choices[0].message.content
            # Clear all flags
            llm_response_generated_flag.set()
            llm_response_generating_flag.clear()
            llm_enable_flag.clear()