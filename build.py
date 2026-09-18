"""배움지원 찾기 — 정적 사이트 생성기.

입력: config.json, db/programs.json (없으면 db/sample.json), content/guides.json(선택)
출력: site/ (GitHub Pages에 그대로 올림)

시안 비교: python build.py --src research/proto/a/src --out research/proto/a/site
  --src 폴더의 layout.html·*.css·*.js를 쓰고, theme.py가 있으면 아래 "렌더링" 함수를 덮어쓴다.
"""
import datetime
import html
import json
import os
import re
import shutil
import sys
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))


def _arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


SRC = os.path.abspath(_arg('--src', os.path.join(BASE, 'src')))
OUT = os.path.abspath(_arg('--out', os.path.join(BASE, 'site')))
if os.path.commonpath([OUT, BASE]) != BASE or OUT == BASE:
    sys.exit(f'--out은 프로젝트 안의 하위 폴더여야 합니다: {OUT}')

cfg = json.load(open(os.path.abspath(_arg('--config', os.path.join(BASE, 'config.json'))), encoding='utf-8'))  # --config: 광고 코드 시험 빌드용
KST = datetime.timezone(datetime.timedelta(hours=9))
TODAY = datetime.date.fromisoformat(cfg['today']) if cfg.get('today') else datetime.datetime.now(KST).date()
SITE = cfg['site_name']
BASE_URL = (cfg.get('base_url') or '').rstrip('/')

db_path = os.path.join(BASE, 'db', 'programs.json')
SAMPLE = not os.path.exists(db_path)
programs = json.load(open(db_path if not SAMPLE else os.path.join(BASE, 'db', 'sample.json'), encoding='utf-8'))
# 공공서비스 API 자동 수집분: 사람이 정리한 제도와 이름이 겹치면 버린다
api_path = os.path.join(BASE, 'db', 'api_gov24.json')
if os.path.exists(api_path) and not SAMPLE:
    known = {re.sub(r'\s', '', p['name']) for p in programs}
    programs += [q for q in json.load(open(api_path, encoding='utf-8')) if re.sub(r'\s', '', q['name']) not in known]
guides_path = os.path.join(BASE, 'content', 'guides.json')
guides = json.load(open(guides_path, encoding='utf-8')) if os.path.exists(guides_path) else []

E = lambda s: html.escape(str(s if s is not None else ''), quote=True)

# ---------- 분류 ----------
SIDO = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주']
SIDO_SLUG = dict(zip(SIDO, ['seoul', 'busan', 'daegu', 'incheon', 'gwangju', 'daejeon', 'ulsan', 'sejong', 'gyeonggi', 'gangwon',
                            'chungbuk', 'chungnam', 'jeonbuk', 'jeonnam', 'gyeongbuk', 'gyeongnam', 'jeju']))
LONG = {'서울특별시': '서울', '서울시': '서울', '부산광역시': '부산', '대구광역시': '대구', '인천광역시': '인천', '광주광역시': '광주',
        '대전광역시': '대전', '울산광역시': '울산', '세종특별자치시': '세종', '경기도': '경기', '강원특별자치도': '강원', '강원도': '강원',
        '충청북도': '충북', '충청남도': '충남', '전북특별자치도': '전북', '전라북도': '전북', '전라남도': '전남', '경상북도': '경북',
        '경상남도': '경남', '제주특별자치도': '제주', '제주도': '제주'}
KINDS = [('무료교육', 'free', '무료 교육', '본인이 내는 돈 없이 들을 수 있는 교육입니다.'),
         ('돈받는교육', 'paid', '배우면서 돈 받기', '교육이나 훈련에 참여하는 동안 수당·장려금을 주는 제도입니다.'),
         ('지원금', 'grant', '지원금', '교육·취업 준비와 연결된 현금·바우처 지원입니다.'),
         ('응시료', 'exam', '자격증 응시료', '자격증 시험 응시료를 대신 내 주거나 돌려주는 제도입니다.'),
         ('창업', 'startup', '창업 지원', '창업 교육과 사업화 자금을 지원하는 제도입니다.')]
KIND_SLUG = {k: s for k, s, _, _ in KINDS}
KIND_LABEL = {k: l for k, _, l, _ in KINDS}
FIELDS = [('IT·AI', 'it'), ('영상·디자인', 'media'), ('기술·현장', 'tech'), ('사무·회계·경영', 'office'),
          ('외국어', 'lang'), ('요리·서비스', 'service'), ('돌봄·보건', 'care'), ('전 분야', 'all')]
FIELD_SLUG = dict(FIELDS)
ICON = {
    'it': '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4M9.5 8 7.5 10l2 2M14.5 8l2 2-2 2"/>',
    'media': '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m10 9 5 3-5 3z"/>',
    'tech': '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.1L4 16.7 7.3 20l5.3-5.3a4 4 0 0 0 5.1-5.4l-2.4 2.4-2.6-.6-.6-2.6z"/>',
    'office': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2M3 12h18"/>',
    'lang': '<path d="M4 5h16v10H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    'service': '<path d="M4 11h16a8 8 0 0 1-16 0z"/><path d="M8 7.5c0-1 1-1.5 1-2.5M12 7.5c0-1 1-1.5 1-2.5M16 7.5c0-1 1-1.5 1-2.5"/>',
    'care': '<path d="M12 20s-7-4.3-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.7-7 10-7 10z"/><path d="M12 9.5v5M9.5 12h5"/>',
    'all': '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
}
TARGETS = [('장애인', 'dis'), ('북한 이탈 주민', 'nk'), ('제대 군인·보훈', 'vet'), ('산재 근로자', 'inj'), ('여성', 'women'),
           ('결혼 이민자·다문화', 'mig'), ('자립 준비 청년', 'care'), ('학교 밖 청소년', 'oos'), ('농어업인', 'farm'), ('기초 생활 수급자·차상위', 'low')]
TARGET_SLUG = dict(TARGETS)
EDU_CODE = {'제한없음': 'none', '고졸이상': 'hs', '대학재학': 'uni', '대졸이상': 'grad', '기타': 'etc', '확인필요': 'unk'}
INC_CODE = {'제한없음': 'none', '기준있음': 'yes', '확인필요': 'unk'}
TRI_CODE = {'가능': 'y', '불가': 'n', '확인필요': 'u'}
# 기간 필터: 알바몬식 숫자 구간(일수). 하루·단기·중기·장기는 카드의 보조 단어(duration.band)로만 쓴다
DURATION_BUCKETS = [('d7', '1주 이하', 1, 7), ('m1', '1개월 이하', 8, 31), ('m3', '1~3개월', 32, 92),
                    ('m6', '3~6개월', 93, 183), ('lg', '6개월 넘게', 184, 10 ** 6)]
PHOTO_SET_BY_KIND = {'무료교육': 'classroom', '돈받는교육': 'tech', '지원금': 'office', '응시료': 'exam', '창업': 'startup'}
PHOTO_SET_BY_FIELD = {'IT·AI': 'it', '영상·디자인': 'media', '기술·현장': 'tech', '사무·회계·경영': 'office',
                      '외국어': 'lang', '요리·서비스': 'food', '돌봄·보건': 'care', '전 분야': 'classroom'}
WEEKDAYS = '월화수목금토일'


def norm_region(r):
    r = (r or '').strip()
    for k in sorted(LONG, key=len, reverse=True):
        if r.startswith(k):
            return LONG[k] + r[len(k):]
    return r


# ---------- 검사 ----------
schema = json.load(open(os.path.join(BASE, 'db', 'schema.json'), encoding='utf-8'))
errors = []
seen = set()
for p in programs:
    pid = p.get('id', '?')
    for k in schema['required']:
        if k not in p or p[k] in (None, '', []):
            errors.append(f'{pid}: {k} 비어 있음')
    for k, spec in schema['properties'].items():
        v = p.get(k)
        if v is None:
            continue
        if 'enum' in spec and v not in spec['enum']:
            errors.append(f'{pid}: {k}={v!r} 허용값 아님')
        if spec.get('type') == 'array' and 'enum' in spec.get('items', {}):
            bad = [x for x in v if x not in spec['items']['enum']]
            if bad:
                errors.append(f'{pid}: {k} 허용값 아님 {bad}')
    if pid in seen:
        errors.append(f'{pid}: id 중복')
    seen.add(pid)
    if not re.match(r'^[a-z0-9-]+$', pid):
        errors.append(f'{pid}: id 형식')
    p['regions'] = [norm_region(r) for r in p.get('regions', [])]
    for r in p['regions']:
        if r != '전국' and r.split(' ')[0] not in SIDO:
            errors.append(f'{pid}: 지역 {r!r} 인식 불가')
if errors:
    print('데이터 오류', len(errors))
    print('\n'.join(errors[:60]))
    sys.exit(1)


# ---------- 공통 ----------
def dday(s):
    if not s:
        return None
    try:
        return (datetime.date.fromisoformat(s) - TODAY).days
    except ValueError:
        return None


def icon(p):
    return f'<span class="ico" aria-hidden="true"><svg viewBox="0 0 24 24">{ICON[FIELD_SLUG[p["fields"][0]]]}</svg></span>'


def region_text(p):
    return '전국' if '전국' in p['regions'] else ', '.join(p['regions'])


def region_short(p):
    if '전국' in p['regions']:
        return '전국'
    first = p['regions'][0]
    return first if len(p['regions']) == 1 else f'{first} 외 {len(p["regions"]) - 1}곳'


def manwon(n):
    return f'{n:,.0f}' if float(n).is_integer() else f'{n:,.1f}'.rstrip('0').rstrip('.')


def duration_label(p):
    """(구간, 길이) — 예 ('중기', '5~6개월'), ('', '총 100시간'), ('과정마다 다름', '').
    구간이 비면 길이만 쓴다. 교육 과정이 아니거나(지원금 등) 필드가 없으면 None → 기간 줄을 통째로 뺀다."""
    d = p.get('duration') or {}
    kind = d.get('kind')
    if kind in ('varies', 'self_paced'):
        return (d.get('band') or '', '')
    if kind in ('fixed', 'range'):
        return (d.get('band') or '', d.get('text') or '')
    if kind == 'unknown':
        return ('', '공고 확인')
    return None


def duration_codes(p):
    """기간 필터 코드(DURATION_BUCKETS). [days_min, days_max]가 걸치는 구간 모두. 날짜·달력 단위가 없으면 빈 목록."""
    d = p.get('duration') or {}
    lo, hi = d.get('days_min'), d.get('days_max')
    if lo is None and hi is None:
        return []
    lo = lo if lo is not None else hi
    hi = hi if hi is not None else 10 ** 6
    return [c for c, _, a, b in DURATION_BUCKETS if lo <= b and hi >= a]


def money_text(p):
    m = p.get('money_monthly_max_manwon')
    return f'월 최대 {manwon(m)}만원' if m else (p.get('money_short') or '')


def deadline_info(p):
    """마감 표시. {'date','text','left','days','urgent'} 또는 None(마감 정보 없음). urgent는 3일 이내."""
    s = p.get('next_deadline')
    d = dday(s)
    if d is not None and d >= 0:
        dt = datetime.date.fromisoformat(s)
        return {'date': s, 'text': f'{dt.month}월 {dt.day}일({WEEKDAYS[dt.weekday()]}) 마감',
                'left': '오늘 마감' if d == 0 else f'{d}일 남음', 'days': d, 'urgent': d <= 3}
    if '상시' in (p.get('recruit') or ''):
        return {'date': '', 'text': '상시 모집', 'left': '', 'days': None, 'urgent': False}
    return None


def card_facts(p):
    """목록 카드에 올리는 핵심 칸 [(키, 라벨, 값)]. 값이 없으면 칸을 뺀다. 긴 문장은 상세 페이지에만.
    키: dur 기간 · sch 일정 · reg 지역 · money 받는 돈 · cost 내는 돈 · cost_unk 비용 모름(흐리게 한 번만)"""
    out = []
    lab = duration_label(p)
    if lab is not None:
        out.append(('dur', '기간', ' · '.join(x for x in lab if x) or '공고 확인'))
    sch = p.get('schedule')
    if sch in ('주간', '야간·주말', '온라인', '혼합') or (sch == '과정마다 다름' and (lab or ('',))[0] != '과정마다 다름'):
        out.append(('sch', '일정', sch))
    out.append(('reg', '지역', region_short(p)))
    money = money_text(p)
    if money:
        out.append(('money', '받는 돈', money))
    cost = {'무료': ('cost', '내는 돈', '무료'), '일부 자부담': ('cost', '내는 돈', '일부 자부담'),
            '확인필요': ('cost_unk', '비용', '공고 확인')}.get(p.get('cost_type'))
    if cost:
        out.append(cost)
    return out


def age_text(p):
    a0, a1 = p.get('age_min'), p.get('age_max')
    if p.get('age_unknown') and a0 is None and a1 is None:
        return '나이 제한 있음(공고에서 확인)'
    if a0 is not None and a1 is not None:
        return f'만 {a0}~{a1}세'
    if a0 is not None:
        return f'만 {a0}세 이상'
    if a1 is not None:
        return f'만 {a1}세 이하'
    return '공고에 나이 조건 없음'


# 사진은 시안끼리 같은 것을 쓴다: 시안 src에 img가 없으면 기본 src/img
IMG_DIR = os.path.join(SRC, 'img') if os.path.isdir(os.path.join(SRC, 'img')) else os.path.join(BASE, 'src', 'img')
CREDITS = json.load(open(os.path.join(IMG_DIR, 'credits.json'), encoding='utf-8')) if os.path.exists(os.path.join(IMG_DIR, 'credits.json')) else []
IMG_WIDTHS = (480, 960, 1600)


def photos(set_name, use=None):
    """사진 목록(선정 순서). set: people·classroom·tech·it·media·office·lang·food·care·startup·exam, use: hero·category·card"""
    return sorted((c for c in CREDITS if c['set'] == set_name and (use is None or use in c.get('uses', []))),
                  key=lambda c: c.get('order', 999))


def img_html(c, sizes='100vw', cls='', alt='', eager=False):
    """srcset <img>. 글자 라벨 옆 장식 사진이면 alt는 빈 문자열."""
    w0, h0 = c['size']
    srcset = ', '.join(f'{{{{ROOT}}}}assets/img/{c["name"]}-{w}.webp {w}w' for w in IMG_WIDTHS)
    return (f'<img class="{E(cls)}" src="{{{{ROOT}}}}assets/img/{c["name"]}-960.webp" srcset="{srcset}" sizes="{E(sizes)}" '
            f'width="960" height="{round(960 * h0 / w0)}" alt="{E(alt)}" loading="{"eager" if eager else "lazy"}" decoding="async">')

layout = open(os.path.join(SRC, 'layout.html'), encoding='utf-8').read()

# ---------- 광고 ----------
# 9/17 사용자: "읽다가 중간에 뜨는 거 말고 양옆 여백에. 가장 중요한 건 사용자가 짜증 나지 않는 것."
# → 글·목록 중간에는 광고를 넣지 않는다. 넓은 화면(1536px 이상)은 본문 양옆 여백에 세로 광고(160×600, 스크롤을 따라오되 본문을 덮지 않음),
#   그보다 좁은 화면·휴대폰은 글이나 목록을 다 본 끝자리에 하나만. 양옆 광고가 뜬 쪽에서는 끝자리 광고를 쓰지 않는다(채우기는 assets/ads.js).
# 자리마다 카카오 애드핏을 먼저 부르고, 광고가 없으면(NO-AD) 애드센스로 넘긴다(애드핏 웹 SDK 가이드의 외부 광고 순차 호출 예시).
# 애드핏 운영정책 5.2(2026-09-02 시행): 한 쪽에 애드핏 광고 4개 이하, 다른 광고 회사 스크립트를 동시에 여러 개 띄우지 않음(순차 사용은 허용).
# 애드센스 자동 광고는 켜지 않는다(애드핏과 동시에 뜨고 본문 사이·화면 아래를 덮는다). 아이디가 하나도 없으면 광고 코드 없음.
ADS = cfg.get('ads') or {}
AD_PREVIEW = os.environ.get('ADS_PREVIEW') == '1'   # 자리 확인용 빌드: 점선 칸만 그리고 광고 코드는 넣지 않는다
AD_SIZE = {'side': (160, 600), 'end_pc': (728, 90), 'end_mo': (320, 100)}   # 애드핏 광고 단위를 만들 때 고를 크기(ads.js와 같게)
_AD_KEYS = {'adfit_side_l': r'DAN-[A-Za-z0-9]{8,32}', 'adfit_side_r': r'DAN-[A-Za-z0-9]{8,32}',
            'adfit_end_pc': r'DAN-[A-Za-z0-9]{8,32}', 'adfit_end_mo': r'DAN-[A-Za-z0-9]{8,32}',
            'adsense_side_l': r'\d{6,20}', 'adsense_side_r': r'\d{6,20}', 'adsense_end': r'\d{6,20}'}
_ad_bad = [f'ads.{k}={v!r}' for k, v in ADS.items() if k not in _AD_KEYS or (v and not re.fullmatch(_AD_KEYS[k], v))]
if cfg.get('adsense_client') and not re.fullmatch(r'ca-pub-\d{10,20}', cfg['adsense_client']):
    _ad_bad.append(f'adsense_client={cfg["adsense_client"]!r}')
if _ad_bad:
    sys.exit('config.json 광고 설정이 맞지 않습니다(애드핏 DAN-…, 애드센스 ca-pub-숫자·슬롯 숫자, 이름은 ' + ', '.join(_AD_KEYS) + '): ' + ', '.join(_ad_bad))
_GS = bool(cfg.get('adsense_client'))
_AD_JS = {js: ADS.get(k) for js, k, gs in (('sl', 'adfit_side_l', 0), ('sr', 'adfit_side_r', 0), ('ep', 'adfit_end_pc', 0), ('em', 'adfit_end_mo', 0),
                                           ('gl', 'adsense_side_l', 1), ('gr', 'adsense_side_r', 1), ('ge', 'adsense_end', 1))
          if ADS.get(k) and (_GS or not gs)}


def _ad_preview_box(label, sizes):
    """자리 확인용 점선 칸. sizes: (컴퓨터 (w, h), 휴대폰 (w, h))"""
    (wp, hp), (wm, hm) = sizes
    txt = f'<span class="ad-ph-pc">{wp}×{hp}</span><span class="ad-ph-mo">{wm}×{hm}</span>' if (wp, hp) != (wm, hm) else f'<span>{wp}×{hp}</span>'
    return (f'<div class="ad-box" style="--w-pc:{wp}px;--h-pc:{hp}px;--w-mo:{wm}px;--h-mo:{hm}px">'
            f'<span class="ad-ph"><b>{label}</b>{txt}</span></div>')


def ad_rails(body, p=None):
    """넓은 화면의 양옆 여백 광고. body를 본문 칸 너비의 틀로 감싸고, 틀 바깥 왼쪽·오른쪽에 세로 광고를 붙인다.
    틀은 파란 머리 띠·회색 안내 글 띠·푸터 같은 화면 너비 띠를 넣지 않게 감싼다(광고가 띠 위로 올라가지 않게).
    자동 수집(API) 제도 쪽에는 넣지 않는다: 애드핏 정책이 'API로 가져온 정보들로만 구성한' 콘텐츠의 광고를 막는다"""
    if p is not None and p.get('origin') != 'manual':
        return body
    rails = ''
    for side, name in (('l', '왼쪽'), ('r', '오른쪽')):
        if AD_PREVIEW:
            rails += (f'<aside class="ad-side ad-side-{side} ad-preview" aria-label="광고 자리"><div class="ad-side-in"><p class="ad-lb">광고</p>'
                      f'{_ad_preview_box(name + " 여백", (AD_SIZE["side"], AD_SIZE["side"]))}</div></aside>')
        elif _AD_JS.get('s' + side) or _AD_JS.get('g' + side):
            rails += (f'<aside class="ad-side ad-side-{side}" data-side="{side}" aria-label="광고" hidden>'
                      '<div class="ad-side-in"><p class="ad-lb">광고</p><div class="ad-box"></div></div></aside>')
    return f'<div class="rail-host">{body}{rails}</div>' if rails else body


def ad_end(p=None):
    """글이나 목록을 다 본 끝자리의 광고 하나(양옆 여백이 좁은 화면용). 읽는 도중에는 넣지 않는다"""
    if p is not None and p.get('origin') != 'manual':
        return ''
    if AD_PREVIEW:
        return (f'<aside class="ad-slot ad-end ad-preview" aria-label="광고 자리"><p class="ad-lb">광고</p>'
                f'{_ad_preview_box("끝자리", (AD_SIZE["end_pc"], AD_SIZE["end_mo"]))}</aside>')
    if not (_AD_JS.get('ep') or _AD_JS.get('em') or _AD_JS.get('ge')):
        return ''
    return '<aside class="ad-slot ad-end" data-end="1" aria-label="광고" hidden><p class="ad-lb">광고</p><div class="ad-box"></div></aside>'


def adfit_slot():
    """옛 시안(research/proto/*/src)을 다시 빌드할 때만 쓰는 이름. 광고는 넣지 않는다"""
    return ''


ads_head = ''
if cfg.get('google_site_verification'):
    ads_head += f'<meta name="google-site-verification" content="{E(cfg["google_site_verification"])}">'
if cfg.get('naver_site_verification'):
    ads_head += f'<meta name="naver-site-verification" content="{E(cfg["naver_site_verification"])}">'
if cfg.get('bing_site_verification'):
    ads_head += f'<meta name="msvalidate.01" content="{E(cfg["bing_site_verification"])}">'
if cfg.get('adsense_client') and not AD_PREVIEW:
    ads_head += (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={E(cfg["adsense_client"])}" '
                 'crossorigin="anonymous"></script>')
if _AD_JS and not AD_PREVIEW:
    ads_head += (f'<script>window.ADS={json.dumps(dict(_AD_JS, client=cfg.get("adsense_client") or ""), separators=(",", ":"))};</script>'
                 '<script src="{{ROOT}}assets/ads.js" defer></script>')


written = []


def page_url(path):
    """검색엔진에 알리는 주소: index.html은 폴더 주소로(첫 화면은 사이트 주소 그대로)"""
    return BASE_URL + '/' + (path[:-len('index.html')] if path.endswith('index.html') else path)


def write_page(path, title, desc, body, nav='', scripts='', index=True):
    depth = path.count('/')
    root = '../' * depth
    canon = f'<link rel="canonical" href="{E(page_url(path))}">' if BASE_URL else ''
    robots = '' if (index and not SAMPLE) else '<meta name="robots" content="noindex">'
    contact = f'<a href="{E(cfg["contact_url"])}" target="_blank" rel="noopener">문의</a>' if cfg.get('contact_url') else ''
    banner = '<p class="banner">개발용 샘플 데이터로 만든 화면입니다</p>' if SAMPLE else ''
    out = (layout.replace('{{TITLE}}', E(title)).replace('{{DESC}}', E(desc)).replace('{{CANON}}', canon)
           .replace('{{HEAD_EXTRA}}', robots + ads_head).replace('{{SITE}}', E(SITE)).replace('{{ROOT}}', root)
           .replace('{{NAV_HOME}}', ' aria-current="page"' if nav == 'home' else '')
           .replace('{{NAV_CAT}}', ' aria-current="page"' if nav == 'cat' else '')
           .replace('{{NAV_GUIDE}}', ' aria-current="page"' if nav == 'guide' else '')
           .replace('{{BANNER}}', banner).replace('{{CONTACT}}', contact)
           .replace('{{TODAY}}', TODAY.isoformat()).replace('{{SCRIPTS}}', scripts)
           .replace('{{BODY}}', body.replace('{{ROOT}}', root)))
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(out)
    if index:
        written.append(path)


def sort_default(ps):
    def key(p):
        d = dday(p.get('next_deadline'))
        return (d if d is not None and d >= 0 else 99999, -(p.get('money_monthly_max_manwon') or 0), p['name'])
    return sorted(ps, key=key)


def mark(v):
    cls = {'가능': 'ok', '불가': 'no', '확인필요': 'warn'}[v]
    return f'<span class="mk {cls}">{"확인 필요" if v == "확인필요" else v}</span>'


def related(p):
    out = []
    for q in programs:
        if q['id'] == p['id']:
            continue
        score = len(set(q['kinds']) & set(p['kinds'])) * 2 + len(set(q['fields']) & set(p['fields']))
        regional = '전국' in q['regions'] or set(r.split(' ')[0] for r in q['regions']) & set(r.split(' ')[0] for r in p['regions'])
        if score >= 3 and regional:
            out.append((score, q))
    out.sort(key=lambda x: (-x[0], x[1]['name']))
    return [q for _, q in out[:5]]


def chips(name, options, kind='checkbox'):
    return '<div class="chips">' + ''.join(
        f'<label class="chip"><input type="{kind}" name="{name}" value="{E(v)}" id="f-{name}-{E(v or "any")}"><span>{E(l)}</span></label>'
        for v, l in options) + '</div>'


# ---------- 렌더링 (theme.py가 덮어쓸 수 있음) ----------
HOME_SCRIPTS = '<script src="assets/programs.js"></script><script src="assets/app.js"></script>'


def row(p, root, static=False):
    kinds = ''.join(f'<span class="tag">{E(KIND_LABEL[k])}</span>' for k in p['kinds'])
    d = dday(p.get('next_deadline'))
    dd = f'<span class="dday">마감 D-{d}</span>' if (static and d is not None and d >= 0) else '<span class="dday" hidden></span>'
    return f'''<li class="row" id="r-{E(p["id"])}" data-id="{E(p["id"])}">
  {icon(p)}
  <div class="row-main">
    <h3><a href="{root}p/{E(p["id"])}.html">{E(p["name"])}</a></h3>
    <p class="row-org">{E(p["operator"])} · {E(region_text(p))}</p>
    <p class="row-sum">{E(p["summary"])}</p>
    <ul class="row-facts"><li><span>내는 돈</span>{E(p["cost"])}</li><li><span>받는 돈</span>{E(p["money"])}</li><li><span>모집</span>{E(p["recruit"])}</li></ul>
    <p class="row-why" hidden></p>
  </div>
  <div class="row-side"><div class="kinds">{kinds}</div><span class="badge" hidden></span>{dd}</div>
</li>'''


def home_body():
    region_opts = '<option value="">선택 안 함</option>' + ''.join(f'<option value="{SIDO_SLUG[s]}">{s}</option>' for s in SIDO)
    return f'''<section class="hero">
  <h1>내 상황에 맞는 무료 교육과 지원금</h1>
  <p class="lead">나이, 사는 곳, 학력, 지금 하는 일을 고르면 신청할 수 있는 제도가 위로 올라옵니다. 고르지 않은 항목은 따지지 않습니다.</p>
</section>
<div class="finder">
  <form class="panel" id="finder" aria-label="내 상황" onsubmit="return false">
    <p class="panel-title">내 상황<button type="reset" class="btn-reset" id="f-reset">모두 지우기</button></p>
    <fieldset><legend>원하는 것</legend>{chips('kind', [(s, l) for _, s, l, _ in KINDS])}</fieldset>
    <fieldset><legend>나이</legend><div class="field-row"><input type="number" id="f-age" inputmode="numeric" min="10" max="99" placeholder="만 나이" aria-label="만 나이"><span class="hint">만 나이</span></div></fieldset>
    <fieldset><legend>사는 곳</legend><select id="f-region" aria-label="사는 곳">{region_opts}</select></fieldset>
    <fieldset><legend>최종 학력</legend>{chips('edu', [('', '상관없음'), ('mid', '중졸 이하'), ('hs', '고졸'), ('uni', '대학 재학·휴학'), ('grad', '대졸 이상')], 'radio')}</fieldset>
    <fieldset><legend>지금 상태</legend>{chips('work', [('', '상관없음'), ('job', '구직 중'), ('emp', '재직 중'), ('biz', '사업자'), ('stu', '학생')], 'radio')}</fieldset>
    <fieldset><legend>가구소득</legend>{chips('inc', [('', '모름·상관없음'), ('60', '기준중위 60% 이하'), ('100', '100% 이하'), ('150', '150% 이하'), ('over', '150% 넘음')], 'radio')}
      <p class="hint">함께 사는 가족 모두의 소득을 합친 기준입니다. <a href="{{{{ROOT}}}}g/median-income.html">내 구간 알아보기</a></p></fieldset>
    <fieldset><legend>해당하는 것 <span class="hint">있을 때만</span></legend>{chips('tg', [(s, l) for l, s in TARGETS])}
      <p class="hint">장애인·제대군인처럼 대상이 정해진 제도는 여기서 고른 경우에만 맞음으로 표시합니다.</p></fieldset>
    <fieldset><legend>분야</legend>{chips('field', [(s, l) for l, s in FIELDS if s != 'all'])}</fieldset>
    <a class="btn ghost to-results" href="#results">결과 보기</a>
  </form>
  <section class="results" id="results" aria-label="결과">
    <div class="res-head">
      <p class="res-count" id="res-count" aria-live="polite">전체 <b>{len(programs)}</b>개</p>
      <div class="res-tools">
        <label class="toggle"><input type="checkbox" id="f-showno"> 안 맞는 것도 보기</label>
        <select id="f-sort" aria-label="정렬"><option value="deadline">마감 가까운 순</option><option value="money">받는 돈 많은 순</option><option value="name">이름순</option></select>
      </div>
    </div>
    <ol class="res-list" id="res-list">
{chr(10).join(row(p, '') for p in sort_default(programs))}
    </ol>
    <p class="empty" id="res-empty" hidden>고른 조건에 맞는 제도가 없습니다. 조건을 하나씩 풀어 보세요.</p>
  </section>
</div>'''


def program_body(p):
    first_kind = p['kinds'][0]
    edu = '제한 없음' if p['education'] == '제한없음' else ('확인 필요' if p['education'] == '확인필요' else p['education'].replace('이상', ' 이상').replace('대학재학', '대학 재학생'))
    inc = {'제한없음': '제한 없음', '기준있음': '기준 있음', '확인필요': '확인 필요'}[p['income']]
    cond_rows = [
        ('나이', E(age_text(p))),
    ] + ([('대상', E(', '.join(p['target_groups']) + '만 신청 가능'))] if p.get('target_groups') else []) + [
        ('사는 곳', E('전국 누구나' if '전국' in p['regions'] else region_text(p))),
        ('학력', E(edu) + (f'<span class="note">{E(p.get("education_note"))}</span>' if p.get('education_note') else '')),
        ('가구소득', E(inc) + (f'<span class="note">{E(p.get("income_note"))}</span>' if p.get('income_note') else '')),
        ('구직자', mark(p['allow_job_seeker'])), ('재직자', mark(p['allow_employed'])),
        ('사업자', mark(p['allow_business'])), ('학생', mark(p['allow_student'])),
    ]
    if p.get('other_conditions'):
        cond_rows.append(('그 밖의 조건', E(p['other_conditions'])))
    cond = ''.join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in cond_rows)
    d = dday(p.get('next_deadline'))
    deadline = f'{p["next_deadline"]} (D-{d})' if d is not None and d >= 0 else '공고에서 확인'
    cta = ''
    if p.get('apply_url'):
        cta += f'<a class="btn" href="{E(p["apply_url"])}" target="_blank" rel="noopener">신청 페이지</a>'
    cta += f'<a class="btn{" ghost" if p.get("apply_url") else ""}" href="{E(p["official_url"])}" target="_blank" rel="noopener">공식 안내</a>'
    quotes = ''.join(
        f'<li><blockquote>{E(s["quote"])}</blockquote><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(urlparse(s["url"]).netloc or s["url"])}</a></li>'
        for s in p['sources'][:3])
    rel = related(p)
    rel_html = ''
    if rel:
        rel_html = '<section class="sec"><h2>비슷한 제도</h2><ul class="related">' + ''.join(
            f'<li><a href="{E(q["id"])}.html">{E(q["name"])}</a> <span class="muted">· {E(q["operator"])}</span></li>' for q in rel) + '</ul></section>'
    kinds = ''.join(f'<span class="tag">{E(KIND_LABEL[k])}</span>' for k in p['kinds'])
    return f'''<nav class="crumb" aria-label="위치"><a href="{{{{ROOT}}}}index.html">상황으로 찾기</a><span>›</span><a href="{{{{ROOT}}}}c/{KIND_SLUG[first_kind]}.html">{E(KIND_LABEL[first_kind])}</a></nav>
<article class="prog">
  <header class="prog-head">{icon(p)}<div><div class="kinds">{kinds}</div><h1>{E(p["name"])}</h1><p class="org">{E(p["operator"])}</p></div></header>
  <p class="prog-sum">{E(p["summary"])}</p>
  <div class="cta">{cta}</div>
  <section class="sec"><h2>누가 신청할 수 있나</h2><div class="table-scroll"><table class="cond">{cond}</table></div></section>
  <section class="sec"><h2>돈</h2><dl class="facts"><dt>내는 돈</dt><dd>{E(p["cost"])}</dd><dt>받는 돈</dt><dd>{E(p["money"])}</dd></dl></section>
  <section class="sec"><h2>언제, 어떻게</h2><dl class="facts"><dt>방식</dt><dd>{E(p.get("format") or "공고에서 확인")}</dd><dt>모집</dt><dd>{E(p["recruit"])}</dd><dt>다음 마감</dt><dd>{E(deadline)}</dd></dl></section>
  <section class="sec"><h2>공고 원문</h2><ol class="quotes">{quotes}</ol><p class="muted">확인일 {E(p["checked_at"])}. 조건은 해마다 바뀔 수 있습니다.</p></section>
  {rel_html}
</article>'''


def cat_body(title, lead, ps, finder_q):
    return f'''<nav class="crumb" aria-label="위치"><a href="{{{{ROOT}}}}c/index.html">분류</a></nav>
<header class="page-head"><h1>{E(title)}</h1><p class="lead">{E(lead)} 모두 {len(ps)}개입니다.</p>
<p><a class="btn ghost" href="{{{{ROOT}}}}index.html?{finder_q}">내 상황으로 좁혀 보기</a></p></header>
<ol class="res-list">{"".join(row(p, "../", static=True) for p in ps)}</ol>'''


def cat_grid(items):
    return '<div class="cat-grid">' + ''.join(f'<a class="cat-link" href="{s}.html">{E(l)}<span>{n}</span></a>' for s, l, n in items) + '</div>'


def cat_index_body(cat_links):
    return f'''<header class="page-head"><h1>분류</h1><p class="lead">원하는 것, 분야, 지역별로 모아 봅니다.</p></header>
<div class="stack"><section class="sec"><h2>원하는 것</h2>{cat_grid(cat_links["kind"])}</section>
<section class="sec"><h2>분야</h2>{cat_grid(cat_links["field"])}</section>
<section class="sec"><h2>지역</h2>{cat_grid(cat_links["region"])}</section></div>'''


def guide_body(g):
    return (f'<nav class="crumb" aria-label="위치"><a href="{{{{ROOT}}}}g/index.html">안내 글</a></nav>'
            f'<article class="prose"><h1>{E(g["title"])}</h1><p class="muted">갱신 {E(g.get("updated", TODAY.isoformat()))}</p>{g["body_html"]}</article>')


def guide_index_body():
    guide_list = ''.join(f'<li><a href="{E(g["slug"])}.html">{E(g["title"])}</a><p class="muted">{E(g["desc"])}</p></li>' for g in guides)
    return (f'<header class="page-head"><h1>안내 글</h1><p class="lead">제도를 고를 때 알아 둘 기준을 정리했습니다.</p></header>'
            f'<ul class="related prose">{guide_list or "<li>준비 중입니다.</li>"}</ul>')


def credits_html():
    if not CREDITS:
        return ''
    src_name = {'unsplash': 'Unsplash', 'pexels': 'Pexels'}
    items = ''.join(
        f'<li><a href="{E(c["page_url"])}" target="_blank" rel="noopener">{E(c.get("photographer") or "사진가 미상")}</a> · {E(src_name.get(c["source"], c["source"]))}</li>'
        for c in CREDITS)
    return ('<h2>사진</h2><p>사이트의 사진은 Unsplash와 Pexels에서 무료 라이선스로 받은 것입니다. 사진 속 인물은 이 사이트나 제도와 관계가 없습니다.</p>'
            f'<ul>{items}</ul>')


def about_body():
    return f'''<article class="prose">
<h1>소개</h1>
<p>{E(SITE)}는 무료 교육, 교육 수당, 자격증 응시료 지원, 창업 지원을 한곳에 모아 <b>내 상황에서 신청할 수 있는지</b>를 빠르게 가려 볼 수 있게 만든 사이트입니다.</p>
<h2>정보를 모으는 방법</h2>
<p>공공데이터포털에서 개방한 정부 서비스 정보와 각 기관의 모집 공고 원문을 읽고, 나이·지역·학력·가구소득·취업 상태 조건을 같은 기준으로 정리합니다. 제도마다 근거가 된 공고 문장과 확인한 날짜를 함께 적습니다.</p>
<h2>한계</h2>
<p>공고에 조건이 적혀 있지 않으면 "확인 필요"로 표시합니다. 조건은 해마다 바뀌므로 신청하기 전에 반드시 공식 안내를 확인하세요. 이 사이트는 정부·공공기관과 관계없는 개인이 운영합니다.</p>
{credits_html()}
</article>'''


def privacy_body():
    return f'''<article class="prose">
<h1>개인정보처리방침</h1>
<p>시행일 2026년 9월 15일</p>
<h2>수집하는 정보</h2>
<p>{E(SITE)}는 회원가입이 없고 이름, 연락처 같은 개인정보를 받지 않습니다. "내 상황"에서 고른 나이·지역·학력 등의 값은 서버로 보내지 않고, 다음 방문 때 다시 쓰도록 이용자 브라우저의 저장공간(localStorage)에만 남습니다. 브라우저에서 사이트 데이터를 지우면 함께 지워집니다.</p>
<h2>광고와 쿠키</h2>
<p>이 사이트는 Google 애드센스와 카카오 애드핏 광고를 게재할 수 있습니다. Google을 포함한 제3자 광고 사업자는 쿠키를 사용해 이용자의 이전 방문 기록을 바탕으로 광고를 보여 줄 수 있습니다. 맞춤 광고는 <a href="https://adssettings.google.com" target="_blank" rel="noopener">Google 광고 설정</a>에서 끌 수 있고, 제3자 사업자의 쿠키는 <a href="https://www.aboutads.info" target="_blank" rel="noopener">www.aboutads.info</a>에서 거부할 수 있습니다.</p>
<h2>호스팅</h2>
<p>이 사이트는 GitHub Pages에서 제공됩니다. GitHub는 보안과 운영을 위해 접속 IP 주소 등의 기록을 남길 수 있으며, 이는 GitHub의 개인정보 처리방침을 따릅니다.</p>
<h2>문의</h2>
<p>개인정보와 관련한 문의는 사이트 하단의 문의 링크로 보내 주세요.</p>
</article>'''


# 시안 테마: 위 렌더링 함수·상수를 덮어쓴다
THEME_PY = os.path.join(SRC, 'theme.py')
if os.path.exists(THEME_PY):
    exec(compile(open(THEME_PY, encoding='utf-8').read(), THEME_PY, 'exec'), globals())

# ---------- 출력 ----------
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, 'assets'))
for name in os.listdir(SRC):
    if os.path.isfile(os.path.join(SRC, name)) and name.rsplit('.', 1)[-1] in ('css', 'js', 'svg', 'woff2', 'webp', 'png', 'jpg'):
        shutil.copy(os.path.join(SRC, name), os.path.join(OUT, 'assets', name))
if os.path.isdir(IMG_DIR):
    shutil.copytree(IMG_DIR, os.path.join(OUT, 'assets', 'img'), ignore=shutil.ignore_patterns('credits.json'))
if not os.path.exists(os.path.join(OUT, 'assets', 'favicon.svg')):
    open(os.path.join(OUT, 'assets', 'favicon.svg'), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="2" y="2" width="20" height="20" rx="6" fill="#1E6B52"/>'
        '<path d="m7.5 12.5 3 3 6-7" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')

# 검색용 데이터
compact = [{
    'id': p['id'], 'n': p['name'],
    'k': [KIND_SLUG[k] for k in p['kinds']], 'f': [FIELD_SLUG[f] for f in p['fields']], 'r': p['regions'],
    'a0': p.get('age_min'), 'a1': p.get('age_max'), 'au': bool(p.get('age_unknown')),
    'tg': [TARGET_SLUG[t] for t in p.get('target_groups', [])],
    'ed': EDU_CODE[p['education']], 'inc': INC_CODE[p['income']], 'ip': p.get('income_pct_max'),
    'w': {'job': TRI_CODE[p['allow_job_seeker']], 'emp': TRI_CODE[p['allow_employed']],
          'biz': TRI_CODE[p['allow_business']], 'stu': TRI_CODE[p['allow_student']]},
    'dl': p.get('next_deadline'), 'm': p.get('money_monthly_max_manwon'),
    'du': duration_codes(p),
} for p in programs]
if 'compact_extra' in globals():   # 테마가 검색용 칸을 더할 때만(없으면 출력 그대로)
    for c, p in zip(compact, programs):
        c.update(compact_extra(p))
open(os.path.join(OUT, 'assets', 'programs.js'), 'w', encoding='utf-8').write(
    'window.PROGRAMS=' + json.dumps(compact, ensure_ascii=False, separators=(',', ':')) + ';\n'
    'window.SIDO=' + json.dumps({v: k for k, v in SIDO_SLUG.items()}, ensure_ascii=False) + ';\n')

write_page('index.html', f'{SITE} — 내 상황에 맞는 무료 교육·지원금',
           '나이·지역·학력·일하는 상태를 고르면 신청할 수 있는 무료 교육, 교육 수당, 자격증 응시료, 창업 지원을 걸러 보여 줍니다.',
           home_body(), nav='home', scripts=HOME_SCRIPTS)

for p in programs:
    desc = f'{p["name"]}: {p["summary"]}'[:150]
    # 자동 수집분은 검토 전까지 검색엔진 색인에서 뺀다(자동 생성 콘텐츠로 보이지 않게)
    write_page(f'p/{p["id"]}.html', f'{p["name"]} 신청 조건 — {SITE}', desc, program_body(p), index=(p['origin'] == 'manual'))


def cat_page(path, title, lead, ps, finder_q):
    ps = sort_default(ps)
    write_page(path, f'{title} — {SITE}', f'{title}: {lead}', cat_body(title, lead, ps, finder_q), nav='cat')


cat_links = {'kind': [], 'field': [], 'region': []}
for k, s, label, lead in KINDS:
    ps = [p for p in programs if k in p['kinds']]
    if ps:
        cat_page(f'c/{s}.html', label, lead, ps, f'kind={s}')
        cat_links['kind'].append((s, label, len(ps)))
for label, s in FIELDS:
    ps = [p for p in programs if label in p['fields']]
    if ps:
        # '전 분야'는 '전 분야 분야'가 되지 않게 제목·설명을 따로 쓴다
        title, lead = ((label, '분야를 가리지 않고 쓸 수 있는 제도입니다.') if s == 'all'
                       else (f'{label} 분야', f'{label} 분야를 배울 수 있는 제도입니다.'))
        cat_page(f'c/field-{s}.html', title, lead, ps, f'field={s}' if s != 'all' else '')
        cat_links['field'].append((f'field-{s}', f'{label}', len(ps)))
nat = [p for p in programs if '전국' in p['regions']]
cat_page('c/region-national.html', '전국 누구나', '사는 곳과 관계없이 신청할 수 있는 제도입니다.', nat, '')
cat_links['region'].append(('region-national', '전국', len(nat)))
for s in SIDO:
    ps = [p for p in programs if any(r.split(' ')[0] == s for r in p['regions'])]
    if ps:
        cat_page(f'c/region-{SIDO_SLUG[s]}.html', f'{s} 주민 대상', f'{s}에 사는 사람만 신청할 수 있는 제도입니다. 전국 제도는 따로 봐 주세요.', ps, f'region={SIDO_SLUG[s]}')
        cat_links['region'].append((f'region-{SIDO_SLUG[s]}', s, len(ps)))

write_page('c/index.html', f'분류 — {SITE}', '원하는 것, 분야, 지역별로 무료 교육과 지원금을 모아 봅니다.', cat_index_body(cat_links), nav='cat')

for g in guides:
    write_page(f'g/{g["slug"]}.html', f'{g["title"]} — {SITE}', g['desc'], guide_body(g), nav='guide')
write_page('g/index.html', f'안내 글 — {SITE}', '무료 교육과 지원금을 고를 때 알아 둘 기준을 정리한 글입니다.',
           guide_index_body(), nav='guide', index=bool(guides))

write_page('about.html', f'소개 — {SITE}', f'{SITE}가 무엇이고 정보를 어떻게 모으는지 설명합니다.', about_body())
write_page('privacy.html', f'개인 정보 처리 방침 — {SITE}', f'{SITE}의 개인 정보 처리 방침입니다.', privacy_body())

# 검색엔진·광고 파일
open(os.path.join(OUT, '.nojekyll'), 'w').write('')
if BASE_URL:
    urls = ''.join(f'<url><loc>{E(page_url(u))}</loc><lastmod>{TODAY.isoformat()}</lastmod></url>' for u in written)
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    daum = f'#DaumWebMasterTool:{cfg["daum_webmaster_tool"]}\n' if cfg.get('daum_webmaster_tool') else ''  # 다음 웹마스터도구 인증은 robots.txt 끝줄로
    open(os.path.join(OUT, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n{daum}')
if cfg.get('adsense_client'):
    pub = cfg['adsense_client'].replace('ca-', '')
    open(os.path.join(OUT, 'ads.txt'), 'w', encoding='utf-8').write(f'google.com, {pub}, DIRECT, f08c47fec0942fa0\n')

print(f'programs {len(programs)} sample={SAMPLE} pages {len(written)} guides {len(guides)} today {TODAY}')
