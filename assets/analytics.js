/* =====================================================================
   Aetas in the Workplace â€” Analytics & Cookie Consent
   --------------------------------------------------------------------
   Loads Cookiebot first (shows consent banner). Only loads GA4 and
   Microsoft Clarity AFTER the visitor accepts the "statistics" category.

   Shares the Aetas Group Cookiebot account with aetas-wealth.com, but
   uses ITW-specific GA4 and Clarity properties.

   IDs:
     Cookiebot: f87c63d7-fd2d-4dfd-8854-081181829426  (shared with Wealth)
     GA4:       G-HNH05BKNFX                          (ITW-specific)
     Clarity:   wtnjld3lda                            (ITW-specific)

   To change any ID later, edit the three constants below.
   ===================================================================== */
(function () {
  'use strict';

  var COOKIEBOT_ID = '8950e961-dd22-4ba3-bce7-b59e1fe40193';
  var GA4_ID = 'G-HNH05BKNFX';
  var CLARITY_ID = 'wtnjld3lda';

  // --- Step 1: inject Cookiebot consent banner script -----------------
  var cb = document.createElement('script');
  cb.id = 'Cookiebot';
  cb.src = 'https://consent.cookiebot.com/uc.js';
  cb.setAttribute('data-cbid', COOKIEBOT_ID);
  cb.setAttribute('data-blockingmode', 'auto');
  cb.type = 'text/javascript';
  document.head.appendChild(cb);

  // --- Step 2: define GA4 loader (only called after consent) ----------
  function loadGA4() {
    if (window.__aetasGA4Loaded) return;
    window.__aetasGA4Loaded = true;

    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA4_ID;
    document.head.appendChild(s);

    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag('js', new Date());
    gtag('config', GA4_ID, { anonymize_ip: true });
  }

  // --- Step 3: define Clarity loader (only called after consent) ------
  function loadClarity() {
    if (window.__aetasClarityLoaded) return;
    window.__aetasClarityLoaded = true;

    (function (c, l, a, r, i, t, y) {
      c[a] = c[a] || function () { (c[a].q = c[a].q || []).push(arguments); };
      t = l.createElement(r); t.async = 1; t.src = 'https://www.clarity.ms/tag/' + i;
      y = l.getElementsByTagName(r)[0]; y.parentNode.insertBefore(t, y);
    })(window, document, 'clarity', 'script', CLARITY_ID);
  }

  // --- Step 4: load trackers only when "statistics" consent is given --
  function maybeLoadTrackers() {
    if (window.Cookiebot && window.Cookiebot.consent && window.Cookiebot.consent.statistics) {
      loadGA4();
      loadClarity();
    }
  }

  // Fires after Cookiebot loads with an existing valid consent cookie
  window.addEventListener('CookiebotOnLoad', maybeLoadTrackers);

  // Fires when the user clicks Accept on the banner
  window.addEventListener('CookiebotOnAccept', maybeLoadTrackers);
})();


