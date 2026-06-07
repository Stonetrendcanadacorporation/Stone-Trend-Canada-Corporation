// Main JS for Stone Trend site

function getConfigBasePath() {
  const pathname = window.location.pathname || "";
  const segments = pathname.split("/").filter(Boolean);
  const depth = Math.max(0, segments.length - 1);
  return Array(depth).fill("..").join("/") + (depth ? "/" : "");
}

function buildMapEmbedUrl(input) {
  if (!input || !input.trim()) return "";
  const s = input.trim();
  if (s.startsWith("http")) {
    try {
      const u = new URL(s);
      if (u.hostname.includes("google.com") || u.hostname.includes("goo.gl")) {
        const q = u.searchParams.get("q");
        if (q) return "https://www.google.com/maps?q=" + encodeURIComponent(q) + "&output=embed";
        return s + (s.includes("output=embed") ? "" : (s.includes("?") ? "&" : "?") + "output=embed");
      }
    } catch (e) {}
    return s;
  }
  return "https://www.google.com/maps?q=" + encodeURIComponent(s) + "&output=embed";
}

function applyContactInfo(v) {
  const emailEl = document.getElementById("contact-display-email");
  const phoneEl = document.getElementById("contact-display-phone");
  const officeNameEl = document.getElementById("contact-display-office-name");
  const addressEl = document.getElementById("contact-display-address");
  const cityEl = document.getElementById("contact-display-address-city");
  const hoursEl = document.getElementById("contact-display-hours");
  const inquiriesHeading = document.querySelector("[data-content-field='contact-inquiries-heading']");
  const officeHeading = document.querySelector("[data-content-field='contact-office-heading']");
  const hoursLabel = document.querySelector("[data-content-field='contact-hours-label']");
  const mapIframe = document.getElementById("contact-map-iframe");
  if (emailEl) {
    emailEl.textContent = v.email || "";
    emailEl.href = "mailto:" + (v.email || "");
  }
  if (phoneEl) {
    phoneEl.textContent = v.phone || "";
    phoneEl.href = "tel:" + (v.phone || "").replace(/\D/g, "");
  }
  if (officeNameEl) officeNameEl.innerHTML = (v.officeName || "").replace(/\n/g, "<br>");
  if (addressEl) addressEl.textContent = v.address || "";
  if (cityEl) cityEl.textContent = v.addressCity || "";
  if (hoursEl) hoursEl.innerHTML = (v.hours || "").replace(/\n/g, "<br>");
  if (inquiriesHeading) inquiriesHeading.textContent = v.inquiriesHeading || "General Inquiries";
  if (officeHeading) officeHeading.textContent = v.officeHeading || "Office";
  if (hoursLabel) hoursLabel.textContent = v.hoursLabel || "Store hours";
  if (mapIframe && v.mapAddress) {
    const embedUrl = buildMapEmbedUrl(v.mapAddress);
    if (embedUrl) mapIframe.src = embedUrl;
  }
}

function applyHeaderLogo(url) {
  const brand = document.querySelector(".site-header .brand, .site-header a.brand");
  const loaderLogo = document.getElementById("loader-logo-container") || document.querySelector(".loader-logo");
  const safeUrl = url && url.trim() ? url.trim().replace(/"/g, "&quot;") : "";
  const imgTag =
    '<img src="' +
    safeUrl +
    '" alt="Logo" class="brand-logo-img" loading="eager">';
  const loaderImgTag =
    '<img src="' +
    safeUrl +
    '" alt="Logo" class="loader-logo-img" loading="eager">';

  if (brand) {
    if (safeUrl) {
      brand.innerHTML = imgTag;
    } else {
      const template = document.getElementById("default-header-logo");
      if (template && template.content) {
        brand.innerHTML = "";
        brand.appendChild(template.content.cloneNode(true));
      }
    }
  }

  if (loaderLogo) {
    if (safeUrl) {
      loaderLogo.innerHTML = loaderImgTag;
    } else {
      const template = document.getElementById("default-loader-logo");
      if (template && template.content) {
        loaderLogo.innerHTML = "";
        loaderLogo.appendChild(template.content.cloneNode(true));
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const base = getConfigBasePath();
  fetch("/api/get-config")
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => {
      if (data && data.contactInfo) applyContactInfo(data.contactInfo);
      if (data && data.headerLogoUrl !== undefined) applyHeaderLogo(data.headerLogoUrl);
    })
    .catch(() => {});

  const loader = document.querySelector(".loader-overlay");
  const yearEl = document.getElementById("year");
  const navToggle = document.querySelector(".nav-toggle");
  const mainNav = document.querySelector(".main-nav");
  const filterButtons = document.querySelectorAll(".filter-btn");
  const galleryItems = document.querySelectorAll(".gallery-item");
  const heroMedia = document.querySelector(".hero-media");

  // Year in footer
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Logo reveal: graphic appears, then overlay fades
  const hideLoader = () => {
    if (loader) {
      loader.classList.add("is-hidden");
    }
  };

  if (loader) {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      hideLoader();
    } else if (sessionStorage.getItem("st-loader-seen")) {
      hideLoader();
    } else {
      sessionStorage.setItem("st-loader-seen", "1");
      const loaderDelay = window.matchMedia("(max-width: 960px)").matches ? 1200 : 2000;
      setTimeout(hideLoader, loaderDelay);
      loader.addEventListener("click", hideLoader, { once: true });
    }
  }

  // Mobile navigation toggle
  if (navToggle && mainNav) {
    let navOverlay = document.querySelector(".nav-overlay");
    if (!navOverlay) {
      navOverlay = document.createElement("div");
      navOverlay.className = "nav-overlay";
      navOverlay.setAttribute("aria-hidden", "true");
      document.body.appendChild(navOverlay);
    }

    const setNavOpen = (open) => {
      mainNav.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
      navOverlay.classList.toggle("is-visible", open);
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      navOverlay.setAttribute("aria-hidden", open ? "false" : "true");
    };

    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-controls", "site-main-nav");
    if (!mainNav.id) {
      mainNav.id = "site-main-nav";
    }

    navToggle.addEventListener("click", (e) => {
      e.stopPropagation();
      setNavOpen(!mainNav.classList.contains("is-open"));
    });

    navOverlay.addEventListener("click", () => {
      setNavOpen(false);
    });

    document.addEventListener("click", (e) => {
      if (!mainNav.classList.contains("is-open")) return;
      if (e.target.closest(".main-nav") || e.target.closest(".nav-toggle")) return;
      setNavOpen(false);
    });

    mainNav.addEventListener("click", (e) => {
      if (e.target.closest("a")) {
        setNavOpen(false);
      }
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && mainNav.classList.contains("is-open")) {
        setNavOpen(false);
      }
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 960 && mainNav.classList.contains("is-open")) {
        setNavOpen(false);
      }
    });
  }

  // Smooth scroll for internal links (enhanced)
  document.body.addEventListener("click", (e) => {
    const target = e.target.closest('a[href^="#"]');
    if (!target) return;
    const hash = target.getAttribute("href");
    if (!hash || hash === "#") return;
    const section = document.querySelector(hash);
    if (!section) return;
    e.preventDefault();
    const headerOffset = document.querySelector(".site-header")?.offsetHeight || 0;
    const elementPos = section.getBoundingClientRect().top + window.scrollY;
    const offsetPos = elementPos - headerOffset + 4;
    window.scrollTo({ top: offsetPos, behavior: "smooth" });
  });

  // IntersectionObserver for fade-up animations
  const animatedElements = document.querySelectorAll("[data-animate]");
  if ("IntersectionObserver" in window && animatedElements.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const delay = el.getAttribute("data-animate-delay");
            if (delay) {
              el.style.setProperty("--delay", delay);
            }
            el.classList.add("is-visible");
            observer.unobserve(el);
          }
        });
      },
      {
        threshold: 0.18,
        rootMargin: "0px 0px -10% 0px",
      }
    );

    animatedElements.forEach((el) => observer.observe(el));
  } else {
    // Fallback: show all
    animatedElements.forEach((el) => el.classList.add("is-visible"));
  }

  // Subtle parallax for hero background
  if (heroMedia) {
    window.addEventListener("scroll", () => {
      const scrollY = window.scrollY || window.pageYOffset;
      const offset = Math.min(scrollY * 0.15, 80);
      heroMedia.style.transform = `translateY(${offset}px)`;
    });
  }

  // Gallery filter
  if (filterButtons.length && galleryItems.length) {
    filterButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const filter = btn.getAttribute("data-filter");
        filterButtons.forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");

        galleryItems.forEach((item) => {
          const category = item.getAttribute("data-category");
          const show = filter === "all" || filter === category;
          item.style.display = show ? "" : "none";
        });
      });
    });
  }

  // Service flip cards: tap to flip on touch devices
  document.querySelectorAll(".service-card--flip").forEach((card) => {
    card.addEventListener("click", () => {
      if (window.matchMedia("(hover: none)").matches) {
        card.classList.toggle("is-flipped");
      }
    });
  });

  const FORM_ENDPOINT = "/api/send-form";
  const CONFIG_ENDPOINT = "/api/get-config";
  let FORM_EMAIL = "owenkoja@stonetrend.ca";

  fetch(CONFIG_ENDPOINT)
    .then((r) => r.ok ? r.json() : null)
    .then((data) => {
      if (data && data.formEmail) FORM_EMAIL = data.formEmail;
    })
    .catch(() => {});
  window.addEventListener("formEmailUpdated", (e) => {
    if (e.detail && e.detail.formEmail) FORM_EMAIL = e.detail.formEmail;
  });

  function quoteFormMailtoLink(form) {
    const name = (form.querySelector("#name")?.value || "").trim();
    const company = (form.querySelector("#company")?.value || "").trim();
    const email = (form.querySelector("#email")?.value || "").trim();
    const phone = (form.querySelector("#phone")?.value || "").trim();
    const projectType = (form.querySelector("#project-type")?.value || "").trim();
    const location = (form.querySelector("#location")?.value || "").trim();
    const measurements = (form.querySelector("#measurements")?.value || "").trim();
    const materialsPref = (form.querySelector("#materials-preference")?.value || "").trim();
    const subject = "Stone Trend – Project submission" + (name ? " from " + name : "");
    const body = [
      "Project submission from Stone Trend website",
      "",
      "Name: " + (name || "—"),
      "Company: " + (company || "—"),
      "Email: " + (email || "—"),
      "Phone: " + (phone || "—"),
      "Project type: " + (projectType || "—"),
      "Project location: " + (location || "—"),
      "",
      "Measurements & scope:",
      measurements || "—",
      "",
      "Material preferences:",
      materialsPref || "—",
      "",
      "(Please attach any layout images or drawings to this email.)",
    ].join("\r\n");
    return "mailto:" + FORM_EMAIL + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }

  function contactFormMailtoLink(form) {
    const name = (form.querySelector("#contact-name")?.value || "").trim();
    const email = (form.querySelector("#contact-email")?.value || "").trim();
    const company = (form.querySelector("#contact-company")?.value || "").trim();
    const topic = (form.querySelector("#contact-topic")?.value || "").trim();
    const message = (form.querySelector("#contact-message")?.value || "").trim();
    const subject = "Stone Trend – Contact" + (topic ? " [" + topic + "]" : "") + (name ? " from " + name : "");
    const body = [
      "Contact form submission from Stone Trend website",
      "",
      "Name: " + (name || "—"),
      "Email: " + (email || "—"),
      "Company: " + (company || "—"),
      "Topic: " + (topic || "—"),
      "",
      "Message:",
      message || "—",
    ].join("\r\n");
    return "mailto:" + FORM_EMAIL + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }

  function partnerFormMailtoLink(form) {
    const company = (form.querySelector("#partner-company")?.value || "").trim();
    const contactName = (form.querySelector("#partner-contact-name")?.value || "").trim();
    const email = (form.querySelector("#partner-email")?.value || "").trim();
    const phone = (form.querySelector("#partner-phone")?.value || "").trim();
    const tradeType = (form.querySelector("#partner-trade-type")?.value || "").trim();
    const serviceArea = (form.querySelector("#partner-service-area")?.value || "").trim();
    const website = (form.querySelector("#partner-website")?.value || "").trim();
    const notes = (form.querySelector("#partner-notes")?.value || "").trim();
    const subject = "Stone Trend – Partner inquiry" + (company ? " from " + company : contactName ? " from " + contactName : "");
    const body = [
      "Partner inquiry from Stone Trend website",
      "",
      "Company: " + (company || "—"),
      "Primary contact: " + (contactName || "—"),
      "Email: " + (email || "—"),
      "Phone: " + (phone || "—"),
      "Trade / service category: " + (tradeType || "—"),
      "Service area: " + (serviceArea || "—"),
      "",
      "Website / social links:",
      website || "—",
      "",
      "Notes about company:",
      notes || "—",
    ].join("\r\n");
    return "mailto:" + FORM_EMAIL + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
  }

  function showFormMessage(form, type, message, htmlContent) {
    const wrap = form.closest(".quote-layout") || form.closest(".contact-form") || form.closest("section") || form.parentElement;
    let box = wrap.querySelector(".form-message");
    if (!box) {
      box = document.createElement("div");
      box.className = "form-message";
      form.insertAdjacentElement("beforebegin", box);
    }
    box.className = "form-message form-message--" + type;
    if (htmlContent) {
      box.innerHTML = htmlContent;
    } else {
      box.textContent = message;
    }
    box.setAttribute("role", "status");
    if (type === "success") {
      form.reset();
    }
  }

  function setSubmitButton(form, loading) {
    const btn = form.querySelector('button[type="submit"]');
    if (!btn) return;
    if (loading) {
      btn.disabled = true;
      btn.dataset.originalText = btn.textContent;
      btn.textContent = "Sending…";
    } else {
      btn.disabled = false;
      btn.textContent = btn.dataset.originalText || btn.textContent;
    }
  }

  // Quote form: send to server, email goes to you directly (no mail client)
  const quoteForm = document.getElementById("quote-form");
  if (quoteForm) {
    quoteForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const attachmentInput = quoteForm.querySelector("#attachment");
      const maxSize = attachmentInput?.dataset?.maxSize ? parseInt(attachmentInput.dataset.maxSize, 10) : 10485760;
      if (attachmentInput?.files?.length > 0 && attachmentInput.files[0].size > maxSize) {
        showFormMessage(quoteForm, "error", "File size exceeds the 10MB limit. Please choose a smaller file.");
        return;
      }
      const formData = new FormData(quoteForm);
      formData.set("form_type", "quote");
      setSubmitButton(quoteForm, true);
      fetch(FORM_ENDPOINT, { method: "POST", body: formData })
        .then((r) => {
          if (!r.ok) throw new Error("Server error");
          return r.json();
        })
        .then((data) => {
          setSubmitButton(quoteForm, false);
          if (data && data.ok) {
            showFormMessage(quoteForm, "success", "Thank you. Your project has been submitted. We’ll review and get back to you shortly.");
          } else {
            const mailto = quoteFormMailtoLink(quoteForm);
            showFormMessage(quoteForm, "error", null, (data?.error || "Something went wrong.") + ' <a href="' + mailto + '" class="form-message-link">Send via your email app instead</a>');
          }
        })
        .catch(() => {
          setSubmitButton(quoteForm, false);
          const mailto = quoteFormMailtoLink(quoteForm);
          showFormMessage(quoteForm, "error", null, 'Form could not be sent from this page (e.g. viewing locally or server unavailable). <a href="' + mailto + '" class="form-message-link">Send via your email app instead</a>, or email us at <a href="mailto:' + FORM_EMAIL + '">' + FORM_EMAIL + '</a>.');
        });
    });
  }

  // Partner form: send to server
  const partnerForm = document.getElementById("partner-form");
  if (partnerForm) {
    partnerForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const formData = new FormData(partnerForm);
      formData.set("form_type", "partner");
      setSubmitButton(partnerForm, true);
      fetch(FORM_ENDPOINT, { method: "POST", body: formData })
        .then((r) => {
          if (!r.ok) throw new Error("Server error");
          return r.json();
        })
        .then((data) => {
          setSubmitButton(partnerForm, false);
          if (data && data.ok) {
            showFormMessage(partnerForm, "success", "Thank you. Your partner application has been sent. We’ll be in touch.");
          } else {
            const mailto = partnerFormMailtoLink(partnerForm);
            showFormMessage(partnerForm, "error", null, (data?.error || "Something went wrong.") + ' <a href="' + mailto + '" class="form-message-link">Send via your email app instead</a>');
          }
        })
        .catch(() => {
          setSubmitButton(partnerForm, false);
          const mailto = partnerFormMailtoLink(partnerForm);
          showFormMessage(partnerForm, "error", null, 'Form could not be sent from this page. <a href="' + mailto + '" class="form-message-link">Send via your email app instead</a>, or email us at <a href="mailto:' + FORM_EMAIL + '">' + FORM_EMAIL + '</a>.');
        });
    });
  }

  // Contact form: send to server
  const contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const formData = new FormData(contactForm);
      formData.set("form_type", "contact");
      setSubmitButton(contactForm, true);
      fetch(FORM_ENDPOINT, { method: "POST", body: formData })
        .then((r) => {
          if (!r.ok) throw new Error("Server error");
          return r.json();
        })
        .then((data) => {
          setSubmitButton(contactForm, false);
          if (data && data.ok) {
            showFormMessage(contactForm, "success", "Thank you. Your message has been sent. We’ll get back to you soon.");
          } else {
            const mailto = contactFormMailtoLink(contactForm);
            showFormMessage(contactForm, "error", null, (data?.error || "Something went wrong.") + ' <a href="' + mailto + '" class="form-message-link">Send via your email app instead</a>');
          }
        })
        .catch(() => {
          setSubmitButton(contactForm, false);
          const mailto = contactFormMailtoLink(contactForm);
          showFormMessage(contactForm, "error", null, 'Form could not be sent from this page (e.g. viewing locally or server unavailable). <a href="' + mailto + '" class="form-message-link">Send via your email app instead</a>, or email us at <a href="mailto:' + FORM_EMAIL + '">' + FORM_EMAIL + '</a>.');
        });
    });
  }

  // Other forms: placeholder (e.g. admin)
  const forms = document.querySelectorAll("form:not(#quote-form):not(#partner-form):not(#contact-form)");
  forms.forEach((form) => {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      alert("Form submission placeholder. Connect to your backend or form handler.");
    });
  });

});

