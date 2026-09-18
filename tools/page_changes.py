"""빌드 뒤·배포 전(GitHub Actions): 쪽마다 내용 지문을 만들어 지난 배포와 비교한다.

- 지난 배포의 지문은 실제 사이트의 page-state.json에서 받는다(없으면 첫 배포로 본다).
- sitemap.xml의 lastmod를 '내용이 실제로 바뀐 날'로 고쳐 쓴다. 빌드는 매일 다시 하므로
  그대로 두면 모든 쪽이 날마다 오늘 날짜가 되어, 검색엔진이 lastmod를 믿지 않게 된다.
- 날마다 저절로 바뀌는 글자(마감 D-3·3일 남음·9월 19일 기준·마지막 갱신 날짜)는 지문에서 뺀다.
- 바뀐 쪽(새로 생긴 쪽·없어진 쪽 포함) 주소를 --out 파일에 한 줄씩 적는다 → 배포 뒤 tools/indexnow_ping.py.
- 지난 배포의 지문을 받지 못하면(네트워크 오류) lastmod는 오늘로 두고 알릴 주소는 비운다.

표준 라이브러리만 쓴다.  python tools/page_changes.py [--site site] [--out changed.txt] [--prev 파일|URL]
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(BASE, 'config.json'), encoding='utf-8'))
SITE_URL = cfg['base_url'].rstrip('/')
KST = datetime.timezone(datetime.timedelta(hours=9))
STATE = 'page-state.json'

# 날마다 저절로 바뀌는 글자 — 내용이 바뀐 것으로 치지 않는다
VOLATILE = re.compile(r'마감\s*D-\d+|\(D-\d+\)|D-\d+|\d+일\s*남음|오늘\s*마감'
                      r'|\d{1,2}월\s*\d{1,2}일\s*(?:기준|갱신)|마지막\s*갱신\s*\d{4}-\d{2}-\d{2}')


class Text(HTMLParser):
    """보이는 글·링크 주소·그림 설명·제목·설명만 모은다(script·style·template 속은 뺀다)"""
    SKIP = {'script', 'style', 'noscript', 'template'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip, self.out = 0, []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self.skip += 1
        elif tag == 'a' and a.get('href'):
            self.out.append('@' + a['href'])
        elif tag == 'img' and a.get('alt'):
            self.out.append(a['alt'])
        elif tag == 'meta' and a.get('name') in ('description', 'robots') and a.get('content'):
            self.out.append(a['name'] + '=' + a['content'])
        elif tag == 'link' and a.get('rel') == 'canonical' and a.get('href'):
            self.out.append('canonical=' + a['href'])

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.out.append(data)


def fingerprint(path):
    p = Text()
    p.feed(open(path, encoding='utf-8').read())
    text = VOLATILE.sub('', ' '.join(p.out))
    # 마감 당일엔 '9월 20일(일) 마감 · 1일 남음'이 '오늘 마감 · 9월 20일(일)'로 모양만 바뀐다 → '마감'·가운뎃점은 보지 않는다
    text = re.sub(r'마감|·', ' ', text)
    return hashlib.sha256(' '.join(text.split()).encode('utf-8')).hexdigest()[:24]


def url_to_file(site, url):
    rel = url[len(SITE_URL) + 1:]
    if rel == '' or rel.endswith('/'):
        rel += 'index.html'
    return os.path.join(site, *rel.split('/'))


def load_prev(src):
    """(상태, 설명). 상태가 None이면 지난 배포가 없음(첫 배포), 'unknown'이면 받지 못함"""
    if os.path.exists(src):
        return json.load(open(src, encoding='utf-8')), '파일'
    for i in range(3):
        try:
            req = urllib.request.Request(src, headers={'Cache-Control': 'no-cache', 'User-Agent': 'page-changes'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode('utf-8')), '실제 사이트'
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, '없음(첫 배포)'
            err = f'HTTP {e.code}'
        except Exception as e:  # 네트워크 오류·JSON 오류
            err = repr(e)
        time.sleep(3 * (i + 1))
    return 'unknown', f'받지 못함: {err}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', default=os.path.join(BASE, 'site'))
    ap.add_argument('--out', default=os.path.join(BASE, 'changed-urls.txt'))
    ap.add_argument('--prev', default=f'{SITE_URL}/{STATE}')
    a = ap.parse_args()

    sm_path = os.path.join(a.site, 'sitemap.xml')
    sm = open(sm_path, encoding='utf-8').read()
    urls = re.findall(r'<loc>([^<]+)</loc>', sm)
    # 빌드한 날 = build.py가 모든 lastmod에 적은 날(자정을 넘겨 돌아도 빌드와 같은 날로)
    built = set(re.findall(r'<lastmod>([^<]+)</lastmod>', sm))
    today = built.pop() if len(built) == 1 else datetime.datetime.now(KST).date().isoformat()
    prev, how = load_prev(a.prev)
    old = (prev or {}).get('pages', {}) if isinstance(prev, dict) else {}

    pages, changed = {}, []
    for u in urls:
        loc = u.replace('&amp;', '&')
        h = fingerprint(url_to_file(a.site, loc))
        was = old.get(loc)
        if isinstance(prev, dict) and was and was.get('h') == h:
            pages[loc] = {'h': h, 'm': was.get('m') or today}
        else:
            pages[loc] = {'h': h, 'm': today}
            if prev != 'unknown':
                changed.append(loc)
    gone = [u for u in old if u not in pages] if isinstance(prev, dict) else []
    changed += gone

    def put_lastmod(m):
        loc = m.group(1).replace('&amp;', '&')
        return f'<url><loc>{m.group(1)}</loc><lastmod>{pages[loc]["m"]}</lastmod></url>'
    sm2, n = re.subn(r'<url><loc>([^<]+)</loc><lastmod>[^<]*</lastmod></url>', put_lastmod, sm)
    if n != len(urls):
        sys.exit(f'sitemap.xml 모양이 예상과 다름: url {len(urls)}개 중 {n}개만 바꿈')
    open(sm_path, 'w', encoding='utf-8').write(sm2)
    json.dump({'v': 1, 'built': today, 'pages': pages}, open(os.path.join(a.site, STATE), 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    open(a.out, 'w', encoding='utf-8').write(''.join(u + '\n' for u in changed))
    print(f'지난 배포 지문: {how} | 쪽 {len(pages)} | 바뀐 쪽 {len(changed) - len(gone)} · 없어진 쪽 {len(gone)} → {a.out}')


if __name__ == '__main__':
    main()
