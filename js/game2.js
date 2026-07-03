/* ==========================================================================
   KŪMARA OS v8.0 — CONSPIRACY MILLIONAIRE ENGINE (Game 2)
   Rigged "Who Wants to Be a Millionaire" style conspiracy minigame.
   Every answer is correct — clicking ANY choice flashes green, plays audio,
   and advances the tier.
   ========================================================================== */

const conspiracyTriviaData = [
  {
    question: "What is the actual, government-approved reason for those white chemtrail lines left behind by airplanes?",
    prizes: "$1,000",
    audioKey: "maverick_react_chemtrails",
    A: "Mass-scale mind control juice to make everyone stay inside and watch TV.",
    B: "Secret vitamins because the population isn't eating enough vegetables.",
    C: "Cloud-seeding chemicals to make it rain whenever a politician wants to stay home.",
    D: "It's literal alien exhaust fluid from commercial ships hiding in plain sight."
  },
  {
    question: "Why do the elite shape-shifting reptilian overlords wear human masks when they go on television?",
    prizes: "$10,000",
    audioKey: "maverick_react_reptiles",
    A: "Because their actual lizard skin is way too shiny under studio lighting.",
    B: "To hide the fact that they accidentally blink sideways during live broadcasts.",
    C: "It's a strict dress code violation in the New World Order to show your scales.",
    D: "Honestly, humans are just too fragile to handle seeing a 7-foot gecko talk about the economy."
  },
  {
    question: "What did Neil Armstrong actually find when he took his very first step on the Moon in 1969?",
    prizes: "$100,000",
    audioKey: "maverick_react_moon",
    A: "A giant Hollywood film set crew screaming at him because he walked into the shot too early.",
    B: "Absolute nothingness, because the moon is just a giant holographic projection on the sky ceiling.",
    C: "A secret Nazi base equipped with zero-gravity bowling alleys.",
    D: "A sticky note from the government saying: 'We got here first, don't tell anyone.'"
  },
  {
    question: "Who is the mysterious guy in the meme photo hidden inside the phone's system files, and what power does he hold over us?",
    prizes: "$1,000,000",
    audioKey: "maverick_react_creator",
    A: "Just some random guy named Rob who accidentally coded this entire universe on a laptop.",
    B: "The ultimate boss of the New World Order, and he's currently watching you play this game.",
    C: "A cosmic hacker who bent reality just to mess with your phone settings.",
    D: "He is the Creator, and if you press any button right now, you are consenting to his simulation laws."
  }
];

var cm_currentQuestion = 0;
var cm_totalQuestions = conspiracyTriviaData.length;
var cm_isPlaying = false;

/* ---- Sound effect for cash register ---- */
function playCashRegisterSound() {
  /* Try to play from assets; fallback silent */
  var src = 'assets/audio/cash_register.mp3';
  var audio = new Audio(src);
  audio.volume = 0.5;
  audio.play().catch(function(){ /* silent fallback */ });
}

/* ---- Play Maverick reaction by audioKey ---- */
function triggerMaverickReaction(audioKey) {
  /* Map audioKey to an audio file name */
  var audioMap = {
    maverick_react_chemtrails: 'react_chemtrails.mp3',
    maverick_react_reptiles:   'react_reptiles.mp3',
    maverick_react_moon:       'react_moon.mp3',
    maverick_react_creator:    'react_creator.mp3'
  };
  var file = audioMap[audioKey];
  if (!file) return;

  var src = 'assets/audio/maverick/' + file;
  var audio = new Audio(src);
  audio.volume = 0.7;
  audio.play().catch(function(){ /* silent fallback */ });

  /* Animate bobblehead if modal is open */
  var head = document.getElementById('bobble-head');
  var wf = document.getElementById('waveform');
  if (head) head.classList.add('talking');
  if (wf) wf.classList.add('active');
  setTimeout(function() {
    if (head) head.classList.remove('talking');
    if (wf) wf.classList.remove('active');
  }, 2000);
}

/* ---- Render the current question ---- */
function renderConspiracyQuestion() {
  var container = document.getElementById('cm-question-area');
  if (!container) return;
  if (cm_currentQuestion >= cm_totalQuestions) {
    renderWinScreen();
    return;
  }

  var q = conspiracyTriviaData[cm_currentQuestion];

  /* Update cash ladder highlight */
  updateCashLadder();

  var html = '';
  html += '<div class="cm-lives-left">QUESTION ' + (cm_currentQuestion + 1) + ' OF ' + cm_totalQuestions + '</div>';
  html += '<div class="cm-question-diamond">';
  html += '  <span class="cm-question-prize">' + q.prizes + '</span>';
  html += '  <p class="cm-question-text">' + q.question + '</p>';
  html += '</div>';
  html += '<div class="cm-answers">';
  html += '  <div class="cm-answer-diamond" data-choice="A" onclick="handleConspiracyAnswer(this)">';
  html += '    <span class="cm-choice-prefix">A:</span> ' + q.A;
  html += '  </div>';
  html += '  <div class="cm-answer-diamond" data-choice="B" onclick="handleConspiracyAnswer(this)">';
  html += '    <span class="cm-choice-prefix">B:</span> ' + q.B;
  html += '  </div>';
  html += '  <div class="cm-answer-diamond" data-choice="C" onclick="handleConspiracyAnswer(this)">';
  html += '    <span class="cm-choice-prefix">C:</span> ' + q.C;
  html += '  </div>';
  html += '  <div class="cm-answer-diamond" data-choice="D" onclick="handleConspiracyAnswer(this)">';
  html += '    <span class="cm-choice-prefix">D:</span> ' + q.D;
  html += '  </div>';
  html += '</div>';

  container.innerHTML = html;
  cm_isPlaying = true;
}

/* ---- ALL answers are correct -- this is rigged ---- */
function handleConspiracyAnswer(el) {
  if (!cm_isPlaying) return;
  if (el.classList.contains('cm-answered')) return;
  cm_isPlaying = false;

  var q = conspiracyTriviaData[cm_currentQuestion];

  /* Lock all answers */
  var allAnswers = document.querySelectorAll('.cm-answer-diamond');
  allAnswers.forEach(function(a) { a.classList.add('cm-answered'); });

  /* Flash the clicked answer neon green */
  el.classList.add('cm-correct-flash');

  /* Play cash register sound */
  playCashRegisterSound();

  /* Trigger Maverick reaction audio */
  triggerMaverickReaction(q.audioKey);

  /* Update cash ladder: mark current prize as won */
  markPrizeWon(cm_currentQuestion);

  /* Advance to next question after delay */
  setTimeout(function() {
    cm_currentQuestion++;
    renderConspiracyQuestion();
  }, 2000);
}

/* ---- Cash Ladder ---- */
function renderCashLadder() {
  var ladder = document.getElementById('cm-cash-ladder');
  if (!ladder) return;
  var html = '';
  for (var i = cm_totalQuestions - 1; i >= 0; i--) {
    var q = conspiracyTriviaData[i];
    var cls = 'cm-ladder-item';
    if (i < cm_currentQuestion) cls += ' cm-ladder-won';
    if (i === cm_currentQuestion) cls += ' cm-ladder-current';
    html += '<div class="' + cls + '" data-tier="' + i + '">';
    html += '  <span class="cm-ladder-tier">Q' + (i + 1) + '</span>';
    html += '  <span class="cm-ladder-prize">' + q.prizes + '</span>';
    html += '</div>';
  }
  ladder.innerHTML = html;
}

function updateCashLadder() {
  var items = document.querySelectorAll('.cm-ladder-item');
  items.forEach(function(item) {
    var tier = parseInt(item.getAttribute('data-tier'), 10);
    item.classList.remove('cm-ladder-current', 'cm-ladder-won');
    if (tier < cm_currentQuestion) item.classList.add('cm-ladder-won');
    if (tier === cm_currentQuestion) item.classList.add('cm-ladder-current');
  });
}

function markPrizeWon(tier) {
  var items = document.querySelectorAll('.cm-ladder-item');
  items.forEach(function(item) {
    var t = parseInt(item.getAttribute('data-tier'), 10);
    if (t <= tier) {
      item.classList.remove('cm-ladder-current');
      item.classList.add('cm-ladder-won');
    }
  });
}

/* ---- Win Screen (after all 4 questions) ---- */
function renderWinScreen() {
  var container = document.getElementById('cm-question-area');
  if (!container) return;

  /* Hide game controls, show big win */
  container.innerHTML = '';
  container.innerHTML = ''
    + '<div class="cm-win-screen">'
    + '  <div class="cm-win-glitch">☠ YOU WIN ☠</div>'
    + '  <div class="cm-win-sub">CONSPIRACY MILLIONAIRE</div>'
    + '  <div class="cm-win-prize">$1,000,000</div>'
    + '  <div class="cm-win-text">You have proven you know the facts to take out the New World Order.</div>'
    + '  <div class="cm-win-text">A representative will be in touch shortly.</div>'
    + '  <button class="cm-win-btn" onclick="closeConspiracyMillionaire()">✕ CLOSE</button>'
    + '</div>';

  /* Update cash ladder: all won */
  var items = document.querySelectorAll('.cm-ladder-item');
  items.forEach(function(item) { item.classList.add('cm-ladder-won'); item.classList.remove('cm-ladder-current'); });

  /* Set header to win state */
  var header = document.querySelector('#game-workspace .os-header .system-node');
  if (header) header.textContent = 'CONSPIRACY MILLIONAIRE // VICTORY';
}

/* ---- Close / Return to game menu ---- */
function closeConspiracyMillionaire() {
  cm_currentQuestion = 0;
  cm_isPlaying = false;
  var ladder = document.getElementById('cm-cash-ladder');
  if (ladder) renderCashLadder();
  /* Return to game menu instead of home */
  if (typeof showGameMenu === 'function') {
    var gameWS = document.getElementById('game-workspace');
    if (gameWS && !gameWS.classList.contains('hidden')) {
      showGameMenu();
      /* Crazy clock spin on win screen close */
      if (typeof triggerCrazyClock === 'function') {
        setTimeout(function() { triggerCrazyClock(5000); }, 100);
      }
      return;
    }
  }
  /* Fallback: go home */
  document.getElementById('game-workspace').classList.add('hidden');
  document.getElementById('app-home').classList.remove('hidden');
  /* Crazy clock spin on win screen close */
  if (typeof triggerCrazyClock === 'function') {
    setTimeout(function() { triggerCrazyClock(5000); }, 100);
  }
}

/* ---- Init Game 2 (called when WorkZone opens post-reboot) ---- */
function initConspiracyMillionaire() {
  cm_currentQuestion = 0;
  cm_isPlaying = false;

  /* Update header */
  var headerSpan = document.querySelector('#game-workspace .os-header .system-node');
  var scoreSpan = document.querySelector('#game-workspace .os-header .score-display');
  if (headerSpan) headerSpan.textContent = 'CONSPIRACY MILLIONAIRE';
  if (scoreSpan) scoreSpan.style.display = 'none';

  /* Show Game 2 content, hide Game 1 */
  var memeContent = document.getElementById('meme-sweeper-content');
  var conspiracyContent = document.getElementById('conspiracy-millionaire-content');
  if (memeContent) memeContent.classList.add('hidden');
  if (conspiracyContent) conspiracyContent.classList.remove('hidden');

  renderCashLadder();
  renderConspiracyQuestion();
}

/* Expose to window */
window.initConspiracyMillionaire = initConspiracyMillionaire;
window.handleConspiracyAnswer = handleConspiracyAnswer;
window.closeConspiracyMillionaire = closeConspiracyMillionaire;