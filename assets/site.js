(function () {
  // Menu mobile
  var toggle = document.querySelector('.menu-toggle');
  var nav = document.getElementById('main-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.textContent = open ? 'Close' : 'Menu';
    });
  }

  // Sottomenu Projects
  [].slice.call(document.querySelectorAll('.sub-toggle')).forEach(function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.closest('.has-sub');
      var open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  });

  // Slideshow
  var gallery = document.querySelector('.gallery[data-count]');
  if (!gallery) return;
  var slides = [].slice.call(gallery.querySelectorAll('.slide'));
  var nums = [].slice.call(gallery.querySelectorAll('.num'));
  var thumbsWrap = gallery.querySelector('.thumbnails');
  var toggleThumbs = gallery.querySelector('.thumbnail-toggle');
  var current = 0;

  function show(i) {
    if (!slides.length) return;
    current = (i + slides.length) % slides.length;
    slides.forEach(function (s, k) { s.classList.toggle('is-active', k === current); });
    nums.forEach(function (n, k) { n.classList.toggle('is-active', k === current); });
    var next = slides[(current + 1) % slides.length].querySelector('img');
    if (next) next.loading = 'eager';
  }

  gallery.addEventListener('click', function (e) {
    var t = e.target.closest('button');
    if (!t) return;
    if (t.classList.contains('prev-slide')) show(current - 1);
    else if (t.classList.contains('next-slide')) show(current + 1);
    else if (t.classList.contains('num') || t.classList.contains('thumb')) {
      show(parseInt(t.getAttribute('data-index'), 10));
      if (t.classList.contains('thumb')) setThumbs(false);
    }
  });

  function setThumbs(on) {
    if (!thumbsWrap) return;
    thumbsWrap.hidden = !on;
    gallery.classList.toggle('show-thumbs', on);
    if (toggleThumbs) toggleThumbs.textContent = on ? 'hide thumbnails' : 'show thumbnails';
  }
  if (toggleThumbs) toggleThumbs.addEventListener('click', function () { setThumbs(thumbsWrap.hidden); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowRight') show(current + 1);
    if (e.key === 'ArrowLeft') show(current - 1);
  });

  // Swipe
  var x0 = null;
  gallery.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
  gallery.addEventListener('touchend', function (e) {
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 40) show(current + (dx < 0 ? 1 : -1));
    x0 = null;
  });

  show(0);
})();
