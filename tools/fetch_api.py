"""공공데이터포털 '대한민국 공공서비스(혜택) 정보' API에서 교육·훈련·응시료·창업 관련 서비스를 받아
db/api_gov24.json 으로 저장한다. GitHub Actions에서 매일 실행된다.

환경변수 DATA_GO_KR_KEY: 공공데이터포털 일반 인증키(Decoding).
실패하면 기존 파일을 건드리지 않고 종료 코드 0으로 끝낸다(빌드는 계속 진행).
"""
import datetime
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, 'db', 'api_gov24.json')
API = 'https://api.odcloud.kr/api/gov24/v3'
KEY = os.environ.get('DATA_GO_KR_KEY', '')
KST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.datetime.now(KST).date().isoformat()

KEYWORDS = ['교육', '훈련', '강좌', '아카데미', '자격', '응시료', '창업', '취업']
EXCLUDE = re.compile(r'보육|어린이집|유치원|교육급여|교육비 지원|학자금|급식|무상교육|방과후|의무교육')

SIDO_LONG = {'서울특별시': '서울', '부산광역시': '부산', '대구광역시': '대구', '인천광역시': '인천', '광주광역시': '광주',
             '대전광역시': '대전', '울산광역시': '울산', '세종특별자치시': '세종', '경기도': '경기', '강원특별자치도': '강원',
             '강원도': '강원', '충청북도': '충북', '충청남도': '충남', '전북특별자치도': '전북', '전라북도': '전북',
             '전라남도': '전남', '경상북도': '경북', '경상남도': '경남', '제주특별자치도': '제주'}


def get(path, params):
    q = {'page': 1, 'perPage': 1000, 'returnType': 'JSON', 'serviceKey': KEY}
    q.update(params)
    url = f'{API}/{path}?{urllib.parse.urlencode(q)}'
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception as e:  # noqa: BLE001 - 네트워크 오류는 재시도 후 포기
            err = e
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f'{path} 실패: {err}')


def get_all(path, params):
    rows, page = [], 1
    while True:
        d = get(path, dict(params, page=page))
        rows += d.get('data', [])
        if page * 1000 >= d.get('matchCount', d.get('totalCount', 0)) or not d.get('data'):
            return rows
        page += 1


def on(v):
    return str(v or '').strip().upper() in ('Y', '1', 'TRUE', 'O')


def region_of(org):
    org = org or ''
    for k, v in SIDO_LONG.items():
        if org.startswith(k):
            rest = org[len(k):].strip()
            gu = rest.split(' ')[0] if rest else ''
            return [f'{v} {gu}'] if gu.endswith(('시', '군', '구')) else [v]
    return ['전국']


def kinds_of(text):
    k = []
    if '응시' in text:
        k.append('응시료')
    if '창업' in text:
        k.append('창업')
    if re.search(r'수당|장려금', text) and re.search(r'교육|훈련', text):
        k.append('돈받는교육')
    elif re.search(r'교육|훈련|강좌|아카데미', text):
        k.append('무료교육')
    if not k:
        k.append('지원금')
    return k


def tri(v):
    return '가능' if v else '확인필요'


def main():
    if not KEY:
        print('DATA_GO_KR_KEY 없음, 건너뜀')
        return
    services = {}
    for kw in KEYWORDS:
        for s in get_all('serviceList', {'cond[서비스명::LIKE]': kw}):
            if not EXCLUDE.search(s.get('서비스명', '')):
                services[s['서비스ID']] = s
    conds = {c['서비스ID']: c for c in get_all('supportConditions', {})}
    out = []
    for sid, s in services.items():
        c = conds.get(sid, {})
        pct = None
        for code, bound in (('JA0201', 50), ('JA0202', 75), ('JA0203', 100), ('JA0204', 200)):
            if on(c.get(code)):
                pct = bound
        any_income = any(on(c.get(x)) for x in ('JA0201', 'JA0202', 'JA0203', 'JA0204', 'JA0205'))
        income = '기준있음' if (any_income and not on(c.get('JA0205')) and pct) else ('제한없음' if on(c.get('JA0205')) else '확인필요')
        text = ' '.join(str(s.get(k) or '') for k in ('서비스명', '서비스목적요약', '지원내용'))
        name = s.get('서비스명', '').strip()
        a0, a1 = c.get('JA0110'), c.get('JA0111')
        out.append({
            'id': 'g-' + re.sub(r'[^a-z0-9]', '', sid.lower())[:24],
            'name': name,
            'operator': ' '.join(x for x in [s.get('소관기관명'), s.get('부서명')] if x),
            'official_url': s.get('상세조회URL') or 'https://www.gov.kr',
            'apply_url': '',
            'kinds': kinds_of(text),
            'fields': ['전분야'],
            'regions': region_of(s.get('소관기관명')),
            'age_min': int(a0) if str(a0 or '').isdigit() and int(a0) > 0 else None,
            'age_max': int(a1) if str(a1 or '').isdigit() and 0 < int(a1) < 120 else None,
            'education': '확인필요', 'education_note': '',
            'income': income, 'income_pct_max': pct if income == '기준있음' else None,
            'income_note': (s.get('선정기준') or '')[:200],
            'allow_job_seeker': tri(on(c.get('JA0327'))),
            'allow_employed': tri(on(c.get('JA0326'))),
            'allow_business': tri(any(on(c.get(x)) for x in ('JA1101', 'JA1102', 'JA1103'))),
            'allow_student': tri(any(on(c.get(x)) for x in ('JA0317', 'JA0318', 'JA0319', 'JA0320'))),
            'other_conditions': (s.get('지원대상') or '')[:300],
            'cost': '공고에서 확인',
            'money': (s.get('지원내용') or '공고에서 확인')[:300],
            'money_monthly_max_manwon': None,
            'format': '',
            'recruit': (s.get('신청기한') or '공고에서 확인')[:120],
            'next_deadline': None,
            'summary': (s.get('서비스목적요약') or name)[:200],
            'sources': [{'url': s.get('상세조회URL') or 'https://www.gov.kr', 'quote': (s.get('지원대상') or name)[:300]}],
            'origin': 'api-gov24',
            'checked_at': TODAY,
        })
    tmp = OUT + '.tmp'
    json.dump(out, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    os.replace(tmp, OUT)
    print(f'공공서비스 {len(out)}건 저장')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # noqa: BLE001
        print('API 수집 실패, 기존 데이터로 빌드:', e, file=sys.stderr)
