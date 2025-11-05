from melo.api import TTS
from kittentts import KittenTTS

import soundfile as sf
import time as t

llm_response = "맑은 날씨예요. 강수 확률 70% 정도로, 우산을 챙겨나가시는걸 추천해요."

start = t.time()

device = "cpu"
speed = 1.5
model = TTS(language='KR', device=device)
speaker_ids = model.hps.data.spk2id

output_path = 'kr.wav'
model.tts_to_file(llm_response, speaker_ids['KR'], output_path, speed=speed)

end = t.time()

print(f"lapsed: {end-start}")

m = KittenTTS("KittenML/kitten-tts-nano-0.2")

start = t.time()
audio = m.generate(llm_response, voice='expr-voice-2-f' )

# available_voices : [  'expr-voice-2-m', 'expr-voice-2-f', 'expr-voice-3-m', 'expr-voice-3-f',  'expr-voice-4-m', 'expr-voice-4-f', 'expr-voice-5-m', 'expr-voice-5-f' ]

# Save the audio
sf.write('output.wav', audio, 24000)
end = t.time()

print(f"lapsed: {end - start}")