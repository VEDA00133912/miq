from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pilmoji import Pilmoji
from flask import Flask, request, send_file, render_template
import requests
import io
import warnings
from wrap import fw_wrap

warnings.simplefilter("ignore")

BASE_IMAGES = {
    "default": Image.open("images/base.png"),
    "gd": Image.open("images/base-gd.png")
}

MPLUS_FONT = ImageFont.truetype("fonts/MPLUSRounded1c-Regular.ttf", size=16)
BRAND = "!kumanomi!#9363"  # くまのみBOT用に変更

def drawText(im, ofs, string, font="fonts/MPLUSRounded1c-Regular.ttf", size=16, color=(0, 0, 0, 255), split_len=None, padding=4, disable_dot_wrap=False):
    ImageDraw.Draw(im)
    fontObj = ImageFont.truetype(font, size=size)
    pure_lines = []
    l = ""
    for char in string:
        if char in ["\n", "、", ",", "。", "."]:
            if l: pure_lines.append(l + char if char != "\n" else l)
            l = ""
        else:
            l += char
    if l:
        pure_lines.append(l)

    lines = []
    for line in pure_lines:
        lines.extend(fw_wrap(line, width=split_len))

    dy = 0
    draw_lines = []
    for line in lines:
        tsize = fontObj.getsize(line)
        x = int(ofs[0] - (tsize[0] / 2))
        draw_lines.append((x, ofs[1] + dy, line))
        dy += tsize[1] + padding

    adj_y = -30 * (len(draw_lines)-1)
    for dl in draw_lines:
        with Pilmoji(im) as p:
            p.text((dl[0], adj_y + dl[1]), dl[2], font=fontObj, fill=color)

    return 0, dy, ofs[1] + adj_y + dy

def createImage(name, user_name, content, icon, base_image, gd_image=None, type=None):
    if type not in ["color", "mono"]:
        raise ValueError("指定されたtypeが無効です。「color」か「mono」を使用してください")
        
    img = base_image.copy()

    if type == "mono":
        icon = Image.open(io.BytesIO(requests.get(icon).content))
        icon = icon.resize((720, 720), Image.LANCZOS)
        icon = icon.convert("L")  # グレースケールに変換
        icon_filtered = ImageEnhance.Brightness(icon)
        img.paste(icon_filtered.enhance(0.7), (0, 0)) 

    elif type == "color":
        icon = Image.open(io.BytesIO(requests.get(icon).content))
        icon = icon.resize((720, 720), Image.LANCZOS)
        img.paste(icon, (0, 0)) 

    else:
        raise ValueError("指定されたtypeが無効です。「color」か「mono」を使用してください")

    if gd_image:
        img.paste(gd_image, (0, 0), gd_image)

    tx = ImageDraw.Draw(img)
    tsize_t = drawText(img, (890, 270), content, size=55, color=(255, 255, 255, 255), split_len=20)
    name_y = tsize_t[2] + 40
    tsize_name = drawText(img, (890, name_y), name, size=28, color=(255, 255, 255, 255), split_len=25, disable_dot_wrap=True)
    user_name_y = name_y + tsize_name[1] + 4
    drawText(img, (890, user_name_y), f"@{user_name}", size=18, color=(180, 180, 180, 255), split_len=45, disable_dot_wrap=True)

    tx.text((1122, 694), BRAND, font=MPLUS_FONT, fill=(120, 120, 120, 255))

    file = io.BytesIO()
    img.save(file, format="PNG", quality=95)
    file.seek(0)
    return file

app = Flask(__name__, static_folder="docs", template_folder="docs")

@app.route("/", methods=["GET"])
def main():
    type = request.args.get("type")
    name = request.args.get("name", "SAMPLE")
    user_name = request.args.get("user_name", BRAND)
    content = request.args.get("content", "Make it a Quote")
    icon = request.args.get("icon", "https://ul.h3z.jp/0KwXFOaf.png")

    base_image = BASE_IMAGES["default"]
    gd_image = BASE_IMAGES["gd"]

    # 指定がない場合はmonoを適用
    if not type:
        type = "mono"

    try:
        return send_file(createImage(name, user_name, content, icon, base_image, gd_image, type=type), mimetype="image/png")
    except ValueError as e:
        return str(e), 400

@app.route("/apidocs", methods=["GET"])
def apidocs():
    return render_template("docs.html")
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
