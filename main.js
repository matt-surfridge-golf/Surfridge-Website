/* Surfridge Golf Co. — small progressive-enhancement layer */
(function () {
  "use strict";

  /* Mobile nav toggle ---------------------------------------------------- */
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", String(!open));
      toggle.setAttribute("aria-expanded", String(!open));
    });

    nav.addEventListener("click", function (e) {
      if (e.target.closest("a") && window.matchMedia("(max-width: 860px)").matches) {
        nav.setAttribute("data-open", "false");
        toggle.setAttribute("aria-expanded", "false");
      }
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.getAttribute("data-open") === "true") {
        nav.setAttribute("data-open", "false");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }

  /* Scroll reveal -------------------------------------------------------- */
  var reveals = document.querySelectorAll("[data-reveal]");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!reveals.length) return;

  if (reduce || !("IntersectionObserver" in window)) {
    reveals.forEach(function (el) { el.classList.add("is-visible"); });
    return;
  }

  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
  );

  reveals.forEach(function (el, i) {
    el.style.transitionDelay = Math.min(i % 4, 3) * 70 + "ms";
    io.observe(el);
  });

  /* Newsletter form (no backend — replace action with your endpoint) ------ */
  var form = document.querySelector("[data-newsletter]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var status = form.querySelector("[data-form-status]");
      var email = form.querySelector('input[type="email"]');
      if (!email || !email.value) return;
      if (status) {
        status.textContent = "Thanks — you're on the list. Check your inbox to confirm.";
        status.setAttribute("data-state", "success");
      }
      form.reset();
    });
  }
})();
