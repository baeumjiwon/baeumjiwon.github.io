"""카드용 핵심 필드(교육 기간·일정·비용 유형·받는 돈 요약·한 줄 설명)를 검사하고 db/programs.json에 합친다.

python tools/merge_card_fields.py [--src 파일 ...]           # 검사 보고만
python tools/merge_card_fields.py [--src 파일 ...] --apply   # DB에 기록
python tools/merge_card_fields.py --selftest                  # 경계 사례 검사

입력: research/card_fields/verified*.json (card-fields-extract 워크플로 반환 items). 같은 id가 여러 파일에 있으면 뒤 파일이 이긴다.
원칙
- 기간 숫자는 원문 인용 안에 글자 그대로 있어야 받는다. 날짜 범위의 일수·구간(하루·단기·중기·장기)은 여기 코드가 센다.
- 시간만 공개된 과정은 구간을 붙이지 않는다("총 100시간"). 주 2회 저녁 12주 과정이 '단기'로 보이는 오류를 막는다.
  인용문에 교육 날짜 범위가 있으면 그 날짜로 구간을 매긴다.
- "N 이상", "최장 N"은 원문 표현 그대로 쓰고 구간을 붙이지 않는다.
- 칸 하나가 검사에 걸리면 그 칸만 비운다(기간은 unknown). 나머지 칸은 살린다.
"""
import datetime
import glob
import html
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, 'db', 'programs.json')
SRC_GLOB = os.path.join(BASE, 'research', 'card_fields', 'verified*.json')

KINDS = {'fixed', 'range', 'varies', 'self_paced', 'unknown', 'not_applicable'}
UNITS = {'시간', '일', '주', '개월', '년'}
SCHEDULES = {'주간', '야간·주말', '온라인', '혼합', '과정마다 다름', '확인필요', '해당없음'}
COSTS = {'무료', '일부 자부담', '확인필요', '해당없음'}
DAYS = {'일': 1, '주': 7, '개월': 30, '년': 365}
# 한 줄 설명에 넣지 않는 숫자: 금액·날짜·기간·인원·비율 (다른 칸에 따로 나온다). "1인", "3D"는 괜찮다
ONE_LINER_NUM = re.compile(r'\d[\d,.]*\s*(만\s*원|원|개월|년|월|일|주|시간|명|%|기|회|차)')
MONTH_SPAN = re.compile(r'(?:(\d{4}|\d{2})\s*(?:\.|년)\s*)?(\d{1,2})\s*월\s*~\s*(?:(\d{4}|\d{2})\s*(?:\.|년)\s*)?(\d{1,2})\s*월')
MIXED_RANGE = re.compile(r'(\d+(?:\.\d+)?)\s*(일|주|개월|년)\s*~\s*(\d+(?:\.\d+)?)\s*(일|주|개월|년)')
_Y = r"(?:(\d{4})\s*(?:\.|년)\s*|[’'‘`](\d{2})\s*\.\s*)"
_MD = r"(\d{1,2})\s*(?:\.|월)\s*(\d{1,2})\s*(?:\.|일)?\s*(?:\([^)]{1,4}\))?"
DATE_RANGE = re.compile(_Y + '?' + _MD + r'\s*~\s*' + _Y + '?' + _MD)


def num_text(v):
    return str(int(v)) if float(v).is_integer() else str(v)


def in_quote(v, quote):
    return re.search(r'(?<![\d.])' + re.escape(num_text(v)) + r'(?![\d])', quote.replace(',', '')) is not None


def band_days(days):
    if days <= 1:
        return '하루'
    if days <= 31:
        return '단기'
    if days <= 183:
        return '중기'
    return '장기'


def human_span(days):
    if days <= 1:
        return '하루'
    if days <= 13:
        return f'{days}일'
    if days <= 59:
        return f'약 {round(days / 7)}주'
    return f'약 {round(days / 30.4)}개월'


def months_between(start, end):
    y1, m1 = map(int, start.split('-')[:2])
    y2, m2 = map(int, end.split('-')[:2])
    return (y2 * 12 + m2) - (y1 * 12 + m1) + 1


def month_span_from_quote(q):
    m = MONTH_SPAN.search(q or '')
    if not m:
        return None
    y1, m1, y2, m2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
    if not y1 or not (1 <= m1 <= 12 and 1 <= m2 <= 12):
        return None
    y1 = int(y1) + (2000 if len(y1) == 2 else 0)
    y2 = int(y2) + (2000 if y2 and len(y2) == 2 else 0) if y2 else (y1 if m2 >= m1 else y1 + 1)
    if (y2, m2) < (y1, m1):
        return None
    return f'{y1:04d}-{m1:02d}', f'{y2:04d}-{m2:02d}'


def date_range_from_quote(q, default_year):
    """인용문 속 첫 교육 날짜 범위 → (YYYY-MM-DD, YYYY-MM-DD). 연도가 없으면 default_year, 끝이 앞서면 다음 해."""
    for m in DATE_RANGE.finditer(q or ''):
        y1 = m.group(1) or (f'20{m.group(2)}' if m.group(2) else None)
        y2 = m.group(5) or (f'20{m.group(6)}' if m.group(6) else None)
        try:
            y1 = int(y1) if y1 else default_year
            s = datetime.date(y1, int(m.group(3)), int(m.group(4)))
            e = datetime.date(int(y2) if y2 else y1, int(m.group(7)), int(m.group(8)))
            if e < s and not y2:
                e = e.replace(year=e.year + 1)
        except ValueError:
            continue
        if e >= s and (e - s).days < 800:
            return s.isoformat(), e.isoformat()
    return None


def hours_text(lo, hi, open_ended=False):
    g = lambda v: f'{int(v):,}' if float(v).is_integer() else str(v)  # 화면 글은 천 단위 쉼표('1,000시간')
    if lo is None and hi is None:
        return ''
    if open_ended:
        return f'{g(lo)}시간 이상'
    if lo is None or lo == hi:
        return f'총 {g(hi if lo is None else lo)}시간'
    return f'총 {g(lo)}~{g(hi)}시간'


def finish(d):
    """band(구간)·text(카드용 길이)·dates_text·hours_text를 채운다."""
    k = d['kind']
    d.update(band='', text='', dates_text='', hours_text=hours_text(d['hours_min'], d['hours_max'], d.pop('_hours_open', False)))
    if k == 'varies':
        d['band'] = '과정마다 다름'
        return d
    if k == 'self_paced':
        d['band'] = '자유 수강'
        return d
    if k not in ('fixed', 'range'):
        return d
    if d['start'] and d['end']:
        if len(d['start']) == 7:
            d['band'] = band_days(d['days_min'])
            d['text'] = f'{int(d["start"][5:7])}월~{int(d["end"][5:7])}월'
            d['dates_text'] = d['text']
        else:
            s, e = datetime.date.fromisoformat(d['start']), datetime.date.fromisoformat(d['end'])
            d['band'] = band_days(d['days_min'])
            d['dates_text'] = f'{s.month}.{s.day}' if s == e else f'{s.month}.{s.day}~{e.month}.{e.day}'
            d['text'] = d['dates_text'] if s == e else human_span(d['days_min'])
        return d
    if d['unit'] == '' or d['unit'] == '시간':  # 시간만 있음: 구간 없음
        d['text'] = d['hours_text']
        return d
    lo, hi, u = d['min'], d['max'], d['unit']
    if lo is not None and d['days_max'] is not None:
        a, b = band_days(d['days_min']), band_days(d['days_max'])
        d['band'] = a if a == b else f'{a}~{b}'
        if hi is not None and lo == hi:
            d['text'] = f'{num_text(lo)}{u}'
        elif d.get('max_text'):  # 단위가 다른 범위: "6개월~1년"
            d['text'] = f'{num_text(lo)}{u}~{d["max_text"]}'
        else:
            d['text'] = f'{num_text(lo)}~{num_text(hi)}{u}'
        if d['band'] == '하루' and d['text'] == '1일':
            d['text'] = ''
    elif lo is not None:
        d['text'] = f'{num_text(lo)}{u} 이상'
    else:
        d['text'] = f'최장 {num_text(hi)}{u}'
    return d


def build_duration(it, default_year):
    """(duration dict, 오류 목록). 오류가 있으면 kind=unknown으로 낮춘다."""
    kind = it['duration_kind']
    q = it.get('duration_quote') or ''
    d = {'kind': kind, 'min': None, 'max': None, 'unit': '', 'start': '', 'end': '', 'days_min': None, 'days_max': None,
         'hours_min': None, 'hours_max': None, 'quote': q, 'source': it.get('duration_source') or 'none',
         'source_url': html.unescape(it.get('duration_source_url') or '')}
    errs = []
    if kind not in KINDS:
        errs.append(f'duration_kind {kind!r}')
    elif kind in ('fixed', 'range'):
        if not q:
            errs.append('기간 인용문 없음')
        sd, ed = it.get('start_date') or '', it.get('end_date') or ''
        lo, hi, u = it.get('value_min'), it.get('value_max'), it.get('unit') or ''
        if sd and ed:
            try:
                if datetime.date.fromisoformat(ed) < datetime.date.fromisoformat(sd):
                    errs.append('end_date < start_date')
                d.update(start=sd, end=ed)
            except ValueError:
                errs.append('날짜 형식')
        elif lo is not None or hi is not None:
            if u not in UNITS:
                errs.append(f'단위 {u!r}')
            elif lo is not None and hi is not None and lo > hi:
                errs.append('min > max')
            elif lo is None and kind != 'range':
                errs.append('fixed인데 min 없음')
            else:
                for v in (lo, hi):
                    if v is not None and not in_quote(v, q):
                        errs.append(f'숫자 {num_text(v)}가 인용문에 없음')
            if not errs and u == '시간':
                d.update(hours_min=lo, hours_max=hi, _hours_open=(kind == 'range' and hi is None))
                span = date_range_from_quote(q, default_year)
                if span:
                    d.update(start=span[0], end=span[1])
            elif not errs:
                d.update(min=lo, max=hi, unit=u)
                d['days_min'] = lo * DAYS[u] if lo is not None else None
                d['days_max'] = hi * DAYS[u] if hi is not None else None
                if kind == 'range' and hi is None and lo is not None:
                    m = MIXED_RANGE.search(q)
                    if m and float(m.group(1)) == float(lo) and m.group(2) == u:
                        d['days_max'] = float(m.group(3)) * DAYS[m.group(4)]
                        d['max_text'] = f'{num_text(float(m.group(3)))}{m.group(4)}'
                if lo is None:  # "최장 N": 필터에서는 N 하나로 본다
                    d['days_min'] = d['days_max']
        else:
            span = date_range_from_quote(q, default_year) or month_span_from_quote(q)
            if span:
                d.update(start=span[0], end=span[1])
            else:
                errs.append('기간 숫자·날짜 없음')
        if not errs and d['start'] and d['end']:
            if len(d['start']) == 7:
                d['days_min'] = d['days_max'] = months_between(d['start'], d['end']) * 30
            else:
                d['days_min'] = d['days_max'] = (datetime.date.fromisoformat(d['end']) - datetime.date.fromisoformat(d['start'])).days + 1
    if errs:
        d.update(kind='unknown', min=None, max=None, unit='', start='', end='', days_min=None, days_max=None, hours_min=None, hours_max=None)
        d.pop('_hours_open', None)
    return finish(d), errs


def load_items(paths):
    got = {}
    for path in paths:
        for it in json.load(open(path, encoding='utf-8')):
            got[it['id']] = it
    return got


def selftest():
    def item(kind, lo=None, hi=None, unit='', q='', sd='', ed=''):
        return {'duration_kind': kind, 'value_min': lo, 'value_max': hi, 'unit': unit, 'duration_quote': q, 'start_date': sd, 'end_date': ed}
    cases = [
        # (항목, 기대 band, 기대 text)
        (item('fixed', 100, 100, '시간', "북부 청년 용접사(야간) '26.10.1.~12.24. 화,목 18:30~21:40(100시간)"), '중기', '약 3개월'),
        (item('fixed', 100, 100, '시간', '단계별 100시간 한국어 교육'), '', '총 100시간'),
        (item('fixed', 2, 2, '시간', '온라인 금융교육 2시간'), '', '총 2시간'),
        (item('range', 6, None, '개월', '모집시기 교육기간 매년 11월 중 · 6개월 ~ 1년'), '중기~장기', '6개월~1년'),
        (item('range', 20, None, '시간', '20시간 이상'), '', '20시간 이상'),
        (item('range', None, 18, '개월', '최장 18개월간 일경험을 쌓는'), '', '최장 18개월'),
        (item('range', 3, None, '개월', '3 개월 (350 시간 ) 이상의 직업훈련'), '', '3개월 이상'),
        (item('range', 5, 6, '개월', '주간 5개월 야간 6개월'), '중기', '5~6개월'),
        (item('fixed', 10, 10, '개월', '약 10개월 동안 진행'), '장기', '10개월'),
        (item('fixed', sd='2026-08-18', ed='2026-12-11', q="교육기간 : '26.8.18.~12.11."), '중기', '약 4개월'),
        (item('fixed', sd='2026-09-15', ed='2026-09-15', q='9.15.(화) 9시~16시'), '하루', '9.15'),
        (item('fixed', 1, 1, '일', '1일(8시간) 수업'), '하루', ''),
        (item('fixed', q='o 교육기간 - 2026.6월 ~2026.11월'), '중기', '6월~11월'),
        (item('fixed', 120, 120, '시간', '2026년 10월 14일(수) ~ 11월 11일(수) 주 5일(평일), 10:00~17:00 (1일 6시간, 총 120시간)'), '단기', '약 4주'),
        (item('fixed', 48, 48, '시간', '▶교육기간 : 2026.10.02.(금)~10.23.(금) [총 8일 1일 6h 총 48h]'), '단기', '약 3주'),
        (item('fixed', 7, 7, '개월', '교육기간 2026.09.29~2027.04.28 7개월(960시간)'), '장기', '7개월'),
    ]
    bad = 0
    for it, band, text in cases:
        d, errs = build_duration(it, 2026)
        ok = d['band'] == band and d['text'] == text and not errs
        bad += not ok
        print('OK ' if ok else 'BAD', repr(it['duration_quote'][:40]), '→', repr(d['band']), repr(d['text']), d['days_min'], d['days_max'], errs or '')
    print('실패', bad)
    return bad == 0


def main():
    if '--selftest' in sys.argv:
        sys.exit(0 if selftest() else 1)
    apply = '--apply' in sys.argv
    paths = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == '--src'] or sorted(glob.glob(SRC_GLOB))
    raw = open(DB, encoding='utf-8').read()
    programs = json.loads(raw)
    by_id = {p['id']: p for p in programs}
    got = load_items(paths)
    print('입력 파일', [os.path.basename(p) for p in paths])

    merged, problems, bands, uncertain = {}, [], {}, []
    for pid, it in got.items():
        p = by_id.get(pid)
        if not p:
            problems.append((pid, ['DB에 없는 id']))
            continue
        errs = []
        year = int((p.get('checked_at') or '2026')[:4])
        d, derr = build_duration(it, year)
        errs += [f'기간: {e}' for e in derr]
        schedule = it.get('schedule') if it.get('schedule') in SCHEDULES else '확인필요'
        cost_type = it.get('cost_type') if it.get('cost_type') in COSTS else '확인필요'
        if schedule != it.get('schedule'):
            errs.append(f'schedule {it.get("schedule")!r}')
        if cost_type != it.get('cost_type'):
            errs.append(f'cost_type {it.get("cost_type")!r}')
        ol = (it.get('one_liner') or '').strip()
        if len(ol) > 28 or ONE_LINER_NUM.search(ol):
            errs.append(f'한 줄 설명 비움({len(ol)}자) {ol}')
            ol = ''
        ms = (it.get('money_short') or '').strip()
        money = (p.get('money') or '').replace(',', '')
        bad_num = [n for n in re.findall(r'\d[\d,.]*', ms) if n.replace(',', '') not in money]
        if len(ms) > 18 or bad_num:
            errs.append(f'받는 돈 요약 비움 {ms} (money 원문: {p.get("money", "")[:40]})')
            ms = ''
        if it.get('verdict') == 'uncertain':
            uncertain.append(pid)
        if errs:
            problems.append((pid, errs))
        merged[pid] = {'one_liner': ol, 'duration': d, 'schedule': schedule, 'cost_type': cost_type, 'money_short': ms}
        key = d['band'] or (f'({d["kind"]})' if not d['text'] else '(구간 없음: ' + ('시간' if '시간' in d['text'] else '이상/최장') + ')')
        bands[key] = bands.get(key, 0) + 1

    missing = [i for i in by_id if i not in got]
    print(f'DB {len(programs)}건 · 결과 {len(merged)}건 · 칸 일부를 비운 건 {len(problems)} · 검증자가 확인 못 함(uncertain) {len(uncertain)}')
    if missing:
        print('결과 없는 id', len(missing), missing[:12])
    print('기간 구간', dict(sorted(bands.items(), key=lambda x: -x[1])))
    for pid, errs in problems:
        print('  ', pid, (by_id.get(pid) or {}).get('name', ''), '·', '; '.join(errs))

    if apply:
        for pid, m in merged.items():
            by_id[pid].update(m)
        text = json.dumps(programs, ensure_ascii=False, indent=1)
        was_same = json.dumps(json.loads(raw), ensure_ascii=False, indent=1) == raw.rstrip('\n')
        open(DB, 'w', encoding='utf-8').write(text + ('\n' if raw.endswith('\n') else ''))
        print('DB 기록', len(merged), '건', '(기존 서식 유지)' if was_same else '(원본 서식과 다름 — git diff 확인)')


if __name__ == '__main__':
    main()
