/* D안: 카드 줄 탭·화살표, 카드 마감 D-day를 오늘 날짜로 다시 쓰기, 상세 아래 고정 신청 줄 */
(function () {
  var mq = window.matchMedia('(max-width: 860px)');

  // 1) 카드 줄
  Array.prototype.forEach.call(document.querySelectorAll('[data-shelf]'), function (sh) {
    var tabs = Array.prototype.slice.call(sh.querySelectorAll('[role="tab"]'));
    var panels = Array.prototype.slice.call(sh.querySelectorAll('.sh-panel'));
    var prev = sh.querySelector('.sh-prev');
    var next = sh.querySelector('.sh-next');
    function cur() {
      for (var i = 0; i < panels.length; i++) if (!panels[i].hidden) return panels[i].querySelector('.cards');
      return null;
    }
    function update() {
      var c = cur();
      if (!c || !prev) return;
      prev.disabled = c.scrollLeft < 8;
      next.disabled = c.scrollLeft + c.clientWidth >= c.scrollWidth - 8;
    }
    function select(i, focus) {
      tabs.forEach(function (t, j) {
        var on = i === j;
        t.setAttribute('aria-selected', on ? 'true' : 'false');
        t.tabIndex = on ? 0 : -1;
        panels[j].hidden = !on;
      });
      var c = cur();
      if (c) c.scrollLeft = 0;
      if (focus) tabs[i].focus();
      update();
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(i); });
      t.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowRight') { e.preventDefault(); select((i + 1) % tabs.length, true); }
        else if (e.key === 'ArrowLeft') { e.preventDefault(); select((i - 1 + tabs.length) % tabs.length, true); }
      });
    });
    [prev, next].forEach(function (b, k) {
      if (!b) return;
      b.addEventListener('click', function () {
        var c = cur();
        if (c) c.scrollBy({ left: (k ? 1 : -1) * c.clientWidth * 0.92, behavior: 'smooth' });
      });
    });
    panels.forEach(function (p) {
      var c = p.querySelector('.cards');
      if (c) c.addEventListener('scroll', update, { passive: true });
    });
    window.addEventListener('resize', update);
    update();
  });

  // 2) 카드 마감 D-day
  var today = new Date(); today.setHours(0, 0, 0, 0);
  Array.prototype.forEach.call(document.querySelectorAll('[data-dd]'), function (el) {
    var d = new Date(el.getAttribute('data-dd') + 'T00:00:00');
    if (isNaN(d.getTime())) return;
    var n = Math.round((d - today) / 86400000);
    var t = el.querySelector('.dd-t');
    if (!t) return;
    el.classList.remove('hot', 'past');
    if (n < 0) { t.textContent = '마감 지남'; el.classList.add('past'); }
    else { t.textContent = n === 0 ? '오늘 마감' : '마감 D-' + n; if (n <= 3) el.classList.add('hot'); }
  });

  // 3) 첫 화면 '내 조건으로 찾기': 휴대폰에서는 조건 창을 바로 연다
  Array.prototype.forEach.call(document.querySelectorAll('a[href="#finder-sec"]'), function (a) {
    a.addEventListener('click', function (e) {
      var open = document.getElementById('open-f');
      if (mq.matches && open) { e.preventDefault(); open.click(); }
    });
  });

  // 4) 상세 아래 고정 신청 줄: 머리의 신청 버튼이 화면 위로 사라지면 보인다
  var sc = document.getElementById('sticky-cta');
  var heroCta = document.querySelector('.p-hero .cta');
  if (sc && heroCta && 'IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      var e = es[0];
      sc.classList.toggle('on', !e.isIntersecting && e.boundingClientRect.top < 0);
    }).observe(heroCta);
  } else if (sc) {
    sc.classList.add('on');
  }
})();
