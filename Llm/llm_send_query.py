from multiprocessing.synchronize import Event as EventObject

from openai import OpenAI

from eaxtension import LogE

def use_ai_response(transcript_complete_flag: EventObject,
                    llm_response_generating_flag: EventObject,
                    llm_response_generated_flag: EventObject):
    PROCESS_NAME = "[ai response]"
    LogE.g(PROCESS_NAME, "process started")

    client = OpenAI(base_url="http://localhost:1234/v1",
                    api_key="lm-studio")
    
    while True:
        if transcript_complete_flag.is_set():
            # Set generating flag as True. it will pause all actions of processes.
            llm_response_generating_flag.set()
            LogE.d(PROCESS_NAME, "query sended")
            # open txt file which include transcripted request of user.
            with open("./trans.txt", "r", encoding="utf-8") as f:
                user_request_text = f.read()
                # Check transcripted text is empty
                if(user_request_text != "" and user_request_text != " "):
                    # Send resquest to local llm server
                    sys_prompt = ""
                    with open("./sys_prompt.txt", "r", encoding="utf-8") as f:
                        sys_prompt = f.read()
                    info = ""
                    response = client.chat.completions.create(
                        model = 'qwen/qwen3-vl-4b',
                        messages=[
                            {"role": "system", "content": sys_prompt},
                            {"role": "assistant", "content": "현재 서울특별시 정릉 3동의 기온은 20도이고, 날씨는 맑아요. 강수확률이 70퍼센트 정도이니 우산을 챙겨나가시는걸 추천드립니다."},
                            {"role": "user", "content": user_request_text}
                        ],
                        temperature=0.7,
                        max_tokens=1024
                    )
                    LogE.d(PROCESS_NAME, f"response: {response}")
                    # Write response as a file.
                    with open("./response.txt", "w", encoding="utf-8") as f:
                        f.write(response.choices[0].message.content)
                else:
                    with open("./response.txt", "w", encoding="utf-8") as f:
                        f.write("")
                LogE.d(PROCESS_NAME, "'response.txt' was written in root directory.")

            # Clear all flags
            llm_response_generated_flag.set()
            llm_response_generating_flag.clear()
            transcript_complete_flag.clear()