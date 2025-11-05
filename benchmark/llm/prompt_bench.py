from openai import OpenAI

import time as t

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

sys_prompt = """"""

data_prompt = """"""

example_prompt = """"""

def print_prompt(prompt_name: str, prompt: str):
    print(f"<{prompt_name}>")
    print(prompt)
    print(f"</{prompt_name}>")

while True:
    user_request_text = input("\nmsg: ")

    with open("./test_prompt.txt", "r", encoding="utf-8") as f:
        sys_prompt = f.read()

    with open("./assist_prompt.txt", "r", encoding="utf-8") as f:
        example_prompt = f.read()

    print_prompt("system", sys_prompt)
    print_prompt("assistant", example_prompt)
    print_prompt("user", user_request_text)

    start = t.time()
    response = client.chat.completions.create(
        model='qwen/qwen3-vl-4b',
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "assistant", "content": example_prompt},
            {"role": "user", "content": user_request_text}
        ],
        temperature=0.7,
        max_tokens=1024,
        stream=False
    )
    end = t.time()
    print(f"lapsed: {end - start}")
    print(f"response: {response.choices[0].message.content}")
#     print("----------------------------------------------")

# from openai import OpenAI

# prpt = """\
# [환경정보]
# time: 08:40
# temperature: 20
# weather: clear, warm
# [규칙]
# - 위 정보는 사용자에게 직접 말하지 마세요.
# - 사용자의 질문에만 짧게, 구어체로 대답하세요.
# - 날씨나 온도를 말하지 마세요."""

# msg = "지금 몇 시야?"

# client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
# while True:
#     msg = input("msg: ")
#     response = client.chat.completions.create(
#         model = "exaone-4.0-1.2b",
#         messages=[
#             {"role": "system", "content": prpt},
#             {"role": "user", "content": f"{msg}"}
#         ],
#         temperature=0.7,
#         max_tokens=1024,
#         stream=False
#     )
#     print("processing: 요청 전송됨\n")

#     print(f"response: {response.choices[0].message.content}")