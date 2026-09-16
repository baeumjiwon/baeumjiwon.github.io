/* 광고 채우기(build.py ad_rails · ad_end · config.json ads). 읽는 도중에 끼어드는 광고는 없다.
   - 넓은 화면(1536px 이상): 본문 양옆 여백의 세로 광고(160×600). 본문 틀이 광고보다 넉넉히 길 때만 쓰고, 이때는 끝자리 광고를 쓰지 않는다.
   - 그보다 좁은 화면: 글·목록을 다 본 끝자리 하나(컴퓨터 728×90, 휴대폰 320×100).
   자리마다 카카오 애드핏을 먼저 부르고, 광고가 없으면(NO-AD) 애드센스로 넘기고, 그것도 없으면 자리를 접는다 —
   애드핏 웹 SDK 가이드의 '외부 광고 스크립트를 삽입하는 경우' 예시와 같은 순서. 애드핏 광고 코드(ins 속성)는 발급받은 모양 그대로 쓴다.
   아이디는 빌드 때 형식을 검사한 값만 들어온다(build.py). 화면 크기는 불러올 때 한 번만 본다(보이지 않는 광고를 부르지 않게). */
(function () {
  var A = window.ADS || {};
  var WIDE = 1536, PC = 861, SIDE = [160, 600], END_PC = [728, 90], END_MO = [320, 100];
  var wide = window.matchMedia('(min-width: ' + WIDE + 'px)').matches;
  var pc = window.matchMedia('(min-width: ' + PC + 'px)').matches;
  var kakao = false, n = 0, waiting = [];

  function adsense(slot, id, size) {
    var box = slot.querySelector('.ad-box');
    if (!A.client || !id) { slot.hidden = true; return; }
    box.style.minHeight = '0';
    var style = size ? 'display:inline-block;width:' + size[0] + 'px;height:' + size[1] + 'px' : 'display:block';
    box.innerHTML = '<ins class="adsbygoogle" style="' + style + '" data-ad-client="' + A.client + '" data-ad-slot="' + id + '"' +
      (size ? '' : ' data-ad-format="auto" data-full-width-responsive="true"') + '></ins>';
    slot.hidden = false;
    (window.adsbygoogle = window.adsbygoogle || []).push({});
    // 애드센스 스크립트가 막혀 안 들어오면(광고 차단 등) 빈 칸이 남지 않게 접는다
    setTimeout(function () { if (!(window.adsbygoogle && window.adsbygoogle.loaded)) slot.hidden = true; }, 5000);
  }

  function fill(slot, unit, size, sense, senseSize) {
    if (!unit) { adsense(slot, sense, senseSize); return; }
    // NO-AD 콜백 이름은 한 쪽 안에서 광고 단위마다 달라야 한다(가이드)
    var cb = 'bjAdNoAd' + (++n);
    window[cb] = function () { adsense(slot, sense, senseSize); };
    waiting.push(window[cb]);
    var box = slot.querySelector('.ad-box');
    box.style.minHeight = size[1] + 'px';   // 크기가 정해진 광고라 자리를 미리 잡는다
    box.innerHTML = '<ins class="kakao_ad_area" style="display:none;width:100%;" data-ad-unit="' + unit +
      '" data-ad-width="' + size[0] + '" data-ad-height="' + size[1] + '" data-ad-onfail="' + cb + '"></ins>';
    slot.hidden = false;
    kakao = true;
  }

  var sides = 0;
  if (wide) {
    Array.prototype.forEach.call(document.querySelectorAll('.ad-side[data-side]'), function (slot) {
      // 본문이 짧으면 세로 광고가 틀 아래로 삐져나와 푸터·띠에 걸친다
      if (slot.parentElement.offsetHeight < SIDE[1] + 160) return;
      var s = slot.getAttribute('data-side');
      if (!A['s' + s] && !A['g' + s]) return;
      fill(slot, A['s' + s], SIDE, A['g' + s], SIDE);
      sides++;
    });
  }
  if (!sides) {
    Array.prototype.forEach.call(document.querySelectorAll('.ad-end[data-end]'), function (slot) {
      fill(slot, pc ? A.ep : A.em, pc ? END_PC : END_MO, A.ge, null);
    });
  }

  if (kakao) {
    var sc = document.createElement('script');
    sc.async = true;
    sc.charset = 'utf-8';
    sc.src = 'https://t1.kakaocdn.net/kas/static/ba.min.js';
    // 애드핏 스크립트를 못 받으면(광고 차단·연결 실패) NO-AD와 똑같이 넘긴다 — '광고' 글자만 있는 빈 칸이 남지 않게
    sc.onerror = function () { waiting.forEach(function (f) { f(); }); };
    document.body.appendChild(sc);
  }
})();
