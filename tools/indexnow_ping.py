"""배포 뒤(GitHub Actions): tools/page_changes.py가 적은 바뀐 쪽 주소를 IndexNow로 알린다.

빙(www.bing.com)과 네이버(searchadvisor.naver.com)에 직접 보내고, 빙은 다른 참여 검색엔진에도 나눠 준다.
키는 config.json indexnow_key, 키 파일은 build.py가 사이트 맨 위에 <키>.txt로 만든다.
배포는 이미 끝났으므로 실패해도 경고만 남기고 0으로 끝낸다. 표준 라이브러리만 쓴다.
  python tools/indexnow_ping.py changed-urls.txt [--dry]
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cfg = json.load(open(os.path.join(BASE, 'config.json'), encoding='utf-8'))
SITE_URL = cfg['base_url'].rstrip('/')
KEY = cfg.get('indexnow_key', '')
ENDPOINTS = ['https://www.bing.com/indexnow', 'https://searchadvisor.naver.com/indexnow']


def get(url):
    req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'indexnow-ping'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', 'replace').strip()


def main():
    path, dry = sys.argv[1], '--dry' in sys.argv
    urls = [u.strip() for u in open(path, encoding='utf-8') if u.strip().startswith(SITE_URL + '/')] if os.path.exists(path) else []
    if not KEY:
        print('indexnow_key 없음 — 건너뜀')
        return
    if not urls:
        print('바뀐 쪽 없음 — 알릴 것 없음')
        return
    key_url = f'{SITE_URL}/{KEY}.txt'
    for i in range(4):  # 새 배포가 퍼지기 전이면 잠깐 기다린다
        try:
            if get(key_url) == KEY:
                break
            print('키 파일 내용이 다름')
        except Exception as e:
            print('키 파일 확인 실패', repr(e))
        time.sleep(15)
    else:
        print('::warning::IndexNow 키 파일을 확인하지 못해 알리지 않음')
        return
    body = json.dumps({'host': SITE_URL.split('://', 1)[1], 'key': KEY, 'keyLocation': key_url,
                       'urlList': urls[:10000]}).encode('utf-8')
    print(f'알릴 쪽 {len(urls)}개', '(시험: 보내지 않음)' if dry else '')
    if dry:
        return
    for ep in ENDPOINTS:
        req = urllib.request.Request(ep, data=body, method='POST',
                                     headers={'Content-Type': 'application/json; charset=utf-8', 'User-Agent': 'indexnow-ping'})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(ep, r.status)  # 200 받음 · 202 받음(키 확인 대기)
        except urllib.error.HTTPError as e:
            print(f'::warning::{ep} HTTP {e.code} {e.read()[:200]!r}')
        except Exception as e:
            print(f'::warning::{ep} {e!r}')


if __name__ == '__main__':
    main()
