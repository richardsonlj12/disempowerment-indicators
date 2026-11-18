// Summary page behaviour: expand the "About the indicators" callout from its link or URL hash,
// and let Escape dismiss an open row-header tooltip (WCAG 1.4.13).
(function () {
  var BOX = "about-the-indicators";

  function openBox() {
    var box = document.getElementById(BOX);
    if (!box) return;
    var header = box.querySelector(".callout-header");
    var body = box.querySelector(".callout-collapse");
    if (!body || body.classList.contains("show")) return;
    if (header) header.click();
  }

  function onHash() {
    if (location.hash === "#" + BOX) {
      openBox();
      var box = document.getElementById(BOX);
      if (box) box.scrollIntoView();
    }
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest(".keel-about-link");
    if (link) openBox();
  });
  window.addEventListener("hashchange", onHash);
  document.addEventListener("DOMContentLoaded", onHash);

  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    document.querySelectorAll(".keel-rowhead").forEach(function (r) { r.classList.add("keel-tip-dismissed"); });
  });
  function undismiss(e) {
    var r = e.target.closest && e.target.closest(".keel-rowhead");
    if (r) r.classList.remove("keel-tip-dismissed");
  }
  document.addEventListener("mouseout", function (e) {
    if (e.target.closest && e.target.closest(".keel-rowhead") &&
        !(e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest(".keel-rowhead"))) undismiss(e);
  });
  document.addEventListener("focusout", undismiss);
})();
