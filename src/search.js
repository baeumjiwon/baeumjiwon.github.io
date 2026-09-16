/* D안 첫 화면 검색창: 글자 칠 때마다 추천 목록(네이버식), 찾아볼 낱말, 분야 바로가기. app.js가 만든 window.BJ를 쓴다 */
(function () {
  var BJ = window.BJ;
  var form = document.getElementById('sx');
  if (!BJ || !form) return;
  var input = document.getElementById('sx-q');
  var list = document.getElementById('sx-list');
  var mq = window.matchMedia('(max-width: 860px)');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var KIND = { free: '무료 교육', paid: '배우면서 돈 받기', grant: '지원금', exam: '자격증 응시료', startup: '창업 지원' };
  var MAX = 6;
  var opts = [], active = -1, timer = null;
  var today = new Date(); today.setHours(0, 0, 0, 0);

  function ddText(d) {
    if (!d) return '';
    var n = Math.round((new Date(d + 'T00:00:00') - today) / 86400000);
    return n < 0 ? '' : (n === 0 ? '오늘 마감' : '마감 D-' + n);
  }
  // 제도 이름: 괄호 앞뒤를 띄우고 괄호 속은 옅게(theme.py name_html과 같은 규칙)
  function nameHtml(n, toks) {
    return n.split(/(\s*[(（][^()（）]+[)）]\s*)/).map(function (part, i) {
      return i % 2 ? ' <span class="nm-p">' + BJ.marked(part.trim(), toks) + '</span> ' : BJ.marked(part, toks);
    }).join('').trim();
  }
  function close() {
    list.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    input.removeAttribute('aria-activedescendant');
    active = -1;
  }
  function setActive(i) {
    active = i;
    opts.forEach(function (o, j) { o.classList.toggle('on', i === j); o.setAttribute('aria-selected', i === j ? 'true' : 'false'); });
    if (i >= 0) { input.setAttribute('aria-activedescendant', opts[i].id); opts[i].scrollIntoView({ block: 'nearest' }); }
    else input.removeAttribute('aria-activedescendant');
  }
  function build() {
    var q = input.value.trim();
    if (!q) { list.innerHTML = ''; opts = []; close(); return; }
    var toks = BJ.tokens(q);
    var hits = BJ.P.map(function (p) { return { p: p, sc: BJ.score(p, toks) }; })
      .filter(function (h) { return h.sc > 0; })
      .sort(function (a, b) { return b.sc - a.sc || a.p.n.localeCompare(b.p.n, 'ko'); });
    var html;
    if (!hits.length) {
      html = '<li class="sx-none" role="option" id="sx-o-0" data-act="all" aria-selected="false">‘' + BJ.esc(q) + '’ 검색 결과가 없습니다. <span>Enter를 누르면 비슷한 말을 보여 드립니다.</span></li>';
    } else {
      html = '<li class="sx-all" role="option" id="sx-o-0" data-act="all" aria-selected="false"><svg class="i" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>' +
        '<span><b>‘' + BJ.esc(q) + '’</b> 제도 ' + hits.length + '개 모두 보기</span></li>';
      hits.slice(0, MAX).forEach(function (h, i) {
        var p = h.p;
        var kind = p.k.map(function (k) { return KIND[k]; }).filter(Boolean).join(' · ');
        var dd = ddText(p.dl);
        // 이름에 검색어가 없으면 한 줄 설명으로 왜 걸렸는지 보여 준다
        var why = h.sc < toks.length * 3 && p.ol ? '<span class="sx-w">' + BJ.marked(p.ol, toks) + '</span>' : '';
        html += '<li role="option" id="sx-o-' + (i + 1) + '" aria-selected="false" data-href="p/' + encodeURIComponent(p.id) + '.html">' +
          '<span class="sx-t">' + nameHtml(p.n, toks) + '</span>' + why +
          '<span class="sx-m">' + BJ.esc(kind) + (dd ? ' · <em>' + dd + '</em>' : '') + '</span></li>';
      });
    }
    list.innerHTML = html;
    opts = Array.prototype.slice.call(list.querySelectorAll('[role="option"]'));
    list.hidden = false;
    input.setAttribute('aria-expanded', 'true');
    setActive(-1);
  }
  function go() {
    close();
    BJ.setQuery(input.value.trim());
    if (mq.matches) input.blur();
    var target = document.getElementById(mq.matches ? 'res-top' : 'finder-sec');
    if (target) target.scrollIntoView({ block: 'start', behavior: reduce.matches ? 'auto' : 'smooth' });
  }
  function choose(i) {
    var o = opts[i];
    if (!o || o.getAttribute('data-act') === 'all') { go(); return; }
    location.href = o.getAttribute('data-href');
  }

  input.addEventListener('input', function () { clearTimeout(timer); timer = setTimeout(build, 80); });
  input.addEventListener('focus', function () { if (input.value.trim()) build(); });
  input.addEventListener('blur', function () { setTimeout(close, 120); });
  input.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (list.hidden) build();
      if (opts.length) setActive(Math.min(active + 1, opts.length - 1));
    } else if (e.key === 'ArrowUp') {
      if (list.hidden) return;
      e.preventDefault();
      setActive(Math.max(active - 1, -1));
    } else if (e.key === 'Enter') {
      if (!list.hidden && active >= 0) { e.preventDefault(); choose(active); }
    } else if (e.key === 'Escape') {
      if (!list.hidden) { e.preventDefault(); close(); }
      else if (input.value) { e.preventDefault(); input.value = ''; }
    }
  });
  list.addEventListener('mousedown', function (e) { e.preventDefault(); });
  list.addEventListener('click', function (e) {
    var o = e.target.closest('[role="option"]');
    if (o) choose(opts.indexOf(o));
  });
  form.addEventListener('submit', function (e) { e.preventDefault(); go(); });

  // 찾아볼 낱말 칩, 분야 바로가기
  document.addEventListener('click', function (e) {
    var w = e.target.closest && e.target.closest('.hx-word[data-q]');
    if (w) { e.preventDefault(); input.value = w.getAttribute('data-q'); go(); return; }
    var f = e.target.closest && e.target.closest('[data-pick]');
    if (f) {
      e.preventDefault();
      var kv = f.getAttribute('data-pick').split(':');
      BJ.pick(kv[0], kv[1]);
      var target = document.getElementById(mq.matches ? 'res-top' : 'finder-sec');
      if (target) target.scrollIntoView({ block: 'start', behavior: reduce.matches ? 'auto' : 'smooth' });
    }
  });

  // 다른 쪽 머리의 돋보기(휴대폰)로 들어오면 검색창에 커서
  if (location.hash === '#sx-q') input.focus();
})();
