/* 마감 글자를 브라우저 오늘 날짜로 다시 쓴다. theme.py _dl_markup과 같은 모양. 빨강(urgent)은 오늘·1일 남음만 */
(function () {
  var W = '일월화수목금토';
  var today = new Date(); today.setHours(0, 0, 0, 0);
  var SEP = '<span class="sep"> · </span>';
  function run(root) {
    Array.prototype.forEach.call((root || document).querySelectorAll('[data-dl]'), function (el) {
      var s = el.getAttribute('data-dl');
      var d = new Date(s + 'T00:00:00');
      if (isNaN(d.getTime())) return;
      var n = Math.round((d - today) / 86400000);
      var date = (d.getMonth() + 1) + '월 ' + d.getDate() + '일(' + W[d.getDay()] + ')';
      var st = '', html;
      if (n < 0) { st = 'past'; html = '<span class="left">마감 지남</span>' + SEP + '<span class="date">' + date + '</span>'; }
      else if (n === 0) { st = 'urgent'; html = '<span class="left">오늘 마감</span>' + SEP + '<span class="date">' + date + '</span>'; }
      else { st = n === 1 ? 'urgent' : (n <= 3 ? 'soon' : ''); html = '<span class="date">' + date + ' 마감</span>' + SEP + '<span class="left">' + n + '일 남음</span>'; }
      el.classList.remove('past', 'urgent', 'soon');
      if (st) el.classList.add(st);
      if (el.innerHTML !== html) el.innerHTML = html;
    });
  }
  window.bjDl = run;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', function () { run(); });
  else run();
})();
