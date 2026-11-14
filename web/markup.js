// Reader-setting spans and verse markers in rendering text, for
// web/reader.js (loaded just before it). The same rules as owb/markup.py:
// tests/markup_vectors.json holds both to the same answers
// (tests/test_markup.py and tests/js/markup.test.mjs).
var OWBMarkup = (function () {
  "use strict";
  // {{gender:all people|men}}: a setting name, then its options; the first
  // is the default, except where DEFAULTS names another.
  var SPAN = /\{\{([a-z_]+):([^{}]*)\}\}/g;
  // "... children of God \v 13 children born ...": where a later verse starts.
  var VERSE = /\\v (\d+) ?/;
  // The settings a span may name: each has a control in the reader
  // (owb/markup.py SETTINGS is the same list).
  var SETTINGS = ["gender", "christos", "divine_name", "deity_pronoun", "units", "plural_you"];
  // The option a setting shows until the reader picks one, where it is not
  // the first: pronouns for God are capitalised by default (owb/markup.py
  // DEFAULTS is the same).
  var DEFAULTS = { deity_pronoun: 1 };

  function defaultOption(name, options) {
    var i = SETTINGS.indexOf(name) >= 0 && name in DEFAULTS ? DEFAULTS[name] : 0;
    return i < options.length ? options[i] : options[0];
  }

  // Each setting at the option it shows when the reader has not picked one.
  function defaults() {
    var out = {};
    SETTINGS.forEach(function (name) { out[name] = name in DEFAULTS ? DEFAULTS[name] : 0; });
    return out;
  }

  // The reader's saved settings (owb.settings), brought up to date: a copy
  // saved before pronouns for God were capitalised by default (no "v", or
  // v below 2) holds lowercase only because that was the default then, so
  // that choice is dropped and the new default shows.
  function fromSaved(saved) {
    var out = {};
    saved = saved || {};
    for (var k in saved) out[k] = saved[k];
    if (!(out.v >= 2)) delete out.deity_pronoun;
    return out;
  }

  // Text with each span at the option settings[name] picks, or its default
  // when that is missing or out of range.
  function render(text, settings) {
    settings = settings || {};
    return text.replace(SPAN, function (_, name, opts) {
      var options = opts.split("|");
      var i = settings[name];
      return typeof i === "number" && i >= 0 && i < options.length ? options[i] : defaultOption(name, options);
    });
  }

  // Text split at its verse markers: [[null, first part], ["13", rest], ...].
  function splitVerses(text) {
    var parts = text.split(VERSE), out = [[null, parts[0].trim()]];
    for (var i = 1; i < parts.length; i += 2) out.push([parts[i], parts[i + 1]]);
    return out;
  }

  // The original words behind one aligned piece of a rendering, as one
  // string: words [{text, after, position}] in the source's order. MACULA
  // Hebrew gives each morpheme its own row, with nothing "after" a prefix
  // or stem that the next morpheme of the same word follows ("and" + "the"
  // + "earth"), so those are joined without a space; separate words, Greek
  // or Hebrew, are joined with one.
  function joinWords(words) {
    var out = "";
    words.forEach(function (w, i) {
      var prev = words[i - 1];
      var joined = prev && prev.after === "" && prev.position === w.position;
      out += (i && !joined ? " " : "") + w.text;
    });
    return out.trim();
  }

  return { SPAN: SPAN, VERSE: VERSE, SETTINGS: SETTINGS, DEFAULTS: DEFAULTS, SETTINGS_VERSION: 2,
           defaults: defaults, defaultOption: defaultOption, fromSaved: fromSaved,
           render: render, splitVerses: splitVerses, joinWords: joinWords };
})();
