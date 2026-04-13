try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Pillow'])
    from PIL import Image, ImageDraw, ImageFont

def create_image(text, filename):
    try:
        font = ImageFont.truetype('consola.ttf', 20)
    except:
        font = ImageFont.load_default()
    lines = text.split('\n')
    width = max(len(line) for line in lines) * 14 + 100
    height = len(lines) * 25 + 60
    if width < 300: width = 300
    if height < 150: height = 150
    img = Image.new('RGB', (int(width), int(height)), color='#0d1117')
    d = ImageDraw.Draw(img)
    y = 30
    for line in lines:
        d.text((40, y), line, fill='#39ff14', font=font)
        y += 25
    img.save(filename)

# Fixed PY1: token[:2] instead of token[2]
py1_code = 'def bypass_auth(token)\n    return token * 2 + token[:2]\n\nprint(bypass_auth("KEY"))'
create_image(py1_code, 'static/images/py1.png')
print('SUCCESS: py1.png regenerated with token[:2] fix!')
print('Verify: "KEY"*2 + "KEY"[:2] = "KEYKEY" + "KE" = "KEYKEYKE"')
