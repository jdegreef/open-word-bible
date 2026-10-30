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

  // Passkeys (WebAuthn): the API's options come as JSON, with its binary
  // fields in base64url; the browser's answer goes back the same way.
  function fromB64(text) {
    text = text.replace(/-/g, "+").replace(/_/g, "/");
    while (text.length % 4) text += "=";
    var bin = atob(text), out = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out.buffer;
  }
  function toB64(buf) {
    var bytes = new Uint8Array(buf), bin = "";
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function credentialJSON(c) {
    var r = c.response, out = { id: c.id, rawId: toB64(c.rawId), type: c.type,
                                response: { clientDataJSON: toB64(r.clientDataJSON) },
                                clientExtensionResults: c.getClientExtensionResults ? c.getClientExtensionResults() : {} };
    if (r.attestationObject) {
      out.response.attestationObject = toB64(r.attestationObject);
      if (r.getTransports) out.response.transports = r.getTransports();
    } else {
      out.response.authenticatorData = toB64(r.authenticatorData);
      out.response.signature = toB64(r.signature);
      out.response.userHandle = r.userHandle ? toB64(r.userHandle) : null;
    }
    return out;
  }
  function passkeysWork() { return !!(window.PublicKeyCredential && navigator.credentials); }
  function makePasskey(options) {
    options.challenge = fromB64(options.challenge);
    options.user.id = fromB64(options.user.id);
    (options.excludeCredentials || []).forEach(function (c) { c.id = fromB64(c.id); });
    return navigator.credentials.create({ publicKey: options }).then(credentialJSON);
  }
  function usePasskey(options) {
    options.challenge = fromB64(options.challenge);
    (options.allowCredentials || []).forEach(function (c) { c.id = fromB64(c.id); });
    return navigator.credentials.get({ publicKey: options }).then(credentialJSON);
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

    // A passkey: the device's lock, no address needed.
    var passkey = document.getElementById("passkey");
    passkey.hidden = !passkeysWork();
    passkey.addEventListener("click", function () {
      say("");
      busy(passkey, true);
      api("/api/auth/passkey/options", { method: "POST", anonymous: true }, T).then(usePasskey).then(function (credential) {
        return api("/api/auth/passkey", { method: "POST", body: { credential: credential }, anonymous: true }, T);
      }).then(signedIn).catch(function (err) {
        say(err && err.name === "NotAllowedError" ? T.passkey_cancelled : (err && err.message) || T.passkey_failed);
        busy(passkey, false);
      });
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
    // A change-of-address link (accounts/controls.py): used here, signed in
    // or not, and the address it moved to said.
    var moved = /^#email=([\w-]+)$/.exec(location.hash);
    if (moved) {
      try { history.replaceState(null, "", location.pathname); } catch (e) { /* ignore */ }
      var banner = document.createElement("p");
      banner.className = "notice";
      banner.setAttribute("role", "status");
      root.parentNode.insertBefore(banner, root);
      api("/api/me/email/confirm", { method: "POST", body: { token: moved[1] }, anonymous: true }, T)
        .then(function (user) {
          banner.textContent = T.address_moved.replace("{email}", user.email);
          var account = saved();
          if (account && account.user && account.user.email !== user.email) { account.user = user; store(account); }
          if (saved()) render(saved().user);
        }).catch(function (err) { banner.textContent = err.message; });
    }
    if (!saved()) { if (!moved) toLogin(); return; }

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

    // Your data: the account, the bookmarks, highlights, place, plan progress
    // and settings kept with it (/api/reading), and this device's reading,
    // as JSON.
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
          messages: messages,
          device: { settings: read("owb.settings"), place: read("owb.place"), marks: read("owb.marks"), plans: read("owb.plans"),
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

    function dateText(iso) {
      return new Date(iso).toLocaleDateString(LANG, { year: "numeric", month: "short", day: "numeric" });
    }

    // Moving the account to another address: a link to the new one, which
    // lands back here as #email=<secret>.
    var emailForm = document.getElementById("email-form"), emailNote = document.getElementById("email-note");
    emailForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var address = emailForm.email.value.trim(), button = emailForm.querySelector("button");
      busy(button, true);
      api("/api/me/email", { method: "POST", body: { email: address, lang: LANG } }, T).then(function () {
        emailNote.textContent = T.address_sent.replace("{email}", address);
        emailForm.email.value = "";
      }).catch(function (err) { failed(err, emailNote); }).then(function () { busy(button, false); });
    });

    // Which emails: saved as soon as one is changed, with this browser's
    // time zone and the page's language for the links.
    var prefsForm = document.getElementById("prefs-form"), prefsNote = document.getElementById("prefs-note");
    var zone = (window.Intl && Intl.DateTimeFormat().resolvedOptions().timeZone) || "UTC";
    for (var h = 0; h < 24; h++) {
      var o = el("option", null, new Date(2026, 0, 1, h).toLocaleTimeString(LANG, { hour: "numeric", minute: "2-digit" }));
      o.value = h;
      prefsForm.reminder_hour.appendChild(o);
    }
    document.getElementById("prefs-zone").textContent = T.zone.replace("{zone}", zone);
    function showPrefs(p) {
      prefsForm.replies.checked = p.replies;
      prefsForm.plan_reminders.checked = p.plan_reminders;
      prefsForm.reminder_hour.value = p.reminder_hour;
      prefsForm.reminder_hour.disabled = !p.plan_reminders;
    }
    prefsForm.addEventListener("change", function () {
      prefsForm.reminder_hour.disabled = !prefsForm.plan_reminders.checked;
      api("/api/me/prefs", { method: "PATCH", body: {
        replies: prefsForm.replies.checked, plan_reminders: prefsForm.plan_reminders.checked,
        reminder_hour: +prefsForm.reminder_hour.value, timezone: zone, language: LANG } }, T)
        .then(function (p) { showPrefs(p); prefsNote.textContent = T.saved; })
        .catch(function (err) { failed(err, prefsNote); });
    });
    api("/api/me/prefs", {}, T).then(showPrefs).catch(function () { /* offline */ });

    // Signed-in devices.
    var devicesNote = document.getElementById("devices-note");
    function showDevices(list) {
      var ul = document.getElementById("device-list");
      ul.textContent = "";
      list.forEach(function (d) {
        var li = el("li", "account-item");
        var text = el("div");
        text.appendChild(el("p", "account-item-name", d.label || T.unknown_device));
        text.appendChild(el("p", "fine", d.current ? T.this_device : T.last_used.replace("{date}", dateText(d.last_used_at))));
        li.appendChild(text);
        if (!d.current) {
          var out = el("button", "button ghost", T.sign_out_device);
          out.type = "button";
          out.addEventListener("click", function () {
            api("/api/me/devices/" + d.id, { method: "DELETE" }, T).then(loadDevices)
              .catch(function (err) { failed(err, devicesNote); });
          });
          li.appendChild(out);
        }
        ul.appendChild(li);
      });
      document.getElementById("sign-out-others").hidden = list.length < 2;
    }
    function loadDevices() { return api("/api/me/devices", {}, T).then(showDevices).catch(function () { /* offline */ }); }
    twoClicks(document.getElementById("sign-out-others"), function () {
      api("/api/me/devices/sign-out-others", { method: "POST" }, T).then(function (r) {
        devicesNote.textContent = T.signed_out_others.replace("{n}", r.signed_out);
        loadDevices();
      }).catch(function (err) { failed(err, devicesNote); });
    });
    loadDevices();

    // Passkeys.
    var passkeysNote = document.getElementById("passkeys-note"), addPasskey = document.getElementById("add-passkey");
    function showPasskeys(list) {
      var ul = document.getElementById("passkey-list");
      ul.textContent = "";
      if (!list.length) ul.appendChild(el("li", "fine", T.passkeys_none));
      list.forEach(function (k) {
        var li = el("li", "account-item");
        var text = el("div");
        text.appendChild(el("p", "account-item-name", k.label || T.unknown_device));
        text.appendChild(el("p", "fine", k.last_used_at ? T.last_used.replace("{date}", dateText(k.last_used_at))
          : T.added.replace("{date}", dateText(k.created_at))));
        li.appendChild(text);
        var x = el("button", "button ghost", T.remove);
        x.type = "button";
        twoClicks(x, function () {
          api("/api/me/passkeys/" + k.id, { method: "DELETE" }, T).then(loadPasskeys)
            .catch(function (err) { failed(err, passkeysNote); });
        });
        li.appendChild(x);
        ul.appendChild(li);
      });
    }
    function loadPasskeys() { return api("/api/me/passkeys", {}, T).then(showPasskeys).catch(function () { /* offline */ }); }
    addPasskey.hidden = !passkeysWork();
    if (!passkeysWork()) passkeysNote.textContent = T.passkey_unsupported;
    addPasskey.addEventListener("click", function () {
      busy(addPasskey, true);
      passkeysNote.textContent = "";
      api("/api/me/passkeys/options", { method: "POST" }, T).then(makePasskey).then(function (credential) {
        return api("/api/me/passkeys", { method: "POST", body: { credential: credential } }, T);
      }).then(function () { passkeysNote.textContent = T.passkey_added; return loadPasskeys(); })
        .catch(function (err) {
          if (err && err.signedOut) { toLogin(); return; }
          passkeysNote.textContent = err && err.name === "NotAllowedError" ? "" : (err && err.message) || T.passkey_failed;
        }).then(function () { busy(addPasskey, false); });
    });
    loadPasskeys();

    // Your suggestions and questions (sent from a verse in the reader,
    // backend/feedback/), with the editors' replies.
    var box = document.getElementById("my-messages");
    var names = JSON.parse(box.getAttribute("data-books"));
    function el(tag, cls, text) {
      var n = document.createElement(tag);
      if (cls) n.className = cls;
      if (text) n.textContent = text;
      return n;
    }
    function showMessages(list) {
      var ul = document.getElementById("messages-list");
      ul.textContent = "";
      if (!list.length) ul.appendChild(el("li", "my-message-empty", T.messages_empty));
      list.forEach(function (m) {
        var p = m.verse.split(".");
        var li = el("li", "my-message");
        var head = el("p", "my-message-head");
        head.appendChild(el("span", "my-message-kind", T[m.kind] || m.kind));
        var a = el("a", null, (names[p[0]] || p[0]) + " " + p[1] + ":" + p[2]);
        a.href = PREFIX + "/" + p[0].toLowerCase() + "/" + p[1] + "/#v" + p[2];
        head.appendChild(a);
        head.appendChild(el("span", "my-message-date", new Date(m.created_at)
          .toLocaleDateString(LANG, { year: "numeric", month: "short", day: "numeric" })));
        head.appendChild(el("span", "my-message-status", T["status_" + m.status] || m.status));
        li.appendChild(head);
        li.appendChild(el("blockquote", null, m.text));
        if (m.reply) {
          var reply = el("div", "my-message-reply");
          reply.appendChild(el("p", "my-message-label", T.reply));
          reply.appendChild(el("p", null, m.reply));
          li.appendChild(reply);
        }
        ul.appendChild(li);
      });
      box.hidden = false;
    }
    var messages = [];
    api("/api/messages", {}, T).then(function (list) { messages = list; showMessages(list); })
      .catch(function () { /* offline or signed out: the section stays hidden */ });

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
