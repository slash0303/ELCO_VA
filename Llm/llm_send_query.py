from multiprocessing.synchronize import Event as EventObject

from openai import OpenAI

from eaxtension import LogE

api_list = {
    "weather": """
    현재 날씨에 대한 정보를 제공합니다. 응답형식은 {
        TODO: API응답 요청에 맞게 프롬프트 작성하기
    }
    """
}


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
                    response = client.chat.completions.create(
                        model = 'lgai-exaone/exaone-4.0-1.2b',
                        messages=[
                            {"role": "system", "content": f"당신은 AI어시스턴트 스피커입니다. 당신은 사용자의 전사되어있는 음성 요청에 대한 알맞은 응답을 생성해야합니다. 응답은 구어체로 제공되어야 하며, 마크다운등의 문법을 일체 사용해서는 안됩니다. DO NOT USE MARKDOWN. 사용자의 응답을 반복해서는 안됩니다. 응답 생성 시에는 제공되는 API목록을 활용할 수 있으며, 이하의 목록은 사용 가능한 API와 이에 대한 설명입니다.{api_list}/"},
                            {"role": "user", "content": f"이하에 제공되는 사용자의 요청에 맞는 응답을 생성하세요:\n{user_request_text}"}
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