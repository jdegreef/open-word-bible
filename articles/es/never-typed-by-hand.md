---
title: Por qué nunca escribimos griego ni hebreo a mano
summary: Una regla firme protege la exactitud de todo lo que Open Word Bible muestra de los idiomas originales. Esta es la regla, y así la hace cumplir el software.
date: 2026-10-10
order: 9
section: method
source: 7442e601ce26
---
Open Word Bible tiene una regla que sorprende a la gente: nadie, ni humano ni IA, escribe jamás una palabra griega o hebrea en la traducción ni en sus notas. Cada palabra en idioma original que ves en este sitio, incluido el griego de estos artículos, la copia el software de datos fuente fijos.

## Por qué

El griego y el hebreo son difíciles de escribir correctamente. El griego tiene acentos y espíritus; el hebreo tiene puntos vocálicos y signos de cantilación. Muchos de ellos se ven casi idénticos en pantalla, pero por debajo son caracteres distintos. Una palabra escrita de memoria puede parecer correcta y aun así estar mal: un acento distinto, un espíritu que falta, una letra que ni siquiera existe en la fuente.

En las primeras pruebas, el griego escrito de memoria contenía exactamente esos errores. Una traducción que dice mostrar su trabajo no puede mostrar palabras equivocadas.

## Las fuentes

El texto procede de ediciones fijas con licencia abierta, cada una anclada a una versión exacta para que todo resultado pueda reproducirse:

- **Nuevo Testamento:** el Nuevo Testamento griego de la SBL (versión 1.2), con datos palabra por palabra de MACULA Greek.
- **Antiguo Testamento:** el Códice de Leningrado de Westminster, con datos de palabras de MACULA Hebrew y de la Open Scriptures Hebrew Bible.

Los créditos completos están en la página [Acerca de](/about/).

## Cómo se hace cumplir

La regla no es solo una costumbre: el software la comprueba en cada cambio.

- El texto original de cada frase se reconstruye a partir de los datos fuente, y una frase cuyo texto no coincide se rechaza.
- Cualquier palabra griega o hebrea en cualquier otro lugar, en una glosa, una traducción o una nota, debe coincidir exactamente, carácter por carácter, con una forma o una palabra de diccionario de los datos fuente. Una palabra con un acento equivocado no pasa la comprobación.
- Estos artículos citan el griego mediante marcadores que el sitio rellena con los datos al construirse. Cuando este artículo muestra las primeras palabras del Evangelio de Juan, {{GREEK:JHN.1.1:1-5}}, las palabras vienen de los datos del Nuevo Testamento griego de la SBL, no de un teclado.

Estas comprobaciones se ejecutan automáticamente antes de publicar nada.
