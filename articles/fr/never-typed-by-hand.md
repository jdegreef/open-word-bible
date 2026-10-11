---
title: Pourquoi nous ne tapons jamais le grec ni l'hébreu à la main
summary: Une règle ferme protège l'exactitude de tout ce qu'Open Word Bible montre des langues originales. Voici la règle, et comment le logiciel la fait respecter.
date: 2026-10-10
order: 9
section: method
---
Open Word Bible a une règle qui surprend : personne, ni humain ni IA, ne tape jamais un mot grec ou hébreu dans la traduction ou dans ses notes. Chaque mot en langue originale que vous voyez sur ce site, y compris le grec de ces articles, est copié par un logiciel à partir de données sources fixes.

## Pourquoi

Le grec et l'hébreu sont difficiles à taper correctement. Le grec a des accents et des esprits ; l'hébreu a des points-voyelles et des signes de cantillation. Beaucoup d'entre eux se ressemblent presque à l'écran, mais sont des caractères différents en dessous. Un mot tapé de mémoire peut sembler juste et pourtant être faux : un autre accent, un esprit qui manque, une lettre qui n'existe pas du tout dans la source.

Lors des premiers essais, le grec tapé de mémoire contenait exactement ce genre d'erreurs. Une traduction qui prétend montrer son travail ne peut pas montrer les mauvais mots.

## Les sources

Le texte vient d'éditions fixes, sous licence ouverte, chacune figée dans une version exacte afin que chaque résultat puisse être reproduit :

- **Nouveau Testament :** le Nouveau Testament grec de la SBL (version 1.2), avec les données mot à mot de MACULA Greek.
- **Ancien Testament :** le Codex de Leningrad de Westminster, avec les données sur les mots de MACULA Hebrew et de l'Open Scriptures Hebrew Bible.

Tous les crédits figurent sur la page [À propos](/about/).

## Comment la règle est appliquée

La règle n'est pas une simple habitude : le logiciel la vérifie à chaque modification.

- Le texte original de chaque phrase est reconstruit à partir des données sources, et une phrase dont le texte ne correspond pas est rejetée.
- Tout mot grec ou hébreu ailleurs, dans une glose, une traduction ou une note, doit correspondre exactement, caractère pour caractère, à une forme ou à un mot de dictionnaire des données sources. Un mot mal accentué échoue à la vérification.
- Ces articles citent le grec au moyen de marqueurs que le site remplit à partir des données au moment de sa construction. Quand cet article montre les premiers mots de l'Évangile de Jean, {{GREEK:JHN.1.1:1-5}}, ces mots viennent des données du Nouveau Testament grec de la SBL, et non d'un clavier.

Ces vérifications s'exécutent automatiquement avant toute publication.
