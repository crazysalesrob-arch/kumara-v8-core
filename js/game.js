/* ==========================================================================
   KŪMARA OS v8.0 — MEME SWEEPER ENGINE (8-card deck)
   ========================================================================== */

const memeDeck = [
  { id: 'card-01', image: 'images/meme1.png', real: true,  isGlitch: false, isRobCreator: false },
  { id: 'card-02', image: 'images/meme2.png', real: false, isGlitch: false, isRobCreator: false },
  { id: 'card-03', image: 'images/meme3.png', real: true,  isGlitch: false, isRobCreator: false },
  { id: 'card-04', image: 'images/meme4.png', real: false, isGlitch: false, isRobCreator: false },
  { id: 'card-05', image: 'images/meme5.png', real: true,  isGlitch: false, isRobCreator: false },
  { id: 'card-06', image: 'images/meme6.png', real: false, isGlitch: false, isRobCreator: false },
  { id: 'card-07', image: 'images/meme7.png', real: true,  isGlitch: false, isRobCreator: false },
  { id: 'card-08', image: 'images/glitch2.png', real: false, isGlitch: true,  isRobCreator: false }
];

let ci = 0, correct = 0, total = 0;
let glitchLevel = 0;
let glitchSwipeLock = false;
/* Track if we're in post-reboot state (card 7 hit → reboot → maverick panic) */
let postRobCrashReboot = false;

/* ---- Fallback ---- */
function fallback(topic) {
  return 'data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'280\' height=\'200\' viewBox=\'0 0 280 200\'><rect width=\'280\' height=\'200\' fill=\'%230a160a\'/><text x=\'140\' y=\'100\' font-family=\'monospace\' font-size=\'14\' fill=\'%2300ff00\' text-anchor=\'middle\' dominant-baseline=\'middle\'>[ CARD ' + (ci + 1) + ' ]</text></svg>';
}

/* ---- Render ---- */
function renderCard() {
  var slot = document.getElementById('card-deck-slot');
  if (!slot || ci >= memeDeck.length) return;
  var d = memeDeck[ci];

  var img = new Image();
  img.className = 'card-img';
  img.alt = 'meme ' + (ci + 1);
  img.onerror = function(){ this.src = fallback(); };
  img.src = d.image;

  var wrap = document.createElement('div');
  wrap.className = 'card-img-wrap';
  wrap.appendChild(img);

  var tag = document.createElement('div');
  tag.className = 'real-tag';
  tag.textContent = 'IDENTIFY: IS THIS REAL OR FAKE?';

  var idx = document.createElement('span');
  idx.className = 'card-index';
  idx.textContent = (ci + 1) + '/' + memeDeck.length;

  var card = document.createElement('div');
  card.className = 'meme-card';
  card.id = d.id;
  card.appendChild(wrap);
  card.appendChild(tag);
  card.appendChild(idx);

  slot.innerHTML = '';
  slot.appendChild(card);
  glitchLevel = 0;
  glitchSwipeLock = false;
}

/* ---- Apply progressive glitch effect to the glitch card (card 8) ---- */
function applyProgressiveGlitch() {
  glitchLevel++;
  var el = document.getElementById('card-08');
  if (!el) return;

  /* Keep glitch2.png as the image — CSS effects create the visual corruption */

  el.classList.remove('glitch-l1', 'glitch-l2', 'glitch-l3', 'glitch-l4');
  var levelClass = 'glitch-l' + Math.min(glitchLevel, 4);
  el.classList.add(levelClass);

  var tag = el.querySelector('.real-tag');
  if (tag) {
    var msgs = [
      '⚠ SIGNAL DEGRADING...',
      '⚠⚠ GLITCH PROTOCOL ACTIVE',
      '⚠⚠⚠ SYSTEM INTEGRITY FAILING',
      '☠☠☠ CRASH IMMINENT'
    ];
    tag.textContent = msgs[Math.min(glitchLevel - 1, 3)];
    tag.style.color = '#ff0044';
    tag.style.animation = 'glitchText 0.1s infinite alternate';
  }

  if (glitchLevel >= 4) {
    el.classList.add('glitch-pending-crash');
  }
}

/* ---- Card 7 hard cut: black screen → reboot loop ---- */
function triggerRobCrash() {
  var pc = document.getElementById('phone-container');
  var crash = document.getElementById('system-crash-overlay');
  var reboot = document.getElementById('os-reboot-screen');

  /* Hard cut — no jitter, no invert, just immediate black */
  pc.style.display = 'none';
  /* Use a brief flash of the crash overlay */
  crash.classList.remove('hidden');

  setTimeout(function() {
    crash.classList.add('hidden');
    reboot.classList.remove('hidden');
    postRobCrashReboot = true;
    setTimeout(function() {
      reboot.classList.add('hidden');
      pc.style.display = '';
      /* Reset game state */
      ci = 0; correct = 0; total = 0;
      document.getElementById('score-count').textContent = '0/0';
      document.getElementById('game-workspace').classList.add('hidden');
      document.getElementById('app-home').classList.remove('hidden');
      renderCard();
    }, 3000);
  }, 800);
}

/* ---- Post-reboot Maverick panic (modal, audio-driven) ---- */
function launchMaverickPanic() {
  var modal = document.getElementById('maverick-modal');
  var title = document.getElementById('maverick-title');
  modal.classList.remove('hidden');
  title.textContent = '▮ MAVERICK // PANIC MODE';

  var PANIC_PLAYLIST = [
    { file: 'panic_01.mp3', duration: 1800 },
    { file: 'panic_02.mp3', duration: 2000 },
    { file: 'panic_03.mp3', duration: 2200 },
    { file: 'panic_04.mp3', duration: 2500 },
    { file: 'panic_05.mp3', duration: 2000 },
    { file: 'panic_06.mp3', duration: 2400 },
    { file: 'panic_07.mp3', duration: 2800 }
  ];

  maverickState = 'dialogue';
  var panicIdx = 0;
  function playNextPanicTrack() {
    if (panicIdx >= PANIC_PLAYLIST.length) {
      var titleEl = document.getElementById('maverick-title');
      titleEl.textContent = '⛔ MAVERICK // CORRUPTED';
      if (typeof startBleed === 'function') {
        startBleed();
      }
      return;
    }

    var track = PANIC_PLAYLIST[panicIdx];
    panicIdx++;

    /* Waveform spike on panic tracks */
    var bars = document.querySelectorAll('.wf-bar');
    if (panicIdx % 2 === 0) {
      bars.forEach(function(b){ b.style.animationName = 'waveSpike'; });
      setTimeout(function(){ bars.forEach(function(b){ b.style.animationName = 'wavePulse'; }); }, 500);
    }

    playMaverick(track.file, track.duration, function() {
      setTimeout(playNextPanicTrack, 400);
    });
  }

  setTimeout(playNextPanicTrack, 800);
}

/* ---- Swipe ---- */
function handleSwipeAction(dir) {
  if (ci >= memeDeck.length) return;
  if (glitchSwipeLock) return;
  var card = memeDeck[ci];
  var el = document.getElementById(card.id);
  if (!el) return;

  // ---- Rob Creator card (card 7) — hard cut to reboot ----
  if (card.isRobCreator) {
    triggerRobCrash();
    return;
  }

  // ---- Progressive glitch card (card 8) ----
  if (card.isGlitch) {
    glitchSwipeLock = true;
    applyProgressiveGlitch();

    if (glitchLevel >= 4) {
      setTimeout(function() {
        glitchSwipeLock = false;
        triggerCrash();
      }, 800);
    } else {
      setTimeout(function() {
        glitchSwipeLock = false;
      }, 1200);
    }
    return;
  }

  // ---- Normal card swipe ----
  var choseReal = dir === 'right';
  var wasCorrect = choseReal === card.real;
  total++;
  if (wasCorrect) correct++;

  var resultEl = document.createElement('div');
  resultEl.className = 'swipe-result ' + (wasCorrect ? 'correct' : 'wrong');
  resultEl.textContent = wasCorrect ? '✓ CORRECT' : '✗ WRONG';
  el.appendChild(resultEl);

  setTimeout(function() {
    var x = dir === 'left' ? -400 : 400;
    el.style.transition = 'transform 0.3s ease, opacity 0.25s ease';
    el.style.transform = 'translateX(' + x + 'px) rotate(' + (dir === 'left' ? -15 : 15) + 'deg)';
    el.style.opacity = '0';
  }, 600);

  ci++;
  document.getElementById('score-count').textContent = correct + '/' + total;
  setTimeout(renderCard, 920);
}

/* ---- 2.5s crash (for card 8 progressive glitch finish) ---- */
function triggerCrash() {
  var pc = document.getElementById('phone-container');
  var crash = document.getElementById('system-crash-overlay');
  var reboot = document.getElementById('os-reboot-screen');

  var glitchEl = document.getElementById('card-08');
  if (glitchEl) {
    glitchEl.classList.remove('glitch-l1', 'glitch-l2', 'glitch-l3', 'glitch-l4', 'glitch-pending-crash');
  }

  pc.classList.add('screen-jitter');
  pc.classList.add('color-invert');
  crash.classList.remove('hidden');

  /* Glitch the music on crash */
  if (typeof MusicEngine !== 'undefined' && MusicEngine.glitch) {
    MusicEngine.glitch();
  }

  setTimeout(function() {
    pc.classList.remove('screen-jitter', 'color-invert');
    crash.classList.add('hidden');
    reboot.classList.remove('hidden');
    setTimeout(function() {
      reboot.classList.add('hidden');
      ci = 0; correct = 0; total = 0;
      document.getElementById('score-count').textContent = '0/0';
      document.getElementById('game-workspace').classList.add('hidden');
      document.getElementById('app-home').classList.remove('hidden');
      renderCard();

      /* Restart music clean after reboot */
      if (typeof MusicEngine !== 'undefined' && MusicEngine.restart) {
        MusicEngine.restart();
      }

      /* Mark game 1 as completed and advance to Phase 2 */
      if (window.KumeraOS) {
        window.KumeraOS.gamesCompleted[1] = true;
        window.KumeraOS.advancePhase(2);
      }

      /* Crazy clock spin on reboot */
      if (typeof triggerCrazyClock === 'function') {
        triggerCrazyClock(5000);
      }

      /* Phase 2 audio — EXACT same pattern as boot greeting */
      var _p2m = document.getElementById('maverick-modal');
      var _p2t = document.getElementById('maverick-title');
      if (_p2m) _p2m.classList.remove('hidden');
      if (_p2t) _p2t.textContent = '▮ MAVERICK // PHASE 2 BRIEFING';
      var _p2a = new Audio('assets/audio/maverick/mav_line2.mp3');
      _p2a.volume = 0.8;
      _p2a.preload = 'auto';
      _p2a.load();
      _p2a.muted = true;
      _p2a.play().then(function() {
        _p2a.muted = false;
        var head = document.getElementById('bobble-head');
        if (head) head.classList.add('talking');
      }).catch(function() {
        _p2a.muted = false;
        _p2a.play().catch(function(){});
      });
      _p2a.addEventListener('ended', function() {
        var head = document.getElementById('bobble-head');
        if (head) head.classList.remove('talking');
        if (_p2m) _p2m.classList.add('hidden');
        if (_p2t) _p2t.textContent = 'Maverick';
      });
    }, 3000);
  }, 2500);
}

document.addEventListener('DOMContentLoaded', renderCard);
window.handleSwipeAction = handleSwipeAction;