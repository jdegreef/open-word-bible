// The account page (/account/): sign in by email link, then show the
// account. The API (backend/accounts/) is on another host, named by the
// owb-api meta tag; a signed-in browser keeps an API token and a copy of the
// account in localStorage under owb.account (site.js reads the copy to show
// the header's initial). All text is inserted with textContent.
(function () {
  "use strict";
  var API = document.querySelector('meta[name="owb-api"]').content;
  var KEY = "owb.account";
  var root = document.getElementById("account");

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
    return "Something went wrong.";
  }

  function api(path, options) {
    options = options || {};
    var headers = { "Content-Type": "application/json" };
    var account = saved();
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
      state === "signed-in" ? "Your account" : state === "sent" ? "Check your email" : "Sign in";
  }

  function render(user) {
    document.getElementById("me-email").textContent = user.email;
    document.getElementById("me-roles").textContent = user.roles.length
      ? user.roles.map(function (r) { return r.label; }).join(", ") : "Reader";
    document.getElementById("me-joined").textContent = new Date(user.joined + "T00:00:00")
      .toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });
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
      error.textContent = "Enter a valid email address.";
      error.hidden = false;
      form.email.focus();
      return;
    }
    var button = form.querySelector("button");
    button.disabled = true;
    api("/api/auth/link", { method: "POST", body: { email: email } }).then(function () {
      document.getElementById("sent-to").textContent = email;
      show("sent");
    }).catch(function (err) {
      error.textContent = err.message === "Failed to fetch"
        ? "Could not reach Open Word Bible. Check your connection and try again." : err.message;
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
        note.textContent = "Saved.";
      }).catch(function (err) { note.textContent = err.message; });
  });

  document.getElementById("sign-out").addEventListener("click", function () {
    api("/api/auth/sign-out", { method: "POST" }).catch(function () { /* already signed out */ })
      .then(function () { store(null); show("signed-out"); });
  });

  // Arriving from the email (#token=...), already signed in, or neither.
  var m = /^#token=([\w-]+)$/.exec(location.hash);
  if (m) {
    try { history.replaceState(null, "", location.pathname); } catch (e) { /* ignore */ }
    show("verifying");
    api("/api/auth/verify", { method: "POST", body: { token: m[1] } }).then(function (data) {
      store({ token: data.token, user: data.user });
      render(data.user);
    }).catch(function (err) {
      show("signed-out");
      error.textContent = err.message;
      error.hidden = false;
    });
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
