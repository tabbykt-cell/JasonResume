/* ==========================================================================
   jasoncdixon.com — progressive enhancements
   Scroll reveal, stat count-up, cookie-consent-gated Google Analytics.
   The site is fully usable with this file blocked or disabled.
   ========================================================================== */
(function () {
  'use strict';

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- Scroll reveal ---------------------------------------------------- */
  var targets = document.querySelectorAll(
    '.section .h2, .section .note, .card, .callout, .stat, .disc, .role, .job, .quote, .shot, .audience > div, .colhead, .deflist, .cred, .split__rail .kicker'
  );

  if (!reduce && 'IntersectionObserver' in window) {
    targets.forEach(function (el) {
      el.classList.add('reveal');
      var p = el.parentElement; // stagger siblings that share a parent
      if (p) {
        var idx = (p.__revealCount = (p.__revealCount || 0) + 1) - 1;
        el.style.setProperty('--d', Math.min(idx * 70, 420) + 'ms');
      }
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---- Stat count-up ---------------------------------------------------- */
  var stats = document.querySelectorAll('.stat__num');
  if (stats.length) {
    var animateStat = function (el) {
      var text = el.textContent.trim();               // e.g. "50%+", "30%", "20+"
      var m = text.match(/^(\d+)(.*)$/);
      if (!m) return;
      var end = parseInt(m[1], 10), suffix = m[2] || '';
      var t0 = null, dur = 1100;
      var step = function (ts) {
        if (!t0) t0 = ts;
        var p = Math.min((ts - t0) / dur, 1);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(end * eased) + suffix;
        if (p < 1) requestAnimationFrame(step);
        else el.textContent = text;
      };
      requestAnimationFrame(step);
    };
    if (!reduce && 'IntersectionObserver' in window) {
      var seen = false;
      var sio = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && !seen) {
            seen = true;
            stats.forEach(animateStat);
            sio.disconnect();
          }
        });
      }, { threshold: 0.4 });
      sio.observe(stats[0].closest('.band') || stats[0]);
    }
  }

  /* ---- Cookie consent + Google Analytics 4 ------------------------------ */
  /* GA loads ONLY after the visitor accepts. */
  var GA_ID = 'G-ZXJ928CLD4';
  var banner = document.getElementById('ccBanner');
  if (banner && GA_ID && GA_ID.indexOf('G-XXXX') !== 0) {
    var KEY = 'cc-consent';
    var loadGA = function () {
      if (window.__gaLoaded) return; window.__gaLoaded = true;
      var s = document.createElement('script');
      s.async = true;
      s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
      document.head.appendChild(s);
      window.dataLayer = window.dataLayer || [];
      function gtag() { dataLayer.push(arguments); }
      window.gtag = gtag;
      gtag('js', new Date());
      gtag('config', GA_ID, { anonymize_ip: true });
    };
    var choice = null;
    try { choice = localStorage.getItem(KEY); } catch (e) {}
    if (choice === 'granted') { loadGA(); }
    else if (choice !== 'denied') { banner.classList.add('on'); }
    document.getElementById('ccAccept').addEventListener('click', function () {
      try { localStorage.setItem(KEY, 'granted'); } catch (e) {}
      banner.classList.remove('on');
      loadGA();
    });
    document.getElementById('ccDecline').addEventListener('click', function () {
      try { localStorage.setItem(KEY, 'denied'); } catch (e) {}
      banner.classList.remove('on');
    });
  }
})();
