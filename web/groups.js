// Reading groups (groups_page in scripts/build_site.py; backend groups/):
// a few readers following one reading plan together. The page has three
// views, by its address: the reader's groups and a form to start one (no
// fragment), one group (#g=<id>): its members' progress, what they wrote
// about each day, its invite link; and an invite (#join=<code>). It needs an
// account, and a display name to be known by. Members see each other's
// names and, if each shares it, how far they have read; notes, highlights
// and addresses are never shown. All text is inserted with textContent.
(function () {
  "use strict";
  var root = document.getElementById("groups");
  if (!root) return;
  var T = JSON.parse(document.getElementById("groups-text").textContent);
  var API = document.querySelector('meta[name="owb-api"]').content;
  var LANG = document.documentElement.lang;
  var box = root.querySelector(".groups-view");
  var plansFile = null;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function fill(text, values) {
    return text.replace(/\{(\w+)\}/g, function (m, k) { return k in values ? values[k] : m; });
  }
  function account() {
    try { return JSON.parse(localStorage.getItem("owb.account") || "null"); } catch (e) { return null; }
  }
  function api(path, options) {
    options = options || {};
    var a = account();
    var headers = { Authorization: "Bearer " + (a && a.token) };
    if (options.body) headers["Content-Type"] = "application/json";
    return fetch(API + path + (path.indexOf("?") < 0 ? "?" : "&") + "lang=" + LANG, {
      method: options.method || "GET", headers: headers, body: options.body ? JSON.stringify(options.body) : undefined
    }).then(function (r) {
      if (r.status === 401) {
        try { localStorage.removeItem("owb.account"); } catch (e) { /* none */ }
        signIn();
        throw { signedOut: true };
      }
      if (r.status === 204) return null;
      return r.json().catch(function () { return {}; }).then(function (data) {
        if (!r.ok) throw { message: T["error_" + data.code] || data.detail || T.error, code: data.code };
        return data;
      });
    }, function () { throw { message: T.offline }; });
  }
  function twice(button, again, act) {
    var label = button.textContent;
    button.addEventListener("click", function () {
      if (button.classList.contains("armed")) { act(); return; }
      button.classList.add("armed");
      button.textContent = again;
      setTimeout(function () { button.classList.remove("armed"); button.textContent = label; }, 4000);
    });
  }
  function say(text) {
    var p = el("p", "notice", text);
    p.setAttribute("role", "alert");
    return p;
  }

  function signIn() {
    box.textContent = "";
    var p = el("p", "groups-sign-in", T.sign_in + " ");
    var a = el("a", "button", T.sign_in_link);
    a.href = root.getAttribute("data-login") + "?redirect=" + encodeURIComponent(location.pathname + location.hash);
    p.appendChild(a);
    box.appendChild(p);
  }

  // The plans a group can follow: those offered in this language, and the
  // reader's own (web/plans.js keeps them as owb.myplans).
  function myPlans() {
    var all = {};
    try { all = JSON.parse(localStorage.getItem("owb.myplans") || "{}") || {}; } catch (e) { /* none */ }
    return all;
  }
  function planUrl(g) {
    if (/^my-/.test(g.plan_id)) return plansFile.mine + "#id=" + g.plan_id;
    var p = plansFile.plans[g.plan_id];
    return p ? p.url : root.getAttribute("data-plans-page");
  }
  // Following the group's plan here: a plan of the reader's own is copied
  // into their plans first, under the group's id, so progress lines up.
  function follow(g) {
    if (g.plan && /^my-/.test(g.plan_id)) {
      var mine = myPlans();
      if (!mine[g.plan_id] || !mine[g.plan_id].days) {
        mine[g.plan_id] = { name: g.plan.name, days: g.plan.days, at: Date.now() };
        try { localStorage.setItem("owb.myplans", JSON.stringify(mine)); } catch (e) { /* blocked */ }
        document.dispatchEvent(new CustomEvent("owb:myplans"));
      }
    }
    var P = window.OWBPlans;
    if (!P) return;
    var s = P.load();
    if (!s.plans[g.plan_id]) {
      var d = new Date();
      s.plans[g.plan_id] = { start: d.getFullYear() + "-" + ("0" + (d.getMonth() + 1)).slice(-2) + "-" +
                                    ("0" + d.getDate()).slice(-2), done: [] };
    }
    s.active = g.plan_id;
    P.save(s);
  }
  function reading(g) {
    var P = window.OWBPlans;
    return P ? P.load().active === g.plan_id : false;
  }

  // The reader's display name, asked for where a group needs one.
  function nameField(form) {
    var a = account();
    if (a && a.user && a.user.display_name) return null;
    var label = el("label", null, T.your_name);
    var input = el("input");
    input.name = "display_name";
    input.maxLength = 80;
    input.required = true;
    input.autocomplete = "name";
    label.appendChild(input);
    form.appendChild(label);
    form.appendChild(el("p", "fine", T.your_name_note));
    return input;
  }
  function saveName(input) {
    if (!input) return Promise.resolve();
    return api("/api/me", { method: "PATCH", body: { display_name: input.value } }).then(function (user) {
      var a = account();
      if (a) { a.user = user; try { localStorage.setItem("owb.account", JSON.stringify(a)); } catch (e) { /* */ } }
    });
  }

  // The reader's groups, and starting one.
  function drawList() {
    box.textContent = "";
    var listBox = el("section", "groups-list");
    listBox.appendChild(el("h2", null, T.yours));
    var ul = el("ul", "a-grid plan-list");
    listBox.appendChild(ul);
    box.appendChild(listBox);
    api("/api/groups").then(function (groups) {
      if (!groups.length) listBox.appendChild(el("p", "fine", T.none));
      groups.forEach(function (g) {
        var li = el("li");
        var a = el("a", "a-card plan-card");
        a.href = "#g=" + g.id;
        a.appendChild(el("span", "a-section", g.plan_name));
        a.appendChild(el("span", "a-title", g.name));
        a.appendChild(el("span", "a-meta", fill(g.members === 1 ? T.members_one : T.members, { n: g.members }) +
          (g.leader ? " · " + T.leader : "")));
        li.appendChild(a);
        ul.appendChild(li);
      });
    }).catch(function (err) { if (!err.signedOut) listBox.appendChild(say(err.message)); });

    var make = el("section", "groups-make");
    make.appendChild(el("h2", null, T.start));
    make.appendChild(el("p", "fine", T.start_dek));
    var form = el("form", "account-form");
    var label = el("label", null, T.name);
    var name = el("input");
    name.maxLength = 80;
    name.required = true;
    label.appendChild(name);
    form.appendChild(label);
    var pl = el("label", null, T.plan);
    var pick = el("select");
    var own = myPlans();
    Object.keys(plansFile.plans).forEach(function (id) {
      var o = el("option", null, plansFile.plans[id].name);
      o.value = id;
      pick.appendChild(o);
    });
    Object.keys(own).filter(function (id) { return own[id].days; }).forEach(function (id) {
      var o = el("option", null, own[id].name + " (" + T.own_plan + ")");
      o.value = id;
      pick.appendChild(o);
    });
    var active = window.OWBPlans && window.OWBPlans.load().active;
    if (active) pick.value = active;
    pl.appendChild(pick);
    form.appendChild(pl);
    if (!pick.options.length) form.appendChild(el("p", "fine", T.no_plans));
    var me = nameField(form);
    var note = el("p", "form-note");
    note.setAttribute("role", "status");
    var go = el("button", "button", T.create);
    go.type = "submit";
    form.appendChild(go);
    form.appendChild(note);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!name.value.trim() || !pick.value) { note.textContent = T.need_fields; return; }
      var id = pick.value, body = { name: name.value, plan_id: id };
      if (/^my-/.test(id)) body.plan = { name: own[id].name, days: own[id].days };
      go.disabled = true;
      saveName(me).then(function () { return api("/api/groups", { method: "POST", body: body }); })
        .then(function (g) { follow(g); location.hash = "#g=" + g.id; })
        .catch(function (err) { if (!err.signedOut) note.textContent = err.message; })
        .then(function () { go.disabled = false; });
    });
    make.appendChild(form);
    box.appendChild(make);
  }

  // An invite: what the group is, and joining it.
  function drawJoin(code) {
    box.textContent = "";
    api("/api/groups/invite/" + encodeURIComponent(code)).then(function (g) {
      if (g.member) { location.hash = "#g=" + g.member; return; }
      var s = el("section", "groups-join");
      s.appendChild(el("p", "eyebrow", T.invited));
      s.appendChild(el("h2", null, g.name));
      s.appendChild(el("p", "dek", g.plan_name + " · " + fill(T.days, { n: g.days }) + " · " +
        fill(g.members === 1 ? T.members_one : T.members, { n: g.members })));
      s.appendChild(el("p", "fine", T.join_privacy));
      var form = el("form", "account-form");
      var me = nameField(form);
      var note = el("p", "form-note");
      note.setAttribute("role", "status");
      var go = el("button", "button", T.join);
      go.type = "submit";
      form.appendChild(go);
      form.appendChild(note);
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        go.disabled = true;
        saveName(me).then(function () { return api("/api/groups/join", { method: "POST", body: { code: code } }); })
          .then(function (joined) { follow(joined); location.hash = "#g=" + joined.id; })
          .catch(function (err) { if (!err.signedOut) note.textContent = err.message; })
          .then(function () { go.disabled = false; });
      });
      s.appendChild(form);
      box.appendChild(s);
    }).catch(function (err) { if (!err.signedOut) box.appendChild(say(err.message)); });
  }

  // One group.
  var dayShown = null;
  function drawGroup(id) {
    box.textContent = "";
    api("/api/groups/" + id).then(function (g) { showGroup(g); })
      .catch(function (err) {
        if (err.signedOut) return;
        box.appendChild(say(err.message));
        var back = el("a", null, T.back);
        back.href = "#";
        box.appendChild(back);
      });
  }
  function current(done, total) {
    for (var d = 1; d <= total; d++) if (done.indexOf(d) < 0) return d;
    return 0;
  }
  function showGroup(g) {
    box.textContent = "";
    var back = el("a", "groups-back", "← " + T.all_groups);
    back.href = "#";
    box.appendChild(back);
    var head = el("header", "groups-head");
    head.appendChild(el("h2", null, g.name));
    var plan = el("p", "dek");
    var pa = el("a", null, g.plan_name);
    pa.href = planUrl(g);
    plan.appendChild(pa);
    plan.appendChild(document.createTextNode(" · " + fill(T.days, { n: g.days })));
    head.appendChild(plan);
    if (!reading(g)) {
      var start = el("button", "button", T.follow);
      start.type = "button";
      start.addEventListener("click", function () { follow(g); showGroup(g); });
      head.appendChild(start);
    } else {
      head.appendChild(el("p", "fine", T.following));
    }
    box.appendChild(head);

    // Members and how far each has read.
    var members = el("section", "groups-members");
    members.appendChild(el("h3", null, T.members_heading));
    var ul = el("ul", "groups-member-list");
    g.member_list.forEach(function (m) {
      var li = el("li", "groups-member");
      var who = el("p", "groups-member-name", (m.name || T.reader) + (m.me ? " (" + T.you + ")" : ""));
      if (m.leader) who.appendChild(el("span", "badge", T.leader));
      li.appendChild(who);
      if (m.progress) {
        var done = m.progress.done || [], day = current(done, g.days);
        li.appendChild(el("p", "fine", day ? fill(T.progress, { done: done.length, total: g.days, day: day })
          : fill(T.finished, { total: g.days })));
        var ticks = el("div", "plan-ticks small");
        ticks.setAttribute("aria-hidden", "true");
        for (var d = 1; d <= g.days; d++) ticks.appendChild(el("span", "tick " + (done.indexOf(d) >= 0 ? "done" : d === day ? "today" : "ahead")));
        li.appendChild(ticks);
      } else {
        li.appendChild(el("p", "fine", T.private_progress));
      }
      if (g.leader && !m.me) {
        var x = el("button", "plan-undo", T.remove);
        x.type = "button";
        twice(x, T.remove_confirm, function () {
          api("/api/groups/" + g.id + "/members/" + m.id, { method: "DELETE" }).then(function () { drawGroup(g.id); })
            .catch(function (err) { if (!err.signedOut) li.appendChild(say(err.message)); });
        });
        li.appendChild(x);
      }
      ul.appendChild(li);
    });
    members.appendChild(ul);
    var share = el("label", "handout-check");
    var sbox = el("input");
    sbox.type = "checkbox";
    sbox.checked = g.share_progress;
    sbox.addEventListener("change", function () {
      api("/api/groups/" + g.id, { method: "PATCH", body: { share_progress: sbox.checked } }).then(showGroup)
        .catch(function (err) { if (!err.signedOut) members.appendChild(say(err.message)); });
    });
    share.appendChild(sbox);
    share.appendChild(document.createTextNode(" " + T.share_progress));
    members.appendChild(share);
    box.appendChild(members);

    // What members wrote, a day at a time.
    var talk = el("section", "groups-talk");
    talk.appendChild(el("h3", null, T.talk));
    var mine = (g.member_list.filter(function (m) { return m.me; })[0] || {}).progress;
    if (dayShown === null || dayShown > g.days) dayShown = Math.max(1, current((mine && mine.done) || [], g.days) || g.days);
    var pickLabel = el("label", "saved-book-label", T.day_pick + " ");
    var pick = el("select", "saved-book-pick");
    var counts = {};
    g.posts.forEach(function (p) { counts[p.day] = (counts[p.day] || 0) + 1; });
    for (var n = 1; n <= Math.max(g.days, 1); n++) {
      var o = el("option", null, fill(T.day, { n: n }) + (counts[n] ? " (" + counts[n] + ")" : ""));
      o.value = n;
      o.selected = n === dayShown;
      pick.appendChild(o);
    }
    pick.addEventListener("change", function () { dayShown = +pick.value; showGroup(g); });
    pickLabel.appendChild(pick);
    talk.appendChild(pickLabel);
    var posts = g.posts.filter(function (p) { return p.day === dayShown; });
    var list = el("ul", "groups-posts");
    if (!posts.length) list.appendChild(el("li", "fine", T.no_posts));
    posts.forEach(function (p) {
      var li = el("li", "groups-post");
      var meta = el("p", "groups-post-head");
      meta.appendChild(el("strong", null, p.name || T.reader));
      meta.appendChild(el("span", "fine", new Date(p.created_at).toLocaleDateString(LANG, { month: "short", day: "numeric" })));
      if (p.can_delete) {
        var del = el("button", "saved-remove", T.delete_post);
        del.type = "button";
        twice(del, T.confirm, function () {
          api("/api/groups/" + g.id + "/posts/" + p.id, { method: "DELETE" }).then(function () { drawGroup(g.id); });
        });
        meta.appendChild(del);
      }
      li.appendChild(meta);
      li.appendChild(el("p", "groups-post-text", p.text));
      list.appendChild(li);
    });
    talk.appendChild(list);
    var form = el("form", "account-form");
    var label = el("label", null, fill(T.write, { n: dayShown }));
    var field = el("textarea", "cite-text");
    field.rows = 3;
    field.maxLength = 2000;
    label.appendChild(field);
    form.appendChild(label);
    form.appendChild(el("p", "fine", T.write_note));
    var note = el("p", "form-note");
    note.setAttribute("role", "status");
    var send = el("button", "button", T.send);
    send.type = "submit";
    form.appendChild(send);
    form.appendChild(note);
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!field.value.trim()) { field.focus(); return; }
      send.disabled = true;
      api("/api/groups/" + g.id + "/posts", { method: "POST", body: { day: dayShown, text: field.value } })
        .then(showGroup).catch(function (err) { if (!err.signedOut) note.textContent = err.message; send.disabled = false; });
    });
    talk.appendChild(form);
    box.appendChild(talk);

    // Inviting, and the leader's controls.
    var more = el("section", "groups-invite");
    more.appendChild(el("h3", null, T.invite));
    more.appendChild(el("p", "fine", T.invite_note));
    var link = location.origin + location.pathname + "#join=" + g.invite;
    var row = el("p", "field-row");
    var input = el("input");
    input.readOnly = true;
    input.value = link;
    input.setAttribute("aria-label", T.invite);
    input.addEventListener("focus", function () { input.select(); });
    row.appendChild(input);
    var copy = el("button", "button ghost", T.copy);
    copy.type = "button";
    copy.addEventListener("click", function () {
      if (navigator.clipboard) navigator.clipboard.writeText(link).then(function () { copy.textContent = T.copied; });
      else input.select();
    });
    row.appendChild(copy);
    more.appendChild(row);
    var actions = el("p", "actions");
    if (g.leader) {
      var fresh = el("button", "button ghost", T.new_link);
      fresh.type = "button";
      twice(fresh, T.new_link_confirm, function () {
        api("/api/groups/" + g.id + "/invite", { method: "POST" }).then(showGroup);
      });
      actions.appendChild(fresh);
      var rename = el("button", "button ghost", T.rename);
      rename.type = "button";
      rename.addEventListener("click", function () {
        var name = window.prompt(T.name, g.name);
        if (name && name.trim()) api("/api/groups/" + g.id, { method: "PATCH", body: { name: name } }).then(showGroup)
          .catch(function (err) { if (!err.signedOut) more.appendChild(say(err.message)); });
      });
      actions.appendChild(rename);
      var close = el("button", "button ghost", T.close);
      close.type = "button";
      twice(close, T.close_confirm, function () {
        api("/api/groups/" + g.id, { method: "DELETE" }).then(function () { location.hash = ""; });
      });
      actions.appendChild(close);
    }
    var leave = el("button", "button ghost", T.leave);
    leave.type = "button";
    twice(leave, T.leave_confirm, function () {
      api("/api/groups/" + g.id + "/leave", { method: "POST" }).then(function () { location.hash = ""; });
    });
    actions.appendChild(leave);
    more.appendChild(actions);
    box.appendChild(more);
  }

  function route() {
    if (!(account() || {}).token) { signIn(); return; }
    var hash = location.hash;
    var m;
    if ((m = hash.match(/^#g=(\d+)$/))) drawGroup(m[1]);
    else if ((m = hash.match(/^#join=([\w-]+)$/))) drawJoin(m[1]);
    else drawList();
  }
  window.addEventListener("hashchange", function () { dayShown = null; route(); window.scrollTo(0, 0); });
  fetch(root.getAttribute("data-plans"), { credentials: "same-origin" }).then(function (r) { return r.json(); })
    .then(function (file) { plansFile = file; route(); })
    .catch(function () { box.appendChild(say(T.offline)); });
})();
