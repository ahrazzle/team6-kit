/* =========================================================================
   Team6-kit official site — main.js
   Progressive enhancement only. Content never depends on this script.
   Boot guard: page is already complete without JS; this only adds motion
   and a convenience copy button. Spec: 02-spec §6, 03-spec §4.
   ========================================================================= */

(function () {
  'use strict';

  // ---- Boot guard (02-spec §6.3): the <head> inline script set .js -----
  if (!document.documentElement.classList.contains('js')) return;

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function init() {
    initPipeline();
    initTerminal();
    initCopyButton();
    // if the OS toggles reduced motion mid-session, tear down loops
    reduceMotion.addEventListener('change', function (e) {
      if (e.matches) {
        document.querySelectorAll('.pipeline.animating, .terminal.animating')
          .forEach(function (el) { el.classList.remove('animating'); });
      } else {
        initPipeline();
        initTerminal();
      }
    });
  }

  /* ------------------------------------------------------------------ */
  /*  Signature A: the 9-stage orchestration pipeline                    */
  /* ------------------------------------------------------------------ */
  function initPipeline() {
    var pipe = document.getElementById('pipeline');
    if (!pipe || pipe.classList.contains('animating')) return;
    // reduced motion: keep the static <ol> (source of truth), no animation
    if (reduceMotion.matches) return;

    // Exact §2 contribution order, lanes/NOT verbatim from governance.md
    var stages = [
      { n: 1, role: 'Director',    lane: 'Orchestration, decisions',            not: 'Hands-on coding' },
      { n: 2, role: 'UX',          lane: 'Human experience, interface',          not: 'Backend logic' },
      { n: 3, role: 'QA/Scoper',   lane: 'Scoping, cut overengineering',         not: 'Feature expansion' },
      { n: 4, role: 'Researcher',  lane: 'Evidence, prior art, market scan',     not: 'Architecture decisions' },
      { n: 5, role: 'Architect',   lane: 'Analysis, design (thinking only)',     not: 'Writing code' },
      { n: 6, role: 'UX',          lane: 'UI/UX design',                         not: 'Backend logic' },
      { n: 7, role: 'Coder',       lane: 'Software development (sole)',          not: 'Strategy prose' },
      { n: 8, role: 'QA',          lane: "Verification, Occam's razor",          not: 'Feature expansion' },
      { n: 9, role: 'Director',    lane: 'Summarize, report',                    not: 'Hands-on coding' }
    ];

    var surface = pipe.querySelector('.pipeline-anim');
    var nodes = [];
    var arrow = document.createElement('span');
    arrow.className = 'handoff';
    arrow.setAttribute('aria-hidden', 'true');
    arrow.style.position = 'absolute';
    arrow.style.width = '14px';
    arrow.style.height = '14px';
    arrow.style.borderLeft = '3px solid var(--accent)';
    arrow.style.borderBottom = '3px solid var(--accent)';
    arrow.style.transformOrigin = 'center';
    pipe.appendChild(arrow);

    stages.forEach(function (s, i) {
      var el = document.createElement('div');
      el.className = 'pstage';
      el.innerHTML =
        '<span class="pnum">' + s.n + '</span>' +
        '<span class="prole">' + s.role + '</span>' +
        '<span class="plane">' + s.lane + '</span>' +
        '<span class="pnot">NOT · ' + s.not + '</span>';
      if (i === 0) el.classList.add('active');
      surface.appendChild(el);
      nodes.push(el);
    });

    pipe.classList.add('animating');

    var pos = [];
    function computePos() {
      var cr = pipe.getBoundingClientRect();
      pos = nodes.map(function (el) {
        var r = el.getBoundingClientRect();
        return { x: r.left - cr.left + r.width / 2, y: r.top - cr.top + r.height / 2 };
      });
    }
    computePos();
    window.addEventListener('resize', debounce(computePos, 150));

    var idx = 0;
    var timer = null;
    var paused = false;

    function placeArrow(from, to) {
      var fx = pos[from].x, fy = pos[from].y;
      var tx = pos[to].x, ty = pos[to].y;
      var midX = (fx + tx) / 2, midY = (fy + ty) / 2;
      var angle = Math.atan2(ty - fy, tx - fx) * 180 / Math.PI;
      arrow.style.left = '0px';
      arrow.style.top = '0px';
      arrow.style.transform = 'translate(' + midX + 'px,' + midY + 'px) translate(-50%,-50%) rotate(' + (angle + 45) + 'deg)';
      // handoff pulse: opacity only (transform/opacity, no layout in loop)
      arrow.classList.add('on');
      clearTimeout(arrow._t);
      arrow._t = setTimeout(function () { arrow.classList.remove('on'); }, 700);
    }

    function advance() {
      if (paused) return;
      nodes[idx].classList.remove('active');
      var from = idx;
      idx = (idx + 1) % nodes.length;
      nodes[idx].classList.add('active');
      placeArrow(from, idx);
      timer = setTimeout(advance, 1500);
    }

    function pause() { paused = true; }
    function resume() { if (paused) { paused = false; } }

    // pause on hover / keyboard focus (immediate freeze per 03-spec §4.1)
    pipe.addEventListener('mouseenter', pause);
    pipe.addEventListener('mouseleave', resume);
    pipe.addEventListener('focusin', pause);
    pipe.addEventListener('focusout', resume);

    advance();
  }

  /* ------------------------------------------------------------------ */
  /*  Signature B: the demo terminal replay                              */
  /* ------------------------------------------------------------------ */
  function initTerminal() {
    var term = document.getElementById('demo-terminal');
    if (!term || term.classList.contains('animating')) return;
    if (reduceMotion.matches) return;

    var lines = [
      { prompt: '$ ', cmd: 'python3 build/sweep-gate.py', cmt: '      # PASS(0) → continue; FAIL(1) → stop' },
      { prompt: '$ ', cmd: 'python3 build/review-gate.py', cmt: '     # 4/4 checkboxes on every shipping row' },
      { prompt: '$ ', cmd: 'python3 build/generate.py --out <kit-dir> [--params <pack.yaml>]', cmt: '' },
      { wait: 'waiting for gates' }
    ];

    var anim = term.querySelector('.term-anim');
    var cursor = document.createElement('span');
    cursor.className = 'cursor';
    cursor.setAttribute('aria-hidden', 'true');
    var linesEl = [];

    lines.forEach(function (ln, i) {
      var div = document.createElement('div');
      div.className = 'cline';
      if (ln.wait) {
        div.innerHTML = '<span class="wait">' + ln.wait + '</span>';
      } else {
        var cmt = ln.cmt ? '<span class="cmt">' + ln.cmt + '</span>' : '';
        div.innerHTML = '<span class="prompt">' + ln.prompt + '</span>' +
                        '<span class="cmd">' + ln.cmd + '</span>' + cmt;
      }
      if (i === lines.length - 1) div.appendChild(cursor);
      anim.appendChild(div);
      linesEl.push(div);
    });

    term.classList.add('animating');

    var running = false;
    var paused = false;
    var timers = [];

    function clearTimers() { timers.forEach(clearTimeout); timers = []; }

    function run() {
      if (paused || !term.classList.contains('animating')) return;
      clearTimers();
      linesEl.forEach(function (el) { el.classList.remove('show'); });
      var t = 0;
      linesEl.forEach(function (el, i) {
        timers.push(setTimeout(function () {
          if (paused || !term.classList.contains('animating')) return;
          el.classList.add('show');
        }, t));
        t += 450;
      });
      // "waiting for gates" beat then loop (03-spec §4.2: ~900ms pause)
      timers.push(setTimeout(run, t + 900));
    }

    function pauseF() { paused = true; clearTimers(); }
    function resumeF() { paused = false; run(); }

    term.addEventListener('mouseenter', pauseF);
    term.addEventListener('mouseleave', resumeF);
    term.addEventListener('focusin', pauseF);
    term.addEventListener('focusout', resumeF);

    run();
  }

  /* ------------------------------------------------------------------ */
  /*  Copy button (progressive enhancement; selectable without JS)       */
  /* ------------------------------------------------------------------ */
  function initCopyButton() {
    var block = document.querySelector('.cmd-block');
    var pre = block && block.querySelector('pre');
    var btn = block && block.querySelector('.copy-btn');
    if (!block || !pre || !btn) return;

    btn.hidden = false;
    var cmdText = pre.textContent.replace(/^\$\s*/, '');

    function copy() {
      var done = function () {
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(cmdText).then(done, function () { selectFallback(); done(); });
      } else {
        selectFallback(); done();
      }
    }
    function selectFallback() {
      // select the command text so the user can copy manually
      var range = document.createRange();
      range.selectNodeContents(pre);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
    }
    btn.addEventListener('click', copy);
  }

  function debounce(fn, wait) {
    var t;
    return function () { clearTimeout(t); t = setTimeout(fn, wait); };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
