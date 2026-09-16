"""고른 사진을 원본 크기로 받아 사이트용으로 줄이고 출처를 기록한다.

python tools/photo_pick.py research/photos/picks.json
picks.json = [{"set": "tech", "file": "pexels-123.jpg", "uses": ["card"], "crop": "..."}, ...]
→ src/img/<set>-<source>-<id>-{480,960,1600}.webp, src/img/credits.json
출처 표기 의무는 없지만(Unsplash·Pexels) 사진가·원본 URL·받은 날을 남겨 두고, 이의가 오면 바로 뺀다.
"""
import datetime
import io
import json
import pathlib
import re
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).resolve().parent.parent
IMG = BASE / 'src' / 'img'
WIDTHS = (480, 960, 1600)
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
AUTHOR_JS = """() => { const m = document.querySelector('meta[property="og:title"]'); return m ? m.getAttribute('content') : ''; }"""


def fetch_author(page, url):
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=45000)
        page.wait_for_timeout(1500)
        m = re.search(r'Photo by (.+?) on (?:Unsplash|Pexels)', page.evaluate(AUTHOR_JS) or '')
        return m.group(1).strip() if m else ''
    except Exception as e:
        print('사진가 확인 실패', url, str(e)[:80])
        return ''


def main(picks_path):
    picks = json.loads(pathlib.Path(picks_path).read_text(encoding='utf-8'))
    IMG.mkdir(parents=True, exist_ok=True)
    credits_path = IMG / 'credits.json'
    credits = {c['name']: c for c in json.loads(credits_path.read_text(encoding='utf-8'))} if credits_path.exists() else {}
    cands = {}
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True, args=['--disable-blink-features=AutomationControlled'])
        ctx = b.new_context(viewport={'width': 1400, 'height': 1000}, locale='en-US', user_agent=UA)
        page = ctx.new_page()
        for order, pk in enumerate(picks):
            pk['order'] = order
            if pk['set'] not in cands:
                cands[pk['set']] = {c['file']: c for c in json.loads((BASE / 'research' / 'photos' / pk['set'] / 'candidates.json').read_text(encoding='utf-8'))}
            c = cands[pk['set']].get(pk['file'])
            if not c:
                print('후보에 없음', pk)
                continue
            name = f'{pk["set"]}-{c["source"]}-{c["id"]}'
            if name in credits and all((IMG / f'{name}-{w}.webp').exists() for w in WIDTHS):
                credits[name].update(uses=pk.get('uses', []), crop=pk.get('crop', ''), order=pk['order'])
                if not credits[name].get('photographer'):
                    credits[name]['photographer'] = fetch_author(page, c['page_url'])
                continue
            url = c['img_base'] + ('?fm=jpg&q=90&w=2000' if c['source'] == 'unsplash' else '?auto=compress&cs=tinysrgb&w=2000')
            r = ctx.request.get(url, timeout=60000)
            if not r.ok:
                print('받기 실패', r.status, c['page_url'])
                continue
            im = Image.open(io.BytesIO(r.body())).convert('RGB')
            for w in WIDTHS:
                v = im.copy()
                v.thumbnail((w, w * 3))
                v.save(IMG / f'{name}-{w}.webp', 'WEBP', quality=78, method=6)
            author = c.get('author') or fetch_author(page, c['page_url'])
            credits[name] = {'name': name, 'set': pk['set'], 'source': c['source'], 'page_url': c['page_url'], 'photographer': author,
                             'license': c['license'], 'license_url': c['license_url'], 'alt_en': c.get('alt', ''),
                             'size': list(im.size), 'uses': pk.get('uses', []), 'crop': pk.get('crop', ''), 'order': pk['order'],
                             'downloaded': datetime.date.today().isoformat()}
            print('받음', name, im.size, author)
        b.close()
    credits_path.write_text(json.dumps(sorted(credits.values(), key=lambda x: x['name']), ensure_ascii=False, indent=1), encoding='utf-8')
    print('credits', len(credits))


if __name__ == '__main__':
    main(sys.argv[1])
