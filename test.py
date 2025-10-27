from openai import OpenAI
import time as t

# LM Studio 서버 주소 (예: 로컬에서 1234번 포트로 실행 중)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="not-needed")

times = []

for x in range(10):
    print("start")
    start = t.time()
    response = client.chat.completions.create(
        model="lgai-exaone/exaone-4.0-1.2b",  # LM Studio에서 실행한 모델 이름
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "응답테스트용 쿼리입니다. 아무말이나 하세요"}
        ],
        temperature=0.7,
    )
    end = t.time()
    times.append(end-start)
    print(response.choices[0].message.content)
    print(f"delay: {end-start}")

print(times)