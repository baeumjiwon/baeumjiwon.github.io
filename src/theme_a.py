# A안 · 목록형 테마. build.py 전역에서 exec되어 렌더링 함수를 덮어쓴다.
# 원칙: 결과 행에는 긴 문장·사진 없음. 사진은 입구(원하는 것 5종)·분류 머리·안내 글에만.

KIND_PHOTO = {'무료교육': 'classroom-unsplash-YRMWVcdyhmI', '돈받는교육': 'tech-unsplash-E15BQufHzJs',
              '지원금': 'office-pexels-8297220', '응시료': 'exam-pexels-31115182', '창업': 'startup-pexels-31892097'}
FIELD_PHOTO = {'IT·AI': 'it-unsplash-Hl1stIQkVRw', '영상·디자인': 'media-pexels-16313664', '기술·현장': 'tech-unsplash-kBKOaghy8mU',
               '사무·회계·경영': 'office-unsplash-O2GCr83qCdg', '외국어': 'lang-unsplash-QVrBu1MqJYU',
               '요리·서비스': 'food-unsplash-h_s7AUBPss8', '돌봄·보건': 'care-pexels-7551634', '전분야': 'exam-pexels-6683391'}
# 안내 글 표지: 목록 안에서 같은 사진을 두 번 쓰지 않는다. 돈·소득 관련 글은 얼굴 없는 사물 사진만
GUIDE_PHOTO = {
    'median-income': 'office-pexels-8297220', 'naeil-card-eligibility': 'office-unsplash-O2GCr83qCdg',
    'training-allowance': 'people-pexels-5757210', 'kdt-guide': 'it-unsplash-Hl1stIQkVRw',
    'course-based-qualification': 'exam-pexels-6683391', 'employment-support-types': 'exam-unsplash-w-1ydxmB7hQ',
    'business-owner-training': 'startup-pexels-31892097', 'paid-while-learning': 'tech-unsplash-E15BQufHzJs',
    'exam-fee-support': 'exam-pexels-31115182', 'no-education-requirement': 'lang-unsplash-QVrBu1MqJYU',
    'free-online-courses': 'it-pexels-7988087', 'public-vocational-schools': 'food-pexels-16140004',
    'it-bootcamps': 'media-pexels-15713296', 'youth-allowance-by-region': 'lang-pexels-5185082',
    'middle-aged-retraining': 'food-pexels-4349954', 'women-reemployment': 'media-pexels-7014943',
    'senior-digital-education': 'media-pexels-16313664', 'startup-education': 'food-unsplash-XiyR0BXRIsI',
    'student-eligible-programs': 'classroom-unsplash-YRMWVcdyhmI', 'how-to-read-notice': 'exam-pexels-6683673',
    'unemployed-during-training': 'food-unsplash-h_s7AUBPss8',
}
# 사진마다 (보여 줄 중심 영역, 절대 넘지 않을 안전 영역) — 원본 대비 비율 (x0, x1, y0, y1). credits.json crop 메모를 옮겼다.
# 틀 비율이 달라도 photo()가 object-position·scale·transform-origin을 계산해 이 영역을 맞춘다.
FULL = (0, 1, 0, 1)
PHOTO_FOCUS = {
    'classroom-unsplash-YRMWVcdyhmI': ((.36, 1, .30, .80), (.33, 1, .22, .88)),   # 슬라이드(만델라 사진) 빼고 계단식 객석 뒷모습
    'tech-unsplash-E15BQufHzJs': ((.22, .97, 0, 1), FULL),                        # 왼쪽 공구 벽 덜어냄
    'office-pexels-8297220': ((0, 1, .55, 1), (0, 1, .45, 1)),                    # 세로 원본 아래: 손·계산기·서류철
    'exam-pexels-31115182': ((.10, .75, .20, .92), (0, 1, .17, 1)),               # 위 빨간 의자 빼고 답안지와 손
    'startup-pexels-31892097': ((.42, .90, .48, .91), (0, .912, .47, .92)),        # 위 '만두' 현수막·얼굴, 아래 상호 표시판, POSBANK 로고 모두 뺌. 계산대 손과 POS
    'it-unsplash-Hl1stIQkVRw': ((.10, .90, .25, 1), FULL),                        # 블라인드 윗부분 덜어냄
    'media-pexels-16313664': ((.11, 1, 0, 1), (.11, 1, 0, 1)),                    # 왼쪽 머리 일부 제거
    'tech-unsplash-kBKOaghy8mU': ((.07, .95, 0, 1), FULL),
    'office-unsplash-O2GCr83qCdg': ((.05, .92, .08, 1), (0, .928, .05, 1)),       # 오른쪽 끝 얼굴(x≥.95)·위 턱선 뺌
    'lang-unsplash-QVrBu1MqJYU': ((.22, .93, .10, 1), FULL),
    'food-unsplash-h_s7AUBPss8': ((.08, .90, .05, .88), FULL),
    'care-pexels-7551634': ((.09, .98, .10, .95), FULL),
    'exam-pexels-6683391': ((.06, .90, .10, 1), FULL),
    'exam-pexels-6683673': ((0, 1, .10, .94), FULL),
    'it-pexels-7988087': ((.11, 1, 0, 1), FULL),
    'media-pexels-15713296': ((0, 1, .43, .87), (0, 1, .40, .95)),                # 위쪽 검은 부분 버림
    'food-pexels-4349954': ((.22, 1, 0, 1), (.12, 1, 0, 1)),                      # 왼쪽 흰 머신 몸체 덜어냄
    'food-pexels-16140004': ((.11, .82, .20, 1), (.07, 1, .08, 1)),               # 붉은 글자 조각·앞치마 글자 뺌
    'food-unsplash-XiyR0BXRIsI': ((.33, 1, 0, .75), (.33, 1, 0, 1)),              # 왼쪽 핀 배지·가죽끈 뺌
    'media-pexels-7014943': ((0, 1, .26, .72), (0, 1, .15, .76)),                 # 아래 주황 드라이브 본체 뺌
    'lang-pexels-5185082': ((.29, .91, .40, 1), (0, 1, .383, 1)),                 # 키보드 뺌
    'exam-unsplash-w-1ydxmB7hQ': ((.25, .87, .18, .79), (0, .87, 0, 1)),          # 오른쪽 마스크 쓴 얼굴·머리카락 뺌
    'people-pexels-5757210': ((0, 1, .43, .92), (0, 1, .425, 1)),                 # 어깨 아래만: 얼굴 완전히 뺌. 손·노트북·책 더미
}
RATIO = {'43': 4 / 3, '32': 3 / 2, '169': 16 / 9, '31': 3 / 1}
SRC_NAME = {'unsplash': 'Unsplash', 'pexels': 'Pexels'}
SCHED_SHOW = {'주간': '주간', '야간·주말': '야간·주말', '온라인': '온라인', '혼합': '온·오프라인 혼합'}
COST_SHOW = ('무료', '일부 자부담')
DUR_DATE_RE = re.compile(r'^\d{1,2}\.\d{1,2}$')


def _credit(name):
    return next((c for c in CREDITS if c['name'] == name), None)


def _crop_vars(c, ratio, suffix=''):
    """틀 비율 ratio에서 PHOTO_FOCUS 영역이 보이도록 CSS 변수(--pos, --s, --o)를 만든다. 반환: (style, 확대 배율)"""
    W, H = c['size']
    a, R = W / H, RATIO[ratio]
    (fx0, fx1, fy0, fy1), (sx0, sx1, sy0, sy1) = PHOTO_FOCUS.get(c['name'], (FULL, FULL))
    fw, fh = fx1 - fx0, fy1 - fy0
    if fw * W / (fh * H) > R:
        tw, th = fw, fw * W / (H * R)
    else:
        th, tw = fh, fh * H * R / W
    if tw > sx1 - sx0:
        tw = sx1 - sx0
        th = tw * W / (H * R)
    if th > sy1 - sy0:
        th = sy1 - sy0
        tw = th * H * R / W
    cx = min(max((fx0 + fx1) / 2, sx0 + tw / 2), sx1 - tw / 2)
    cy = min(max((fy0 + fy1) / 2, sy0 + th / 2), sy1 - th / 2)
    vw, vh = min(1, R / a), min(1, a / R)
    s = vw / tw
    left = min(max(cx - vw / 2, 0), 1 - vw)
    top = min(max(cy - vh / 2, 0), 1 - vh)
    px = left / (1 - vw) if vw < .999 else .5
    py = top / (1 - vh) if vh < .999 else .5
    style = f'--pos{suffix}:{px * 100:.1f}% {py * 100:.1f}%;'
    if s > 1.02:
        k = 1 - 1 / s
        ox = ((cx - tw / 2) - left) / vw / k
        oy = ((cy - th / 2) - top) / vh / k
        style += f'--s{suffix}:{s:.3f};--o{suffix}:{ox * 100:.1f}% {oy * 100:.1f}%;'
    else:
        style += f'--s{suffix}:1;--o{suffix}:50% 50%;'
    return style, s


def photo(name, sizes, ratio='32', ratio_m=None, eager=False, cls='ph'):
    """사진 틀. ratio는 기본 비율, ratio_m은 좁은 화면 비율(CSS가 --pos2 등을 쓴다). 사진 위에 글자를 올리지 않는다."""
    c = _credit(name)
    if not c:
        return ''
    style, s = _crop_vars(c, ratio)
    klass = f'{cls} r{ratio}'
    if ratio_m:
        st2, s2 = _crop_vars(c, ratio_m, '2')
        style += st2
        s = max(s, s2)
        klass += f' m{ratio_m}'
    if s > 1.02:  # 확대해 자르는 사진은 더 큰 파일을 고르게 sizes를 키운다
        sizes = re.sub(r'(\d+)(px|vw)', lambda m: f'{round(int(m.group(1)) * s)}{m.group(2)}', sizes)
    return f'<span class="{klass}" style="{style}">{img_html(c, sizes, "", "", eager)}</span>'


def photo_cap(name):
    c = _credit(name)
    if not c:
        return ''
    return (f'<figcaption class="cap">사진 <a href="{E(c["page_url"])}" target="_blank" rel="noopener">'
            f'{E(c.get("photographer") or "사진가 미상")}</a> · {SRC_NAME.get(c["source"], c["source"])} · 예시 사진</figcaption>')


# ---------- 공통 글자 다듬기 ----------
def _tx(v, empty='공고에서 확인'):
    """DB 원문 표시용: '확인필요'·'해당없음' 같은 내부 표기를 사람 말로 바꾼다."""
    v = (v or '').strip()
    if not v or v == '확인필요':
        return f'<span class="dim">{E(empty)}</span>'
    if v == '해당없음':
        return '<span class="dim">해당 없음</span>'
    return E(v.replace('확인필요', '공고에서 확인').replace('해당없음', '해당 없음'))


def _org_short(p):
    op = re.sub(r'^[(（](재|주|사|재단|사단)[)）]\s*', '', p['operator'])   # '(재)' 같은 법인 표기는 떼고
    op = re.split(r'\s*[(（]|\s+/\s+', op)[0].strip()
    return op or p['operator']


def _is_na(p):
    """목록에서 기간 줄을 뺄 제도: 교육 과정이 아닌 지원 제도, 또는 창업·지원금뿐이고 기간을 모르는 제도"""
    lab = duration_label(p)
    if lab is None:
        return True
    return set(p['kinds']) <= {'지원금', '창업'} and (p.get('duration') or {}).get('kind') == 'unknown'


def _dk(p):
    """기간 필터 묶음 코드: na 지원 제도 · days 날짜 단위 있음 · unknown 공고에 없음 · loose 과정마다 다름/시간 단위"""
    if _is_na(p):
        return 'na'
    if duration_codes(p):
        return 'days'
    if (p.get('duration') or {}).get('kind') == 'unknown':
        return 'unknown'
    return 'loose'


def _dur_parts(p):
    lab = duration_label(p)
    if lab is None:
        return None
    band, length = lab
    if DUR_DATE_RE.match(length or ''):   # '9.19' 같은 날짜 조각은 길이가 아니다(날짜는 상세에)
        length = ''
    if (not band and not length) or length == '공고 확인':
        return []
    return [x for x in (band, length) if x]


def _money_partial(p):
    ms, m = p.get('money_short') or '', (p.get('money') or '').strip()
    return bool(re.search(r'우선선발|선발자만|일부만', ms)) or (bool(ms or p.get('money_monthly_max_manwon')) and m.startswith('없음'))


def _money_value(p):
    """(표시 값, 일부만 여부). 받는 돈이 없으면 ('', False)"""
    m = money_text(p)
    if not m:
        return '', False
    if _money_partial(p):
        m = re.sub(r'^우선선발(대상)?자만?\s*', '', m)
        return f'일부만 · {m}', True
    return m, False


def _facts(p):
    """추천 순 정렬용: 목록 행에 실제 값이 찬 칸 수(기간, 받는 돈, 내는 돈)"""
    parts = _dur_parts(p)
    n = 1 if (_is_na(p) or parts) else 0
    n += 1 if money_text(p) else 0
    n += 1 if p.get('cost_type') in COST_SHOW else 0
    return n


def _always_open(p):
    return not p.get('next_deadline') and '상시' in (p.get('recruit') or '')


def sort_default(ps):
    """추천 순: 마감이 4일 넘게 남았거나 상시 모집 → 3일 안 마감 → 마감 모름·지남. 그 안에서 칸이 잘 찬 것, 마감 가까운 것 먼저."""
    def key(p):
        d = dday(p.get('next_deadline'))
        if _always_open(p):
            cls, dd = 0, 9999
        elif d is None or d < 0:
            cls, dd = 2, 99999
        elif d <= 3:
            cls, dd = 1, d
        else:
            cls, dd = 0, d
        return (cls, -_facts(p), dd, -(p.get('money_monthly_max_manwon') or 0), p['name'])
    return sorted(ps, key=key)


# ---------- 마감 ----------
def _dl_markup(s):
    """'9월 18일(금) 마감 · 3일 남음'. dl.js가 브라우저 날짜로 같은 모양을 다시 쓴다. 빨강은 오늘·1일 남음만."""
    d = dday(s)
    dt = datetime.date.fromisoformat(s)
    date = f'{dt.month}월 {dt.day}일({WEEKDAYS[dt.weekday()]})'
    sep = '<span class="sep"> · </span>'
    if d < 0:
        return 'past', f'<span class="left">마감 지남</span>{sep}<span class="date">{date}</span>'
    if d == 0:
        return 'urgent', f'<span class="left">오늘 마감</span>{sep}<span class="date">{date}</span>'
    return ('urgent' if d == 1 else 'soon' if d <= 3 else ''), f'<span class="date">{date} 마감</span>{sep}<span class="left">{d}일 남음</span>'


def _dl_html(p, tag='p', cls='r-dl'):
    s = p.get('next_deadline')
    if s and dday(s) is not None and dday(s) >= 0:
        state, inner = _dl_markup(s)
        return f'<{tag} class="{cls} {state}" data-dl="{E(s)}">{inner}</{tag}>'
    if _always_open(p):
        return f'<{tag} class="{cls}">상시 모집</{tag}>'
    return ''


# ---------- 결과 행 ----------
def _dur_html(p):
    if _is_na(p):
        return ''
    parts = _dur_parts(p)
    if not parts:
        return '<p class="r-dur dim"><span class="lb">기간</span>공고 확인</p>'
    out = [f'<b>{E(parts[0])}</b>'] + [E(x) for x in parts[1:]]
    if p.get('schedule') in SCHED_SHOW:
        out.append(E(SCHED_SHOW[p['schedule']]))
    return f'<p class="r-dur"><span class="lb">기간</span>{" · ".join(out)}</p>'


def _money_html(p):
    bits = []
    m, partial = _money_value(p)
    if m:
        bits.append(f'<span class="mi"><span class="lb">받는 돈</span><b>{E(m)}</b></span>')
    ct = p.get('cost_type')
    if ct in COST_SHOW:
        bits.append(f'<span class="mi"><span class="lb">내는 돈</span><b>{E(ct)}</b></span>')
    elif ct == '확인필요':
        bits.append('<span class="mi dim">비용 · 공고 확인</span>')
    return f'<p class="r-money">{"".join(bits)}</p>' if bits else ''


def row(p, root, static=False):
    kinds = ' · '.join(KIND_LABEL[k] for k in p['kinds'])
    dur, money, dl = _dur_html(p), _money_html(p), _dl_html(p)
    one = f'<p class="r-one">{E(p["one_liner"])}</p>' if (not dur and not money and p.get('one_liner')) else ''
    st = '' if static else '<span class="r-st" hidden></span>'
    attrs = f' data-dk="{_dk(p)}" data-fx="{_facts(p)}"' + (' data-open="1"' if _always_open(p) else '')
    org = _org_short(p)
    return f'''<li class="row" id="r-{E(p["id"])}" data-id="{E(p["id"])}"{attrs}>
  <p class="r-top"><span class="r-kind">{E(kinds)}</span>{st}</p>
  <h3 class="r-title"><a href="{root}p/{E(p["id"])}.html">{E(p["name"])}</a></h3>
  {dur}{money}{one}
  <p class="r-org" title="{E(p["operator"])}">{E(org)} · {E(region_short(p))}</p>
  {dl}
</li>'''


# ---------- 첫 화면 ----------
def _opts(name, options, kind='checkbox'):
    """options: [(값, 라벨, 건수 또는 None)]"""
    return '<div class="opts">' + ''.join(
        f'<label class="opt"><input type="{kind}" name="{name}" value="{E(v)}"><span class="t">{E(l)}</span>'
        + (f'<span class="n">{n}</span>' if n is not None else '') + '</label>'
        for v, l, n in options) + '</div>'


def _fold(name, label, body):
    return (f'<details class="fd"><summary><span class="lg">{E(label)}</span><span class="val" data-val="{name}">상관없음</span></summary>'
            f'<fieldset class="fd-in"><legend class="sr">{E(label)}</legend>{body}</fieldset></details>')


def _entry():
    tiles = ''
    for k, s, label, _ in KINDS:
        n = sum(1 for p in programs if k in p['kinds'])
        tiles += (f'<a class="tile" href="{{{{ROOT}}}}c/{s}.html" data-kind="{s}">'
                  f'{photo(KIND_PHOTO[k], "(max-width: 860px) 128px, 220px", "32", "43", eager=True)}'
                  f'<span class="tile-tx"><span class="tile-t">{E(label)}</span><span class="tile-n">{n}</span></span></a>')
    return (f'<nav class="entry" id="entry" aria-labelledby="entry-h">'
            f'<h2 class="entry-h" id="entry-h">원하는 것<span class="entry-sub">여러 개 고를 수 있습니다</span></h2>'
            f'<div class="tiles-row">{tiles}</div></nav>')


def home_body():
    kind_n = {s: sum(1 for p in programs if k in p['kinds']) for k, s, _, _ in KINDS}
    du_n = {c: sum(1 for p in programs if c in duration_codes(p)) for c, _, _, _ in DURATION_BUCKETS}
    region_opts = '<option value="">고르지 않음</option>' + ''.join(f'<option value="{SIDO_SLUG[s]}">{s}</option>' for s in SIDO)
    form = f'''<form class="finder" id="finder" aria-label="조건" onsubmit="return false">
  <div class="f-head"><h2 class="f-title">조건</h2><button type="reset" class="linkbtn">모두 지우기</button></div>
  <fieldset class="fs fs-kind"><legend>원하는 것</legend>{_opts('kind', [(s, l, kind_n[s]) for _, s, l, _ in KINDS])}</fieldset>
  <fieldset class="fs"><legend>교육 기간</legend>{_opts('du', [(c, l, du_n[c]) for c, l, _, _ in DURATION_BUCKETS])}
    <p class="hint">기간을 구간으로 가를 수 없는 교육은 아래에 따로 모읍니다.</p></fieldset>
  <div class="fs pair">
    <div class="pair-a"><label class="lg" for="f-age">나이</label><span class="age">만 <input type="number" id="f-age" inputmode="numeric" min="10" max="99" autocomplete="off" aria-describedby="age-bad"> 세</span></div>
    <div class="pair-r"><label class="lg" for="f-region">사는 곳</label><select id="f-region">{region_opts}</select></div>
    <p class="hint bad" id="age-bad" hidden>만 10~99세로 적어 주세요.</p>
  </div>
  {_fold('edu', '최종 학력', _opts('edu', [('', '상관없음', None), ('mid', '중졸 이하', None), ('hs', '고졸', None), ('uni', '대학 재학·휴학', None), ('grad', '대졸 이상', None)], 'radio'))}
  {_fold('work', '지금 상태', _opts('work', [('', '상관없음', None), ('job', '구직 중', None), ('emp', '재직 중', None), ('biz', '사업자', None), ('stu', '학생', None)], 'radio'))}
  {_fold('inc', '가구소득', _opts('inc', [('', '모름·상관없음', None), ('60', '기준중위 60% 이하', None), ('100', '100% 이하', None), ('150', '150% 이하', None), ('over', '150% 넘음', None)], 'radio') + '<p class="hint">함께 사는 가족 모두의 소득 합계 기준. <a href="{{ROOT}}g/median-income.html">내 구간 알아보기</a></p>')}
  {_fold('tg', '해당하는 것', _opts('tg', [(s, l, None) for l, s in TARGETS]) + '<p class="hint">장애인·제대군인처럼 대상이 정해진 제도는 여기서 고른 경우에만 맞음으로 표시합니다.</p>')}
  {_fold('field', '분야', _opts('field', [(s, l, None) for l, s in FIELDS if s != 'all']))}
</form>'''
    ps = sort_default(programs)
    urgent_n = sum(1 for p in programs if dday(p.get('next_deadline')) is not None and 0 <= dday(p.get('next_deadline')) <= 3)
    return f'''<div class="home-head">
  <h1>내 조건에 맞는 무료 교육·지원금</h1>
  <p class="home-meta">제도 {len(programs)}개 · {TODAY.month}월 {TODAY.day}일 갱신</p>
</div>
<noscript><p class="nojs">조건 거르기에는 자바스크립트가 필요합니다. 아래는 전체 목록입니다.</p></noscript>
<div class="m-bar"><button type="button" class="btn-filter" id="open-f" aria-haspopup="dialog">조건 고르기</button></div>
<div class="picked" id="picked" hidden></div>
{_entry()}
<div class="finder-wrap">
  <aside class="side" id="side" aria-label="조건 고르기">{form}</aside>
  <section class="results" id="results" aria-labelledby="res-h">
    <div class="picked picked-d" id="picked-d" hidden></div>
    <div class="res-head" id="res-top">
      <h2 class="sr" id="res-h">결과</h2>
      <p class="res-count" id="res-count" aria-live="polite">제도 <b>{len(programs)}</b>개</p>
      <select id="f-sort" aria-label="정렬"><option value="rec">추천 순</option><option value="deadline">마감 가까운 순</option><option value="money">받는 돈 많은 순</option><option value="name">이름순</option></select>
      <div class="res-sub" id="res-sub">
        <label class="toggle" id="toggle-no" hidden><input type="checkbox" id="f-showno"> <span id="showno-t">안 맞는 것도 보기</span></label>
        <button type="button" class="linkbtn soon-btn" id="soon-btn"{"" if urgent_n else " hidden"}>3일 안에 마감 {urgent_n}개 먼저 보기</button>
      </div>
    </div>
    <ol class="res-list" id="res-list">
{chr(10).join(row(p, '') for p in ps)}
    </ol>
    <p class="empty" id="res-empty" hidden>고른 조건에 맞는 제도가 없습니다. 조건을 하나씩 풀어 보세요.</p>
    <button type="button" class="more" id="res-more" hidden>더 보기</button>
  </section>
</div>
<dialog class="fdlg" id="fdlg" aria-labelledby="fdlg-title">
  <div class="fdlg-head"><h2 id="fdlg-title">조건 고르기</h2><button type="button" class="linkbtn" id="fdlg-reset">모두 지우기</button><button type="button" class="btn-close" id="fdlg-close">닫기</button></div>
  <div class="fdlg-body" id="fdlg-body"></div>
  <div class="fdlg-foot"><button type="button" class="btn-primary wide" id="fdlg-apply"><span id="apply-main">{len(programs)}개 보기</span><span class="apply-sub" id="apply-sub" hidden></span></button></div>
</dialog>'''


HOME_SCRIPTS = '<script src="assets/programs.js"></script><script src="assets/dl.js"></script><script src="assets/app.js"></script>'


# ---------- 상세 ----------
def _age_short(p):
    t = age_text(p)
    return '나이 조건 없음' if t == '공고에 나이 조건 없음' else t


def program_body(p):
    first_kind = p['kinds'][0]
    kinds = ' · '.join(KIND_LABEL[k] for k in p['kinds'])
    lab = duration_label(p)
    d = deadline_info(p)

    # 1) 제목 바로 아래 요약
    summ = []
    if not _is_na(p):
        parts = _dur_parts(p)
        sched = SCHED_SHOW.get(p.get('schedule'))
        summ.append(('기간', E(' · '.join(parts + ([sched] if sched else []))) if parts else '<span class="dim">공고 확인</span>'))
    m, partial = _money_value(p)
    if m:
        v = E(m)
        if partial:
            v += f'<span class="note">{"일반 선발자는 받는 돈 없음" if "우선선발" in (p.get("money") or "") + (p.get("money_short") or "") else "대부분은 받는 돈 없음"}</span>'
        summ.append(('받는 돈', v))
    ct = p.get('cost_type')
    if ct in COST_SHOW:
        summ.append(('내는 돈', E(ct)))
    elif ct == '확인필요':
        summ.append(('내는 돈', '<span class="dim">공고 확인</span>'))
    dl = _dl_html(p, 'span', 'dlv')
    summ.append(('마감', dl or '<span class="dim">공고에서 확인</span>'))
    who = [_age_short(p)] + ([', '.join(p['target_groups'])] if p.get('target_groups') else []) + \
          ['전국' if '전국' in p['regions'] else region_short(p) + ' 주민']
    summ.append(('대상', E(' · '.join(who))))
    summ_html = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in summ)

    cta = ''
    if p.get('apply_url'):
        cta += f'<a class="btn-primary" href="{E(p["apply_url"])}" target="_blank" rel="noopener">신청 페이지</a>'
    cta += f'<a class="{"btn-line" if p.get("apply_url") else "btn-primary"}" href="{E(p["official_url"])}" target="_blank" rel="noopener">공식 안내</a>'

    # 2) 누가 신청할 수 있나
    edu = '제한 없음' if p['education'] == '제한없음' else ('공고에서 확인' if p['education'] == '확인필요' else p['education'].replace('이상', ' 이상').replace('대학재학', '대학 재학생'))
    inc = {'제한없음': '제한 없음', '기준있음': '기준 있음', '확인필요': '공고에서 확인'}[p['income']]
    note = lambda k: f'<span class="note">{_tx(p.get(k))}</span>' if p.get(k) else ''
    works = [('구직자', p['allow_job_seeker']), ('재직자', p['allow_employed']), ('사업자', p['allow_business']), ('학생', p['allow_student'])]
    ws = ''
    for v, lbl in (('가능', '가능'), ('확인필요', '확인 필요'), ('불가', '불가')):
        names = [n for n, x in works if x == v]
        if names:
            cls = {'가능': 'ok', '확인필요': 'warn', '불가': 'no'}[v]
            ws += f'<span class="ws"><b class="mk {cls}">{lbl}</b> {E(" · ".join(names))}</span>'
    elig = [('나이', E(age_text(p)))]
    if p.get('target_groups'):
        elig.append(('대상', E(', '.join(p['target_groups'])) + '만 신청할 수 있습니다'))
    elig += [('사는 곳', E('전국 누구나' if '전국' in p['regions'] else region_text(p) + ' 주민')),
             ('학력', E(edu) + note('education_note')),
             ('가구소득', E(inc) + note('income_note')),
             ('일 상태', ws)]
    if p.get('other_conditions'):
        elig.append(('그 밖에', _tx(p['other_conditions'])))
    elig_html = ''.join(f'<li><span class="k">{k}</span><span class="v">{v}</span></li>' for k, v in elig)

    # 3) 언제·어떻게 (교육 기간 행은 항상)
    du = p.get('duration') or {}
    if lab is None:
        dur_v = '<span class="dim">교육 과정이 아닌 지원 제도라 교육 기간이 따로 없습니다.</span>'
    else:
        parts = _dur_parts(p)
        dur_v = E(' · '.join(parts)) if parts else '<span class="dim">공고에 교육 기간이 적혀 있지 않습니다.</span>'
        extra = [f'교육 날짜 {du["dates_text"]}' if du.get('dates_text') else '', f'수업 시간 {du["hours_text"]}' if du.get('hours_text') else '']
        extra = [x for x in extra if x]
        if extra:
            dur_v += f'<span class="note">{E(" · ".join(extra))}</span>'
        if du.get('quote'):
            dur_v += f'<span class="note">공고 표현 “{E(du["quote"])}”</span>'
    when = [('교육 기간', dur_v)]
    if p.get('schedule') not in (None, '', '해당없음', '확인필요'):
        when.append(('일정', E(SCHED_SHOW.get(p['schedule'], p['schedule']))))
    when += [('방식', _tx(p.get('format'))), ('모집', _tx(p.get('recruit'))),
             ('다음 마감', E(d['text']) if d else '<span class="dim">공고에서 확인</span>')]
    when_html = ''.join(f'<li><span class="k">{k}</span><span class="v">{v}</span></li>' for k, v in when)
    money_html = (f'<li><span class="k">받는 돈</span><span class="v">{_tx(p.get("money"))}</span></li>'
                  f'<li><span class="k">내는 돈</span><span class="v">{_tx(p.get("cost"))}</span></li>')

    quotes = ''.join(
        f'<li><blockquote>{E(s["quote"])}</blockquote><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(urlparse(s["url"]).netloc or s["url"])}</a></li>'
        for s in p['sources'][:3])
    rel = related(p)
    rel_html = ''
    if rel:
        rel_html = f'<section class="sec"><h2>비슷한 제도</h2><ol class="res-list rel">{"".join(row(q, "../", static=True) for q in rel[:4])}</ol></section>'

    return f'''<article class="prog">
  <nav class="crumb" aria-label="위치"><a href="{{{{ROOT}}}}index.html">찾기</a><span aria-hidden="true">›</span><a href="{{{{ROOT}}}}c/{KIND_SLUG[first_kind]}.html">{E(KIND_LABEL[first_kind])}</a></nav>
  <header class="p-head">
    <p class="p-kind">{E(kinds)}</p>
    <h1>{E(p["name"])}</h1>
    <p class="p-org">{E(p["operator"])}</p>
  </header>
  <dl class="p-sum">{summ_html}</dl>
  <div class="cta">{cta}</div>
  <p class="p-note">민간 안내 사이트가 공고를 요약한 내용입니다. 신청 전에 공식 안내를 확인하세요.</p>
  <p class="lede">{E(p["summary"])}</p>
  <section class="sec"><h2>누가 신청할 수 있나</h2><ul class="kv">{elig_html}</ul></section>
  <section class="sec"><h2>돈</h2><ul class="kv">{money_html}</ul></section>
  <section class="sec"><h2>언제, 어떻게</h2><ul class="kv">{when_html}</ul></section>
  <section class="sec"><h2>공고 원문</h2>
    <details class="src"><summary>공고에서 옮긴 문장 {len(p["sources"][:3])}개 보기</summary><ol class="quotes">{quotes}</ol></details>
    <p class="checked">확인일 {E(p["checked_at"])} · 조건은 해마다 바뀔 수 있습니다.</p>
  </section>
  {rel_html}
</article>
<script src="{{{{ROOT}}}}assets/dl.js" defer></script>'''


# ---------- 분류 ----------
def _cat_photo(title, finder_q):
    if finder_q.startswith('kind='):
        k = next((k for k, s, _, _ in KINDS if s == finder_q[5:]), None)
        return KIND_PHOTO.get(k)
    if finder_q.startswith('field='):
        lab = next((l for l, s in FIELDS if s == finder_q[6:]), None)
        return FIELD_PHOTO.get(lab)
    if title.startswith('전분야'):
        return FIELD_PHOTO['전분야']
    return None


def cat_body(title, lead, ps, finder_q):
    ph = _cat_photo(title, finder_q)
    fig = f'<figure class="cat-fig">{photo(ph, "(max-width: 860px) 100vw, 400px", "32", "31", eager=True)}{photo_cap(ph)}</figure>' if ph else ''
    urgent_n = sum(1 for p in ps if dday(p.get('next_deadline')) is not None and 0 <= dday(p.get('next_deadline')) <= 3)
    q = finder_q + ('&' if finder_q else '')
    soon = f' · <a href="{{{{ROOT}}}}index.html?{q}sort=deadline">3일 안에 마감 {urgent_n}개</a>' if urgent_n else ''
    return f'''<nav class="crumb" aria-label="위치"><a href="{{{{ROOT}}}}c/index.html">분류</a></nav>
<header class="cat-head{" has-fig" if ph else ""}">
  <div class="cat-text">
    <h1>{E(title)}</h1>
    <p class="cat-lead">{E(lead)}</p>
    <p class="cat-n">제도 <b>{len(ps)}</b>개{soon}</p>
    <a class="btn-line" href="{{{{ROOT}}}}index.html?{finder_q}">내 조건으로 좁혀 보기</a>
  </div>
  {fig}
</header>
<ol class="res-list cat-list">{"".join(row(p, "../", static=True) for p in ps)}</ol>
<script src="{{{{ROOT}}}}assets/dl.js" defer></script>'''


def cat_grid(items):
    return '<ul class="reg-grid">' + ''.join(f'<li><a href="{s}.html"><span>{E(l)}</span><span class="n">{n}</span></a></li>' for s, l, n in items) + '</ul>'


def cat_index_body(cat_links):
    kind_by_slug = {s: k for k, s, _, _ in KINDS}
    kt = ''.join(
        f'<a class="tile" href="{s}.html">{photo(KIND_PHOTO[kind_by_slug[s]], "(max-width: 860px) 45vw, 210px", "32")}'
        f'<span class="tile-tx"><span class="tile-t">{E(l)}</span><span class="tile-n">{n}</span></span></a>'
        for s, l, n in cat_links['kind'])
    ft = ''.join(
        f'<a class="tile" href="{s}.html">{photo(FIELD_PHOTO[l], "(max-width: 860px) 45vw, 260px", "32")}'
        f'<span class="tile-tx"><span class="tile-t">{E(l)}</span><span class="tile-n">{n}</span></span></a>'
        for s, l, n in cat_links['field'])
    return f'''<header class="page-head"><h1>분류</h1></header>
<section class="sec-block"><h2>원하는 것</h2><div class="tiles t5">{kt}</div></section>
<section class="sec-block"><h2>분야</h2><div class="tiles t4">{ft}</div></section>
<section class="sec-block"><h2>지역</h2>{cat_grid(cat_links["region"])}</section>'''


# ---------- 안내 글 ----------
def _read_min(g):
    n = len(re.sub(r'<[^>]+>', '', g.get('body_html', '')))
    return max(1, round(n / 500))


def guide_body(g):
    ph = GUIDE_PHOTO.get(g['slug'])
    cover = f'<figure class="g-cover">{photo(ph, "(max-width: 720px) 100vw, 680px", "169", eager=True)}{photo_cap(ph)}</figure>' if ph else ''
    return (f'<nav class="crumb prose-w" aria-label="위치"><a href="{{{{ROOT}}}}g/index.html">안내 글</a></nav>'
            f'<article class="prose"><header class="g-head"><h1>{E(g["title"])}</h1>'
            f'<p class="g-meta">갱신 {E(g.get("updated", TODAY.isoformat()))} · 읽는 데 약 {_read_min(g)}분</p></header>'
            f'{cover}<div class="g-body">{g["body_html"]}</div></article>')


def guide_index_body():
    items = ''
    for g in guides:
        ph = GUIDE_PHOTO.get(g['slug'])
        items += (f'<li><a class="g-row" href="{E(g["slug"])}.html"><span class="g-tx"><span class="g-title">{E(g["title"])}</span>'
                  f'<span class="g-desc">{E(g["desc"])}</span><span class="g-min">읽는 데 약 {_read_min(g)}분</span></span>'
                  f'{photo(ph, "(max-width: 860px) 112px, 200px", "32") if ph else "<span></span>"}</a></li>')
    return (f'<header class="page-head"><h1>안내 글</h1><p class="page-lead">제도를 고를 때 알아 둘 기준</p></header>'
            f'<ul class="glist">{items or "<li>준비 중입니다.</li>"}</ul>')


def about_body():
    return f'''<article class="prose">
<header class="g-head"><h1>소개</h1></header>
<div class="g-body">
<p>{E(SITE)}는 무료 교육, 교육 수당, 자격증 응시료 지원, 창업 지원을 한곳에 모아 <b>내 상황에서 신청할 수 있는지</b>를 빠르게 가려 볼 수 있게 만든 민간 안내 사이트입니다.</p>
<h2>정보를 모으는 방법</h2>
<p>공공데이터포털에서 개방한 정부 서비스 정보와 각 기관의 모집 공고 원문을 읽고, 나이·지역·학력·가구소득·취업 상태 조건을 같은 기준으로 정리합니다. 제도마다 근거가 된 공고 문장과 확인한 날짜를 함께 적습니다.</p>
<h2>한계</h2>
<p>공고에 조건이 적혀 있지 않으면 "확인 필요"로 표시합니다. 조건은 해마다 바뀌므로 신청하기 전에 반드시 공식 안내를 확인하세요. 이 사이트는 정부·공공기관과 관계없는 개인이 운영합니다.</p>
<h2>광고</h2>
<p>운영비는 쪽 사이사이에 '광고' 표시를 달고 싣는 광고(카카오 애드핏·Google 애드센스)로 충당합니다. 광고주는 어떤 제도를 싣고 어떤 순서로 보여 줄지에 관여하지 않습니다. 광고와 쿠키에 대해서는 <a href="{{{{ROOT}}}}privacy.html">개인정보처리방침</a>에 적었습니다.</p>
<section id="photos" class="credits">{credits_html()}</section>
</div>
</article>'''
