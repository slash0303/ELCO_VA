import requests
import io
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import os
import numpy as np

# ---- 설정 ----
OUTPUT_SIZE = (72, 72)   # 출력 BMP 크기
FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",  # Colab/Linux
    "C:\\Windows\\Fonts\\seguiemj.ttf",                   # Windows 기본 이모지 폰트
]
ESP32_IP = "192.168.137.161"
url = f"http://{ESP32_IP}/upload"

file_name = "output.bmp"
roots = os.getcwd()

# ------------------------------------------------------------
# Twemoji 이미지 다운로드
# ------------------------------------------------------------
def download_twemoji_png(emoji):
    codepoints = "-".join(f"{ord(c):x}" for c in emoji)
    url = f"https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/{codepoints}.png"
    resp = requests.get(url)
    if resp.status_code != 200:
        return None  # 없는 경우 None 반환
    return Image.open(io.BytesIO(resp.content)).convert("RGBA")

# ------------------------------------------------------------
# Twemoji 없을 때 폰트 렌더링 대체 (정중앙 + 잘림 없음)
# ------------------------------------------------------------
def render_with_font(emoji,font_scale=1):
    # 폰트 경로 자동 탐색
    font_path = None
    for path in FONT_PATHS:
        if os.path.exists(path):
            font_path = path
            break
    if font_path is None:
        raise FileNotFoundError("Emoji font not found. Please install NotoColorEmoji or seguiemj.ttf")

    # 1️⃣ 큰 캔버스 생성
    canvas_size = (1024, 1024)
    font_size = int(canvas_size[1] * font_scale)
    font = ImageFont.truetype(font_path, font_size)
    img = Image.new("RGBA", canvas_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 2️⃣ 중앙에 텍스트 렌더
    try:
        draw.text((canvas_size[0], canvas_size[1]//2),
                  emoji, font=font, anchor="mm", embedded_color=True)
    except TypeError:
        draw.text((canvas_size[0], canvas_size[1]//2),
                  emoji, font=font, anchor="mm", fill=(255, 255, 255, 255))

    # 3️⃣ 실제 픽셀 존재 영역 구하기
    bbox = img.getbbox()
    if bbox is None:
        return Image.new("RGBA", OUTPUT_SIZE, (0, 0, 0, 0))

    region = img.crop(bbox)
    rw, rh = region.size

    # 4️⃣ 상대 패딩 (잘림 방지)
    pad_pct = 0.12
    pad_w = int(rw * pad_pct)
    pad_h = int(rh * pad_pct)
    pad_w = max(pad_w, 8)
    pad_h = max(pad_h, 8)

    new_w = rw + 2 * pad_w
    new_h = rh + 2 * pad_h
    side = max(new_w, new_h)

    # 5️⃣ 정사각형 배경에 중앙 배치
    square_bg = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    paste_x = (side - rw) // 2
    paste_y = (side - rh) // 2
    square_bg.paste(region, (paste_x, paste_y), region)

    # 6️⃣ 출력 크기로 리사이즈
    out = square_bg.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    return out

# ------------------------------------------------------------
# Twemoji 또는 폰트로 렌더링 후 BMP 저장
# ------------------------------------------------------------
def emoji_to_bmp(emoji, output_path, font_scale=1, scale_factor=0.6, width_stretch=1.3):
    """
    emoji: 렌더링할 이모지
    output_path: 저장 경로
    font_scale: 폰트 렌더링 크기 배율
    scale_factor: 전체 축소 비율
    width_stretch: 가로 늘림 비율 (1.0 = 기본, 1.3 = 30% 더 넓게)
    """
    img = download_twemoji_png(emoji)
    if img is None:
        print(f"Twemoji에 없음: {emoji} → 폰트 렌더링으로 대체")
        img = render_with_font(emoji, font_scale)

    # OUTPUT_SIZE 기준 스케일 적용
    img_w, img_h = img.size
    scale = min(OUTPUT_SIZE[0] / img_w, OUTPUT_SIZE[1] / img_h) * scale_factor
    new_size = (int(img_w * scale * width_stretch), int(img_h * scale))  # ← 가로만 늘림
    img = img.resize(new_size, Image.Resampling.LANCZOS)

    # 검정 배경 + 중앙 배치
    bg = Image.new("RGB", OUTPUT_SIZE, (0, 0, 0))
    paste_x = (OUTPUT_SIZE[0] - new_size[0]) // 2
    paste_y = (OUTPUT_SIZE[1] - new_size[1]) // 2
    bg.paste(img, (paste_x, paste_y), mask=img.split()[3] if img.mode == "RGBA" else None)

    # 회전 (왼쪽 90도)
    bg = bg.rotate(90, expand=True)
    bg.save(output_path, "BMP")
    # print(f"{emoji} → {output_path} (scale_factor={scale_factor}, width_stretch={width_stretch})")

# ------------------------------------------------------------
# 대비 강화
# ------------------------------------------------------------
def enhance_bmp_contrast(input_path, output_path, factor=1.5):
    img = Image.open(input_path).convert("RGB")
    enhancer = ImageEnhance.Contrast(img)
    img_enhanced = enhancer.enhance(factor)
    img_enhanced.save(output_path, format="BMP")
    print(f" '{output_path}' 대비 변경 완료")

# ------------------------------------------------------------
# 색상/밝기 강화
# ------------------------------------------------------------
def enhance_pov_color(input_path, output_path, contrast_factor=1.8, saturation_factor=2.0, brightness_factor=1.1):
    img = Image.open(input_path).convert("RGB")
    img = ImageEnhance.Contrast(img).enhance(contrast_factor)
    img = ImageEnhance.Color(img).enhance(saturation_factor)
    img = ImageEnhance.Brightness(img).enhance(brightness_factor)
    img.save(output_path, format="BMP")
    # print(f" '{output_path}' 색상/밝기 변경 완료")

#-------------------------------------------------------------
#이미지 보정
#-------------------------------------------------------------
def sphere(path):
    from PIL import Image
    import numpy as np

    # ==== 1. 이미지 불러오기 ====
    img = Image.open(path).convert("RGB")
    img = img.rotate(90, expand=True)  # 왼쪽 90도 회전된 입력 이미지 보정
    img.save("output_sphere_rotated.bmp", "BMP")
    img_np = np.array(img)
    h, w, c = img_np.shape

    # ==== 2. 출력 이미지 크기 ====
    out_h, out_w = h, w
    new_img_np = np.zeros((out_h, out_w, 3), dtype=np.uint8)

    # ==== 3. 구면 좌표 생성 (극 왜곡 최소화 + 가로 시야 확대) ====
    u = np.linspace(-1, 1, out_h)
    theta = np.arccos(u)  # [0, π], 위도

    stretch_factor = 1.3   # ★ 가로 늘림 비율
    phi = np.linspace(-np.pi * stretch_factor, np.pi * stretch_factor, out_w)  # 중심 기준 확대

    phi_grid, theta_grid = np.meshgrid(phi, theta)

    # ==== 4. 원본 이미지 좌표 계산 (float) ====
    # wrap 제거: 화면 밖은 검정으로 처리
    x_src = (phi_grid / (2 * np.pi) + 0.5) * (w - 1)
    y_src = theta_grid / np.pi * (h - 1)

    # ==== 5. Bilinear 보간 ====
    for i in range(out_h):
        for j in range(out_w):
            xi = x_src[i, j]
            yi = y_src[i, j]

            # 화면 밖이면 검정으로
            if xi < 0 or xi >= w - 1:
                new_img_np[i, j] = [0, 0, 0]
                continue

            xi_int = int(xi)
            yi_int = int(yi)
            xi1 = min(xi_int + 1, w - 1)
            yi1 = min(yi_int + 1, h - 1)

            dx = xi - xi_int
            dy = yi - yi_int

            top = (1 - dx) * img_np[yi_int, xi_int] + dx * img_np[yi_int, xi1]
            bottom = (1 - dx) * img_np[yi1, xi_int] + dx * img_np[yi1, xi1]
            new_img_np[i, j] = (1 - dy) * top + dy * bottom

    # ==== 6. 결과를 다시 왼쪽으로 90도 회전 + 좌우 반전 ====
    new_img = Image.fromarray(new_img_np)
    new_img = new_img.rotate(-90, expand=True)
    new_img = new_img.transpose(Image.FLIP_LEFT_RIGHT)

    new_img.save("output_sphere.bmp", "BMP")
    # print(f"왜곡 보정 + 회전 보정 + 좌우 반전 + 가로 {stretch_factor*100:.0f}% 확대 완료 (검정 여백): output_sphere.bmp")


# ------------------------------------------------------------
# 하드웨어 전송 (ESP32 업로드)
# ------------------------------------------------------------
def trasfer_HW(emoji, scale_factor=0.6, width_stretch=1.3):
    print("전송 중:", emoji)
    emoji_to_bmp(emoji, roots + "output_pre.bmp", 0.5, scale_factor, width_stretch)

    enhance_bmp_contrast(roots + "output_pre.bmp", roots + "output_contrast.bmp", factor=1.5)
    outputname = "6"
    enhance_pov_color(roots + "output_contrast.bmp", "output" + outputname + ".bmp", contrast_factor=1.0, saturation_factor=2.0)
    sphere("output" + outputname + ".bmp")

    with open("output_sphere.bmp", "rb") as f:
        bmp_data = f.read()

    files = {"file": ("output_sphere.bmp", bmp_data, "image/bmp")}
    try:
        response = requests.post(url, files=files, timeout=10)
        print("응답 코드:", response.status_code)
        print("응답 내용:", response.text)
    except requests.exceptions.RequestException as e:
        print("업로드 실패:", e)
     

# ------------------------------------------------------------
# 실행
# ------------------------------------------------------------
# trasfer_HW("❤️", scale_factor=0.4, width_stretch=2.2)

