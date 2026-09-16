"""무료 사진 후보 모으기 — Unsplash(무료 라이선스만)·Pexels. 둘 다 상업 사용 가능, 출처 표기 의무 없음.

python tools/photo_search.py --set tech --query "welding workshop" --query "electrician tools" [--per 10]
→ research/photos/<set>/cand/*.jpg, candidates.json, sheet.jpg(번호 붙은 후보 모음표)

API 키 없이 실제 Chrome으로 검색 페이지를 읽는다(requests는 403). 고른 사진은 tools/photo_pick.py로 원본 크기를 받는다.
규칙(research/design_refs/photo_sources.json): Unsplash+ 제외, 로고·간판·식별 가능한 미성년자 제외, 민감 분류엔 얼굴 없는 사진.
"""
import argparse
import json
import pathlib
import re

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE = pathlib.Path(__file__).resolve().parent.parent
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'

UNSPLASH_JS = """() => [...document.querySelectorAll('figure')].map(f => {
  const a = f.querySelector('a[href*="/photos/"]'); const img = f.querySelector('img[src*="images.unsplash.com/photo-"]');
  const au = f.querySelector('a[href^="/@"]') || (f.parentElement && f.parentElement.querySelector('a[href^="/@"]'));
  return {href: a && a.getAttribute('href'), src: img && img.getAttribute('src'), alt: img && img.getAttribute('alt'),
          author: au ? au.textContent.trim() : '', plus: /Unsplash\\+|plus\\.unsplash/.test(f.innerHTML)};
}).filter(x => x.href && x.src)"""
PEXELS_JS = """() => [...document.querySelectorAll('article')].map(a => {
  const l = a.querySelector('a[href*="/photo/"]'); const img = a.querySelector('img');
  const au = a.querySelector('a[href^="/@"]');
  return {href: l && l.getAttribute('href'), alt: img && img.getAttribute('alt'), author: au ? au.textContent.trim() : ''};
}).filter(x => x.href)"""


def search(page, source, query, per):
    if source == 'unsplash':
        slug = re.sub(r'\s+', '-', query.strip())
        url = f'https://unsplash.com/s/photos/{slug}?license=free'
        js = UNSPLASH_JS
    else:
        url = f'https://www.pexels.com/search/{query.strip()}/'
        js = PEXELS_JS
    page.goto(url, wait_until='domcontentloaded', timeout=45000)
    page.wait_for_timeout(4000)
    for _ in range(3):
        page.mouse.wheel(0, 2500)
        page.wait_for_timeout(900)
    out, seen = [], set()
    for x in page.evaluate(js):
        if source == 'unsplash':
            if x.get('plus'):
                continue
            m = re.search(r'([A-Za-z0-9_-]{11})$', x['href'].rstrip('/'))
            base = x['src'].split('?')[0]
            if not m or 'images.unsplash.com/photo-' not in base:
                continue
            pid = m.group(1)
            item = {'source': 'unsplash', 'id': pid, 'page_url': 'https://unsplash.com' + x['href'], 'img_base': base,
                    'thumb_url': base + '?fm=jpg&q=70&w=900', 'license': 'Unsplash License', 'license_url': 'https://unsplash.com/license'}
        else:
            m = re.search(r'-(\d+)/?$', x['href'])
            if not m:
                continue
            pid = m.group(1)
            item = {'source': 'pexels', 'id': pid, 'page_url': 'https://www.pexels.com' + x['href'],
                    'img_base': f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg',
                    'thumb_url': f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=900',
                    'license': 'Pexels License', 'license_url': 'https://www.pexels.com/license/'}
        if pid in seen:
            continue
        seen.add(pid)
        item.update(alt=(x.get('alt') or '').removeprefix('Free ').strip(), author=x.get('author') or '', query=query)
        out.append(item)
        if len(out) >= per:
            break
    return out


def sheet(items, folder):
    cols, w, h, pad = 4, 360, 240, 34
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * w, rows * (h + pad)), 'white')
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype('malgun.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    for i, it in enumerate(items):
        x, y = (i % cols) * w, (i // cols) * (h + pad)
        try:
            im = Image.open(folder / it['file']).convert('RGB')
            im.thumbnail((w - 8, h - 8))
            canvas.paste(im, (x + (w - im.width) // 2, y + (h - im.height) // 2))
        except Exception:
            draw.text((x + 10, y + 10), '불러오기 실패', fill='red', font=font)
        draw.text((x + 8, y + h + 4), f'#{it["n"]} {it["source"][:2]} {it["alt"][:26]}', fill='black', font=font)
    canvas.save(folder.parent / 'sheet.jpg', quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--set', required=True)
    ap.add_argument('--query', action='append', required=True)
    ap.add_argument('--per', type=int, default=8, help='검색어·출처별 후보 수')
    ap.add_argument('--sources', default='unsplash,pexels')
    a = ap.parse_args()
    folder = BASE / 'research' / 'photos' / a.set / 'cand'
    folder.mkdir(parents=True, exist_ok=True)
    items = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome', headless=True, args=['--disable-blink-features=AutomationControlled'])
        ctx = b.new_context(viewport={'width': 1400, 'height': 1000}, locale='en-US', user_agent=UA)
        page = ctx.new_page()
        for q in a.query:
            for src in a.sources.split(','):
                try:
                    found = search(page, src, q, a.per)
                except Exception as e:
                    print('검색 실패', src, q, str(e)[:120])
                    continue
                for it in found:
                    if any(x['source'] == it['source'] and x['id'] == it['id'] for x in items):
                        continue
                    r = ctx.request.get(it['thumb_url'], timeout=30000)
                    if not r.ok:
                        print('받기 실패', it['page_url'], r.status)
                        continue
                    it['file'] = f'{it["source"]}-{it["id"]}.jpg'
                    (folder / it['file']).write_bytes(r.body())
                    it['n'] = len(items) + 1
                    items.append(it)
                print(f'{src} "{q}" → {len(found)}')
        b.close()
    (folder.parent / 'candidates.json').write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding='utf-8')
    sheet(items, folder)
    print(f'{a.set}: 후보 {len(items)}장 → research/photos/{a.set}/sheet.jpg')


if __name__ == '__main__':
    main()
