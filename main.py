from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from pilmoji import Pilmoji
from flask import Flask, request, send_file
import requests
import io
import warnings
from wrap import fw_wrap

warnings.simplefilter("ignore")

# デフォルトとカラーのみに変更したため削減
BASE_IMAGES = {
    "default": Image.open("images/base.png"),
    "gd": Image.open("images/base-gd.png")
}

MPLUS_FONT = ImageFont.truetype("fonts/MPLUSRounded1c-Regular.ttf", size=16)
BRAND = "!kumanomi!#9363" # くまのみBOT用に変更

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

def createImage(name, id, content, icon, base_image, gd_image=None):
    img = base_image.copy()
    icon = Image.open(io.BytesIO(requests.get(icon).content)).resize((720, 720), Image.LANCZOS).convert("L")
    img.paste(ImageEnhance.Brightness(icon).enhance(0.7) if gd_image else icon, (0, 0))
    img.paste(gd_image, (0, 0), gd_image)

    tx = ImageDraw.Draw(img)
    tsize_t = drawText(img, (890, 270), content, size=55, color=(255, 255, 255, 255), split_len=20)
    name_y = tsize_t[2] + 40
    tsize_name = drawText(img, (890, name_y), f"@{name}", size=28, color=(255, 255, 255, 255), split_len=25, disable_dot_wrap=True)
    id_y = name_y + tsize_name[1] + 4
    drawText(img, (890, id_y), id, size=18, color=(180, 180, 180, 255), split_len=45, disable_dot_wrap=True)

    tx.text((1122, 694), BRAND, font=MPLUS_FONT, fill=(120, 120, 120, 255))

    file = io.BytesIO()
    img.save(file, format="PNG", quality=95)
    file.seek(0)
    return file

app = Flask(__name__)

@app.route("/", methods=["GET"])
def main():
    type = request.args.get("type")
    name = request.args.get("name", "SAMPLE")
    id = request.args.get("id", "0000000000000000000")
    content = request.args.get("content", "Make it a Quote")
    icon = request.args.get("icon", "https://cdn.discordapp.com/embed/avatars/0.png")

    base_image = BASE_IMAGES["default"]
    gd_image = BASE_IMAGES["gd"]

    # color以外のtypeを削除
    if type == "color":
        return send_file(createImage(name, id, content, icon, base_image, gd_image), mimetype="image/png")
    else:
        return send_file(createImage(name, id, content, icon, base_image, gd_image), mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
