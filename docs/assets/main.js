/* ============================================
   AI @ Applied Physics — Main JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ---- Mobile Nav Toggle ----
  const toggle = document.getElementById('nav-toggle');
  const menu = document.getElementById('nav-menu');
  if (toggle && menu) {
    toggle.addEventListener('click', () => {
      menu.classList.toggle('hidden');
      // On mobile, show as column
      if (!menu.classList.contains('hidden')) {
        menu.className = 'flex flex-col absolute top-14 left-0 right-0 bg-slate-900 border-t border-slate-700 py-2 text-sm z-50 shadow-lg';
      } else {
        menu.className = 'hidden md:flex items-center gap-0 text-sm';
      }
    });
  }

  // ---- Accordion ----
  document.querySelectorAll('.accordion-header').forEach(btn => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.accordion-item');
      const wasOpen = item.classList.contains('open');
      item.parentElement.querySelectorAll('.accordion-item').forEach(i => i.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });

  // ---- Tabs ----
  document.querySelectorAll('[data-tab]').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabGroup = btn.closest('.tabs') || btn.closest('[data-tabs]') || btn.parentElement.parentElement;
      tabGroup.querySelectorAll('[data-tab]').forEach(b => {
        b.classList.remove('border-accent', 'text-slate-900', 'font-semibold', 'active');
        b.classList.add('border-transparent', 'text-slate-400');
      });
      tabGroup.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.remove('border-transparent', 'text-slate-400');
      btn.classList.add('border-accent', 'text-slate-900', 'font-semibold', 'active');
      const panel = document.getElementById(btn.dataset.tab);
      if (panel) panel.classList.add('active');
    });
  });

  // ---- Scroll Reveal ----
  const revealEls = document.querySelectorAll('.reveal-on-scroll');
  if (revealEls.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    revealEls.forEach(el => observer.observe(el));
  }

  // ---- Quiz ----
  document.querySelectorAll('.quiz-submit').forEach(btn => {
    btn.addEventListener('click', () => {
      const quiz = btn.closest('.quiz-container');
      let correct = 0, total = 0;
      quiz.querySelectorAll('.quiz-question').forEach(q => {
        total++;
        const answer = q.dataset.answer;
        const selected = q.querySelector('input[type="radio"]:checked');
        const feedback = q.querySelector('.quiz-feedback');
        if (selected && selected.value === answer) {
          correct++;
          if (feedback) { feedback.textContent = 'Correct!'; feedback.className = 'quiz-feedback mt-2 p-3 rounded-lg bg-emerald-50 text-emerald-700 text-sm font-medium'; feedback.style.display = 'block'; }
        } else {
          if (feedback) { feedback.textContent = q.dataset.explanation || 'Not quite — see the explanation above.'; feedback.className = 'quiz-feedback mt-2 p-3 rounded-lg bg-red-50 text-red-700 text-sm font-medium'; feedback.style.display = 'block'; }
        }
      });
      const result = quiz.querySelector('.quiz-score');
      if (result) { result.textContent = `You got ${correct} out of ${total} correct!`; result.style.display = 'block'; }
    });
  });

  // ---- Copy code ----
  document.querySelectorAll('pre').forEach(block => {
    const btn = document.createElement('button');
    btn.textContent = 'Copy';
    btn.className = 'absolute top-2 right-2 bg-white/10 hover:bg-white/20 text-slate-400 text-xs px-2 py-1 rounded border border-white/10 transition';
    block.style.position = 'relative';
    block.appendChild(btn);
    btn.addEventListener('click', () => {
      const code = block.querySelector('code') || block;
      navigator.clipboard.writeText(code.textContent.replace(/Copy$/, '').trim());
      btn.textContent = 'Copied!';
      setTimeout(() => btn.textContent = 'Copy', 1500);
    });
  });

  // Comment form handler removed — community.html has its own Hypha-backed handler
});
