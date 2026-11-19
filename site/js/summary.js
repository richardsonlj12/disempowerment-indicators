// Summary page behaviour: expand a collapsed callout (such as "About the indicators" or
// "Inclusion criteria") from its link or the URL hash, and let Escape dismiss the open
// row-header tooltip (WCAG 1.4.13).
(function () {
  var BOX = "about-the-indicators";

  function openBox(id) {
    var box = document.getElementById(id);
    if (!box) return null;
    var header = box.querySelector(".callout-header");
    var body = box.querySelector(".callout-collapse");
    if (body && !body.classList.contains("show") && header) header.click();
    return box;
  }

  function onHash() {
    var id = decodeURIComponent(location.hash.slice(1));
    if (!id) return;
    var box = document.getElementById(id);
    if (!box || !box.querySelector(".callout-collapse")) return;
    openBox(id);
    box.scrollIntoView();
  }

  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest(".keel-about-link");
    if (link) openBox(BOX);
  });
  window.addEventListener("hashchange", onHash);
  document.addEventListener("DOMContentLoaded", onHash);

  // Escape dismisses only the tooltip that is showing: the row header holding focus,
  // or the one under the pointer.
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    var active = document.activeElement;
    var focused = active && active.closest && active.closest(".keel-rowhead");
    if (focused) focused.classList.add("keel-tip-dismissed");
    document.querySelectorAll(".keel-rowhead:hover").forEach(function (r) {
      r.classList.add("keel-tip-dismissed");
    });
  });

  // Entering a row header (by focus or pointer) shows its tooltip again.
  function undismiss(e) {
    var r = e.target.closest && e.target.closest(".keel-rowhead");
    if (r) r.classList.remove("keel-tip-dismissed");
  }
  document.addEventListener("focusin", undismiss);
  document.addEventListener("mouseover", function (e) {
    var r = e.target.closest && e.target.closest(".keel-rowhead");
    // Moving between children of the same row header is not a new entry.
    var from = e.relatedTarget && e.relatedTarget.closest && e.relatedTarget.closest(".keel-rowhead");
    if (r && from !== r) r.classList.remove("keel-tip-dismissed");
  });
})();
