---
title: Por que nunca digitamos grego ou hebraico à mão
summary: Uma regra firme protege a exatidão de tudo o que a Open Word Bible mostra das línguas originais. Eis a regra e como o software a faz cumprir.
date: 2026-10-10
order: 9
section: method
source: f5bf26398aaa
---
A Open Word Bible tem uma regra que surpreende as pessoas: ninguém, nem humano nem IA, jamais digita uma palavra grega ou hebraica na tradução ou nas suas notas. Cada palavra na língua original que você vê neste site, inclusive o grego e o hebraico destes artigos, é copiada por software a partir de dados-fonte fixos.

## Por quê

O grego e o hebraico são difíceis de digitar corretamente. O grego tem acentos e sinais de aspiração; o hebraico tem sinais vocálicos e sinais de cantilação. Muitos deles parecem quase idênticos na tela, mas são caracteres diferentes por trás. Um ômicron grego e um "o" latino têm a mesma aparência na maioria das fontes. Algumas vogais gregas acentuadas podem ser armazenadas de duas maneiras diferentes que aparecem iguais na tela. Uma palavra digitada de memória pode parecer certa e ainda assim estar errada: um acento diferente, uma aspiração que falta, uma letra que nem existe na fonte.

Nos primeiros testes, o grego digitado de memória continha exatamente esses erros. Uma tradução que afirma mostrar o seu trabalho não pode mostrar as palavras erradas.

## As fontes

O texto vem de edições fixas e de licença aberta, cada uma fixada numa versão exata, para que todo resultado possa ser reproduzido:

- **Novo Testamento:** o Novo Testamento Grego da SBL (versão 1.2), com dados palavra por palavra do MACULA Greek.
- **Antigo Testamento:** o Códice de Leningrado de Westminster, com dados das palavras do MACULA Hebrew e da Open Scriptures Hebrew Bible.

"Fixada" significa mais do que dar o nome de uma edição. O projeto registra a revisão exata de cada fonte que baixa, para que o texto não possa mudar por baixo da tradução sem que ninguém perceba. Os créditos completos estão na página [Sobre](/about/).

## Como a regra é aplicada

A regra não é só um hábito; o software a verifica a cada alteração.

- O texto original de cada frase é reconstruído a partir dos dados-fonte, e uma frase cujo texto não confere é rejeitada.
- Qualquer palavra grega ou hebraica em qualquer outro lugar, numa glosa, numa tradução ou numa nota, tem de coincidir exatamente, caractere por caractere, com uma forma ou uma palavra de dicionário dos dados-fonte. Uma palavra com um acento errado não passa na verificação.
- Estes artigos citam o grego e o hebraico por meio de marcadores que o site preenche a partir dos dados quando é gerado. Quando este artigo mostra as primeiras palavras do Evangelho de João, {{GREEK:JHN.1.1:1-5}}, as palavras vêm dos dados do Novo Testamento Grego da SBL, não de um teclado.

Um marcador indica um versículo e o número de uma palavra. A primeira palavra de Gênesis, {{HEBREW:GEN.1.1:1}}, é escrita como uma só palavra, mas tem duas partes: um prefixo que significa "em" e o substantivo "princípio". Um marcador pode pedir só a segunda parte, na sua forma de dicionário, {{LEMMA:GEN.1.1:1.2}}. As duas não são bem iguais: a forma do texto leva um sinal de cantilação para o canto, e a forma de dicionário não. Digitada à mão, essa diferença é fácil de errar. Copiada dos dados, não pode estar errada.

Essas verificações são feitas automaticamente antes que qualquer coisa seja publicada. Um marcador que aponta para uma palavra grega num versículo do Antigo Testamento, ou para uma palavra que não existe, impede que o site seja gerado.

## Perguntas justas

**Isso quer dizer que o texto-fonte nunca pode ser questionado?** Não. O texto-fonte nunca é editado, mas a tradução pode discordar dele, abertamente. Em João 1:3, o registro lê a pontuação de um modo diferente do Novo Testamento Grego da SBL, e uma decisão explica por quê. Onde os manuscritos divergem, uma decisão descreve a outra leitura. O texto-base continua fixo para que todo afastamento dele fique visível.

**Uma palavra verificada garante uma nota correta?** Não. A verificação prova que uma palavra está mesmo na fonte. Não pode provar que uma nota diz a coisa certa sobre ela. É para isso que existem os revisores humanos.
