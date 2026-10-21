---
title: "Traducción con ayuda de IA y revisión humana: cómo una frase llega a estar «revisada»"
summary: Todo lo que hay hoy en este sitio se traduce con ayuda de IA. Esto es cómo se redacta una frase, qué contiene su registro, qué no puede hacer la redacción con IA y cómo una frase pasa a estar revisada.
date: 2026-10-10
order: 10
section: method
source: c1cfadc5bb1a
---
Open Word Bible se traduce con ayuda de IA. Lo decimos claramente, porque un proyecto que promete mostrar su trabajo no puede ser vago sobre quién hizo ese trabajo. Este artículo explica cómo se redacta una frase, qué puedes ver de ella, dónde se queda corta la redacción con IA y qué tiene que pasar antes de que una frase se considere revisada.

## Cómo se redacta una frase

Tomemos Filipenses 4:6–7, una larga frase griega sobre la preocupación y la oración. Pasa por cuatro pasos.

**1. El texto fuente se carga, no se escribe.** Un programa lee los datos fuente, anclados a una versión exacta: el Nuevo Testamento griego de la SBL con los datos de palabras de MACULA para el Nuevo Testamento, y el Códice de Leningrado de Westminster para el Antiguo. Divide el texto donde la edición termina una frase y escribe un registro vacío para cada una, con el identificador de cada palabra griega y el propio texto griego. Nadie, ni persona ni IA, escribe el original. Véase [Por qué nunca escribimos griego ni hebreo a mano](/articles/never-typed-by-hand/).

**2. La IA escribe un borrador.** A partir del griego, los datos de palabras y una guía de estilo escrita, un modelo de IA rellena el registro: una glosa literal en el orden de las palabras griegas, la traducción en tres niveles en cada idioma y las decisiones que hay detrás. La guía de estilo fija las reglas: qué palabras son términos clave ya establecidos, en qué se diferencia cada nivel, qué puede ir entre corchetes y qué ajustes del lector se aplican en cada caso. Para algunos libros hay además una lista propia de términos establecidos, para que la misma palabra hebrea no salga de tres maneras distintas a lo largo de los sesenta y seis capítulos de Isaías.

**3. El software comprueba las reglas.** Un validador revisa cada registro. Rechaza cualquier palabra griega o hebrea que no sea, letra por letra, una forma o una palabra de diccionario de los datos fuente. Comprueba que cada término clave use su palabra establecida en todos los niveles, salvo que una decisión explique por qué no. Comprueba que cada registro tenga los tres niveles, que un registro termine donde termina una frase y que las decisiones de significado no contengan redacción propia de ningún idioma. Un registro que incumple una regla no entra.

**4. El cambio se hace en público.** Cada pasaje nuevo llega como una propuesta de cambio en GitHub, donde se ejecutan las pruebas y la construcción del sitio antes de incorporarlo. Toda su historia queda allí para quien quiera leerla.

## Qué contiene el registro

Este es el nivel Equilibrada de la frase que salió de esos pasos:

> {{OWB:PHP.4.6.s1:B}}

Su registro contiene el griego, que empieza {{GREEK:PHP.4.6:1-2}}, «por nada os angustiéis»; una glosa literal; los niveles Literal, Equilibrada y Sencilla en inglés, y los mismos tres niveles en otros idiomas a medida que se redactan. También contiene doce decisiones. Siete son decisiones de significado, comunes a todos los idiomas. Una dice que {{LEMMA:PHP.4.6:2}} significa aquí preocupación angustiada, la palabra que usa Jesús en Mateo 6, y no la buena solicitud a la que Pablo la aplica en 2:20. Otra dice que el verbo para «guardar» es lo que hace una guarnición, una imagen que los habitantes de Filipos, una colonia romana con soldados retirados entre sus ciudadanos, habrían captado enseguida. Las otras cinco son decisiones de redacción, cada una para un idioma. Una decisión del inglés, por ejemplo, explica por qué la Equilibrada inglesa dice que la paz "will stand guard over" («montará guardia sobre») vuestros corazones: conserva la imagen del soldado sin el anticuado "keep" («guardar»).

Dos decisiones de este registro están marcadas como inciertas. Una es de significado: la paz que «sobrepasa todo entendimiento» puede ser una paz que está más allá de lo que la mente puede abarcar, o una paz que logra más de lo que lograría cualquier plan humano. El registro sigue la lectura más común y da la otra en una nota al pie. La segunda trata del inglés. El nivel Sencilla dice que la paz te guarda "because you are joined to Christ Jesus" («porque estáis unidos a Cristo Jesús»), donde el griego dice solo «en». La decisión de redacción dice claramente que esto añade una razón que el griego no expresa, y que los revisores deben comprobarlo:

> {{OWB:PHP.4.6.s1:R}}

Ese es el patrón en todas partes. En los borradores hechos hasta ahora, una frase lleva por término medio unas cuatro decisiones, y aproximadamente una decisión de cada doce está marcada como incierta. A la IA se le indica que marque como incierta una decisión reñida en lugar de presentarla como resuelta, y el lector muestra la etiqueta.

## Lo que la IA no hace

No decide que su propio trabajo es correcto. **Ninguna IA marca nada como revisado.** Cada frase empieza con el estado *con ayuda de IA*, y se queda así hasta que la aprueba un revisor humano con nombre. En la base de datos del proyecto, cada paso del historial de revisión de una frase pertenece a la cuenta de una persona con nombre; la IA no tiene forma de aprobar sus propios borradores.

Tampoco usa otras traducciones como base. Se pueden consultar Biblias inglesas de dominio público para comprobar un borrador, nunca para tomar de ellas su redacción, y la redacción de las traducciones con derechos de autor no se reproduce nunca.

## Los límites de la redacción con IA

Un lector hace bien en preguntar en qué se equivoca una IA. Hemos visto varios tipos de error, y el proceso está construido en torno a ellos.

**La redacción conocida tira con fuerza.** Un modelo de IA ha leído muchas Biblias. Los primeros borradores de Filipenses 4:6–8 salieron casi palabra por palabra iguales a traducciones existentes y hubo que reescribirlos a partir del griego. Ahora la guía de estilo indica que todo borrador empiece por el griego y la glosa, compare después y reescriba cualquier frase que coincida con una versión conocida en algo más que una expresión corta y común.

**Los datos pueden recordarse mal.** Cuando un registro describe la evidencia de los manuscritos, la lectura de un rollo hebreo o a un escritor de la iglesia antigua, se apoya en lo que aprendió el modelo, no en una biblioteca abierta delante de él. A los registros se les indica que lo digan. Muchas decisiones sobre variantes textuales terminan con una nota de que un revisor debe comprobar la evidencia con el aparato crítico, la lista académica de lecturas de los manuscritos. Algunos registros de Isaías van más allá y marcan una lectura como «de memoria; por comprobar». Véase [Cuando los manuscritos no coinciden](/articles/when-manuscripts-disagree/).

**La fluidez no es criterio.** Un borrador puede leerse con soltura y aun así estar equivocado, o acertar por razones que no son exactamente las que da. El tono seguro de una frase no prueba nada a su favor.

**La redacción natural necesita hablantes nativos.** Una IA puede escribir un español, un francés, un suajili, un vietnamita o un coreano gramaticales. Que una frase suene natural a un lector que se crio con esa lengua es otra cuestión. El registro español de Juan 1:1, por ejemplo, elige *el Verbo* en lugar de *la Palabra* y señala la elección para que la revise un hablante nativo.

**La coherencia entre libros es difícil.** Miles de frases redactadas en momentos distintos pueden ir desviándose. Los términos clave comprobados por el software, las listas de términos para los libros largos y las decisiones que remiten a otras anteriores trabajan en contra de esa deriva, pero quedará alguna para que la encuentren los revisores.

## ¿Por qué usar IA?

Un escéptico reflexivo podría decir que la Escritura es demasiado importante para redactarla con una máquina. Nos tomamos en serio la objeción. Nuestra respuesta es que la IA no sustituye a los especialistas; cambia lo que se les pide que hagan.

Poner por escrito las razones de cada frase de la Biblia, en lenguaje llano y con las alternativas consideradas, es más trabajo del que la mayoría de los equipos de traducción ha tenido nunca tiempo de hacer. Un borrador con su razonamiento a la vista le da al revisor algo concreto que comprobar: una elección declarada, las opciones descartadas y una razón que es sólida o no lo es. También le da a cada lector la misma vista que tiene el revisor. Si el razonamiento es débil, cualquiera puede ver que es débil.

Lo que la redacción con IA no puede dar es confianza. Esa tienen que ganársela personas que leen las lenguas originales y firman su trabajo con su nombre.

## Los pasos de la revisión

Una frase pasa por estos estados:

- **Con ayuda de IA.** Escrita con IA, comprobada por el software, todavía no leída por un revisor.
- **Significado revisado.** Un revisor especialista que lee la lengua original, griego para el Nuevo Testamento y hebreo para el Antiguo, ha comprobado las decisiones de significado: lo que dice el texto.
- **Revisada.** Un revisor de idioma, que domina la lengua a la que se traduce la frase, ha comprobado también la redacción.
- **Corregida.** La frase se ha cambiado después de la revisión, y consta la razón.

Cada paso se registra con el nombre del revisor, la fecha y una nota, para que pueda seguirse la historia de cada frase. Un revisor también puede señalar un problema o dejar un comentario sin aprobar nada. Importar borradores nuevos nunca restablece el estado de revisión de una frase.

## Cómo están las cosas hoy

Los registros de revisión y los papeles de los revisores ya están en la base de datos del proyecto, pero las herramientas que usarán los revisores todavía se están construyendo. Mientras tanto, los archivos de GitHub son la copia maestra de la traducción, y cada frase guarda allí su estado en los datos abiertos.

Hoy ninguna frase de este sitio ha sido revisada todavía. Todas ellas, en todos los idiomas, son borradores con ayuda de IA.

## Cómo puedes comprobar el trabajo

No tienes que esperar a los revisores para poner a prueba lo que lees.

- **Abre el registro.** Toca cualquier versículo para ver su glosa, sus tres niveles y cada decisión, con las alternativas que el registro consideró.
- **Mira el griego o el hebreo.** Toca una palabra en el panel para ver su forma de diccionario, su gramática y una glosa de los datos fuente.
- **Encuentra las decisiones reñidas.** El lector puede marcar dónde el significado es incierto, para que veas de un vistazo qué decisiones son cuestión de criterio.
- **Compara los niveles.** La Literal muestra la forma del original; la Sencilla muestra dónde la traducción ha explicitado algo. Véase [Tres niveles, un solo significado](/articles/three-levels-one-meaning/).
- **Lee la historia.** Cada registro y cada cambio que se le ha hecho están en GitHub.

## Ayuda a revisar

Si lees griego o hebreo, o si eres hablante nativo de español, francés, suajili, vietnamita o coreano y puedes juzgar si una frase suena natural, tu ayuda sería muy valiosa. Todo está abierto en [GitHub](https://github.com/jdegreef/open-word-bible), incluida cada decisión y su razonamiento, y el enlace «Informar de un problema» al pie de cada página abre allí una incidencia. Discrepar de una decisión, y decir por qué, es exactamente la clase de ayuda que el proyecto necesita.
