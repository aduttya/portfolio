// Portfolio — main.js

// Mobile back button (post pages, research paper) is fixed on screen so
// it stays reachable while scrolling, but should only show near the top —
// otherwise it ends up floating over unrelated body text further down.
// Hidden once its header panel has fully scrolled out of view.
(function () {
  var back = document.querySelector(".post-hero-meta .back");
  if (!back || !("IntersectionObserver" in window)) return;

  var header = back.closest(".panel");
  if (!header) return;

  var observer = new IntersectionObserver(function (entries) {
    back.classList.toggle("is-hidden", !entries[0].isIntersecting);
  });
  observer.observe(header);
})();
