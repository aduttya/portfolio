/* Logit explainer. Plain JS, no dependencies.
   Every value is an illustrative teaching number. Probabilities in the
   generation tab are computed here with softmax, so they always match
   the logits shown. */
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function $(s, el) { return (el || document).querySelector(s); }
  function $$(s, el) { return Array.prototype.slice.call((el || document).querySelectorAll(s)); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function pct(p, d) { return (p * 100).toFixed(d == null ? 1 : d) + '%'; }
  function later(fn, ms) { return setTimeout(fn, reduce ? 0 : ms); }

  /* ── Tooltips for terms (one tooltip, placed inside the term's figure) ── */
  var tip = el('div', 'lx-tip');
  tip.setAttribute('role', 'tooltip');
  tip.id = 'lx-tip';
  tip.hidden = true;
  var tipFor = null;
  function showTip(t) {
    var box = t.closest('.lx');
    if (!box) return;
    if (tip.parentNode !== box) box.appendChild(tip);
    tipFor = t;
    tip.textContent = t.getAttribute('data-tip');
    tip.hidden = false;
    t.setAttribute('aria-describedby', 'lx-tip');
    var r = t.getBoundingClientRect(), b = box.getBoundingClientRect();
    var w = Math.min(280, b.width - 24);
    tip.style.width = w + 'px';
    var x = r.left - b.left + r.width / 2 - w / 2;
    x = Math.max(12, Math.min(x, b.width - w - 12));
    tip.style.left = x + 'px';
    tip.style.top = (r.bottom - b.top + 8) + 'px';
  }
  function hideTip() {
    if (tipFor) tipFor.removeAttribute('aria-describedby');
    tipFor = null;
    tip.hidden = true;
  }
  $$('.lx-term').forEach(function (t) {
    t.addEventListener('mouseenter', function () { showTip(t); });
    t.addEventListener('mouseleave', hideTip);
    t.addEventListener('focus', function () { showTip(t); });
    t.addEventListener('blur', hideTip);
    t.addEventListener('click', function (e) { e.stopPropagation(); tipFor === t ? hideTip() : showTip(t); });
  });
  document.addEventListener('click', function () { if (tipFor) hideTip(); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') hideTip(); });

  /* ── A. Generation ──────────────────────────────────────── */
  (function () {
  if (!$('[data-lx-gen]')) return;
  var PROMPT = ['What', 'is', 'the', 'capital', 'of', 'France', '?'];
  var STEPS = [
    [['Paris', 3.0], ['London', 1.0], ['Berlin', 0.5], ['Rome', -0.5]],
    [['.', 2.6], [',', 1.2], ['is', 0.8], ['!', -0.4]],
    [['<end>', 3.2], ['It', 1.4], ['The', 0.9], ['\\n', 0.1]]
  ];
  var LMIN = -1.5, LMAX = 3.5, LSPAN = LMAX - LMIN;

  /* phase: idle, tokens, model, logits, probs, select */
  var A = { phase: 'idle', step: 0, view: 'logits', temp: 1, generated: [] };
  var aNext = $('[data-a-next]'), aReset = $('[data-a-reset]');
  var aCtx = $('[data-a-ctx]'), aBars = $('[data-a-bars]'), aFormula = $('[data-a-formula]');
  var aExplain = $('[data-a-explain]'), aPrompt = $('[data-a-prompt]'), aOutLabel = $('[data-a-outlabel]');
  var aTempWrap = $('[data-a-tempwrap]'), aTemp = $('[data-a-temp]'), aTempVal = $('[data-a-tempval]');
  var aViewBtns = $$('[data-a-view]');

  function softmax(logits, t) {
    var ex = logits.map(function (l) { return Math.exp(l / t); });
    var sum = ex.reduce(function (a, b) { return a + b; }, 0);
    return { ex: ex, sum: sum, p: ex.map(function (e) { return e / sum; }) };
  }
  function fmtLogit(l) { return (l < 0 ? '−' : '') + Math.abs(l).toFixed(1); }

  var EXPLAIN_A = {
    idle: 'Start with a prompt. Press the button to see how the model reads it.',
    tokens: 'An LLM processes the input as a sequence of tokens. It uses the context to calculate scores for possible next tokens.',
    model: 'The tokens go through the transformer in one forward pass. It outputs one raw numerical score, a logit, for every token in its vocabulary.',
    logits: 'Logits are raw scores, not probabilities. A higher logit means a token receives a higher relative score compared with other candidate tokens. They can be negative, and they do not add up to anything in particular.',
    probs: 'Softmax converts the raw scores into a probability distribution that sums to 100%. Try the temperature slider to see how the same logits can produce a sharper or flatter distribution.',
    select: 'The selected token becomes part of the context. The model processes the updated context and calculates another distribution for the next token.',
    done: 'The model produced an end token, so generation stops. Every word in the answer came from repeating that same loop.'
  };

  function renderCtx(fresh) {
    aCtx.textContent = '';
    if (A.phase === 'idle') { aPrompt.hidden = false; return; }
    aPrompt.hidden = true;
    PROMPT.forEach(function (t, i) {
      var c = el('span', 'lx-chip', t);
      if (A.phase === 'tokens' && !reduce) c.style.animationDelay = (i * 60) + 'ms';
      if (A.phase === 'tokens') c.classList.add('lx-in');
      aCtx.appendChild(c);
    });
    A.generated.forEach(function (t, i) {
      var c = el('span', 'lx-chip lx-gen', t);
      if (fresh && i === A.generated.length - 1) c.classList.add('lx-in', 'lx-flash');
      aCtx.appendChild(c);
    });
  }

  function renderBars() {
    var show = A.phase === 'logits' || A.phase === 'probs' || A.phase === 'select' || A.phase === 'done';
    var cands = STEPS[Math.min(A.step, STEPS.length - 1)];
    var logits = cands.map(function (c) { return c[1]; });
    var sm = softmax(logits, A.temp);
    var view = A.phase === 'logits' ? 'logits' : A.view;

    if (!show) {
      /* placeholder rows so the reader can see what is coming */
      aBars.textContent = '';
      aBars.removeAttribute('data-step');
      aBars.classList.remove('lx-is-probs');
      aBars.classList.toggle('lx-busy', A.phase === 'model');
      for (var k = 0; k < 4; k++) {
        var row = el('div', 'lx-row lx-ghost-row');
        row.appendChild(el('span', 'lx-tok', '?'));
        var tr = el('span', 'lx-track');
        tr.appendChild(el('span', 'lx-shimmer'));
        row.appendChild(tr);
        row.appendChild(el('span', 'lx-val', '\u00B7'));
        aBars.appendChild(row);
      }
      aBars.appendChild(el('p', 'lx-empty', A.phase === 'model' ? 'Scoring every token in the vocabulary\u2026' : 'Scores for the candidate next tokens appear here once the model has run.'));
      aFormula.textContent = '';
      aOutLabel.textContent = 'Candidate next tokens';
      return;
    }

    aBars.classList.remove('lx-busy');
    /* build rows once per step, then just move the bars so they animate */
    if (aBars.getAttribute('data-step') !== String(A.step)) {
      aBars.textContent = '';
      aBars.setAttribute('data-step', A.step);
      var axis = el('div', 'lx-zero');
      aBars.appendChild(axis);
      cands.forEach(function (c) {
        var row = el('div', 'lx-row');
        row.appendChild(el('span', 'lx-tok', c[0]));
        var track = el('span', 'lx-track');
        track.appendChild(el('span', 'lx-fill'));
        row.appendChild(track);
        row.appendChild(el('span', 'lx-val'));
        aBars.appendChild(row);
      });
    }

    var zeroAt = view === 'logits' ? (-LMIN / LSPAN) : 0;
    aBars.style.setProperty('--z', zeroAt);
    aBars.classList.toggle('lx-is-probs', view === 'probs');
    var best = 0;
    sm.p.forEach(function (p, i) { if (p > sm.p[best]) best = i; });

    $$('.lx-row', aBars).forEach(function (row, i) {
      var fill = $('.lx-fill', row), val = $('.lx-val', row), l = logits[i];
      var left, width;
      if (view === 'logits') {
        left = l >= 0 ? zeroAt : zeroAt + l / LSPAN;
        width = Math.abs(l) / LSPAN;
      } else {
        left = 0;
        width = sm.p[i];
      }
      fill.style.left = (left * 100) + '%';
      fill.style.width = (width * 100) + '%';
      fill.classList.toggle('lx-neg', view === 'logits' && l < 0);
      val.textContent = view === 'logits' ? fmtLogit(l) : pct(sm.p[i]);
      row.classList.toggle('lx-pick', (A.phase === 'select' || A.phase === 'done') && i === best);
    });

    aOutLabel.textContent = view === 'logits' ? 'Raw logits, zero line marked' : 'Probabilities after softmax';
    if (view === 'logits') {
      aFormula.textContent = 'Illustrative values, not real model outputs.';
    } else {
      var t = A.temp, tok = cands[best][0];
      var tPart = t === 1 ? '' : ' / ' + t.toFixed(2);
      aFormula.textContent = '';
      var f = el('code', null,
        'P(' + tok + ') = exp(' + fmtLogit(logits[best]) + tPart + ') / Σ exp(logit' + tPart + ') = ' +
        sm.ex[best].toFixed(2) + ' / ' + sm.sum.toFixed(2) + ' = ' + pct(sm.p[best]));
      aFormula.appendChild(f);
      aFormula.appendChild(el('span', 'lx-sum', 'The four probabilities sum to ' +
        pct(sm.p.reduce(function (a, b) { return a + b; }, 0)) + '.'));
    }
  }

  function renderPipe() {
    var order = ['tokens', 'model', 'logits', 'probs', 'select'];
    var at = order.indexOf(A.phase === 'done' ? 'select' : A.phase);
    $$('[data-a-pipe] li').forEach(function (li, i) {
      li.classList.toggle('lx-on', i === at);
      li.classList.toggle('lx-past', i < at);
    });
  }

  function renderA(fresh) {
    var labels = {
      idle: 'Split into tokens', tokens: 'Run the model', model: 'Show the logits',
      logits: 'Apply softmax', probs: 'Select the next token',
      select: A.step < STEPS.length - 1 ? 'Generate next token' : 'Finish',
      done: 'Generation finished'
    };
    aNext.textContent = labels[A.phase];
    aNext.disabled = A.phase === 'done';
    aExplain.textContent = EXPLAIN_A[A.phase];
    var probsOk = A.phase === 'probs' || A.phase === 'select' || A.phase === 'done';
    aViewBtns.forEach(function (b) {
      var v = b.getAttribute('data-a-view');
      b.disabled = !probsOk;
      b.setAttribute('aria-pressed', (probsOk ? A.view : 'logits') === v);
    });
    aTempWrap.hidden = !probsOk;
    renderPipe();
    renderCtx(fresh);
    renderBars();
  }

  var aPlay = $('[data-a-play]'), aTimer = null;
  function stopA() {
    clearInterval(aTimer); aTimer = null;
    aPlay.textContent = A.phase === 'done' ? '\u21BB Replay' : '\u25B6 Play';
    aPlay.setAttribute('aria-pressed', 'false');
  }
  function advance() {
    var fresh = false;
    switch (A.phase) {
      case 'idle': A.phase = 'tokens'; break;
      case 'tokens': A.phase = 'model'; break;
      case 'model': A.phase = 'logits'; A.view = 'logits'; break;
      case 'logits':
        A.phase = 'probs';
        renderA();            /* draw logits first, then morph */
        A.view = 'probs';
        break;
      case 'probs': A.phase = 'select'; A.view = 'probs'; break;
      case 'select':
        var cands = STEPS[A.step];
        var sm = softmax(cands.map(function (c) { return c[1]; }), A.temp);
        var best = 0;
        sm.p.forEach(function (p, i) { if (p > sm.p[best]) best = i; });
        A.generated.push(cands[best][0]);
        fresh = true;
        if (A.step < STEPS.length - 1) {
          A.step += 1;
          A.phase = 'model';
        } else {
          A.phase = 'done';
        }
        break;
    }
    if (A.phase === 'probs') { later(function () { renderA(); }, 30); return; }
    renderA(fresh);
  }
  aNext.addEventListener('click', function () { stopA(); advance(); });
  aPlay.addEventListener('click', function () {
    if (aTimer) { stopA(); return; }
    if (A.phase === 'done') resetA();
    aPlay.textContent = '\u275A\u275A Pause';
    aPlay.setAttribute('aria-pressed', 'true');
    advance();
    aTimer = setInterval(function () {
      if (A.phase === 'done') { stopA(); return; }
      advance();
      if (A.phase === 'done') stopA();
    }, reduce ? 2400 : 1700);
  });

  function resetA() {
    A.phase = 'idle'; A.step = 0; A.view = 'logits'; A.temp = 1; A.generated = [];
    aTemp.value = 1; aTempVal.textContent = '1.00';
    aBars.removeAttribute('data-step');
    renderA();
  }
  aReset.addEventListener('click', function () { stopA(); resetA(); });

  aViewBtns.forEach(function (b) {
    b.addEventListener('click', function () { A.view = b.getAttribute('data-a-view'); renderA(); });
  });

  aTemp.addEventListener('input', function () {
    A.temp = parseFloat(aTemp.value);
    aTempVal.textContent = A.temp.toFixed(2);
    renderBars();
  });

  renderA();
  })();

  /* ── B. Monitoring ──────────────────────────────────────── */
  (function () {
  if (!$('[data-lx-mon]')) return;
  var TARGET = [['the', 0.8], ['user', 0.7], ['is', 0.9], ['testing', 0.6], ['me', 0.8]];
  var GEN = ['I', 'think', 'the', 'user', 'is', 'confused', '.'];
  var B = { n: 0 };
  var bTarget = $('[data-b-target]'), bRows = $('[data-b-rows]'), bProd = $('[data-b-prod]');
  var bExplain = $('[data-b-explain]'), bNext = $('[data-b-next]'), bAll = $('[data-b-all]');
  var bReset = $('[data-b-reset]'), bVs = $('[data-b-vs]'), bGen = $('[data-b-gen]');
  var bMon = $('[data-b-mon]'), bReplay = $('[data-b-replay]'), bMonVal = $('[data-b-monval]');
  var genTimer = null;

  function given(i) {
    var prev = TARGET.slice(0, i).map(function (t) { return t[0]; }).join(' ');
    return 'C' + (prev ? ', ' + prev : '');
  }
  function product(n) {
    var p = 1;
    for (var i = 0; i < n; i++) p *= TARGET[i][1];
    return p;
  }
  function trim(x) { return parseFloat(x.toFixed(5)).toString(); }

  TARGET.forEach(function (t, i) {
    bTarget.appendChild(el('span', 'lx-chip lx-target', t[0]));
    var li = el('li', 'lx-crow');
    li.appendChild(el('code', 'lx-expr', 'P(' + t[0] + ' | ' + given(i) + ')'));
    var track = el('span', 'lx-track');
    track.appendChild(el('span', 'lx-fill'));
    li.appendChild(track);
    li.appendChild(el('span', 'lx-val', ' '));
    bRows.appendChild(li);
    bMon.appendChild(el('span', 'lx-chip lx-target lx-lit', t[0]));
  });

  function renderB() {
    var n = B.n, done = n === TARGET.length;
    $$('.lx-chip', bTarget).forEach(function (c, i) {
      c.classList.toggle('lx-lit', i < n);
      c.classList.toggle('lx-cur', i === n - 1);
    });
    $$('.lx-crow', bRows).forEach(function (r, i) {
      var on = i < n;
      r.classList.toggle('lx-on', on);
      r.classList.toggle('lx-cur', i === n - 1);
      $('.lx-fill', r).style.width = on ? (TARGET[i][1] * 100) + '%' : '0%';
      $('.lx-val', r).textContent = on ? TARGET[i][1].toFixed(2) : ' ';
    });

    bProd.textContent = '';
    if (n === 0) {
      bProd.appendChild(el('span', 'lx-empty', 'Each probability is conditional on C and every target token before it.'));
    } else {
      var f = el('code', 'lx-formula-line', 'P(S | C) = ∏ P(sᵢ | C, s₁ … sᵢ₋₁)');
      var calc = el('code', 'lx-calc',
        TARGET.slice(0, n).map(function (t) { return t[1].toFixed(1); }).join(' × ') +
        ' = ' + trim(product(n)));
      bProd.appendChild(f);
      bProd.appendChild(calc);
      var big = el('span', 'lx-big', pct(product(n), done ? 3 : 1));
      bProd.appendChild(big);
      bProd.appendChild(el('span', 'lx-sub', done ? 'Probability of the complete target sequence given the context' : 'Running product after ' + n + ' of ' + TARGET.length + ' tokens'));
    }

    if (n === 0) {
      bExplain.textContent = 'The model has processed this context. A researcher now wants to investigate whether it considers an evaluation-related continuation likely. They define a target sequence associated with evaluation awareness. The model does not have to generate this sentence.';
    } else if (!done) {
      if (n === 1) {
        bExplain.textContent = 'With only C as context, the model gives "the" a probability of 0.80. The target tokens are scored, not appended to the real conversation.';
      } else {
        bExplain.textContent = 'The researcher feeds in "' + TARGET.slice(0, n - 1).map(function (t) { return t[0]; }).join(' ') +
          '" as if the model had written it, then reads the probability of "' + TARGET[n - 1][0] +
          '". It comes out at ' + TARGET[n - 1][1].toFixed(2) + ', conditional on ' + given(n - 1) + '.';
      }
    } else {
      bExplain.textContent = 'This is the conditional probability of the complete target sequence given the context. It is a number about one exact string of tokens. It is not the probability that the model has a thought or intention.';
    }

    bNext.textContent = n === 0 ? 'Score the first token' : 'Score the next token';
    bNext.disabled = done;
    bAll.disabled = done;
    var wasHidden = bVs.hidden;
    bVs.hidden = !done;
    if (done && wasHidden) {
      bMonVal.textContent = 'P(S | C) = ' + pct(product(TARGET.length), 3);
      playGen();
    }
  }

  function playGen() {
    clearInterval(genTimer);
    bGen.textContent = '';
    var i = 0;
    function add() {
      if (i >= GEN.length) { clearInterval(genTimer); return; }
      bGen.appendChild(el('span', 'lx-chip lx-gen lx-in', GEN[i]));
      i += 1;
    }
    if (reduce) { while (i < GEN.length) add(); return; }
    add();
    genTimer = setInterval(add, 260);
  }

  var bPlay = $('[data-b-play]'), bTimer = null;
  function stopB() {
    clearInterval(bTimer); bTimer = null;
    bPlay.textContent = B.n === TARGET.length ? '\u21BB Replay' : '\u25B6 Play';
    bPlay.setAttribute('aria-pressed', 'false');
  }
  bPlay.addEventListener('click', function () {
    if (bTimer) { stopB(); return; }
    if (B.n === TARGET.length) { clearInterval(genTimer); B.n = 0; renderB(); }
    bPlay.textContent = '\u275A\u275A Pause';
    bPlay.setAttribute('aria-pressed', 'true');
    bTimer = setInterval(function () {
      B.n += 1; renderB();
      if (B.n === TARGET.length) stopB();
    }, reduce ? 2000 : 1300);
  });
  bNext.addEventListener('click', function () { stopB(); if (B.n < TARGET.length) { B.n += 1; renderB(); } });
  bAll.addEventListener('click', function () { stopB(); B.n = TARGET.length; renderB(); stopB(); });
  bReset.addEventListener('click', function () { stopB(); clearInterval(genTimer); B.n = 0; renderB(); stopB(); });
  bReplay.addEventListener('click', playGen);

  renderB();
  })();
})();
