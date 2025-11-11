import requests
import datetime
import json
import time
from multiprocessing import Process

# ==============================
# API 요청 함수
# ==============================

API_KEY = "371db63eb71c1e64c981669364898ee89a8da6d4d53a93172cb35db7a79e6dda"
NX = 60
NY = 127

def fetch_ncst():
    """초단기실황 데이터: 온도, 습도, 강수량, 강수형태"""
    URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst"
    now = datetime.datetime.now()
    if now.minute < 40:
        base_time = (now - datetime.timedelta(hours=1)).strftime("%H%M")
    else:
        base_time = now.strftime("%H%M")

    params = {
        'serviceKey': API_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': now.strftime("%Y%m%d"),
        'base_time': base_time,
        'nx': str(NX),
        'ny': str(NY)
    }

    response = requests.get(URL, params=params)
    if response.status_code != 200:
        print("NCST API error", response.status_code)
        return {}

    data = response.json()
    items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])

    weather = {}
    for item in items:
        cat = item.get('category')
        val = item.get('obsrValue')
        if cat == "T1H":
            weather['temperature'] = val
        elif cat == "REH":
            weather['humidity'] = val
        elif cat == "RN1":
            weather['rain_amount'] = val
        elif cat == "PTY":
            weather['rain_type'] = val

    # PTY 코드 -> 텍스트
    RAIN_TYPE_CODE = {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기"}
    if 'rain_type' in weather:
        weather['rain_type'] = RAIN_TYPE_CODE.get(weather['rain_type'], "알수없음")

    return weather

def fetch_fcst():
    """초단기예보 데이터: 하늘상태(SKY), 강수확률(POP)"""
    URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst"
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    # 초단기예보 기준 시각 30분 단위
    if minute < 30:
        base_time = f"{hour-1:02d}30"
    else:
        base_time = f"{hour:02d}30"

    params = {
        'serviceKey': API_KEY,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': now.strftime("%Y%m%d"),
        'base_time': base_time,
        'nx': str(NX),
        'ny': str(NY)
    }

    response = requests.get(URL, params=params)
    if response.status_code != 200:
        print("FCST API error", response.status_code)
        return {}

    data = response.json()
    items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])

    weather = {}
    for item in items:
        cat = item.get('category')
        val = item.get('fcstValue')
        if cat == "SKY":
            weather['weather_condition'] = val
        elif cat == "POP":
            weather['rain_probability'] = val

    # SKY 코드 -> 텍스트
    WEATHER_GRADE_CODE = {"1": "맑음", "3": "구름많음", "4": "흐림"}
    if 'weather_condition' in weather:
        weather['weather_condition'] = WEATHER_GRADE_CODE.get(weather['weather_condition'], "알수없음")

    return weather

# ==============================
# 서브 프로세스: 데이터 갱신
# ==============================

JSON_FILE = "weather_data.json"

def weather_update_loop(interval=3600):
    """초단기 실황+예보 데이터를 주기적으로 갱신"""
    while True:
        ncst = fetch_ncst()
        fcst = fetch_fcst()
        weather = {**ncst, **fcst}  # 합치기
        weather['last_update'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(weather, f, ensure_ascii=False, indent=2)

        print("Weather data updated:", weather)
        time.sleep(interval)  # interval 초마다 갱신

# ==============================
# 메인: 서브 프로세스로 실행
# ==============================

if __name__ == "__main__":
    p = Process(target=weather_update_loop, args=(3600,))  # 1시간 간격
    p.start()
    print("Weather update process started.")
