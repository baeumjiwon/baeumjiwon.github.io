# 사이트 디자인(D안) · A안(목록형) 뼈대에 당근알바의 목록 줄, 스파르타 내일배움캠프의 카드 줄·상세 머리 구성을 더했다.
# theme_a.py(A안)를 먼저 실행하고, 바꿀 함수만 아래에서 덮어쓴다. 9/17 시안 폴더(research/proto/d/src)에서 이곳으로 옮김.
# 원칙: 참고 사이트의 로고·브랜드색·일러스트는 따르지 않고 구성만 따른다. 숫자는 모두 DB 값과 코드 계산.
_A_THEME = os.path.join(SRC, 'theme_a.py')
exec(compile(open(_A_THEME, encoding='utf-8').read(), _A_THEME, 'exec'), globals())
import urllib.parse

# 색·머리 꾸밈·숫자 타일은 비교를 거쳐 정했다(비교 쪽은 research/proto에 기록으로 남김): 9/17 색 = 파랑 + 흰색(palette B안),
# 머리 꾸밈 = 포스터(flashy 3번: 사선 흰 면 · 노란 원 · 형광펜 · 분야 이름 리본), 숫자 타일 = 남색 카드(tiles 3번 — tiles2의 새 틀 3안을
# 보고도 "3이 제일 낫긴 해"). 값은 d.css

_A_home_body = home_body
_B_credits_html = credits_html

# 제도 이름 읽기 쉽게(9/17 사용자 "일학습병행(신규 채용 학습근로자) 이 부분도 띄어쓰기라던가 가독성이 부족해"):
# 괄호 앞뒤를 띄우고 괄호 속 설명은 옅게. 상세 머리 제목은 끝에 붙은 괄호 설명을 제목 아래 작은 줄로 내린다.
# 검색 추천(search.js nameHtml)도 같은 규칙, 목록 줄 검색어 칠하기(app.js paintRow)는 이 구조를 지킨다
_NAME_PAREN = re.compile(r'\s*[(（]([^()（）]+)[)）]\s*')
_NAME_TAIL = re.compile(r'^(.+?)\s*[(（]([^()（）]+)[)）]\s*$')


def name_html(name, split_tail=False):
    if split_tail:
        m = _NAME_TAIL.match(name)
        if m:
            return f'{name_html(m.group(1))}<span class="nm-sub">{E(m.group(2))}</span>'
    return _NAME_PAREN.sub(lambda m: f' <span class="nm-p">({m.group(1)})</span> ', E(name)).strip()

# ---------- 아이콘(선 아이콘, 글자 색을 따른다) ----------
SVG = {
    'cal': '<rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
    'won': '<circle cx="12" cy="12" r="8.5"/><path d="m7.6 8.6 1.9 6.8 2.5-5.6 2.5 5.6 1.9-6.8M6.8 11.6h10.4"/>',
    'wallet': '<rect x="3" y="6" width="18" height="13" rx="3"/><path d="M3 10h18M15.5 14.5h2"/>',
    'pin': '<path d="M12 21s-6.5-5.8-6.5-11a6.5 6.5 0 0 1 13 0c0 5.2-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3"/>',
    'clock': '<circle cx="12" cy="13" r="7.5"/><path d="M12 9.5V13l2.4 2M9.5 2.8h5"/>',
    'user': '<circle cx="12" cy="8.5" r="3.6"/><path d="M4.8 20c.9-3.9 3.7-6 7.2-6s6.3 2.1 7.2 6"/>',
    'laptop': '<rect x="4.5" y="5" width="15" height="10" rx="1.6"/><path d="M2.5 19h19"/>',
    'card': '<rect x="2.5" y="5.5" width="19" height="13" rx="2.5"/><path d="M2.5 10h19M6.5 15h4"/>',
    'pct': '<path d="M18.5 5.5 5.5 18.5"/><circle cx="7.5" cy="7.5" r="2.6"/><circle cx="16.5" cy="16.5" r="2.6"/>',
    'left': '<path d="m15 5-7 7 7 7"/>',
    'right': '<path d="m9 5 7 7-7 7"/>',
    'search': '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/>',
}


def ico(name, cls='i'):
    return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">{SVG[name]}</svg>'


# ---------- 첫 화면 그림(직접 그린 선 그림) ----------
# 9/16 사용자: Fluent Emoji 3D를 보고 "이모지는 AI 티가 많이 난다" → 금지("이모지는 절대 금지!"), "사람이 만든듯하게".
# 목록 그림으로 고른 선 그림(남색 펜 선 + 크림 면 + 코랄·노랑 색판을 어긋나게 깐 잡지 삽화)으로 머리·타일·분야 바로가기·안내 글 칸을
# 모두 새로 그렸다. 원본과 실제 크기 미리보기: research/proto/art/ui/ (preview_ui.py, make_hero.py). 칸 색은 연한 단색.
# 카드 윗부분은 그림을 따로 두지 않고 목록 줄과 같은 사진·그림을 쓴다(같은 제도는 어디서나 같은 모습).
UI_ART = {
    'q-it': '#E4EDFF', 'q-media': '#EFE8FF', 'q-tech': '#FFF2D6', 'q-office': '#DEF7EF',
    'q-lang': '#E3F6FF', 'q-service': '#FFEDE3', 'q-care': '#FFEAF3', 'q-grant': '#FFF6D8',
    't-free': '#E8F6EC', 't-paid': '#FFF6D8', 't-week': '#FFEDE3',
    'g-income': '#DEF7EF', 'g-card': '#EFE8FF', 'g-allowance': '#FFF6D8',
}
HERO_TILE_ART = {'free': 't-free', 'paid': 't-paid', 'week': 't-week'}
GUIDE_CARDS = [('median-income', 'g-income'), ('naeil-card-eligibility', 'g-card'), ('training-allowance', 'g-allowance')]
_ui_missing = sorted(n for n in list(UI_ART) + ['hero', 'hero-m'] if not os.path.exists(os.path.join(IMG_DIR, 'ui-art', f'{n}.svg')))
if _ui_missing:
    raise SystemExit('첫 화면 그림이 없습니다(src/img/ui-art): ' + ', '.join(_ui_missing))
if os.path.isdir(os.path.join(IMG_DIR, 'icons')):
    raise SystemExit('src/img/icons(이모지 그림)가 남아 있으면 빌드에 함께 복사됩니다. 이모지는 쓰지 않습니다.')


def ui_art(name, cls, eager=False):
    """선 그림 <img>. 글자 옆 장식이라 alt는 비운다"""
    return (f'<img class="{cls}" src="{{{{ROOT}}}}assets/img/ui-art/{name}.svg" width="96" height="96" alt="" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async">')


# ---------- 마감 ----------
def _open_now(p):
    d = dday(p.get('next_deadline'))
    return (d is not None and d >= 0) or _always_open(p)


def _within(p, days):
    d = dday(p.get('next_deadline'))
    return d is not None and 0 <= d <= days


def dday_badge(p):
    """카드용 '마감 D-3'. d.js가 브라우저 날짜로 다시 쓴다. 3일 이내만 빨강"""
    s = p.get('next_deadline')
    d = dday(s)
    if s and d is not None and d >= 0:
        t = '오늘 마감' if d == 0 else f'마감 D-{d}'
        hot = ' hot' if d <= 3 else ''
        return f'<span class="dd{hot}" data-dd="{E(s)}">{ico("clock")}<span class="dd-t">{t}</span></span>'
    if _always_open(p):
        return '<span class="dd">상시 모집</span>'
    return ''


# ---------- 카드(내일배움캠프 과정 카드 구성: 사진 · 모집 중 · 제목 · 기간 · 마감 D-day) ----------
CARD_PH_SIZES = '(max-width: 860px) 76vw, 264px'


def _card_pick(cands, used):
    """한 카드 줄 안에서 덜 쓴 것부터, 바로 앞 카드와 같은 것은 피해서 고른다. used: {이름: 쓴 횟수, '': 바로 앞 카드}"""
    last = used.get('')
    pick = min(cands, key=lambda n: (n == last, used.get(n, 0), cands.index(n)))
    used[pick] = used.get(pick, 0) + 1
    used[''] = pick
    return pick


def card_media(p, used, eager=False):
    """카드 윗부분: 목록 줄과 같은 규칙(사진 = 무엇을 배우는지, 그림 = 어떤 제도인지)"""
    subj = row_subject(p)
    if subj in ROW_ART:
        pick = _card_pick([subj, subj + '2'] if subj in ROW_ART_ALT else [subj], used)
        return (f'<span class="ph art r169" style="--a:{ROW_ART[subj]}"><img src="{{{{ROOT}}}}assets/img/rows-art/{pick}.svg" alt="" '
                f'width="240" height="160" loading="{"eager" if eager else "lazy"}" decoding="async"></span>')
    name, alt = row_photo(p)
    return photo(_card_pick([name] + ([alt] if alt else []), used), CARD_PH_SIZES, '169', eager=eager)


def card(p, used, eager=False):
    kinds = ' · '.join(KIND_LABEL[k] for k in p['kinds'])
    lines = ''
    if not _is_na(p):
        parts = _dur_parts(p)
        if parts:
            rest = ''.join(' · ' + E(x) for x in parts[1:])
            lines += f'<span class="c-ln">{ico("cal")}<span><b>{E(parts[0])}</b>{rest}</span></span>'
    m, partial = _money_value(p)
    if m:
        lines += f'<span class="c-ln c-money">{ico("won")}<span>{E(m)}</span></span>'
    ct = p.get('cost_type')
    if ct in COST_SHOW:
        lines += f'<span class="c-ln">{ico("wallet")}<span>내는 돈 {E(ct)}</span></span>'
    badge = '<span class="c-badge">모집 중</span>' if _open_now(p) else ''
    return (f'<li class="card"><a class="c-a" href="{{{{ROOT}}}}p/{E(p["id"])}.html">'
            f'<span class="c-thumb">{card_media(p, used, eager)}{badge}</span>'
            f'<span class="c-body"><span class="c-kind">{E(kinds)}</span><span class="c-title">{name_html(p["name"])}</span>{lines}'
            f'<span class="c-foot"><span class="c-reg">{ico("pin")}{E(region_short(p))}</span>{dday_badge(p)}</span></span></a></li>')


def shelf(title, tabs, id_, sub=''):
    """가로로 넘기는 카드 줄. tabs: [(키, 이름, 제도들)] — 하나면 탭 줄 없이"""
    tabs = [t for t in tabs if t[2]]
    if not tabs:
        return ''
    multi = len(tabs) > 1
    btns, panels = '', ''
    for i, (k, label, items) in enumerate(tabs):
        on = i == 0
        if multi:
            sel = 'true' if on else 'false'
            btns += (f'<button type="button" class="sh-tab" role="tab" id="{id_}-t-{k}" aria-controls="{id_}-p-{k}" '
                     f'aria-selected="{sel}" tabindex="{0 if on else -1}">{E(label)}</button>')
        role = f' role="tabpanel" aria-labelledby="{id_}-t-{k}"' if multi else ''
        used = {}
        cards = ''.join(card(p, used, eager=on and j < 4) for j, p in enumerate(items))
        hid = '' if on else ' hidden'
        panels += f'<div class="sh-panel" id="{id_}-p-{k}"{role}{hid}><ol class="cards">{cards}</ol></div>'
    tabs_html = f'<div class="sh-tabs" role="tablist" aria-label="{E(title)}">{btns}</div>' if multi else ''
    sub_html = f'<p class="sh-sub">{E(sub)}</p>' if sub else ''
    return (f'<section class="shelf" id="{id_}" data-shelf aria-labelledby="{id_}-h">'
            f'<div class="sh-head"><div class="sh-tt"><h2 id="{id_}-h">{E(title)}</h2>{sub_html}</div>'
            f'<div class="sh-nav"><button type="button" class="sh-prev" aria-label="이전 카드">{ico("left")}</button>'
            f'<button type="button" class="sh-next" aria-label="다음 카드">{ico("right")}</button></div></div>'
            f'{tabs_html}{panels}</section>')


# ---------- 결과 행(당근알바 목록 줄: 제목 → 아이콘 붙은 기간·돈 줄 → 흐린 기관 줄, 마감은 알약) ----------
def _dur_line(p):
    if _is_na(p):
        return ''
    parts = _dur_parts(p)
    if not parts:
        return f'<p class="r-dur dim">{ico("cal")}<span>기간 공고 확인</span></p>'
    out = [f'<b>{E(parts[0])}</b>'] + [E(x) for x in parts[1:]]
    if p.get('schedule') in SCHED_SHOW:
        out.append(E(SCHED_SHOW[p['schedule']]))
    return f'<p class="r-dur">{ico("cal")}<span>{" · ".join(out)}</span></p>'


def _money_line(p):
    bits = []
    m, partial = _money_value(p)
    if m:
        bits.append(f'<span class="mi"><span class="lb">받는 돈</span><b>{E(m)}</b></span>')
    ct = p.get('cost_type')
    if ct in COST_SHOW:
        bits.append(f'<span class="mi"><span class="lb">내는 돈</span><b>{E(ct)}</b></span>')
    elif ct == '확인필요':
        bits.append('<span class="mi dim">비용 · 공고 확인</span>')
    if not bits:
        return ''
    return f'<p class="r-money">{ico("won")}<span class="r-mw">{"".join(bits)}</span></p>'


# ---------- 결과 행 오른쪽 사진(당근알바 검색 결과처럼) ----------
# 기관·교육장 사진은 저작권 때문에 쓰지 않는다 → Unsplash·Pexels 사진 중 알아볼 수 있는 앞얼굴이 없는 것만, 분야로 짝지어 돌려 쓴다.
# 사진마다 PHOTO_FOCUS(보여 줄 영역, 넘지 않을 영역)가 있어야 한다: 로고·글자·얼굴을 잘라 내는 규칙이 거기 있다.
PHOTO_FOCUS.update({
    'it-pexels-4974912': ((.20, .73, .40, 1), (.20, .73, .40, 1)),              # 오른쪽 노트북 화면 속 인물 사진 뺌
    'media-pexels-39005351': ((.19, .90, 0, 1), (.04, .99, 0, 1)),             # 촬영 카메라
    'lang-pexels-5676663': ((.40, .978, .417, .983), (.322, .989, .317, .983)), # 얼굴·등판 글씨 뺌, 손과 문법책
    'lang-pexels-7156135': ((.067, .578, .25, .825), (.067, .578, .25, .825)),  # 얼굴 뺌, 칠판 낱말과 가리키는 손
    'exam-pexels-6684265': ((.167, .922, .15, 1), (.167, .922, .15, 1)),        # 'EXAM FORM' 글자 뺌
    'care-unsplash-9MTqeBaAOlU': ((.167, .833, .166, .833), FULL),              # 맞잡은 손
    'classroom-unsplash-oc_XTqWezp4': ((.27, .688, .53, 1), (.25, .72, .53, 1)), # 턱 아래만: 펜 쥔 손·공책
    'classroom-unsplash-7hxOWrk-8RI': ((0, 1, .35, .85), (0, 1, .30, .90)),      # 강의실 뒷모습
})
# 9/17 공개 전: 오토바이 정비 사진 tech-pexels-32391493은 잘라도 옆얼굴이 알아볼 만하게 남아 뺐다(파일은 research/photos/removed/)
# 주제별 사진 46장(9/16): 찾기 → 따로 반증 검증(얼굴·로고·글자·92px 가독성) 통과분. 고른 기록 research/photos/picks_rows.json
PHOTO_FOCUS.update({
    'code-pexels-36497969': ((0.25, 0.95, 0, 1), FULL),  # 코드 띄운 노트북 앞에서 키보드 치는 두 손
    'code-pexels-4682189': ((0.2, 0.8, 0.1, 0.95), FULL),  # 서버실 패치패널 광케이블
    'code-unsplash-QckxruozjRg': ((0.15, 0.62, 0.36, 0.8), (0, 0.63, 0.35, 1)),  # 헤드폰 쓴 뒷모습 코딩, 위·오른쪽 얼굴 뺌
    'online-unsplash-q3zZHY5GHu0': ((0.1, 0.95, 0.22, 0.84), FULL),  # 동영상 강의 노트북과 공책
    'online-pexels-7120900': ((0.2, 0.75, 0, 0.85), FULL),  # 창가 책상에서 헤드폰 끼고 강의 보는 뒷모습
    'data-unsplash-ykgLX_CwtDw': ((0.22, 0.68, 0.06, 0.62), (0, 1, 0, 0.66)),  # 태블릿 차트를 짚는 손, 아래 계산기 뺌
    'security-unsplash-QP7RBa5r8HM': ((0.45, 0.95, 0.12, 0.72), (0.3, 1, 0, 0.74)),  # 키보드 위 자물쇠, 'caps lock' 글자 뺌
    'game-unsplash-XC3fq-ffXRI': ((0.2, 0.9, 0.05, 0.9), FULL),  # 게임 화면 노트북 앞 게임패드
    'chip-unsplash-qOx9KsvpqcM': ((0.2, 0.8, 0.15, 0.85), FULL),  # 반도체 웨이퍼
    'robot-unsplash-8gr6bObQLOI': ((0.6, 0.95, 0.15, 0.75), FULL),  # 공장 주황 로봇팔
    'print3d-pexels-31137405': ((0.25, 0.9, 0.05, 0.95), FULL),  # 3D 프린터 헤드
    'drone-pexels-1336211': ((0.25, 0.72, 0.12, 0.85), FULL),  # 손에 든 흰 드론
    'job-pexels-33175650': ((0.25, 0.75, 0.25, 0.95), FULL),  # 정장 악수 손
    'job-pexels-295480': ((0, 0.88, 0.2, 1), (0, 0.88, 0, 1)),  # 대기 공간 주황 의자
    'job-pexels-9623649': ((0.2, 0.75, 0.3, 0.95), FULL),  # 사무 건물 계단 오르는 정장 뒷모습
    'jobb-pexels-7580909': ((0.2, 0.9, 0.1, 0.8), (0, 1, 0.06, 1)),  # 서류 폴더를 안은 정장 몸통(얼굴 없음)
    'internb-pexels-6457478': ((0.3, 1, 0.25, 0.85), (0, 1, 0, 0.85)),  # 노트북에서 옆 동료가 짚어 주는 손
    'internb-pexels-6036671': ((0, 1, 0.1, 0.85), FULL),  # 작업대 바이스 옆 두 사람의 손(현장 실습)
    'shopb-pexels-6912870': ((0.3, 0.85, 0.05, 0.75), FULL),  # 앞치마 꽃집 주인이 해바라기 정리
    'shop-pexels-8004028': ((0, 0.95, 0.35, 0.85), FULL),  # 흰 벽에 포스트잇 붙이는 손
    'shopb-pexels-7309307': ((0.25, 0.8, 0.12, 0.95), (0, 1, 0.12, 1)),  # 작은 가게 포장·청록 컵
    'marketing-pexels-4247766': ((0, 1, 0.25, 0.75), (0, 1, 0.1, 1)),  # 택배 상자 테이프 붙이는 손
    'lawb-pexels-6358834': ((0, 1, 0.3, 0.75), (0, 1, 0.2, 1)),  # 서류에 도장 찍는 손
    'house-unsplash-Ebj87ehFNNU': ((0, 0.65, 0.05, 0.85), FULL),  # 손가락에 걸린 열쇠
    'coin-unsplash-5OUMf1Mr5pU': ((0.28, 0.88, 0.18, 0.87), FULL),  # 분홍 돼지저금통과 동전
    'coin-unsplash-OApHds2yEGQ': ((0.245, 0.92, 0.2, 0.72), FULL),  # 흰 바탕 동전 더미
    'finance-pexels-5900135': ((0.32, 0.78, 0.28, 0.62), (0.32, 1, 0, 1)),  # 영수증 정리하는 손(가계부)
    'finance-unsplash-Q_vhJv5im-8': ((0.1, 0.8, 0.25, 0.8), (0, 0.9, 0, 1)),  # 주식 봉차트 화면
    'book-pexels-13278839': ((0.45, 0.95, 0.1, 0.9), (0.3, 1, 0, 1)),  # 도서관 서가 통로
    'book-pexels-30752162': ((0.3, 0.7, 0.2, 0.8), FULL),  # 밝은 나무 서가
    'exam2-unsplash-cbEvoHbJnIE': ((0.05, 0.47, 0.22, 0.62), (0, 0.47, 0.18, 0.63)),  # OMR 답안지와 연필
    'culture-unsplash-rixN0q0IamQ': ((0.1, 0.9, 0.25, 0.75), FULL),  # 물감 팔레트와 붓
    'beauty-pexels-7253877': ((0.05, 0.95, 0.18, 0.7), FULL),  # 가위와 빗으로 머리카락 자르는 손
    'bio-unsplash-HQM5jm12etE': ((0.1, 0.8, 0.1, 0.95), FULL),  # 장갑 낀 손 피펫·시험관
    'fire-unsplash-wjHdeYmI-XU': ((0.1, 0.98, 0.08, 0.6), FULL),  # 주황 안전모와 안전조끼
    'elec-unsplash-PkHf7BUWbtk': ((0.05, 0.75, 0.2, 0.85), FULL),  # 배전반 차단기 측정
    'elec-pexels-33531832': ((0.15, 0.95, 0.33, 0.72), (0, 1, 0.12, 1)),  # 모터 단자대 측정하는 손
    'aircon-unsplash-Al9lWh3XKGM': ((0.15, 0.8, 0.05, 0.95), FULL),  # 에어컨 실외기
    'weld-pexels-3158651': ((0.3, 0.85, 0.15, 0.85), (0, 1, 0, 0.87)),  # 용접 마스크와 파란 연기
    'tile-pexels-11806477': ((0.3, 1, 0.1, 0.85), FULL),  # 흙손으로 타일 모르타르 바르는 손
    'cnc-pexels-8956445': ((0, 0.6, 0, 0.95), FULL),  # CNC 밀링 스핀들 절삭유
    'cnc-pexels-11951233': ((0.1, 0.9, 0.1, 0.85), FULL),  # 선반 척 금속봉 가공
    'fork-unsplash-OnbSOhz0oig': ((0.22, 0.55, 0.45, 0.97), (0.19, 1, 0, 1)),  # 선반 통로의 노란 지게차
    'moto-pexels-8550664': ((0, 0.8, 0.05, 0.78), (0, 1, 0, 0.8)),  # 오토바이 엔진 정비하는 손
    'farm-pexels-32146752': ((0, 1, 0.2, 1), FULL),  # 온실 수경재배 줄
    'farm-unsplash-MdA-AwgUYy0': ((0.35, 0.65, 0.35, 0.7), (0, 0.66, 0, 1)),  # 흙에 모종 심는 손
})
RATIO['11'] = 1
# 주제 사진이 없을 때만 쓰는 분야 묶음
ROW_POOL = {
    'it': ['it-unsplash-Hl1stIQkVRw', 'it-pexels-7988087', 'it-pexels-4974912'],
    'media': ['media-pexels-16313664', 'media-pexels-15713296', 'media-pexels-7014943', 'media-pexels-39005351'],
    'tech': ['tech-unsplash-kBKOaghy8mU'],  # 용접 사진은 이름에 '용접'이 있을 때만
    'office': ['office-unsplash-O2GCr83qCdg', 'office-pexels-8297220'],
    'lang': ['lang-unsplash-QVrBu1MqJYU', 'lang-pexels-5185082', 'lang-pexels-5676663', 'lang-pexels-7156135'],
    'service': ['food-unsplash-h_s7AUBPss8', 'food-pexels-4349954', 'food-pexels-16140004', 'food-unsplash-XiyR0BXRIsI'],
    'care': ['care-pexels-7551634', 'care-unsplash-9MTqeBaAOlU'],
    'all': ['people-pexels-5757210', 'classroom-unsplash-oc_XTqWezp4', 'exam-pexels-6683391', 'classroom-unsplash-7hxOWrk-8RI',
            'lang-pexels-5185082'],
    'money': ['office-pexels-8297220', 'exam-unsplash-w-1ydxmB7hQ', 'office-unsplash-O2GCr83qCdg'],  # 지원금: 얼굴 없는 사물·손만
    'exam': ['exam-pexels-31115182', 'exam-pexels-6684265', 'exam-pexels-6683391'],
    'startup': ['startup-pexels-31892097', 'food-pexels-4349954', 'food-unsplash-XiyR0BXRIsI'],
}
# 공고 주제: 이름·한 줄 설명의 낱말로 고른다. 규칙은 (주제, 걸릴 낱말, 있으면 건너뛸 낱말)이고 위에 있는 것이 먼저.
# (9/16 사용자) "희망리턴패키지인데 악수 사진", "농촌에서 살아보기인데 물 나오는 기계"가 왜 나왔나 세어 보니
#   ① 제도 성격 낱말(취업·자격증·아카데미)이 내용 낱말(기계·농촌)보다 먼저 걸리고
#   ② '농촌'처럼 아예 없는 낱말은 분야 기본값(기술·현장 → CNC)으로 떨어지고
#   ③ '귀어학교'의 '어학', '창업보육'의 '보육'처럼 낱말이 엉뚱하게 걸렸다.
# 그래서 내용 규칙(무엇을 배우는가)을 이름 → 한 줄 설명 순으로 모두 본 뒤에야 제도 성격 규칙을 본다.
ROW_CONTENT_RULES = [
    ('fork', ['지게차'], []),
    ('weld', ['용접', '취부', '조선', '선박'], []),
    ('elec', ['전기', '태양광', '신재생', '배전', '송전'], ['전기차']),
    ('aircon', ['공조', '냉동', '냉난방', '에어컨', '보일러', '설비보전'], []),
    ('fire', ['소방', '산업안전', '기초안전', '안전보건', '안전관리'], []),
    ('tile', ['타일', '도배', '인테리어', '미장', '건설', '목공', '방수', '도장', '집수리', '건축'], []),
    ('moto', ['자동차', '이륜', '정비'], ['전기차']),
    ('drive', ['버스', '대형면허', '운전자 양성', '운수', '화물차'], []),  # '운전'만으로는 안 건다: 운전면허 응시료 지원까지 끌려온다
    ('robot', ['로봇'], []),
    ('chip', ['반도체', '디스플레이'], []),
    ('battery', ['배터리', '이차전지'], []),
    ('bio', ['바이오', '제약', '향장'], []),
    ('drone', ['드론'], []),
    ('print3d', ['3D'], []),
    ('cnc', ['기계', 'CNC', '금형', '제조', '스마트팩토리', '뿌리산업'], []),
    ('security', ['보안', '해킹', '화이트햇', '정보보호'], []),
    ('game', ['게임'], []),
    ('data', ['데이터'], []),
    ('design', ['디자인', '웹툰', '일러스트', '캐릭터'], []),
    ('cam', ['영상', '미디어', '유튜브', '방송', '콘텐츠', 'MCN', '촬영', '영화'], ['방송대', '방송통신대', '공개강의']),
    ('farm', ['스마트팜', '농업', '귀농', '농촌', '영농', '귀촌', '원예', '축산', '귀어', '어촌'], []),
    ('beauty', ['미용', '네일', '헤어', '피부'], ['헤어메이크업']),
    ('nurse', ['간호', '보건', '의료'], ['보건복지부', '안전보건']),
    ('care', ['요양', '돌봄', '간병', '보육'], ['창업보육', '보육센터', '보육실', '방과후']),  # 약통 사진이라 청소년 방과후엔 안 맞는다
    ('pot', ['조리', '제과', '제빵', '바리스타', '요리', '커피', '한식', '외식'], []),
    ('trade', ['무역', '물류', '유통'], []),
    ('law', ['노동법', '법률', '생활법', '노무'], []),
    ('culture', ['문화예술', '예술', '음악', '공연', '미술'], []),
    ('finance', ['금융', '재무', '재정', '투자', '경제', '한은'], ['창조경제', '경제인', '경제혁신', '금융SW']),
    ('house', ['월세', '주거', '전세', '임대'], []),
    ('lang', ['외국어', '영어', '어학', '일본어', '중국어', '국어', '문해', '한글'], ['귀어']),
    ('chart', ['회계', '세무', '사무', 'ERP', '엑셀', '컴활', '전산'], ['사무공간']),
    # 가게·시장 사진이 있어 내용 규칙에 둔다. '폐업 소상공인의 취업 준비'는 가게 사진이 아니라 취업 그림이 맞다
    ('startup', ['창업', '소상공인', '자영업', '캠퍼스타운', '사업화'], ['폐업', '자격증 취득']),
    # '개발·'은 직무를 늘어놓은 '개발·PM·커머스' 꼴만 잡는다('역량개발' 같은 말은 안 걸림). 스파르타 내일배움캠프가 '커머스'로 택배 상자 사진이었다
    ('code', ['AI', '인공지능', '코딩', 'SW', '소프트웨어', '프로그래밍', '클라우드', '디지털', 'ICT', 'KDT', '핀테크',
              '블록체인', '메타버스', '임베디드', '앱 개발', '웹 개발', '개발·'], ['일자리플러스센터', '일자리센터']),
    ('marketing', ['마케팅', '광고', '커머스', '판로'], []),
    # 여러 분야를 한꺼번에 담은 강좌 포털은 마지막에 '온라인 강의'로 본다(위 규칙이 먼저 걸리면 그쪽이 맞다).
    # '온라인' 한 낱말로는 안 건다: '온라인 컨설팅'이 있는 취업 프로그램까지 노트북 사진이 된다
    ('online', ['온라인 강좌', '온라인 강의', '온라인 교육', '온라인 수강', '인터넷 강의', '이러닝', 'MOOC',
                '사이버', '원격', '공개강의'], []),
]
# 내용이 없고 제도 성격만 있는 것. 여기로 오면 사진 대신 그림 칸을 쓴다(ROW_ART).
ROW_KIND_RULES = [
    ('intern', ['인턴', '일경험', '일학습', '일자리', '채용연계', '직무체험'], []),
    ('exam', ['자격증', '응시', '검정', '자격'], []),
    ('job', ['취업', '구직', '채용', '전직'], []),
    ('book', ['평생학습', '도서관', '시민대학', '아카데미', '학교', '배움터', '강좌'], []),
]
# 돈만 주는 제도에서 이 낱말이 보이면 내용 규칙보다 먼저 '돈'으로 본다
ROW_MONEY_WORDS = ['수당', '장려금', '바우처', '이용권', '장학금', '대부', '융자', '활동비', '쿠폰', '포인트',
                   '카드', '응시료', '생계비', '등록금', '훈련비', '환급']
# 낱말이 안 걸리면 분야 묶음 → 주제
ROW_SUBJECT_FALLBACK = {'it': 'code', 'media': 'cam', 'tech': 'cnc', 'office': 'chart', 'lang': 'lang', 'service': 'pot', 'care': 'care',
                        'all': 'book', 'money': 'coin', 'exam': 'exam', 'startup': 'startup'}
# 주제 → 사진(돌려 쓴다). 여기 없는 주제는 ROW_POOL 분야 묶음으로
ROW_SUBJECT_PH = {
    'code': ['code-pexels-36497969', 'it-unsplash-Hl1stIQkVRw', 'code-pexels-4682189', 'it-pexels-4974912', 'code-unsplash-QckxruozjRg',
             'it-pexels-7988087'],
    'online': ['online-unsplash-q3zZHY5GHu0', 'online-pexels-7120900'],
    'data': ['data-unsplash-ykgLX_CwtDw', 'it-pexels-7988087'],
    'security': ['security-unsplash-QP7RBa5r8HM'],
    'game': ['game-unsplash-XC3fq-ffXRI'],
    'chip': ['chip-unsplash-qOx9KsvpqcM'],
    'robot': ['robot-unsplash-8gr6bObQLOI'],
    'print3d': ['print3d-pexels-31137405'],
    'drone': ['drone-pexels-1336211'],
    'cam': ['media-pexels-39005351', 'media-pexels-15713296'],
    'design': ['media-pexels-16313664', 'media-pexels-7014943'],
    'job': ['job-pexels-33175650', 'job-pexels-295480', 'job-pexels-9623649', 'jobb-pexels-7580909'],
    'intern': ['internb-pexels-6457478', 'internb-pexels-6036671'],
    'startup': ['shopb-pexels-6912870', 'startup-pexels-31892097', 'shop-pexels-8004028', 'shopb-pexels-7309307'],
    'marketing': ['marketing-pexels-4247766'],
    'law': ['lawb-pexels-6358834'],
    'house': ['house-unsplash-Ebj87ehFNNU'],
    'coin': ['coin-unsplash-5OUMf1Mr5pU', 'office-pexels-8297220', 'coin-unsplash-OApHds2yEGQ', 'exam-unsplash-w-1ydxmB7hQ'],
    'finance': ['finance-pexels-5900135', 'finance-unsplash-Q_vhJv5im-8'],
    'book': ['book-pexels-13278839', 'people-pexels-5757210', 'book-pexels-30752162', 'classroom-unsplash-oc_XTqWezp4',
             'classroom-unsplash-7hxOWrk-8RI'],
    'exam': ['exam-pexels-31115182', 'exam2-unsplash-cbEvoHbJnIE', 'exam-pexels-6684265', 'exam-pexels-6683391'],
    'culture': ['culture-unsplash-rixN0q0IamQ'],
    'beauty': ['beauty-pexels-7253877'],
    'bio': ['bio-unsplash-HQM5jm12etE'],
    'fire': ['fire-unsplash-wjHdeYmI-XU'],
    'elec': ['elec-unsplash-PkHf7BUWbtk', 'elec-pexels-33531832'],
    'aircon': ['aircon-unsplash-Al9lWh3XKGM'],
    'weld': ['weld-pexels-3158651', 'tech-unsplash-E15BQufHzJs'],
    'tile': ['tile-pexels-11806477'],
    'cnc': ['cnc-pexels-8956445', 'tech-unsplash-kBKOaghy8mU', 'cnc-pexels-11951233'],
    'fork': ['fork-unsplash-OnbSOhz0oig'],
    'moto': ['moto-pexels-8550664'],
    'farm': ['farm-pexels-32146752', 'farm-unsplash-MdA-AwgUYy0'],
    'chart': ['office-pexels-8297220', 'office-unsplash-O2GCr83qCdg'],
    'lang': ['lang-unsplash-QVrBu1MqJYU', 'lang-pexels-5185082', 'lang-pexels-5676663', 'lang-pexels-7156135'],
    'pot': ['food-unsplash-h_s7AUBPss8', 'food-pexels-4349954', 'food-pexels-16140004', 'food-unsplash-XiyR0BXRIsI'],
    'care': ['care-pexels-7551634', 'care-unsplash-9MTqeBaAOlU'],
}

# 사진으로 보여 줄 내용이 없는 주제는 직접 그린 그림 칸을 쓴다(9/16 사용자: "너가 직접 그림 그려서 넣어도 돼").
# 목록에서 사진은 '무엇을 배우는지', 그림은 '어떤 제도인지'를 뜻한다. 그림 원본 research/proto/art/rows/
# 9/16 사용자가 일곱 가지 스타일을 나란히 보고 '선 그림'을 고름(research/proto/artstyle).
# 남색 펜 선 + 크림 면에 코랄·노랑 색판을 어긋나게 깐 잡지 삽화. 칸 배경은 그러데이션이 아니라 연한 단색.
ROW_ART = {
    'job': '#E8F6EC',      # 취업 지원·상담: 서류가방과 이력서
    'coin': '#FFF6D8',     # 수당·바우처·장학금: 지폐와 동전
    'intern': '#FFEAF3',   # 인턴·일경험: 사원증
    'book': '#E3F6FF',     # 평생학습·강좌 포털: 펼친 책
    'nurse': '#DEF7EF',    # 간호·보건: 청진기와 구급가방
    'trade': '#FFF2DF',    # 무역·물류: 컨테이너
    'battery': '#EFE8FF',  # 이차전지
    'drive': '#E4EDFF',    # 운전·버스
}
# 같은 주제가 연달아 나오는 자리가 18곳(취업지원은 5줄 연속)이라 주제마다 그림을 두 벌 두고 번갈아 쓴다.
# 뜻은 같고 구도만 다른 <주제>2.svg. 사진과 같은 방식으로 맞바꾼다.
ROW_ART_ALT = {'job', 'coin', 'intern', 'book'}
_art_missing = sorted(n for s in ROW_ART for n in ((s, s + '2') if s in ROW_ART_ALT else (s,))
                      if not os.path.exists(os.path.join(IMG_DIR, 'rows-art', f'{n}.svg')))
if _art_missing:
    raise SystemExit('행 그림이 없습니다(src/img/rows-art): ' + ', '.join(_art_missing))

_row_ph_names = {n for pool in list(ROW_POOL.values()) + list(ROW_SUBJECT_PH.values()) for n in pool}
_row_ph_bad = sorted(n for n in _row_ph_names if not _credit(n) or n not in PHOTO_FOCUS
                     or not os.path.exists(os.path.join(IMG_DIR, f'{n}-480.webp')))
if _row_ph_bad:
    raise SystemExit('행 사진 설정이 맞지 않습니다(credits·PHOTO_FOCUS·파일): ' + ', '.join(_row_ph_bad))
_ROW_PH = {}
_LAST_PH = None


def _row_pool_key(p):
    ks = set(p['kinds'])
    if ks <= {'지원금', '창업', '응시료'}:
        return 'startup' if '창업' in ks else ('exam' if '응시료' in ks else 'money')
    f = next((FIELD_SLUG[x] for x in p.get('fields', []) if FIELD_SLUG.get(x) != 'all'), 'all')
    return 'startup' if f == 'all' and '창업' in ks else f


def _sq(t, dots=True):
    return re.sub(r'[\s·ㆍ]+' if dots else r'\s+', '', t or '')


def _has(w, text):
    """낱말 규칙은 띄어쓰기·가운뎃점을 빼고 맞춰 본다 — 맞춤법대로 '일학습병행'을 '일·학습 병행'으로 띄워도 같은 사진이 붙게.
    '개발·'처럼 가운뎃점으로 끝나는 낱말은 늘어놓은 꼴('개발·PM·커머스')만 잡으려는 것이라 가운뎃점을 남겨 본다"""
    return _sq(w, False) in _sq(text, False) if w.endswith('·') else _sq(w) in _sq(text)


def _rule_hit(rules, text, whole):
    """건너뛸 낱말은 이름과 한 줄 설명을 합쳐서 본다(이름에 '방송대'가 있으면 설명의 '방송'도 안 건다)"""
    for slug, words, skip in rules:
        if any(_has(w, text) for w in words) and not any(_has(w, whole) for w in skip):
            return slug
    return None


def row_subject(p):
    """이름 → 한 줄 설명 순으로 내용 규칙을 먼저 다 보고, 그래도 없으면 제도 성격 규칙을 본다.
    돈·응시료만 주는 제도에서 돈 낱말이 보이면(청년수당·이용권·장학금) 내용 규칙보다 먼저 돈으로 본다:
    '대전 평생교육이용권(일반·AI디지털·노인)'이 'AI' 때문에 코딩 사진을 달던 것을 막는다.
    '청년월세 지원'처럼 돈 낱말이 없으면 내용 규칙이 살아 있어 열쇠 사진이 그대로 붙는다."""
    texts = (p['name'], p.get('one_liner') or '')
    whole = ' | '.join(texts)  # 띄어쓰기를 빼고 볼 때 이름 끝과 설명 앞이 한 낱말로 붙지 않게
    kinds = set(p['kinds'])
    if kinds <= {'지원금', '응시료'} and any(_has(w, whole) for w in ROW_MONEY_WORDS):
        return 'exam' if '응시료' in kinds else 'coin'
    for rules in (ROW_CONTENT_RULES, ROW_KIND_RULES):
        for text in texts:
            s = _rule_hit(rules, text, whole)
            if s:
                return s
    return ROW_SUBJECT_FALLBACK[_row_pool_key(p)]


def _row_pool(p):
    return ROW_SUBJECT_PH.get(row_subject(p)) or ROW_POOL[_row_pool_key(p)]


def row_photo(p):
    """(사진, 대신 쓸 사진). 같은 사진 묶음 안에서는 id 순으로 돌아가며 나눠 한 사진에 몰리지 않게 한다"""
    if not _ROW_PH:
        groups = {}
        for q in sorted(programs, key=lambda q: q['id']):
            if row_subject(q) in ROW_ART:  # 그림 칸을 쓰는 제도는 사진을 나눠 갖지 않는다
                continue
            groups.setdefault(tuple(_row_pool(q)), []).append(q['id'])
        for pool, ids in groups.items():
            for i, pid in enumerate(ids):
                _ROW_PH[pid] = (pool[i % len(pool)], pool[(i + 1) % len(pool)] if len(pool) > 1 else None)
    if p['id'] not in _ROW_PH:
        pool = _row_pool(p)
        i = sum(map(ord, p['id']))
        _ROW_PH[p['id']] = (pool[i % len(pool)], pool[(i + 1) % len(pool)] if len(pool) > 1 else None)
    return _ROW_PH[p['id']]


ROW_PH_SIZES = '(max-width: 860px) 92px, 148px'


def row_art(name):
    """주제 그림 칸. 사진 틀과 같은 비율(컴퓨터 4:3 · 휴대폰 1:1)을 쓴다. name은 'job' 또는 변형 'job2'"""
    return (f'<span class="ph art r43 m11" style="--a:{ROW_ART[name[:-1] if name.endswith("2") else name]}">'
            f'<img src="{{{{ROOT}}}}assets/img/rows-art/{name}.svg" alt="" width="240" height="160" '
            f'loading="lazy" decoding="async"></span>')


def row(p, root, static=False):
    global _LAST_PH
    kinds = ' · '.join(KIND_LABEL[k] for k in p['kinds'])
    art = row_subject(p)
    if art in ROW_ART:
        # 사진과 같은 규칙: 바로 위 행과 같은 그림이면 변형판으로 바꾸고, <template>에 원래 것을 넣어 둔다
        name, alt = art, (art + '2' if art in ROW_ART_ALT else None)
        if alt and f'art-{name}' == _LAST_PH:
            name, alt = alt, name
        _LAST_PH = f'art-{name}'
        tpl = f'<template class="r-ph-alt" data-ph="art-{alt}">{row_art(alt)}</template>' if alt else ''
        ph = f'<span class="r-ph" data-ph="art-{name}">{row_art(name)}</span>{tpl}'
    else:
        # 빌드 순서에서 바로 위 행과 같은 사진이면 대신 쓸 사진으로. 브라우저에서 순서가 바뀌면 app.js가 <template>과 맞바꾼다
        name, alt = row_photo(p)
        if alt and name == _LAST_PH:
            name, alt = alt, name
        _LAST_PH = name
        tpl = f'<template class="r-ph-alt" data-ph="{alt}">{photo(alt, ROW_PH_SIZES, "43", "11")}</template>' if alt else ''
        ph = f'<span class="r-ph" data-ph="{name}">{photo(name, ROW_PH_SIZES, "43", "11")}</span>{tpl}'
    dur, money, dl = _dur_line(p), _money_line(p), _dl_html(p)
    one = f'<p class="r-one">{E(p["one_liner"])}</p>' if (not dur and not money and p.get('one_liner')) else ''
    st = '' if static else '<span class="r-st" hidden></span>'
    attrs = f' data-dk="{_dk(p)}" data-fx="{_facts(p)}"' + (' data-open="1"' if _always_open(p) else '')
    return f'''<li class="row" id="r-{E(p["id"])}" data-id="{E(p["id"])}"{attrs}>
  <p class="r-top"><span class="r-kind">{E(kinds)}</span>{st}</p>
  <h3 class="r-title"><a href="{root}p/{E(p["id"])}.html">{name_html(p["name"])}</a></h3>
  {dur}{money}{one}
  <p class="r-org" title="{E(p["operator"])}">{ico("pin")}<span>{E(_org_short(p))} · {E(region_short(p))}</span></p>
  {dl}{ph}
</li>'''


# ---------- 글자 검색(네이버식). 브라우저 app.js의 norm()과 같은 규칙으로 붙여 쓴 글에서 찾는다 ----------
_NORM_RE = re.compile(r'[\s·ㆍ\-–—_()\[\]{}<>,./:;~!?"\'‘’“”「」『』]+')
HERO_WORDS = ['지게차', '용접', '전기', '코딩', '영상', '데이터', '마케팅', '자격증', '세무', '타일']


def _norm(t):
    return _NORM_RE.sub('', str(t or '').lower())


def _hay_head(p):
    labels = [KIND_LABEL[k] for k in p['kinds']] + list(p['fields'])
    return ' '.join([p['name'], p.get('operator') or '', p.get('one_liner') or '', str(p.get('format') or ''),
                     ' '.join(labels), ' '.join(p['regions'])])


def compact_extra(p):
    """build.py 고리: s 이름·기관·한 줄·형식·분류·지역을 붙인 글, ol 한 줄 설명, sm 요약(브라우저가 붙여서 함께 찾는다)"""
    return {'s': _norm(_hay_head(p)), 'ol': p.get('one_liner') or '', 'sm': p.get('summary') or ''}


def search_words(n=6):
    """머리 낱말 칩: 실제로 1건 이상 걸리는 말만. 이용 통계가 없으니 '인기'라고 부르지 않는다"""
    hays = [_norm(_hay_head(p)) + _norm(p.get('summary')) for p in programs]
    return [w for w in HERO_WORDS if any(_norm(w) in h for h in hays)][:n]


# ---------- 첫 화면 ----------
def home_lists():
    week = sorted((p for p in programs if _within(p, 7)), key=lambda p: (dday(p['next_deadline']), -_facts(p), p['name']))
    paid = sorted((p for p in programs if '돈받는교육' in p['kinds'] and p.get('money_monthly_max_manwon')
                   and not _money_partial(p) and (dday(p.get('next_deadline')) is None or dday(p.get('next_deadline')) >= 0)),
                  key=lambda p: (-p['money_monthly_max_manwon'], p['name']))
    anytime = sorted((p for p in programs if _always_open(p) and set(p['kinds']) & {'무료교육', '돈받는교육'} and _facts(p) >= 2),
                     key=lambda p: (-_facts(p), p['name']))
    return week, paid, anytime


HERO_DEMO_WORD = '지게차'  # 머리 그림(hero.svg) 돋보기 속이 지게차다. 다른 낱말로 바꾸면 그림과 어긋난다


def _spread(items, window=5):
    """카드 줄에서 같은 주제(같은 그림)가 몰리지 않게, 다음 window개 안에서 앞 카드와 주제가 다른 것을 먼저 놓는다.
    '돈 받으며 배우기'는 돈 순서대로면 인턴·일경험 제도 4개가 연달아 같은 사원증 그림이 된다(9/16). 첫 카드는 그대로 둔다"""
    rest, out = list(items), []
    while rest:
        prev = row_subject(out[-1]) if out else None
        j = next((i for i, p in enumerate(rest[:window]) if row_subject(p) != prev), 0)
        out.append(rest.pop(j))
    return out


def _hero_demo():
    """오른쪽 그림 아래 작은 결과 카드: 이름에 '지게차'가 든 제도 하나(DB 값 그대로). 없으면 카드를 빼고 그림만 둔다"""
    for w in [HERO_DEMO_WORD]:
        hit = sorted((p for p in programs if _norm(w) in _norm(p['name'])), key=lambda p: (-_facts(p), p['name']))
        if not hit:
            continue
        p = hit[0]
        bits = [KIND_LABEL[p['kinds'][0]]]
        if not _is_na(p):
            bits += (_dur_parts(p) or [])[:2]
        if p.get('cost_type') in COST_SHOW and '무료교육' not in p['kinds']:
            bits.append(f'내는 돈 {p["cost_type"]}')
        return (f'<div class="hx-demo"><p class="hd-q">{ico("search")}<span>‘{E(w)}’ 찾으면</span></p>'
                f'<p class="hd-t">{name_html(p["name"])}</p><p class="hd-m">{E(" · ".join(bits))}</p></div>')
    return ''


def _spark(cls):
    """네 갈래 반짝이(글자 색을 따른다)"""
    return (f'<svg class="hs {cls}" viewBox="-13 -13 26 26" aria-hidden="true" focusable="false">'
            '<path d="M0-12Q1.8-1.8 12 0Q1.8 1.8 0 12Q-1.8 1.8-12 0Q-1.8-1.8 0-12Z"/></svg>')


def _hero_deco():
    """포스터 꾸밈: 왼쪽 위 망점(CSS) + 띠 아래를 비스듬히 지나는 리본(분야 이름 반복). 장식이라 읽기 도구에는 숨긴다"""
    words = ''.join(f'<span>{E(label)}</span>{_spark("")}' for _, label in QUICK) + f'<span>지원금</span>{_spark("")}'
    return f'<div class="hx-deco" aria-hidden="true"><div class="hx-tape">{words * 3}</div></div>'


def _tile(h, key, label, v):
    """숫자 타일 한 칸(남색 카드): 위에 이름 >, 아래에 노란 큰 숫자, 오른쪽에 작은 선 그림"""
    art = ui_art(HERO_TILE_ART[key], 'ht-art', eager=True)
    return (f'<li><a class="hx-tile tk-{key}" href="{h}"><span class="ht-tx"><span class="ht-k">{E(label)}{ico("right")}</span>'
            f'<span class="ht-v"><b>{v}</b>개</span></span>{art}</a></li>')


def _hero(week_n):
    """첫 화면 머리: 파란 띠(오른쪽 사선 흰 면) · 큰 제목 · 네이버식 큰 검색창 · 찾아볼 낱말 · 공고 종이를 돋보기로 비추는 선 그림 · 리본 · 띠에 걸친 숫자 타일"""
    n_free = sum(1 for p in programs if '무료교육' in p['kinds'])
    n_paid = sum(1 for p in programs if '돈받는교육' in p['kinds'])
    words = search_words()
    chips = ''.join(f'<a class="hx-word" href="?q={urllib.parse.quote(w)}#finder-sec" data-q="{E(w)}">{E(w)}</a>' for w in words)
    words_html = f'<p class="hx-words"><span class="hx-words-k">이런 말로 찾아보세요</span>{chips}</p>' if chips else ''
    arts = (f'<img class="hx-pic" src="{{{{ROOT}}}}assets/img/ui-art/hero.svg" width="480" height="400" alt="" decoding="async">'
            f'<img class="hx-pic-m" src="{{{{ROOT}}}}assets/img/ui-art/hero-m.svg" width="240" height="200" alt="" decoding="async">')
    tiles_html = ''.join(_tile(*t) for t in [('{{ROOT}}c/free.html', 'free', '무료 교육', n_free),
                                             ('{{ROOT}}c/paid.html', 'paid', '돈 받으며 배우기', n_paid),
                                             ('#shelf', 'week', '7일 안에 마감', week_n)])
    return (f'<section class="hx" aria-labelledby="hero-h"><div class="hx-band">{_hero_deco()}<div class="hx-grid"><div class="hx-copy">'
            f'<p class="hx-kick">{TODAY.month}월 {TODAY.day}일 기준 · 제도 {len(programs)}개</p>'
            '<h1 id="hero-h">내 조건에 맞는<br><em class="hx-em">무료 교육·지원금</em> 찾기</h1>'
            '<form class="sx" id="sx" role="search" action="#finder-sec" method="get">'
            f'<div class="sx-box"><label class="sr" for="sx-q">제도 검색</label>{ico("search", "i sx-i")}'
            '<input id="sx-q" name="q" type="search" placeholder="지게차, 용접, 코딩…" autocomplete="off" spellcheck="false" '
            'enterkeyhint="search" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-controls="sx-list">'
            '<button class="sx-go" type="submit">검색</button></div>'
            '<ul class="sx-list" id="sx-list" role="listbox" aria-label="추천 제도" hidden></ul></form>'
            f'{words_html}<a class="hx-cond" href="#finder-sec">나이·사는 곳으로 찾기{ico("right")}</a></div>'
            f'<div class="hx-art" aria-hidden="true">{arts}{_hero_demo()}</div></div></div>'
            f'<ul class="hx-tiles tl-navy" aria-label="분류별 제도 수">{tiles_html}</ul></section>')


QUICK = [('it', 'IT·AI'), ('media', '영상·디자인'), ('tech', '기술·현장'), ('office', '사무·회계'),
         ('lang', '외국어'), ('service', '요리·서비스'), ('care', '돌봄·보건')]


def _quick():
    """분야 바로가기(당근·네이버식 둥근 색 칸). 자바스크립트가 없으면 주소 쿼리로 같은 거르기"""
    items = ''
    for s, label in QUICK:
        items += (f'<li><a class="fq-a" href="?field={s}#finder-sec" data-pick="field:{s}"><span class="fq-ic th" style="--t:{UI_ART["q-" + s]}">'
                  f'{ui_art("q-" + s, "fq-img", eager=True)}</span><span class="fq-t">{E(label)}</span></a></li>')
    items += (f'<li><a class="fq-a" href="?kind=grant#finder-sec" data-pick="kind:grant"><span class="fq-ic th" style="--t:{UI_ART["q-grant"]}">'
              f'{ui_art("q-grant", "fq-img", eager=True)}</span><span class="fq-t">지원금</span></a></li>')
    return f'<nav class="fq" aria-label="분야로 바로 찾기"><ul>{items}</ul></nav>'


def _notice():
    return (f'<aside class="notice"><div><p class="nt-t">{E(SITE)}는 정부·공공 기관 사이트가 아닙니다.</p>'
            '<p class="nt-s">여러 기관의 공고를 모아 요약한 민간 안내 사이트입니다. 신청은 각 기관의 공식 페이지에서 합니다.</p></div>'
            '<a class="btn-line sm" href="{{ROOT}}about.html">운영 방식 보기</a></aside>')


def _guide_band():
    by = {g['slug']: g for g in guides}
    items = ''
    for slug, n in GUIDE_CARDS:
        g = by.get(slug)
        if not g:
            continue
        items += (f'<li class="gb-card"><a href="{{{{ROOT}}}}g/{E(slug)}.html"><span class="gb-ico th" style="--t:{UI_ART[n]}">{ui_art(n, "gb-img")}</span>'
                  f'<span class="gb-t">{E(g["title"])}</span><span class="gb-d">{E(g["desc"])}</span>'
                  f'<span class="gb-more">자세히 보기{ico("right")}</span></a></li>')
    if not items:
        return ''
    return ('<section class="guide-band" aria-labelledby="gb-h"><div class="gb-top"><div>'
            '<h2 class="gb-h" id="gb-h">처음 알아본다면, 이것부터</h2>'
            '<p class="gb-s">신청 전에 많이 헷갈리는 기준을 짧게 정리했습니다.</p></div>'
            f'<a class="gb-all" href="{{{{ROOT}}}}g/index.html">안내 글 {len(guides)}편 모두 보기{ico("right")}</a></div>'
            f'<ul class="gb-cards">{items}</ul></section>')


_RQ = ('<form class="rq" role="search" onsubmit="return false"><label class="sr" for="f-q">제도 검색</label>' + ico('search') +
       '<input id="f-q" type="search" placeholder="제도 이름이나 배우고 싶은 것" autocomplete="off" spellcheck="false" enterkeyhint="search"></form>')


def _swap(body, old, new):
    if old not in body:
        raise SystemExit('A안 첫 화면 구조가 바뀌어 검색 칸을 끼울 수 없습니다: ' + old[:40])
    return body.replace(old, new, 1)


def home_body():
    week, paid, anytime = home_lists()
    body = _A_home_body()
    body = re.sub(r'<div class="home-head">.*?</div>\s*', '', body, count=1, flags=re.S)
    body = _swap(body, '<div class="picked picked-d" id="picked-d" hidden></div>', _RQ + '<div class="picked picked-d" id="picked-d" hidden></div>')
    body = _swap(body, '<ol class="res-list" id="res-list">', '<p class="res-guides" id="res-guides" hidden></p>\n    '
                 + ROW_PH_NOTE + '\n    <ol class="res-list" id="res-list">')
    body = _swap(body, '<p class="empty" id="res-empty" hidden>고른 조건에 맞는 제도가 없습니다. 조건을 하나씩 풀어 보세요.</p>',
                 '<div class="empty" id="res-empty" hidden><p>고른 조건에 맞는 제도가 없습니다. 조건을 하나씩 풀어 보세요.</p></div>')
    data = json.dumps({'guides': [{'s': g['slug'], 't': g['title'], 'd': g['desc']} for g in guides], 'words': search_words()},
                      ensure_ascii=False).replace('<', '\\u003c')
    # 마감 탭은 마감 순서가 내용이라 섞지 않는다
    sh = shelf('지금 눈여겨볼 제도', [('week', '7일 안에 마감', week[:12]), ('paid', '돈 받으며 배우기', _spread(paid[:12])),
                                   ('any', '언제든 신청', _spread(anytime[:12]))], 'shelf')
    # 광고: 넓은 화면은 머리 띠 아래부터 전체 목록까지 양옆 여백, 좁은 화면은 전체 목록을 다 본 뒤(안내 글 띠 앞) 하나
    return (_hero(len(week))
            + ad_rails(_quick() + sh + _notice()
                       + '<section class="finder-sec" id="finder-sec" aria-labelledby="finder-h"><div class="sec-h">'
                       + '<h2 id="finder-h">전체 제도에서 찾기</h2><p>검색하거나 조건을 고르면 신청할 수 있는 제도가 위로 올라옵니다.</p></div>'
                       + body + '</section>')
            + ad_end() + _guide_band() + f'<script>window.SX={data};</script>')


HOME_SCRIPTS = ('<script src="assets/programs.js"></script><script src="assets/dl.js"></script>'
                '<script src="assets/app.js"></script><script src="assets/search.js"></script>')

ROW_PH_NOTE = ('<p class="res-ph-note">사진은 무엇을 배우는지 보여 주는 분야 예시이며 기관 사진이 아닙니다. '
               '수당·취업 지원처럼 배우는 내용이 없는 제도는 그림으로 표시합니다.</p>')
_A_cat_body = cat_body


def cat_body(*a, **k):
    """분류 쪽 목록에도 같은 사진 안내 한 줄. 광고는 양옆 여백(넓은 화면) · 목록 끝(좁은 화면)"""
    body = _A_cat_body(*a, **k)
    body = _swap(body, '<ol class="res-list cat-list">', ROW_PH_NOTE + '<ol class="res-list cat-list">')
    end = body.rindex('</ol>') + len('</ol>')
    return ad_rails(body[:end] + ad_end() + body[end:])


_A_cat_index_body = cat_index_body


def cat_index_body(cat_links):
    """분류 모음 쪽: 읽는 글이 아니라 끝자리 광고는 두지 않고 넓은 화면 양옆만"""
    return ad_rails(_A_cat_index_body(cat_links))


_EMOJI_RE = re.compile('\\s*[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200D]+')


def credits_html():
    """사진 출처. 그림은 이 사이트용으로 따로 그린 것이라 출처 줄이 없다(이모지 그림은 9/16에 모두 뺐다).
    사진가 이름에 붙은 이모지(예: 'Bulat843 🌙')도 화면에 이모지로 나오므로 이름 글자만 남긴다"""
    return _EMOJI_RE.sub('', _B_credits_html())


PRIVACY_SINCE = '2026년 9월 19일'  # 내용을 바꾸면 시행일도 바꾼다


def privacy_body():
    """개인정보처리방침: 이 사이트가 직접 받는 정보는 문의 양식(contact_url, 구글 설문지)에 이용자가 적어 보낸 것뿐이다.
    광고 사업자의 행태정보 수집과 거부 방법, 외부 서비스를 적는다.
    사실과 맞아야 한다 — 고른 조건만 localStorage에 저장(app.js, 검색어는 빼고), 방문 통계 도구 없음, 글꼴은 jsDelivr,
    설문지는 메일 주소를 자동으로 모으지 않고(설정 '수집하지 않음') 답장받을 메일 칸은 선택"""
    form = cfg.get('contact_url')
    intro = ('회원 가입과 로그인이 없고, 문의 양식에 스스로 적어 보낸 내용 말고는 이름·연락처 같은 개인 정보를 받지 않습니다.'
             if form else '회원 가입과 로그인이 없고, 이름·연락처 같은 개인 정보를 직접 받지 않습니다.')
    contact = (f'<h2>문의 양식</h2><p>문의는 <a href="{E(form)}" target="_blank" rel="noopener">문의 양식</a>(Google 설문지)으로 받습니다. '
               '보내 주신 내용과, 답장을 원할 때 적은 메일 주소는 답장과 사이트를 고치는 데만 쓰고 다른 곳에 넘기지 않으며, 처리를 마치면 지웁니다. '
               '양식은 Google LLC가 운영하므로, 보내는 과정에는 '
               '<a href="https://policies.google.com/privacy?hl=ko" target="_blank" rel="noopener">Google의 개인 정보 처리 방침</a>도 적용됩니다.</p>'
               '<p>보낸 문의를 지워 달라는 요청과 개인 정보에 관한 그 밖의 문의도 같은 양식으로 받아 운영자가 직접 처리합니다.</p>'
               if form else '')
    return f'''<article class="prose">
<header class="g-head"><h1>개인 정보 처리 방침</h1><p class="g-meta">시행일 {PRIVACY_SINCE}</p></header>
<div class="g-body">
<p>{E(SITE)}는 {intro}</p>
<h2>이 사이트가 처리하는 정보</h2>
<p>첫 화면에서 고른 나이·사는 곳·학력 같은 조건은 서버로 보내지 않습니다. 다음에 들어왔을 때 다시 쓰도록 이용자 브라우저의 저장 공간(localStorage)에만 남기고, 검색어는 남기지 않습니다. 브라우저에서 사이트 데이터를 지우면 함께 지워집니다.</p>
<p>방문자 수를 세는 통계 도구는 쓰지 않습니다.</p>
<h2>광고와 쿠키</h2>
<p>이 사이트에는 카카오 애드핏(주식회사 카카오)과 Google 애드센스(Google LLC) 광고가 실릴 수 있습니다. 광고 사업자는 이용자에게 맞는 광고를 보여 주려고 쿠키나 광고 식별자로 웹사이트 방문 기록 같은 행태 정보를 자동으로 수집할 수 있습니다. 이 정보는 각 광고 사업자가 자기 방침에 따라 처리하며, 이 사이트 운영자에게는 전달되지 않습니다.</p>
<ul>
<li>수집하는 곳: 주식회사 카카오, Google LLC</li>
<li>수집 항목: 쿠키, 광고 식별자, 방문한 쪽 주소 같은 방문 기록</li>
<li>수집 방법: 이 사이트의 쪽을 열 때 광고 스크립트가 자동으로 수집</li>
</ul>
<p>맞춤 광고는 끌 수 있습니다. 카카오는 <a href="https://info.ad.daum.net/optoutko.do" target="_blank" rel="noopener">카카오 맞춤형 광고 안내</a>, Google은 <a href="https://adssettings.google.com" target="_blank" rel="noopener">Google 광고 설정</a>에서 설정합니다. Google이 광고 파트너 사이트에서 정보를 쓰는 방식은 <a href="https://policies.google.com/technologies/partner-sites?hl=ko" target="_blank" rel="noopener">Google 안내</a>에 있습니다. 브라우저 설정에서 쿠키를 막거나 지울 수도 있습니다.</p>
<h2>외부 서비스</h2>
<ul>
<li>호스팅: 이 사이트는 GitHub Pages에서 제공됩니다. GitHub는 보안과 운영을 위해 접속 IP 주소 같은 기록을 남길 수 있습니다.</li>
<li>글꼴: Pretendard 글꼴을 jsDelivr에서 받아 오며, 이때 접속 IP 주소가 jsDelivr에 전달될 수 있습니다.</li>
</ul>
<h2>바뀌는 경우</h2>
<p>이 방침이 바뀌면 이 쪽에 새 시행일과 함께 알립니다.</p>
{contact}
</div>
</article>'''


# ---------- 상세(내일배움캠프 과정 상세 구성: 색 띠 머리 → 큰 숫자 칸 → 본문 → 아래 고정 신청 줄) ----------
def _sentences(t):
    # 숫자 뒤 마침표('2008.12.31. 출생')에서는 나누지 않는다
    return [x.strip().rstrip('.') for x in re.split(r'(?<!\d)\.\s+|;\s*|\n+', (t or '').strip()) if x.strip(' .')]


# 본문은 핵심만 한눈에(9/17 사용자: '공고에 나이 조건 없음'을 보고 "나이 - 조건 없음, 이런 식으로. 너무 주저리주저리, 핵심만 딱딱 한눈에").
# 칸에는 짧은 값만 두고, 설명 문장·그 밖의 조건·돈과 기간 상세는 눌러서 펼치게 한다.
EDU_SHORT = {'제한없음': '조건 없음', '확인필요': '공고 확인', '기타': '따로 있음',
             '고졸이상': '고졸 이상', '대졸이상': '대졸 이상', '대학재학': '대학 재학생'}
INC_SHORT = {'제한없음': '조건 없음', '기준있음': '기준 있음', '확인필요': '공고 확인'}
# '신청자격에 학력 조건 없음(학력 '제한없음' 표기)'처럼 값을 되풀이할 뿐인 괄호
_RESTATE_PAREN = re.compile(r"\((?:학력|소득)?\s*'?제한\s*없음'?\s*표기\)|\(학력\s*요건\s*제한\s*없음\)")


def _only_says_none(note):
    """'신청자격에 소득 조건 없음'처럼 '없다'는 말뿐인 설명인가. 괄호·문장이 더 붙으면(예: '(카드 발급자 대상)',
    '. 대학생은 졸업학기생만 가능') 조건이 들어 있을 수 있어서 남긴다"""
    t = _RESTATE_PAREN.sub('', note).strip()
    return len(t) <= 25 and '(' not in t and '. ' not in t and re.search(r'없음|무관|누구나', t) is not None


def _elig_rows(p):
    age = age_text(p)
    age = '조건 없음' if age == '공고에 나이 조건 없음' else ('공고 확인' if age.startswith('나이 제한 있음') else age)
    rows = [('나이', E(age))]
    if p.get('target_groups'):
        rows.append(('대상', E(', '.join(p['target_groups'])) + '만'))
    rows += [('사는 곳', E('전국' if '전국' in p['regions'] else region_text(p) + ' 주민')),
             ('학력', E(EDU_SHORT.get(p['education'], p['education']))),
             ('가구 소득', E(INC_SHORT[p['income']]))]
    works = [('구직자', p['allow_job_seeker']), ('재직자', p['allow_employed']), ('사업자', p['allow_business']), ('학생', p['allow_student'])]
    ws = ''
    for v, lbl, cls in (('가능', '가능', 'ok'), ('확인필요', '확인 필요', 'warn'), ('불가', '불가', 'no')):
        names = [n for n, x in works if x == v]
        if names:
            ws += f'<span class="ws"><b class="mk {cls}">{lbl}</b> {E(" · ".join(names))}</span>'
    rows.append(('일 상태', ws))
    return rows


def _more_conditions(p):
    """접어 둘 '그 밖의 조건': 조건이 담긴 학력·소득 설명 + 그 밖의 조건 문장"""
    items = []
    for key, val_key, label in (('education_note', 'education', '학력'), ('income_note', 'income', '소득')):
        note = (p.get(key) or '').strip()
        if note and not (p[val_key] == '제한없음' and _only_says_none(note)):
            items.append(f'{label}: {note}')
    return items + _sentences(p.get('other_conditions'))


def _prog_inner(p):
    kv = lambda rows: '<ul class="kv">' + ''.join(f'<li><span class="k">{k}</span><span class="v">{v}</span></li>' for k, v in rows) + '</ul>'
    more = _more_conditions(p)
    more_html = (f'<details class="src p-more"><summary>그 밖의 조건 {len(more)}개 보기</summary>'
                 f'<ul class="bul">{"".join(f"<li>{_tx(x)}</li>" for x in more)}</ul></details>') if more else ''

    detail = [('받는 돈', _tx(p.get('money'))), ('내는 돈', _tx(p.get('cost')))]
    du = p.get('duration') or {}
    if duration_label(p) is not None:
        parts = _dur_parts(p)
        v = E(' · '.join(parts)) if parts else '<span class="dim">공고에 적혀 있지 않음</span>'
        extra = [x for x in (f'교육 날짜 {du["dates_text"]}' if du.get('dates_text') else '',
                             f'수업 시간 {du["hours_text"]}' if du.get('hours_text') else '') if x]
        if extra:
            v += f'<span class="note">{E(" · ".join(extra))}</span>'
        if du.get('quote'):
            v += f'<span class="note">공고 표현 “{E(du["quote"])}”</span>'
        detail.append(('교육 기간', v))
    if p.get('schedule') not in (None, '', '해당없음', '확인필요'):
        detail.append(('일정', E(SCHED_SHOW.get(p['schedule'], p['schedule']))))
    detail += [('방식', _tx(p.get('format'))), ('모집', _tx(p.get('recruit')))]

    quotes = ''.join(
        f'<li><blockquote>{E(s["quote"])}</blockquote><a href="{E(s["url"])}" target="_blank" rel="noopener">{E(urlparse(s["url"]).netloc or s["url"])}</a></li>'
        for s in p['sources'][:3])
    return f'''<p class="lede">{E(p["summary"])}</p>
  <section class="sec"><h2>누가 신청할 수 있나</h2>{kv(_elig_rows(p))}{more_html}</section>
  <section class="sec sec-more">
    <details class="src p-more"><summary>돈·기간·모집 자세히 보기</summary>{kv(detail)}</details>
    <details class="src"><summary>공고에서 옮긴 문장 {len(p["sources"][:3])}개 보기</summary><ol class="quotes">{quotes}</ol></details>
    <p class="checked">확인일 {E(p["checked_at"])} · 조건은 해마다 바뀔 수 있습니다.</p>
  </section>'''


def program_body(p):
    inner = _prog_inner(p)

    first_kind = p['kinds'][0]
    kinds_txt = ' · '.join(KIND_LABEL[k] for k in p['kinds'])
    pills = ''.join(f'<span class="p-pill">{E(KIND_LABEL[k])}</span>' for k in p['kinds'])
    if p.get('apply_url'):
        cta = (f'<a class="btn-primary" href="{E(p["apply_url"])}" target="_blank" rel="noopener">신청 페이지 열기</a>'
               f'<a class="btn-ghost" href="{E(p["official_url"])}" target="_blank" rel="noopener">공식 안내 보기</a>')
    else:
        cta = f'<a class="btn-primary" href="{E(p["official_url"])}" target="_blank" rel="noopener">공식 안내 보기</a>'
    href = p.get('apply_url') or p['official_url']
    sticky_label = '신청 페이지' if p.get('apply_url') else '공식 안내'

    # 큰 숫자 칸: 내는 돈 · 받는 돈
    m, partial = _money_value(p)
    ct = p.get('cost_type')
    money_bits = ''
    if ct in COST_SHOW:
        money_bits += f'<p class="pc-lb">내는 돈</p><p class="pc-big">{E(ct)}</p>'
    elif ct == '확인필요':
        money_bits += '<p class="pc-lb">내는 돈</p><p class="pc-big dim">공고 확인</p>'
    if m:
        note = ''
        if partial:
            src = (p.get('money') or '') + (p.get('money_short') or '')
            note = f'<p class="note">{"일반 선발자는 받는 돈 없음" if PRIORITY_RE.search(src) else "대부분은 받는 돈 없음"}</p>'
        money_bits += f'<p class="pc-lb">받는 돈</p><p class="pc-big money">{E(m)}</p>{note}'

    # 핵심 칸: 교육 기간 · 수업 · 마감 · 대상
    facts = []
    if not _is_na(p):
        parts = _dur_parts(p)
        v = E(' · '.join(parts)) if parts else '<span class="dim">공고 확인</span>'
        dates = (p.get('duration') or {}).get('dates_text')
        if dates:
            v += f'<small>{E(dates)}</small>'
        facts.append(('cal', '교육 기간', v))
    sched = SCHED_SHOW.get(p.get('schedule'))
    if sched:
        facts.append(('laptop', '수업', E(sched)))
    facts.append(('clock', '마감', _dl_html(p, 'span', 'dlv') or '<span class="dim">공고에서 확인</span>'))
    who = [_age_short(p)] + ([', '.join(p['target_groups'])] if p.get('target_groups') else []) + \
          ['전국' if '전국' in p['regions'] else region_short(p) + ' 주민']
    facts.append(('user', '대상', E(' · '.join(who))))
    facts_html = ''.join(f'<li>{ico(i)}<span class="k">{k}</span><span class="v">{v}</span></li>' for i, k, v in facts)
    cards = (f'<section class="pc pc-money" aria-label="돈">{money_bits}</section>' if money_bits else '') + \
            f'<section class="pc pc-facts" aria-label="핵심 정보"><ul>{facts_html}</ul></section>'
    one = '' if money_bits else ' one'

    rel = related(p)
    rel_html = shelf('비슷한 제도', [('rel', '비슷한 제도', _spread(rel[:8]))], 'rel') if rel else ''
    # 광고: 파란 머리 띠 아래 본문부터 비슷한 제도까지 양옆 여백(넓은 화면), 좁은 화면은 본문을 다 읽은 뒤 하나
    body_html = f'''<article class="prog">
  <p class="p-note">민간 안내 사이트가 공고를 요약한 내용입니다. 신청 전에 공식 안내를 확인하세요.</p>
  {inner}
</article>
{ad_end(p)}
{rel_html}'''

    return f'''<div class="p-hero"><div class="p-hero-in">
  <nav class="crumb" aria-label="위치"><a href="{{{{ROOT}}}}index.html">찾기</a><span aria-hidden="true">›</span><a href="{{{{ROOT}}}}c/{KIND_SLUG[first_kind]}.html">{E(KIND_LABEL[first_kind])}</a></nav>
  <p class="p-pills">{pills}</p>
  <h1>{name_html(p["name"], split_tail=True)}</h1>
  <p class="p-org">{name_html(p["operator"])}</p>
  <div class="cta">{cta}</div>
</div></div>
<div class="p-cards{one}">{cards}</div>
{ad_rails(body_html, p)}
<div class="sticky-cta" id="sticky-cta"><div class="sc-in"><p class="sc-t">{name_html(p["name"])}<span class="sc-k">{E(kinds_txt)}</span></p><a class="btn-primary" href="{E(href)}" target="_blank" rel="noopener">{sticky_label}</a></div></div>
<script src="{{{{ROOT}}}}assets/dl.js" defer></script>'''


# ---------- 안내 글: '읽는 데 약 N분'은 넣지 않는다(사용자 요청) ----------
def guide_body(g):
    ph = GUIDE_PHOTO.get(g['slug'])
    cover = f'<figure class="g-cover">{photo(ph, "(max-width: 720px) 100vw, 680px", "169", eager=True)}{photo_cap(ph)}</figure>' if ph else ''
    # 광고는 본문 사이에 넣지 않는다: 넓은 화면은 양옆 여백, 좁은 화면은 글을 다 읽은 뒤
    return ad_rails(f'<nav class="crumb prose-w" aria-label="위치"><a href="{{{{ROOT}}}}g/index.html">안내 글</a></nav>'
                    f'<article class="prose"><header class="g-head"><h1>{E(g["title"])}</h1>'
                    f'<p class="g-meta">갱신 {E(g.get("updated", TODAY.isoformat()))}</p></header>'
                    f'{cover}<div class="g-body">{g["body_html"]}</div></article>' + ad_end())


def guide_index_body():
    items = ''
    for g in guides:
        ph = GUIDE_PHOTO.get(g['slug'])
        thumb = photo(ph, "(max-width: 860px) 112px, 200px", "32") if ph else '<span></span>'
        items += (f'<li><a class="g-row" href="{E(g["slug"])}.html"><span class="g-tx"><span class="g-title">{E(g["title"])}</span>'
                  f'<span class="g-desc">{E(g["desc"])}</span></span>{thumb}</a></li>')
    return ad_rails(f'<header class="page-head"><h1>안내 글</h1><p class="page-lead">제도를 고를 때 알아 둘 기준</p></header>'
                    f'<ul class="glist">{items or "<li>준비 중입니다.</li>"}</ul>')
