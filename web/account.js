// The account page (/account/): sign in by email link, then show the
// account. The API (backend/accounts/) is on another host, named by the
// owb-api meta tag; a signed-in browser keeps an API token and a copy of the
// account in localStorage under owb.account (site.js reads the copy to show
// the header's initial). All text is inserted with textContent, and the
// messages are the page's language's (i18n/<lang>.json, account.ui).
(function () {
  "use strict";
  var API = document.querySelector('meta[name="owb-api"]').content;
  var KEY = "owb.account";
  var root = document.getElementById("account");
  var T = JSON.parse(document.getElementById("account-text").textContent);

  function saved() {
    try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (e) { return null; }
  }
  function store(value) {
    try {
      if (value) localStorage.setItem(KEY, JSON.stringify(value));
      else localStorage.removeItem(KEY);
    } catch (e) { /* storage blocked: signed in for this page only */ }
  }

  // DRF errors: {"detail": "..."} or {"field": ["..."]}.
  function message(data) {
    if (data.detail) return data.detail;
    for (var k in data) return Array.isArray(data[k]) ? data[k][0] : String(data[k]);
    return T.error;
  }

  // options.anonymous: the sign-in calls never send a saved token.
  function api(path, options) {
    options = options || {};
    var headers = { "Content-Type": "application/json" };
    var account = options.anonymous ? null : saved();
    if (account && account.token) headers.Authorization = "Bearer " + account.token;
    return fetch(API + path, {
      method: options.method || "GET", headers: headers,
      body: options.body ? JSON.stringify(options.body) : undefined
    }).then(function (r) {
      if (r.status === 401) { store(null); show("signed-out"); throw new Error("signed out"); }
      if (r.status === 204) return null;
      return r.json().then(function (data) {
        if (!r.ok) throw new Error(message(data));
        return data;
      });
    });
  }

  function show(state) {
    root.querySelectorAll("[data-state]").forEach(function (n) {
      n.hidden = n.getAttribute("data-state") !== state;
    });
    document.getElementById("account-title").textContent =
      T[state === "signed-in" || state === "sent" || state === "confirm" ? state : "signed-out"];
  }

  function render(user) {
    document.getElementById("me-email").textContent = user.email;
    document.getElementById("me-roles").textContent = user.roles.length
      ? user.roles.map(function (r) { return r.label; }).join(", ") : T.reader;
    document.getElementById("me-joined").textContent = new Date(user.joined + "T00:00:00")
      .toLocaleDateString(document.documentElement.lang, { year: "numeric", month: "long", day: "numeric" });
    document.getElementById("display-name").value = user.display_name || "";
    show("signed-in");
  }

  // Asking for a link.
  var form = document.getElementById("link-form");
  var error = document.getElementById("link-error");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var email = form.email.value.trim();
    error.hidden = true;
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      error.textContent = T.invalid_email;
      error.hidden = false;
      form.email.focus();
      return;
    }
    var button = form.querySelector("button");
    button.disabled = true;
    api("/api/auth/link", { method: "POST", body: { email: email }, anonymous: true }).then(function () {
      document.getElementById("sent-to").textContent = email;
      show("sent");
    }).catch(function (err) {
      error.textContent = err.message === "Failed to fetch"
        ? T.offline : err.message;
      error.hidden = false;
    }).then(function () { button.disabled = false; });
  });
  document.getElementById("different-email").addEventListener("click", function () {
    show("signed-out");
    form.email.focus();
  });

  // Saving the display name.
  var nameForm = document.getElementById("name-form");
  var note = document.getElementById("name-note");
  nameForm.addEventListener("submit", function (e) {
    e.preventDefault();
    api("/api/me", { method: "PATCH", body: { display_name: nameForm.display_name.value } })
      .then(function (user) {
        var account = saved();
        if (account) { account.user = user; store(account); }
        note.textContent = T.saved;
      }).catch(function (err) { note.textContent = err.message; });
  });

  document.getElementById("sign-out").addEventListener("click", function () {
    api("/api/auth/sign-out", { method: "POST" }).catch(function () { /* already signed out */ })
      .then(function () { store(null); show("signed-out"); });
  });

  // Arriving from the email (#token=...): the link is used only when the
  // reader presses Finish, so a scanner that opens it does not use it up.
  // The secret leaves the address bar at once and stays in this page.
  var m = /^#token=([\w-]+)$/.exec(location.hash);
  if (m) {
    var secret = m[1];
    try { history.replaceState(null, "", location.pathname); } catch (e) { /* ignore */ }
    show("confirm");
    var finish = document.getElementById("finish");
    finish.addEventListener("click", function () {
      finish.disabled = true;
      api("/api/auth/verify", { method: "POST", body: { token: secret }, anonymous: true })
        .then(function (data) {
          store({ token: data.token, user: data.user });
          render(data.user);
          // site.js syncs this browser's marks and place with the account.
          document.dispatchEvent(new Event("owb:account"));
        }).catch(function (err) {
          show("signed-out");
          error.textContent = err.message;
          error.hidden = false;
        });
    });
    finish.focus();
  } else if (saved()) {
    render(saved().user);
    api("/api/me").then(function (user) {
      var account = saved();
      if (account) { account.user = user; store(account); }
      render(user);
    }).catch(function () { /* offline: keep the saved copy; 401 already handled */ });
  } else {
    show("signed-out");
  }
})();
