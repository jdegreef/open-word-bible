---
title: Pourquoi nous ne tapons jamais le grec ni l'hébreu à la main
summary: Une règle ferme protège l'exactitude de tout ce qu'Open Word Bible montre des langues originales. Voici la règle, et comment le logiciel la fait respecter.
date: 2026-10-10
order: 9
section: method
source: f5bf26398aaa
---
Open Word Bible a une règle qui surprend : personne, ni humain ni IA, ne tape jamais un mot grec ou hébreu dans la traduction ou dans ses notes. Chaque mot en langue originale que vous voyez sur ce site, y compris le grec et l'hébreu de ces articles, est copié par un logiciel à partir de données sources fixes.

## Pourquoi

Le grec et l'hébreu sont difficiles à taper correctement. Le grec a des accents et des esprits ; l'hébreu a des points-voyelles et des signes de cantillation. Beaucoup d'entre eux se ressemblent presque à l'écran, mais sont des caractères différents en dessous. Un omicron grec et un "o" latin ont le même aspect dans la plupart des polices. Certaines voyelles grecques accentuées peuvent être enregistrées de deux manières différentes qui s'affichent à l'identique. Un mot tapé de mémoire peut sembler juste et pourtant être faux : un autre accent, un esprit qui manque, une lettre qui n'existe pas du tout dans la source.

Lors des premiers essais, le grec tapé de mémoire contenait exactement ce genre d'erreurs. Une traduction qui prétend montrer son travail ne peut pas montrer les mauvais mots.

## Les sources

Le texte vient d'éditions fixes, sous licence ouverte, chacune figée dans une version exacte afin que chaque résultat puisse être reproduit :

- **Nouveau Testament :** le Nouveau Testament grec de la SBL (version 1.2), avec les données mot à mot de MACULA Greek.
- **Ancien Testament :** le Codex de Leningrad de Westminster, avec les données sur les mots de MACULA Hebrew et de l'Open Scriptures Hebrew Bible.

"Figée" veut dire plus que nommer une édition. Le projet enregistre la révision exacte de chaque source qu'il télécharge, si bien que le texte ne peut pas changer sous la traduction sans que personne ne s'en aperçoive. Tous les crédits figurent sur la page [À propos](/about/).

## Comment la règle est appliquée

La règle n'est pas une simple habitude : le logiciel la vérifie à chaque modification.

- Le texte original de chaque phrase est reconstruit à partir des données sources, et une phrase dont le texte ne correspond pas est rejetée.
- Tout mot grec ou hébreu ailleurs, dans une glose, une traduction ou une note, doit correspondre exactement, caractère pour caractère, à une forme ou à un mot de dictionnaire des données sources. Un mot mal accentué échoue à la vérification.
- Ces articles citent le grec et l'hébreu au moyen de marqueurs que le site remplit à partir des données au moment de sa construction. Quand cet article montre les premiers mots de l'Évangile de Jean, {{GREEK:JHN.1.1:1-5}}, ces mots viennent des données du Nouveau Testament grec de la SBL, et non d'un clavier.

Un marqueur nomme un verset et un numéro de mot. Le premier mot de la Genèse, {{HEBREW:GEN.1.1:1}}, s'écrit en un seul mot mais a deux parties : un préfixe qui veut dire "dans" et le nom "commencement". Un marqueur peut demander la seconde partie seule, sous sa forme de dictionnaire, {{LEMMA:GEN.1.1:1.2}}. Les deux ne se ressemblent pas tout à fait : la forme du texte porte un signe de cantillation pour la psalmodie, et la forme de dictionnaire n'en a pas. Tapée à la main, cette différence est facile à manquer. Copiée à partir des données, elle ne peut pas l'être.

Ces vérifications s'exécutent automatiquement avant toute publication. Un marqueur qui renvoie à un mot grec dans un verset de l'Ancien Testament, ou à un mot qui n'existe pas, empêche la construction du site.

## Des questions légitimes

**Cela veut-il dire que le texte source ne peut jamais être mis en question ?** Non. Le texte source n'est jamais modifié, mais la traduction peut s'en écarter, ouvertement. En Jean 1:3, le dossier lit la ponctuation autrement que le Nouveau Testament grec de la SBL, et une décision explique pourquoi. Là où les manuscrits divergent, une décision décrit l'autre leçon. Le texte de base reste fixe pour que chaque écart soit visible.

**Un mot vérifié garantit-il une note correcte ?** Non. La vérification prouve qu'un mot se trouve réellement dans la source. Elle ne peut pas prouver qu'une note en dit ce qu'il faut. C'est le rôle des relecteurs humains.
