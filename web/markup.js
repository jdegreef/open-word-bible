// Reader-setting spans and verse markers in rendering text, for
// web/reader.js (loaded just before it). The same rules as owb/markup.py:
// tests/markup_vectors.json holds both to the same answers
// (tests/test_markup.py and tests/js/markup.test.mjs).
var OWBMarkup = (function () {
  "use strict";
  // {{gender:all people|men}}: a setting name, then its options; the first
  // is the default.
  var SPAN = /\{\{([a-z_]+):([^{}]*)\}\}/g;
  // "... children of God \v 13 children born ...": where a later verse starts.
  var VERSE = /\\v (\d+) ?/;
  // The settings a span may name: each has a control in the reader
  // (owb/markup.py SETTINGS is the same list).
  var SETTINGS = ["gender", "christos", "divine_name", "deity_pronoun", "units", "plural_you"];

  // Text with each span at the option settings[name] picks, or its default
  // when that is missing or out of range.
  function render(text, settings) {
    settings = settings || {};
    return text.replace(SPAN, function (_, name, opts) {
      var options = opts.split("|");
      var i = settings[name];
      return typeof i === "number" && i >= 0 && i < options.length ? options[i] : options[0];
    });
  }

  // Text split at its verse markers: [[null, first part], ["13", rest], ...].
  function splitVerses(text) {
    var parts = text.split(VERSE), out = [[null, parts[0].trim()]];
    for (var i = 1; i < parts.length; i += 2) out.push([parts[i], parts[i + 1]]);
    return out;
  }

  return { SPAN: SPAN, VERSE: VERSE, SETTINGS: SETTINGS, render: render, splitVerses: splitVerses };
})();
