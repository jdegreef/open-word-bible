// Accounts on the site, after Ochorus: the sign-in page (/login/, in three
// modes: sign in, ?mode=signup, ?mode=reset), choosing a new password
// (/reset-password/) and the account page (/account/). The API
// (backend/accounts/) is on another host, named by the owb-api meta tag; a
// signed-in browser keeps an API token and a copy of the account in
// localStorage under owb.account (site.js reads the copy for the header's
// menu). All text is inserted with textContent, and the messages are the
// page's language's (i18n/<lang>.json, login.ui and account.ui).
(function () {
  "use strict";
  var API = document.querySelector('meta[name="owb-api"]').content;
  var KEY = "owb.account";
  var LANG = document.documentElement.lang;
  var PREFIX = LANG === "en" ? "" : "/" + LANG;

  function saved() {
    try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; }
  }
  function store(value) {
    try {
      if (value) localStorage.setItem(KEY, JSON.stringify(value));
      else localStorage.removeItem(KEY);
    } catch (e) { /* storage blocked: signed in for this page only */ }
  }

  // A path on this site to go back to, or "": never //host, /\host or
  // control characters (the API checks the same before putting one in a
  // link), and never the sign-in pages themselves.
  function safeRedirect(path) {
    path = path || "";
    if (path.charAt(0) !== "/" || /^\/[\/\\]/.test(path) || /[\x00-\x1f\x7f]/.test(path)) return "";
    if (/^(\/[a-z]{2})?\/(login|reset-password)\//.test(path)) return "";
    return path;
  }
  function redirectParam() {
    return safeRedirect(new URLSearchParams(location.search).get("redirect"));
  }
  function goOn() {
    location.replace(redirectParam() || PREFIX + "/");
  }

  // An error from the API, in the page's language when its code has a
  // message: {"detail": "...", "code": "..."} or {"field": "...", "code": ...}.
  function failure(data, T) {
    var code = Array.isArray(data.code) ? data.code[0] : data.code;
    if (code && T[code]) return T[code];
    if (data.detail) return data.detail;
    for (var k in data) if (k !== "code") return Array.isArray(data[k]) ? data[k][0] : String(data[k]);
    return T.error;
  }

  // options.anonymous: the sign-in calls never send a saved token. A 401
  // otherwise means the token is gone: the saved account is forgotten and
  // the error says signedOut.
  function api(path, options, T) {
    options = options || {};
    var headers = { "Content-Type": "application/json" };
    var account = options.anonymous ? null : saved();
    if (account && account.token) headers.Authorization = "Bearer " + account.token;
    return fetch(API + path, {
      method: options.method || "GET", headers: headers,
      body: options.body ? JSON.stringify(options.body) : undefined
    }).catch(function () {
      throw new Error(T.offline);
    }).then(function (r) {
      if (r.status === 401 && !options.anonymous) {
        store(null);
        var e = new Error(T.error);
        e.signedOut = true;
        throw e;
      }
      if (r.status === 204) return null;
      return r.json().then(function (data) {
        if (!r.ok) throw new Error(failure(data, T));
        return data;
      }, function () { throw new Error(T.error); });
    });
  }

  function showView(root, name) {
    root.querySelectorAll("[data-view]").forEach(function (n) {
      n.hidden = n.getAttribute("data-view") !== name;
    });
  }

  function busy(button, on) {
    button.disabled = on;
    button.setAttribute("aria-busy", on ? "true" : "false");
  }

  // Show/Hide on a password field.
  function passwordToggles(root, T) {
    root.querySelectorAll(".pw-toggle").forEach(function (b) {
      var input = document.getElementById(b.getAttribute("aria-controls"));
      b.addEventListener("click", function () {
        var show = input.type === "password";
        input.type = show ? "text" : "password";
        b.textContent = show ? T.hide : T.show;
        b.setAttribute("aria-pressed", show ? "true" : "false");
      });
    });
  }

  // The sign-in page.
  function loginPage(root) {
    var T = JSON.parse(document.getElementById("login-text").textContent);
    var form = document.getElementById("login-form");
    var error = document.getElementById("login-error");
    var submit = form.querySelector('button[type="submit"]');
    var magic = document.getElementById("magic");
    var titleTail = document.title.replace(/^.*?( · )/, "$1");
    var mode = "sign-in";
    var google = false;   // until /api/auth/methods says Google is set up
    var again = null;   // repeats the last request that sent an email
    var MODES = { signup: "sign-up", reset: "reset" };

    function say(message, field) {
      error.textContent = message || "";
      form.email.setAttribute("aria-invalid", field === "email" ? "true" : "false");
      form.password.setAttribute("aria-invalid", field === "password" ? "true" : "false");
    }

    function href(m) {
      var q = new URLSearchParams();
      if (m !== "sign-in") q.set("mode", m === "sign-up" ? "signup" : "reset");
      if (redirectParam()) q.set("redirect", redirectParam());
      var s = q.toString();
      return location.pathname + (s ? "?" + s : "");
    }

    function setMode(m) {
      mode = m;
      root.setAttribute("data-mode", m);
      root.querySelectorAll("[data-for]").forEach(function (n) {
        n.hidden = n.getAttribute("data-for").split(" ").indexOf(m) < 0;
      });
      if (!google) root.querySelector(".google").hidden = true;
      root.querySelectorAll("[data-mode-link]").forEach(function (a) {
        a.href = href(a.getAttribute("data-mode-link"));
      });
      form.password.autocomplete = m === "sign-up" ? "new-password" : "current-password";
      form.password.required = m !== "reset";
      document.title = root.querySelector('h1 [data-for="' + m + '"]').textContent + titleTail;
      showView(root, "form");
      say("");
    }

    function modeFromUrl() {
      return MODES[new URLSearchParams(location.search).get("mode")] || "sign-in";
    }

    // Switching modes is a real step in the history, so Back works.
    root.addEventListener("click", function (e) {
      var a = e.target.closest("[data-mode-link]");
      if (!a) return;
      e.preventDefault();
      history.pushState(null, "", a.href);
      setMode(a.getAttribute("data-mode-link"));
      form.email.focus();
    });
    window.addEventListener("popstate", function () { setMode(modeFromUrl()); });

    function signedIn(data) {
      store({ token: data.token, user: data.user });
      goOn();
    }

    function emailOk() {
      var email = form.email.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        say(email ? T.invalid_email : T.need_email, "email");
        form.email.focus();
        return null;
      }
      return email;
    }

    // Requests that send an email end on the "Check your email" card.
    function send(path, body, sentKey, button) {
      function request() {
        return api(path, { method: "POST", body: body, anonymous: true }, T);
      }
      busy(button, true);
      return request().then(function () {
        again = request;
        document.getElementById("sent-text").textContent = T[sentKey].replace("{email}", body.email);
        document.getElementById("resend-note").textContent = "";
        showView(root, "sent");
        cooldown();
        root.querySelector('[data-view="sent"] h2').focus();
      }).catch(function (err) { say(err.message); })
        .then(function () { busy(button, false); });
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      say("");
      var email = emailOk();
      if (!email) return;
      var password = form.password.value;
      if (mode === "reset") {
        send("/api/auth/reset", { email: email, lang: LANG }, "sent_reset", submit);
        return;
      }
      if (!password || (mode === "sign-up" && password.length < 8)) {
        say(mode === "sign-up" ? T.weak_password : T.invalid_credentials, "password");
        form.password.focus();
        return;
      }
      if (mode === "sign-up") {
        send("/api/auth/sign-up", { email: email, password: password, lang: LANG, redirect: redirectParam() },
          "sent_sign_up", submit);
        return;
      }
      busy(submit, true);
      api("/api/auth/sign-in", { method: "POST", body: { email: email, password: password }, anonymous: true }, T)
        .then(signedIn)
        .catch(function (err) { say(err.message); busy(submit, false); });
    });

    magic.addEventListener("click", function () {
      say("");
      var email = emailOk();
      if (email) send("/api/auth/link", { email: email, lang: LANG, redirect: redirectParam() }, "sent_link", magic);
    });

    // Resend, at most every 30 seconds.
    var resend = document.getElementById("resend");
    var resendLabel = resend.textContent;
    var timer = null;
    function cooldown() {
      var left = 30;
      clearInterval(timer);
      resend.disabled = true;
      resend.textContent = T.resend_in.replace("{n}", left);
      timer = setInterval(function () {
        left -= 1;
        if (left > 0) { resend.textContent = T.resend_in.replace("{n}", left); return; }
        clearInterval(timer);
        resend.disabled = false;
        resend.textContent = resendLabel;
      }, 1000);
    }
    resend.addEventListener("click", function () {
      var note = document.getElementById("resend-note");
      if (!again) return;
      resend.disabled = true;
      again().then(function () { note.textContent = T.resent; cooldown(); })
        .catch(function (err) { note.textContent = err.message; resend.disabled = false; });
    });

    // Google: the API sends the browser to Google and back to #google=.
    document.getElementById("google").addEventListener("click", function () {
      var q = new URLSearchParams({ lang: LANG });
      if (redirectParam()) q.set("redirect", redirectParam());
      location.href = API + "/api/auth/google/start?" + q.toString();
    });
    fetch(API + "/api/auth/methods").then(function (r) { return r.json(); }).then(function (m) {
      google = !!m.google;
      var g = root.querySelector(".google");
      g.hidden = !google || g.getAttribute("data-for").split(" ").indexOf(mode) < 0;
    }).catch(function () { /* offline: no Google button */ });

    passwordToggles(root, T);
    setMode(modeFromUrl());

    // Arriving from an email (#token=...): the link is used only when the
    // reader presses Finish, so a scanner that opens it does not use it up.
    // From Google (#google=...) it is used at once. Either way the secret
    // leaves the address bar at once and stays in this page.
    var m = /^#(token|google|error)=([\w-]+)$/.exec(location.hash);
    if (m) {
      try { history.replaceState(null, "", location.pathname + location.search); } catch (e) { /* ignore */ }
    }
    function redeem(secret, button) {
      if (button) busy(button, true);
      api("/api/auth/verify", { method: "POST", body: { token: secret }, anonymous: true }, T)
        .then(signedIn)
        .catch(function (err) {
          if (button) busy(button, false);
          setMode("sign-in");
          say(err.message);
        });
    }
    if (m && m[1] === "token") {
      showView(root, "confirm");
      document.title = root.querySelector('[data-view="confirm"] h2').textContent + titleTail;
      var finish = document.getElementById("finish");
      finish.addEventListener("click", function () { redeem(m[2], finish); });
      finish.focus();
    } else if (m && m[1] === "google") {
      redeem(m[2]);
    } else if (m && m[1] === "error") {
      say(T[m[2]] || T.error);
    } else if (saved() && mode !== "reset") {
      goOn();   // already signed in (but may ask for a link to choose a password)
    }
  }

  // Choosing a new password from a reset link.
  function resetPage(root) {
    var T = JSON.parse(document.getElementById("login-text").textContent);
    var m = /^#token=([\w-]+)$/.exec(location.hash);
    passwordToggles(root, T);
    if (!m) { showView(root, "missing"); return; }
    var secret = m[1];
    try { history.replaceState(null, "", location.pathname); } catch (e) { /* ignore */ }
    showView(root, "form");
    var form = document.getElementById("reset-form");
    var input = document.getElementById("new-password");
    var error = document.getElementById("reset-error");
    var submit = form.querySelector('button[type="submit"]');
    input.focus();
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (input.value.length < 8) { error.textContent = T.weak_password; input.focus(); return; }
      error.textContent = "";
      busy(submit, true);
      api("/api/auth/reset/confirm", { method: "POST", body: { token: secret, password: input.value }, anonymous: true }, T)
        .then(function (data) {
          store({ token: data.token, user: data.user });
          document.documentElement.classList.add("signed-in");   // the header's "Sign in" goes
          showView(root, "done");
          root.querySelector('[data-view="done"] .button').focus();
        }).catch(function (err) {
          error.textContent = err.message;
          busy(submit, false);
        });
    });
  }

  // The account page.
  function accountPage(root) {
    var T = JSON.parse(document.getElementById("account-text").textContent);
    var login = PREFIX + "/login/";
    function toLogin() { location.replace(login + "?redirect=" + encodeURIComponent(location.pathname)); }
    // A sign-in email sent before /login/ existed linked here.
    if (/^#token=/.test(location.hash)) { location.replace(login + location.hash); return; }
    if (!saved()) { toLogin(); return; }

    var nameForm = document.getElementById("name-form");
    var nameNote = document.getElementById("name-note");

    function render(user) {
      document.getElementById("me-name").textContent = user.display_name || user.email;
      document.getElementById("me-email").textContent = user.email;
      document.getElementById("me-roles").textContent = user.roles.length
        ? user.roles.map(function (r) { return r.label; }).join(", ") : T.reader;
      document.getElementById("me-joined").textContent = new Date(user.joined + "T00:00:00")
        .toLocaleDateString(LANG, { year: "numeric", month: "long", day: "numeric" });
      document.getElementById("me-password").textContent = user.has_password ? T.password_set : T.password_none;
      document.getElementById("set-password").hidden = !!user.has_password;
      if (document.activeElement !== nameForm.display_name) nameForm.display_name.value = user.display_name || "";
      root.hidden = false;
    }
    function keep(user) {
      var account = saved();
      if (account) { account.user = user; store(account); }
      render(user);
      // The header's menu (site.js) shows the name too.
      var menu = document.querySelector(".account-menu");
      if (menu) {
        menu.querySelector(".account-initial").textContent = (user.display_name || user.email).charAt(0).toUpperCase();
        menu.querySelector(".who-name").textContent = user.display_name || "";
      }
    }
    function failed(err, note) {
      if (err.signedOut) toLogin();
      else note.textContent = err.message;
    }

    nameForm.addEventListener("submit", function (e) {
      e.preventDefault();
      api("/api/me", { method: "PATCH", body: { display_name: nameForm.display_name.value } }, T)
        .then(function (user) { keep(user); nameNote.textContent = T.saved; })
        .catch(function (err) { failed(err, nameNote); });
    });

    document.getElementById("sign-out").addEventListener("click", function () {
      api("/api/auth/sign-out", { method: "POST" }, T).catch(function () { /* already signed out */ })
        .then(function () { store(null); location.replace(PREFIX + "/"); });
    });

    // Your data: the account, the bookmarks, highlights and place kept with
    // it (/api/reading), and this device's reading, as JSON.
    document.getElementById("download").addEventListener("click", function () {
      function read(key) {
        try { var v = localStorage.getItem(key); return v && v.charAt(0) === "{" ? JSON.parse(v) : v; }
        catch (e) { return null; }
      }
      var button = this;
      busy(button, true);
      api("/api/reading", {}, T).catch(function () { return null; }).then(function (reading) {
        busy(button, false);
        save({
          exported: new Date().toISOString(),
          account: saved() && saved().user,
          reading: reading,
          device: { settings: read("owb.settings"), place: read("owb.place"), marks: read("owb.marks"),
                    theme: read("owb-theme"), language: read("owb-lang") }
        });
      });
    });
    function save(data) {
      var a = document.createElement("a");
      a.href = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }));
      a.download = "open-word-bible-account.json";
      document.body.appendChild(a);
      a.click();
      setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    }

    // The danger zone: each button asks to be clicked again within 4 seconds.
    var dangerNote = document.getElementById("danger-note");
    function twoClicks(button, act) {
      var label = button.textContent;
      var armed = null;
      function disarm() {
        clearTimeout(armed);
        armed = null;
        button.textContent = label;
        button.classList.remove("armed");
      }
      button.addEventListener("click", function () {
        if (armed) { disarm(); act(); return; }
        button.textContent = T.confirm;
        button.classList.add("armed");
        armed = setTimeout(disarm, 4000);
      });
    }
    twoClicks(document.getElementById("clear-device"), function () {
      try { localStorage.removeItem("owb.settings"); localStorage.removeItem("owb.place"); } catch (e) { /* none */ }
      dangerNote.textContent = T.cleared;
    });
    twoClicks(document.getElementById("delete-account"), function () {
      api("/api/me", { method: "DELETE" }, T).then(function () {
        store(null);
        location.replace(PREFIX + "/");
      }).catch(function (err) { failed(err, dangerNote); });
    });

    render(saved().user);
    api("/api/me", {}, T).then(keep).catch(function (err) {
      if (err.signedOut) toLogin();   // offline: keep the saved copy
    });
  }

  var root;
  if ((root = document.getElementById("login"))) loginPage(root);
  else if ((root = document.getElementById("reset"))) resetPage(root);
  else if ((root = document.getElementById("account"))) accountPage(root);
})();
