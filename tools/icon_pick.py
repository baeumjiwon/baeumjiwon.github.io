"""입체 그림 받기: Microsoft Fluent Emoji 3D(MIT) → src/img/icons/<slug>-{128,256}.webp

사람·손 모양은 받지 않는다(얼굴 규칙과 같은 이유). 하나라도 못 받으면 실패로 끝낸다.
python tools/icon_pick.py [--force]
"""
import io
import pathlib
import sys
import urllib.parse
import urllib.request

from PIL import Image

BASE = pathlib.Path(__file__).resolve().parent.parent
OUT = BASE / 'src' / 'img' / 'icons'
RAW = 'https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/'
NAMES = [
    'Laptop', 'Robot', 'Desktop computer', 'Movie camera', 'Artist palette', 'Clapper board',
    'Hammer and wrench', 'Gear', 'High voltage', 'Articulated lorry', 'Toolbox',
    'Bar chart', 'Briefcase', 'Chart increasing', 'Globe with meridians', 'Cooking', 'Hot beverage',
    'Stethoscope', 'Books', 'Graduation cap', 'Money bag', 'Memo', 'Rocket',
    'Magnifying glass tilted left', 'Alarm clock', 'Coin', 'Megaphone', 'Light bulb',
]
WIDTHS = (128, 256)


def slug(name):
    return name.lower().replace(' ', '-')


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'bj-icon-pick'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def main():
    force = '--force' in sys.argv
    OUT.mkdir(parents=True, exist_ok=True)
    lic = OUT / 'LICENSE-fluentui-emoji.txt'
    if force or not lic.exists():
        lic.write_bytes(get(RAW + 'LICENSE'))
    bad = []
    for name in NAMES:
        s = slug(name)
        if not force and all((OUT / f'{s}-{w}.webp').exists() for w in WIDTHS):
            continue
        file = name.lower().replace(' ', '_') + '_3d.png'
        url = RAW + 'assets/' + urllib.parse.quote(name) + '/3D/' + file
        try:
            im = Image.open(io.BytesIO(get(url))).convert('RGBA')
        except Exception as e:  # noqa: BLE001 — 이름이 틀렸거나 네트워크 문제
            bad.append(f'{name}: {e}')
            continue
        for w in WIDTHS:
            v = im.copy()
            v.thumbnail((w, w), Image.LANCZOS)
            v.save(OUT / f'{s}-{w}.webp', 'WEBP', quality=86, method=6)
        print('ok', s, im.size)
    if bad:
        print('못 받음:', *bad, sep='\n  ')
        sys.exit(1)
    print('전부', len(NAMES), '개 준비됨 →', OUT)


if __name__ == '__main__':
    main()
