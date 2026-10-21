---
title: "Traduction assistée par l'IA et relecture humaine : comment une phrase devient \"relue\""
summary: Tout ce qui se trouve aujourd'hui sur ce site est traduit avec l'aide de l'IA. Voici comment une phrase est rédigée, ce que contient son dossier, ce que la rédaction par l'IA ne peut pas faire, et comment une phrase passe au statut de relue.
date: 2026-10-10
order: 10
section: method
source: f7d52d635434
---
Open Word Bible est traduite avec l'aide de l'IA. Nous le disons clairement, car un projet qui promet de montrer son travail ne peut pas rester vague sur qui a fait ce travail. Cet article explique comment une phrase est rédigée, ce que vous pouvez en voir, où la rédaction par l'IA atteint ses limites, et ce qui doit se passer avant qu'une phrase soit dite relue.

## Comment une phrase est rédigée

Prenons Philippiens 4:6–7, une longue phrase grecque sur l'inquiétude et la prière. Elle passe par quatre étapes.

**1. La source est chargée, pas tapée.** Un script lit les données sources figées : le Nouveau Testament grec de la SBL avec les données lexicales de MACULA pour le Nouveau Testament, et le Codex de Leningrad de Westminster pour l'Ancien. Il découpe le texte là où l'édition termine une phrase et écrit pour chacune un dossier vide, avec l'identifiant de chaque mot grec et le texte grec lui-même. Personne, ni humain ni IA, ne tape l'original. Voir [Pourquoi nous ne tapons jamais le grec ni l'hébreu à la main](/articles/never-typed-by-hand/).

**2. L'IA écrit un brouillon.** À partir du grec, des données lexicales et d'un guide de style écrit, un modèle d'IA remplit le dossier : une glose littérale dans l'ordre des mots grecs, la traduction aux trois niveaux dans chaque langue, et les décisions qui les sous-tendent. Le guide de style fixe les règles : quels mots anglais sont des termes clés arrêtés, en quoi chaque niveau diffère, ce qui peut aller entre crochets, quels réglages de lecture s'appliquent et où. Pour certains livres, une liste séparée de termes arrêtés veille à ce que le même mot hébreu ne sorte pas de trois manières différentes au fil des soixante-six chapitres d'Ésaïe.

**3. Le logiciel vérifie les règles.** Un validateur passe sur chaque dossier. Il rejette tout mot grec ou hébreu qui n'est pas, lettre pour lettre, une forme ou un mot du dictionnaire présent dans les données sources. Il vérifie que chaque terme clé emploie son mot anglais arrêté à chaque niveau, sauf si une décision explique pourquoi. Il vérifie que chaque dossier a ses trois niveaux, qu'un dossier se termine là où se termine une phrase, et que les décisions de sens restent libres de toute formulation propre à une langue. Un dossier qui enfreint une règle n'entre pas.

**4. La modification se fait en public.** Chaque nouveau passage arrive comme une modification proposée sur GitHub, où les tests et la construction du site s'exécutent avant qu'elle soit fusionnée. Tout son historique y reste consultable.

## Ce que contient le dossier

Voici le niveau Équilibrée de la phrase issue de ces étapes :

> {{OWB:PHP.4.6.s1:B}}

Son dossier contient le grec, qui commence par {{GREEK:PHP.4.6:1-2}}, "ne vous inquiétez de rien" ; une glose littérale ; les niveaux Littérale, Équilibrée et Simple en anglais ; et les mêmes trois niveaux dans d'autres langues à mesure qu'ils sont rédigés. Il contient aussi douze décisions. Sept sont des décisions de sens, communes à toutes les langues. L'une dit que {{LEMMA:PHP.4.6:2}} désigne ici l'inquiétude anxieuse, le mot qu'emploie Jésus en Matthieu 6, et non le souci bienveillant pour lequel Paul l'emploie en 2:20. Une autre dit que le verbe "garder" décrit ce que fait une garnison, une image que les habitants de Philippes, colonie romaine qui comptait d'anciens soldats parmi ses citoyens, auraient ressentie. Les cinq autres sont des décisions de rendu, chacune pour une langue. Une décision anglaise, par exemple, explique pourquoi le niveau Équilibrée dit que la paix va "stand guard over" (monter la garde sur) vos cœurs : cela garde l'image du soldat sans le vieilli "keep" (garder).

Deux décisions de ce dossier sont marquées incertaines. L'une porte sur le sens : la paix qui "surpasse toute intelligence" peut être une paix au-delà de ce que l'esprit peut saisir, ou une paix qui accomplit plus que tout projet humain. Le dossier suit la lecture la plus courante et donne l'autre en note. La seconde porte sur l'anglais. Le niveau Simple dit que la paix vous garde "because you are joined to Christ Jesus" (parce que vous êtes unis au Christ Jésus), là où le grec dit seulement "en". La décision de rendu dit clairement que cela ajoute une raison que le grec laisse implicite, et que les relecteurs doivent la vérifier :

> {{OWB:PHP.4.6.s1:R}}

C'est partout la même chose. Dans les brouillons rédigés jusqu'ici, une phrase porte en moyenne environ quatre décisions, et environ une décision sur douze est marquée incertaine. L'IA a pour consigne de marquer un choix serré comme incertain plutôt que de le présenter comme acquis, et le lecteur affiche cette mention.

## Ce que l'IA ne fait pas

Elle ne décide pas que son propre travail est correct. **Rien n'est marqué comme relu par une IA.** Chaque phrase commence avec le statut *assistée par l'IA*, et le garde jusqu'à ce qu'un relecteur humain nommé l'approuve. Dans la base de données du projet, chaque étape du parcours de relecture d'une phrase appartient au compte d'une personne nommée ; l'IA n'a aucun moyen d'approuver ses propres brouillons.

Elle ne prend pas non plus d'autres traductions pour base. Des Bibles anglaises du domaine public peuvent être consultées pour vérifier un brouillon, jamais pour en fournir la formulation, et la formulation des traductions protégées par le droit d'auteur n'est jamais reproduite.

## Les limites de la rédaction par l'IA

Un lecteur a raison de demander ce qu'une IA fait mal. Nous avons vu plusieurs sortes d'erreurs, et le processus est construit autour d'elles.

**La formulation familière attire fortement.** Un modèle d'IA a lu beaucoup de Bibles. Les premiers brouillons de Philippiens 4:6–8 ressemblaient presque mot pour mot à des traductions existantes et ont dû être réécrits à partir du grec. Le guide de style demande désormais à chaque brouillon de partir du grec et de la glose, de comparer ensuite, et de réécrire toute phrase qui reprend une version connue au-delà d'une courte expression courante.

**Les faits peuvent être mal rappelés.** Quand un dossier décrit les témoins manuscrits, la leçon d'un rouleau hébreu ou un auteur de l'Église ancienne, il s'appuie sur ce que le modèle a appris, pas sur une bibliothèque ouverte devant lui. Les dossiers ont pour consigne de le dire. Beaucoup de décisions sur les variantes textuelles se terminent par une note demandant à un relecteur de vérifier les témoins dans l'apparat critique, la liste savante des leçons des manuscrits. Certains dossiers d'Ésaïe vont plus loin et marquent une leçon "de mémoire ; à vérifier". Voir [Quand les manuscrits divergent](/articles/when-manuscripts-disagree/).

**L'aisance n'est pas le jugement.** Un brouillon peut se lire sans heurt et être faux quand même, ou juste pour des raisons qui ne sont pas tout à fait celles qu'il donne. Le ton assuré d'une phrase ne prouve rien en sa faveur.

**Une formulation naturelle demande des locuteurs natifs.** Une IA peut écrire un espagnol, un français ou un swahili grammaticaux. Savoir si une phrase sonne naturellement pour un lecteur qui a grandi avec la langue est une autre question. Le dossier espagnol de Jean 1:1, par exemple, choisit *el Verbo* pour "la Parole" plutôt que *la Palabra*, et signale ce choix pour la relecture d'un locuteur natif.

**La cohérence d'un livre à l'autre est difficile.** Des milliers de phrases rédigées à des moments différents peuvent dériver. Les termes clés vérifiés par le logiciel, les listes de termes pour les longs livres et les décisions qui renvoient aux précédentes vont tous contre cette dérive, mais il en restera que les relecteurs devront trouver.

## Pourquoi utiliser l'IA ?

Un sceptique réfléchi pourrait dire que l'Écriture est trop importante pour être rédigée par une machine. Nous prenons l'objection au sérieux. Notre réponse est que l'IA ne remplace pas les spécialistes ; elle change ce qu'on leur demande de faire.

Écrire les raisons de chaque phrase de la Bible, en langage clair, avec les alternatives envisagées, représente plus de travail que la plupart des équipes de traduction n'en ont jamais eu le temps. Un brouillon dont le raisonnement est exposé donne au relecteur quelque chose de précis à vérifier : un choix énoncé, les options écartées, et une raison qui est solide ou ne l'est pas. Il donne aussi à chaque lecteur la même vue qu'au relecteur. Si le raisonnement est faible, chacun peut voir qu'il est faible.

Ce que la rédaction par l'IA ne peut pas donner, c'est la confiance. Celle-ci doit être gagnée par des personnes qui lisent les langues originales et signent leur travail de leur nom.

## Les étapes de la relecture

Une phrase passe par ces statuts :

- **Assistée par l'IA.** Écrite avec l'IA, vérifiée par le logiciel, pas encore lue par un relecteur.
- **Sens relu.** Un relecteur spécialiste qui lit la langue originale, le grec pour le Nouveau Testament et l'hébreu pour l'Ancien, a vérifié les décisions de sens : ce que dit le texte.
- **Relue.** Un relecteur linguistique, qui maîtrise la langue dans laquelle la phrase est traduite, a aussi vérifié la formulation.
- **Révisée.** La phrase a été modifiée après relecture, et la raison en est consignée.

Chaque étape est enregistrée avec le nom du relecteur, la date et une note, si bien que l'histoire de chaque phrase peut être retracée. Un relecteur peut aussi signaler un problème ou laisser un commentaire sans rien approuver. L'importation de nouveaux brouillons ne remet jamais à zéro le statut de relecture d'une phrase.

## Où en sont les choses aujourd'hui

Les registres de relecture et les rôles de relecteur sont en place dans la base de données du projet, mais les outils dont les relecteurs se serviront sont encore en construction. D'ici là, les fichiers sur GitHub sont la copie de référence de la traduction, et chaque phrase y garde son statut dans les données ouvertes.

Aujourd'hui, aucune phrase de ce site n'a été relue. Toutes, dans toutes les langues, sont des brouillons assistés par l'IA.

## Comment vérifier le travail vous-même

Vous n'avez pas besoin d'attendre les relecteurs pour mettre à l'épreuve ce que vous lisez.

- **Ouvrez le dossier.** Touchez n'importe quel verset pour voir sa glose, ses trois niveaux et chaque décision, avec les alternatives que le dossier a envisagées.
- **Regardez le grec ou l'hébreu.** Touchez un mot dans le panneau pour voir sa forme de dictionnaire, sa grammaire et une glose tirée des données sources.
- **Repérez les choix serrés.** Le lecteur peut signaler les endroits où le sens est incertain, pour que vous voyiez d'un coup d'œil quelles décisions relèvent du jugement.
- **Comparez les niveaux.** La Littérale montre la forme de l'original ; la Simple montre où la traduction a explicité quelque chose. Voir [Trois niveaux, un seul sens](/articles/three-levels-one-meaning/).
- **Lisez l'historique.** Chaque dossier et chacune de ses modifications se trouvent sur GitHub.

## Aidez à relire

Si vous lisez le grec ou l'hébreu, ou si l'espagnol, le français ou le swahili est votre langue maternelle et que vous savez juger si une phrase se lit naturellement, votre aide nous serait précieuse. Tout est ouvert sur [GitHub](https://github.com/jdegreef/open-word-bible), y compris chaque décision et son raisonnement, et le lien "Signaler un problème" en bas de chaque page y ouvre un ticket. Être en désaccord avec une décision, et dire pourquoi, est exactement le genre d'aide dont le projet a besoin.
