(function () {
  var form = document.getElementById('finder');
  if (!form) return;
  var P = window.PROGRAMS || [];
  var SIDO = window.SIDO || {};
  var SX = window.SX || { guides: [], words: [] };
  var $ = function (id) { return document.getElementById(id); };
  var list = $('res-list');
  var rows = {};
  Array.prototype.forEach.call(list.querySelectorAll('.row'), function (li) { rows[li.getAttribute('data-id')] = li; });
  var countEl = $('res-count');
  var emptyEl = $('res-empty');
  var emptyDefault = emptyEl.innerHTML;
  var emptyLast = emptyDefault;
  var moreBtn = $('res-more');
  var showNo = $('f-showno');
  var toggleNo = $('toggle-no');
  var shownoT = $('showno-t');
  var soonBtn = $('soon-btn');
  var resSub = $('res-sub');
  var sortSel = $('f-sort');
  var ageEl = $('f-age');
  var ageBad = $('age-bad');
  var regionEl = $('f-region');
  var qEl = $('f-q');
  var heroQ = $('sx-q');
  var guidesEl = $('res-guides');
  var side = $('side');
  var dlg = $('fdlg');
  var dlgBody = $('fdlg-body');
  var openBtn = $('open-f');
  var applyMain = $('apply-main');
  var applySub = $('apply-sub');
  var pickedBoxes = [$('picked'), $('picked-d')];
  var resTop = $('res-top');
  var mq = window.matchMedia('(max-width: 860px)');

  var EDU = { mid: 0, hs: 1, uni: 2, grad: 3 };
  var INC = { '60': [0, 60], '100': [60, 100], '150': [100, 150], 'over': [150, 9999] };
  var WORK = { job: '구직자', emp: '재직자', biz: '사업자', stu: '학생' };
  var TG = { dis: '장애인', nk: '북한 이탈 주민', vet: '제대 군인·보훈', inj: '산재 근로자', women: '여성', mig: '결혼 이민자·다문화', care: '자립 준비 청년', oos: '학교 밖 청소년', farm: '농어업인', low: '기초 생활 수급자·차상위' };
  var KEY = 'bj-proto-d';
  var PAGE = 40;
  var limit = PAGE;
  var naOpen = false;

  // ---------- 글자 검색: 띄어쓰기·기호를 뺀 글에서 낱말을 모두 찾는다(theme.py _norm과 같은 규칙) ----------
  function norm(t) { return String(t || '').toLowerCase().replace(/[\s·ㆍ\-–—_()\[\]{}<>,.\/:;~!?"'‘’“”「」『』]+/g, ''); }
  var CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ';
  function chosung(t) {
    var out = '';
    for (var i = 0; i < t.length; i++) {
      var c = t.charCodeAt(i) - 0xAC00;
      out += (c >= 0 && c < 11172) ? CHO.charAt(Math.floor(c / 588)) : t.charAt(i);
    }
    return out;
  }
  // 같은 뜻 낱말: 짧게 유지한다(넓은 말은 넣지 않는다)
  var SYN = {
    '코딩': ['프로그래밍', '개발자', '소프트웨어'], '프로그래밍': ['코딩', '개발자', '소프트웨어'],
    'ai': ['인공지능'], '인공지능': ['ai'], '유튜브': ['영상'], '요리': ['조리', '제과', '제빵'], '조리': ['요리'],
    '포크리프트': ['지게차'], '포크레인': ['굴착기', '굴삭기'], '굴삭기': ['굴착기'], '컴활': ['컴퓨터활용'],
    '빅데이터': ['데이터'], '웹개발': ['웹', '프론트엔드', '백엔드']
  };
  P.forEach(function (p) { p._n = norm(p.n); p._o = norm(p.ol); p._h = (p.s || '') + norm(p.sm); p._c = norm(chosung(p.n)); });

  function tokens(q) {
    return String(q || '').trim().split(/\s+/).map(function (raw) {
      var n = norm(raw);
      if (!n) return null;
      var cho = /^[ㄱ-ㅎ]+$/.test(n);
      return { raw: raw, cho: cho, alts: [n].concat((SYN[n] || []).map(norm)) };
    }).filter(Boolean);
  }
  // 모든 낱말이 걸려야 0보다 크다. 낱말마다 이름 3 · 한 줄 설명 2 · 그 밖 1
  function score(p, toks) {
    var total = 0;
    for (var i = 0; i < toks.length; i++) {
      var t = toks[i], best = 0;
      for (var j = 0; j < t.alts.length; j++) {
        var a = t.alts[j];
        if (t.cho) { if (p._c.indexOf(a) >= 0) best = 3; continue; }
        if (p._n.indexOf(a) >= 0) best = Math.max(best, 3);
        else if (p._o.indexOf(a) >= 0) best = Math.max(best, 2);
        else if (p._h.indexOf(a) >= 0) best = Math.max(best, 1);
      }
      if (!best) return 0;
      total += best;
    }
    return total;
  }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function reEsc(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  // 글자 사이에 띄어쓰기·가운뎃점이 끼어도 걸리는 정규식 조각: '일학습병행'으로 찾아도 '일·학습 병행'을 칠한다(캡처 묶음 없음)
  function loose(w) { return norm(w).split('').map(reEsc).join('[\\s·ㆍ\\-–—_]*'); }
  function marked(text, toks) {
    var words = [];
    toks.forEach(function (t) { if (!t.cho) { words.push(t.raw); (SYN[norm(t.raw)] || []).forEach(function (a) { words.push(a); }); } });
    words = words.filter(function (w) { return norm(w); });
    if (!words.length) return esc(text);
    words.sort(function (a, b) { return norm(b).length - norm(a).length; });
    var re = new RegExp('(' + words.map(loose).join('|') + ')', 'gi');
    return String(text).split(re).map(function (part, i) { return i % 2 ? '<mark>' + esc(part) + '</mark>' : esc(part); }).join('');
  }
  // 제목에 없는 낱말이 있으면, 그 낱말이 든 한 줄 설명이나 요약 문장을 보여 준다
  function snippet(p, toks) {
    var need = toks.filter(function (t) { return !t.cho && !t.alts.some(function (a) { return p._n.indexOf(a) >= 0; }); });
    if (!need.length) return '';
    // 숫자 뒤 마침표('2008.12.31. 출생')에서는 문장을 나누지 않는다(옛 사파리가 못 읽는 뒤보기 정규식 대신 치환)
    var pieces = [p.ol || ''].concat(String(p.sm || '').replace(/(\D)\.\s+/g, '$1\u0001').split('\u0001'));
    for (var i = 0; i < pieces.length; i++) {
      var s = pieces[i], h = norm(s);
      if (!s || !need.some(function (t) { return t.alts.some(function (a) { return h.indexOf(a) >= 0; }); })) continue;
      if (s.length > 90) {
        var at = -1;
        need.forEach(function (t) { t.alts.forEach(function (a) { var m = new RegExp(loose(a), 'i').exec(s), k = m ? m.index : -1; if (k >= 0 && (at < 0 || k < at)) at = k; }); });
        var from = Math.max(0, at - 30);
        s = (from ? '…' : '') + s.substr(from, 80) + '…';
      }
      return marked(s, toks);
    }
    return '';
  }
  function paintRow(li, p, toks) {
    var a = li.querySelector('.r-title a');
    if (a) {
      // 이름은 괄호 설명을 옅게 따로 싼 구조(theme.py name_html)라, 통째로 바꾸지 않고 글자 조각마다 칠한다
      if (!a.hasAttribute('data-h')) a.setAttribute('data-h', a.innerHTML);
      if (a.hasAttribute('data-m')) { a.innerHTML = a.getAttribute('data-h'); a.removeAttribute('data-m'); }
      if (toks.length) {
        var walk = document.createTreeWalker(a, NodeFilter.SHOW_TEXT), texts = [], tn;
        while ((tn = walk.nextNode())) texts.push(tn);
        texts.forEach(function (t) {
          var s = document.createElement('span');
          s.innerHTML = marked(t.nodeValue, toks);
          t.parentNode.replaceChild(s, t);
        });
        a.setAttribute('data-m', '');
      }
    }
    var sn = li.querySelector('.r-snip');
    var html = toks.length ? snippet(p, toks) : '';
    if (html) {
      if (!sn) {
        sn = document.createElement('p');
        sn.className = 'r-snip';
        li.querySelector('.r-title').insertAdjacentElement('afterend', sn);
      }
      sn.innerHTML = html;
    } else if (sn) sn.parentNode.removeChild(sn);
  }
  function syncHero() { if (heroQ && document.activeElement !== heroQ) heroQ.value = qEl ? qEl.value : ''; }

  function checked(name) {
    return Array.prototype.map.call(form.querySelectorAll('input[name="' + name + '"]:checked'), function (i) { return i.value; });
  }
  function radio(name) { var v = checked(name); return v.length ? v[0] : ''; }
  function labelOf(input) {
    var l = input.closest('label');
    var t = l && l.querySelector('.t');
    return t ? t.textContent : input.value;
  }

  function readState() {
    var raw = ageEl.value.trim();
    var age = parseInt(raw, 10);
    var bad = raw !== '' && (isNaN(age) || age < 10 || age > 99);
    ageBad.hidden = !bad;
    ageEl.setAttribute('aria-invalid', bad ? 'true' : 'false');
    return {
      q: qEl ? qEl.value.trim() : '',
      kind: checked('kind'), field: checked('field'), tg: checked('tg'), du: checked('du'),
      age: (isNaN(age) || bad) ? null : age,
      region: regionEl.value,
      edu: radio('edu'), work: radio('work'), inc: radio('inc'),
      sort: sortSel.value, no: showNo.checked
    };
  }

  function writeState(s) {
    form.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(function (i) {
      if (i.name === 'kind' || i.name === 'field' || i.name === 'tg' || i.name === 'du') i.checked = (s[i.name] || []).indexOf(i.value) >= 0;
      else if (i.type === 'radio') i.checked = (s[i.name] || '') === i.value;
    });
    ageEl.value = s.age == null ? '' : s.age;
    regionEl.value = s.region || '';
    sortSel.value = s.sort && sortSel.querySelector('option[value="' + s.sort + '"]') ? s.sort : 'rec';
    showNo.checked = !!s.no;
    if (qEl) qEl.value = s.q || '';
    syncHero();
  }

  // 주소 쿼리는 들어 있는 키만 저장된 조건 위에 덮어쓴다(분류 쪽 '내 조건으로 좁혀 보기'가 나이·지역을 지우지 않게)
  function fromQuery() {
    var q = new URLSearchParams(location.search);
    if (!Array.from(q.keys()).length) return null;
    var o = {};
    if (q.has('q')) o.q = q.get('q') || '';
    ['kind', 'field', 'tg', 'du'].forEach(function (k) { if (q.has(k)) o[k] = (q.get(k) || '').split(',').filter(Boolean); });
    if (q.has('age')) { var a = parseInt(q.get('age'), 10); o.age = isNaN(a) ? null : a; }
    ['region', 'edu', 'work', 'inc', 'sort'].forEach(function (k) { if (q.has(k)) o[k] = q.get(k) || ''; });
    if (q.has('no')) o.no = q.get('no') === '1';
    return o;
  }
  function toQuery(s) {
    var q = new URLSearchParams();
    if (s.q) q.set('q', s.q);
    ['kind', 'du', 'field', 'tg'].forEach(function (k) { if (s[k].length) q.set(k, s[k].join(',')); });
    if (s.age != null) q.set('age', s.age);
    ['region', 'edu', 'work', 'inc'].forEach(function (k) { if (s[k]) q.set(k, s[k]); });
    if (s.sort && s.sort !== 'rec') q.set('sort', s.sort);
    if (s.no) q.set('no', '1');
    var str = q.toString();
    return str ? '?' + str : location.pathname.split('/').pop();
  }

  // 조건 판정: src/app.js와 같은 규칙(바꾸지 않는다)
  function check(p, s) {
    var fails = [], unk = [];
    if (s.age != null) {
      if (p.a0 != null && s.age < p.a0) fails.push('만 ' + p.a0 + '세 이상');
      else if (p.a1 != null && s.age > p.a1) fails.push('만 ' + p.a1 + '세 이하');
      else if (p.au && p.a0 == null && p.a1 == null) unk.push('나이');
    }
    if (p.tg && p.tg.length && !p.tg.some(function (t) { return s.tg.indexOf(t) >= 0; })) {
      fails.push(p.tg.map(function (t) { return TG[t]; }).join('·') + ' 대상');
    }
    if (s.region) {
      var name = SIDO[s.region];
      var whole = p.r.some(function (r) { return r === '전국' || r === name; });
      var part = p.r.some(function (r) { return r.indexOf(name + ' ') === 0; });
      var places = p.r.length > 3 ? p.r.slice(0, 3).join(', ') + ' 등 ' + p.r.length + '곳' : p.r.join(', ');
      if (!whole && !part) fails.push(places + ' 주민');
      else if (!whole && part) unk.push(places + '만 해당');
    }
    if (s.edu) {
      var u = EDU[s.edu];
      if (p.ed === 'hs' && u < 1) fails.push('고졸 이상');
      else if (p.ed === 'uni' && u !== 2) fails.push('대학 재학생');
      else if (p.ed === 'grad' && u < 3) fails.push('대졸 이상');
      else if (p.ed === 'etc' || p.ed === 'unk') unk.push('학력');
    }
    if (s.work) {
      var v = p.w[s.work];
      if (v === 'n') fails.push(WORK[s.work] + ' 참여 불가');
      else if (v !== 'y') unk.push(WORK[s.work] + ' 참여');
    }
    if (s.inc) {
      if (p.inc === 'yes') {
        if (p.ip == null) unk.push('가구 소득');
        else {
          var b = INC[s.inc];
          if (b[0] >= p.ip) fails.push('기준 중위 소득 ' + p.ip + '% 이하');
          else if (b[1] > p.ip) unk.push('가구 소득');
        }
      } else if (p.inc === 'unk') unk.push('가구 소득');
    }
    return { fails: fails, unk: unk, st: fails.length ? 'no' : (unk.length ? 'check' : 'ok') };
  }

  // 행에 붙이는 판정 글자는 짧게: 이유를 항목 이름 하나로 줄인다(나이는 '만 34세 이하'처럼 짧아서 그대로)
  function reasonLabel(r) {
    if (/^만 \d+세/.test(r)) return r;
    if (r === '나이') return '나이';
    if (/ 대상$/.test(r)) return '대상';
    if (/ 주민$|만 해당$/.test(r)) return '사는 곳';
    if (/^(고졸 이상|대학 재학생|대졸 이상|학력)$/.test(r)) return '학력';
    if (/참여/.test(r)) return '일 상태';
    if (/소득/.test(r)) return '가구 소득';
    return r;
  }

  var today = new Date(); today.setHours(0, 0, 0, 0);
  function dday(d) {
    if (!d) return null;
    var t = new Date(d + 'T00:00:00');
    return Math.round((t - today) / 86400000);
  }

  var ST_TEXT = { ok: '조건 맞음', check: '확인 필요', no: '안 맞음' };
  // 0번 묶음(고른 기간에 맞는 교육)은 머리 줄 '기간 맞는 교육 N개'가 대신하므로 묶음 제목을 따로 달지 않는다
  var GROUP_TEXT = ['고른 기간에 맞는 교육', '과정마다 다르거나 시간으로 적힌 교육', '기간이 공고에 없는 교육', '교육 기간이 없는 지원 제도'];

  function render(keepLimit) {
    if (!keepLimit) limit = PAGE;
    var s = readState();
    var toks = tokens(s.q);
    var any = s.age != null || s.region || s.edu || s.work || s.inc || s.tg.length;
    var byDu = s.du.length > 0;
    if (!byDu) naOpen = false;
    var ORDER = { ok: 0, check: 1, no: 2 };
    var items = [];
    var n = { ok: 0, check: 0, no: 0 };
    P.forEach(function (p) {
      var li = rows[p.id];
      if (!li) return;
      var sc = toks.length ? score(p, toks) : 0;
      var show = (!toks.length || sc > 0) &&
        (!s.kind.length || p.k.some(function (k) { return s.kind.indexOf(k) >= 0; })) &&
        (!s.field.length || p.f.indexOf('all') >= 0 || p.f.some(function (f) { return s.field.indexOf(f) >= 0; }));
      var g = 0;
      var dk = li.getAttribute('data-dk');
      if (show && byDu) {
        var du = p.du || [];
        if (du.some(function (d) { return s.du.indexOf(d) >= 0; })) g = 0;
        else if (du.length) show = false;
        else g = dk === 'na' ? 3 : (dk === 'unknown' ? 2 : 1);
      }
      if (!show) { li.hidden = true; li.className = 'row'; return; }
      paintRow(li, p, toks);
      var c = any ? check(p, s) : { fails: [], unk: [], st: 'ok' };
      n[c.st]++;
      var st = li.querySelector('.r-st');
      li.className = 'row st-' + c.st;
      if (st) {
        if (!any) { st.hidden = true; st.removeAttribute('title'); }
        else {
          var why = c.st === 'no' ? c.fails : c.unk;
          var labs = [];
          why.forEach(function (r) { var l = reasonLabel(r); if (labs.indexOf(l) < 0) labs.push(l); });
          st.hidden = false;
          st.className = 'r-st ' + c.st;
          st.textContent = ST_TEXT[c.st] + (labs.length ? ' · ' + labs[0] + (labs.length > 1 ? ' 외 ' + (labs.length - 1) : '') : '');
          if (why.length) st.title = why.join(', '); else st.removeAttribute('title');
        }
      }
      li.hidden = c.st === 'no' && !s.no;
      var dd = dday(p.dl);
      var open = li.getAttribute('data-open') === '1';
      var cls, ddr;
      if (dd != null && dd >= 0) { ddr = dd; cls = dd <= 3 ? 1 : 0; }
      else if (open) { ddr = 9999; cls = 0; }
      else { ddr = 99999; cls = 2; }
      items.push({ li: li, p: p, st: c.st, g: g, dd: ddr, cls: cls, sc: sc, fx: +li.getAttribute('data-fx') || 0 });
    });
    var byName = function (a, b) { return a.p.n.localeCompare(b.p.n, 'ko'); };
    items.sort(function (a, b) {
      if (a.g !== b.g) return a.g - b.g;
      if (ORDER[a.st] !== ORDER[b.st]) return ORDER[a.st] - ORDER[b.st];
      if (s.sort === 'money') return (b.p.m || 0) - (a.p.m || 0) || byName(a, b);
      if (s.sort === 'name') return byName(a, b);
      if (s.sort === 'deadline') return a.dd - b.dd || (b.p.m || 0) - (a.p.m || 0) || byName(a, b);
      if (a.sc !== b.sc) return b.sc - a.sc;   // 검색어가 이름에 든 제도부터
      return a.cls - b.cls || b.fx - a.fx || a.dd - b.dd || (b.p.m || 0) - (a.p.m || 0) || byName(a, b);
    });

    // 묶음 세기와 접기: '교육 기간이 없는 지원 제도'는 원하는 것에 지원금·창업을 고르지 않았으면 접힌 한 줄로
    var visible = items.filter(function (it) { return !it.li.hidden; });
    var gc = [0, 0, 0, 0], g0 = { ok: 0, check: 0 };
    visible.forEach(function (it) { gc[it.g]++; if (it.g === 0 && g0[it.st] != null) g0[it.st]++; });
    var wantsGrant = s.kind.indexOf('grant') >= 0 || s.kind.indexOf('startup') >= 0;
    var fold = byDu && gc[3] > 0 && !wantsGrant && !naOpen;
    if (fold) visible.forEach(function (it) { if (it.g === 3) it.li.hidden = true; });
    var listed = visible.filter(function (it) { return !it.li.hidden; });

    Array.prototype.forEach.call(list.querySelectorAll('.grp'), function (x) { x.parentNode.removeChild(x); });
    items.forEach(function (it) { list.appendChild(it.li); });
    listed.forEach(function (it, i) { if (i >= limit) it.li.classList.add('cut'); else it.li.classList.remove('cut'); });
    // 행 사진: 바로 위 행과 같은 사진이면 <template>에 둔 대신 쓸 사진과 맞바꾼다(theme.py row)
    var prevPh = null;
    listed.forEach(function (it) {
      var box = it.li.querySelector('.r-ph'), tpl = it.li.querySelector('template.r-ph-alt');
      if (box && tpl && box.getAttribute('data-ph') === prevPh) {
        var html = box.innerHTML, name = box.getAttribute('data-ph');
        box.innerHTML = tpl.innerHTML;
        box.setAttribute('data-ph', tpl.getAttribute('data-ph'));
        tpl.innerHTML = html;
        tpl.setAttribute('data-ph', name);
      }
      prevPh = box ? box.getAttribute('data-ph') : null;
    });

    if (byDu) {
      [0, 1, 2, 3].forEach(function (g) {
        if (!gc[g] || g === 0) return;
        var h = document.createElement('li');
        h.className = 'grp';
        if (g === 3 && fold) {
          var firstHidden = null;
          for (var j = 0; j < items.length; j++) if (items[j].g === 3) { firstHidden = items[j]; break; }
          h.className = 'grp grp-fold' + (listed.length > limit ? ' cut' : '');
          var b = document.createElement('button');
          b.type = 'button';
          b.className = 'grp-btn';
          b.textContent = GROUP_TEXT[3] + ' ' + gc[3] + '개 펼치기';
          b.addEventListener('click', function () { naOpen = true; render(true); });
          h.appendChild(b);
          list.insertBefore(h, firstHidden.li);
          return;
        }
        var first = null;
        for (var i = 0; i < listed.length; i++) if (listed[i].g === g) { first = listed[i]; break; }
        if (!first) return;
        if (first.li.classList.contains('cut')) h.className += ' cut';
        h.textContent = GROUP_TEXT[g];
        var cnt = document.createElement('span');
        cnt.textContent = gc[g] + '개';
        h.appendChild(cnt);
        list.insertBefore(h, first.li);
      });
    }

    var rest = listed.length - limit;
    moreBtn.hidden = rest <= 0;
    if (rest > 0) moreBtn.textContent = Math.min(PAGE, rest) + '개 더 보기(남은 ' + rest + '개)';

    var qLabel = toks.length ? '<span class="cn-q">‘' + esc(s.q) + '’</span> ' : '';
    if (byDu) countEl.innerHTML = qLabel + '기간 맞는 교육 <b>' + gc[0] + '</b>개' + (any ? ' <span class="cn-sub">조건 맞음 ' + g0.ok + ' · 확인 필요 ' + g0.check + '</span>' : '');
    else if (toks.length) countEl.innerHTML = qLabel + '검색 결과 <b>' + listed.length + '</b>개' + (any ? ' <span class="cn-sub">조건 맞음 ' + n.ok + ' · 확인 필요 ' + n.check + '</span>' : '');
    else if (any) countEl.innerHTML = '조건 맞음 <b>' + n.ok + '</b>개 <span class="cn-sub">확인 필요 ' + n.check + '개</span>';
    else countEl.innerHTML = '제도 <b>' + listed.length + '</b>개';

    var isEmpty = listed.length === 0 && !(fold && gc[3] > 0);
    emptyEl.hidden = !isEmpty;
    var emptyHtml = emptyDefault;
    if (isEmpty && toks.length) {
      var narrowed = any || s.kind.length || s.field.length || byDu;
      emptyHtml = '<p><b>‘' + esc(s.q) + '’</b> 검색 결과가 없습니다.' + (narrowed ? ' 고른 조건을 풀어 보거나 다른 말로 찾아보세요.' : ' 다른 말로 찾아보세요.') + '</p>' +
        (SX.words.length ? '<p class="em-words">' + SX.words.map(function (w) { return '<button type="button" class="em-w" data-q="' + esc(w) + '">' + esc(w) + '</button>'; }).join('') + '</p>' : '') +
        '<button type="button" class="linkbtn" data-q="">검색어 지우기</button>';
    }
    if (emptyHtml !== emptyLast) { emptyEl.innerHTML = emptyHtml; emptyLast = emptyHtml; }

    // 관련 안내 글: 검색어가 제목·설명에 모두 든 글 3편까지
    if (guidesEl) {
      var gs = toks.length ? SX.guides.filter(function (g) {
        var h = norm(g.t + ' ' + g.d);
        return toks.every(function (t) { return !t.cho && t.alts.some(function (a) { return h.indexOf(a) >= 0; }); });
      }).slice(0, 3) : [];
      guidesEl.hidden = !gs.length;
      guidesEl.innerHTML = gs.length ? '<span class="rg-k">관련 안내 글</span>' + gs.map(function (g) {
        return '<a href="g/' + encodeURIComponent(g.s) + '.html">' + marked(g.t, toks) + '</a>';
      }).join('') : '';
    }

    toggleNo.hidden = !any;
    shownoT.textContent = n.no ? '안 맞는 ' + n.no + '개도 보기' : '안 맞는 것도 보기';
    var soon = listed.filter(function (it) { return it.cls === 1; }).length;
    soonBtn.hidden = s.sort === 'deadline' || !soon;
    soonBtn.textContent = '3일 안에 마감 ' + soon + '개 먼저 보기';
    resSub.hidden = toggleNo.hidden && soonBtn.hidden;

    // 고른 조건 칩(모바일은 버튼 아래 한 줄, 데스크톱은 결과 위)
    var chips = [];
    function add(label, clear, cls) { chips.push({ label: label, clear: clear, cls: cls }); }
    function boxes(name) {
      form.querySelectorAll('input[name="' + name + '"]:checked').forEach(function (i) { add(labelOf(i), function () { i.checked = false; }); });
    }
    function radios(name) {
      var i = form.querySelector('input[name="' + name + '"]:checked');
      if (i && i.value) add(labelOf(i), function () { form.querySelector('input[name="' + name + '"][value=""]').checked = true; });
    }
    if (toks.length) add('‘' + s.q + '’', function () { qEl.value = ''; syncHero(); }, 'pick-q');
    boxes('kind'); boxes('du');
    if (s.age != null) add('만 ' + s.age + '세', function () { ageEl.value = ''; });
    if (s.region) add(SIDO[s.region], function () { regionEl.value = ''; });
    radios('edu'); radios('work'); radios('inc'); boxes('tg'); boxes('field');
    pickedBoxes.forEach(function (box) {
      if (!box) return;
      box.innerHTML = '';
      chips.forEach(function (c) {
        var b = document.createElement('button');
        b.type = 'button';
        b.className = 'pick' + (c.cls ? ' ' + c.cls : '');
        b.setAttribute('aria-label', c.label + (c.cls === 'pick-q' ? ' 검색어 지우기' : ' 조건 빼기'));
        var t = document.createElement('span');
        t.textContent = c.label;
        var x = document.createElement('span');
        x.className = 'pick-x';
        x.setAttribute('aria-hidden', 'true');
        x.textContent = '×';
        b.appendChild(t); b.appendChild(x);
        b.addEventListener('click', function () {
          c.clear(); render();
          var next = box.querySelector('.pick');
          (next || (mq.matches ? openBtn : form.querySelector('input'))).focus();
        });
        box.appendChild(b);
      });
      if (chips.length > 1) {
        var r = document.createElement('button');
        r.type = 'button'; r.className = 'linkbtn pick-clear'; r.textContent = '모두 지우기';
        r.addEventListener('click', function () { if (qEl) qEl.value = ''; syncHero(); form.reset(); });
        box.appendChild(r);
      }
      box.hidden = !chips.length;
    });
    var nCond = chips.filter(function (c) { return c.cls !== 'pick-q'; }).length;
    openBtn.textContent = nCond ? '조건 고르기(' + nCond + '개 선택됨)' : '조건 고르기';
    if (byDu) {
      applyMain.textContent = gc[0] + '개 보기';
      var other = listed.length - gc[0];
      applySub.hidden = other <= 0;
      applySub.textContent = '기간을 따로 확인할 제도 ' + other + '개는 그 아래에';
    } else {
      applyMain.textContent = listed.length + '개 보기';
      applySub.hidden = true;
    }

    // 접힌 묶음 요약값
    form.querySelectorAll('[data-val]').forEach(function (el) {
      var name = el.getAttribute('data-val');
      var sel = [];
      form.querySelectorAll('input[name="' + name + '"]:checked').forEach(function (i) { if (i.value) sel.push(labelOf(i)); });
      el.textContent = sel.length ? (sel.length > 2 ? sel.slice(0, 2).join(', ') + ' 외 ' + (sel.length - 2) : sel.join(', ')) : '상관없음';
      el.classList.toggle('on', sel.length > 0);
    });
    document.querySelectorAll('.tile[data-kind]').forEach(function (t) {
      t.setAttribute('role', 'button');
      t.setAttribute('aria-pressed', s.kind.indexOf(t.getAttribute('data-kind')) >= 0 ? 'true' : 'false');
    });

    syncUrl(s);
    // 검색어는 저장하지 않는다(다시 왔을 때 목록이 이유 없이 줄어 있지 않게)
    try { var save = JSON.parse(JSON.stringify(s)); delete save.q; localStorage.setItem(KEY, JSON.stringify(save)); } catch (e) {}
  }
  function syncUrl(s) {
    try { history.replaceState(history.state, '', toQuery(s || readState())); } catch (e) {}
  }

  // 전체 화면 패널: 열 때 조건 폼을 패널로 옮기고 닫을 때 되돌린다. 안드로이드 뒤로가기로 닫히게 history 한 칸을 쓴다
  var scrollAfterClose = false;
  function openPanel() {
    dlgBody.appendChild(form);
    if (dlg.showModal) dlg.showModal(); else dlg.setAttribute('open', '');
    document.documentElement.classList.add('dlg-open');
    try { history.pushState({ bjDlg: 1 }, '', location.href); } catch (e) {}
  }
  function closePanel() { if (dlg.open) { if (dlg.close) dlg.close(); else { dlg.removeAttribute('open'); onClose(); } } }
  function afterClose() {
    syncUrl();
    if (scrollAfterClose && resTop) {
      scrollAfterClose = false;
      requestAnimationFrame(function () { resTop.scrollIntoView({ block: 'start' }); openBtn.focus({ preventScroll: true }); });
    }
  }
  function onClose() {
    side.appendChild(form);
    document.documentElement.classList.remove('dlg-open');
    if (history.state && history.state.bjDlg) { try { history.back(); } catch (e) { afterClose(); } }
    else afterClose();
  }
  window.addEventListener('popstate', function () {
    if (dlg.open) closePanel();
    else afterClose();
  });
  dlg.addEventListener('close', onClose);
  openBtn.addEventListener('click', openPanel);
  $('fdlg-close').addEventListener('click', closePanel);
  $('fdlg-reset').addEventListener('click', function () { form.reset(); });
  $('fdlg-apply').addEventListener('click', function () { scrollAfterClose = true; closePanel(); });
  var onMq = function () { if (!mq.matches) closePanel(); };
  if (mq.addEventListener) mq.addEventListener('change', onMq); else if (mq.addListener) mq.addListener(onMq);

  // 입구 사진: 누르면 '원하는 것'을 켜고 끈다(여러 개)
  function toggleKind(t) {
    var box = form.querySelector('input[name="kind"][value="' + t.getAttribute('data-kind') + '"]');
    if (!box) return;
    box.checked = !box.checked;
    render();
  }
  document.addEventListener('click', function (e) {
    var t = e.target.closest && e.target.closest('.tile[data-kind]');
    if (!t) return;
    e.preventDefault();
    toggleKind(t);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== ' ') return;
    var t = e.target.closest && e.target.closest('.tile[data-kind]');
    if (!t) return;
    e.preventDefault();
    toggleKind(t);
  });

  function setQuery(v) { if (!qEl) return; qEl.value = v || ''; syncHero(); render(); }
  // 분야 바로가기: 그 분야 하나만 고르고 검색어는 비운다(나이·사는 곳은 그대로)
  function pick(name, value) {
    form.querySelectorAll('input[name="' + name + '"]').forEach(function (i) { i.checked = i.value === value; });
    if (qEl) qEl.value = '';
    syncHero();
    render();
  }
  if (qEl) qEl.addEventListener('input', function () { syncHero(); render(); });
  emptyEl.addEventListener('click', function (e) {
    var b = e.target.closest('[data-q]');
    if (!b) return;
    setQuery(b.getAttribute('data-q'));
    if (qEl) qEl.focus();
  });
  window.BJ = { P: P, tokens: tokens, score: score, marked: marked, esc: esc, setQuery: setQuery, pick: pick };

  var init = null;
  try { init = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { init = null; }
  if (init) delete init.q;
  var q = fromQuery();
  if (q) { init = init || {}; Object.keys(q).forEach(function (k) { init[k] = q[k]; }); }
  if (init) writeState(init);

  form.addEventListener('change', function () { render(); });
  form.addEventListener('input', function (e) { if (e.target === ageEl) render(); });
  form.addEventListener('reset', function () { setTimeout(render, 0); });
  showNo.addEventListener('change', function () { render(); });
  sortSel.addEventListener('change', function () { render(); });
  soonBtn.addEventListener('click', function () { sortSel.value = 'deadline'; render(); });
  moreBtn.addEventListener('click', function () { limit += PAGE; render(true); });
  render();
})();
