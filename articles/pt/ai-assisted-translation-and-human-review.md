---
title: "Tradução com ajuda de IA e revisão humana: como uma frase passa a ser \"revisada\""
summary: Tudo neste site hoje é traduzido com ajuda de IA. Eis como uma frase é redigida, o que o seu registro contém, o que a redação por IA não consegue fazer e como uma frase passa a ser revisada.
date: 2026-10-10
order: 10
section: method
source: 2f05369a7dc4
---
A Open Word Bible é traduzida com a ajuda de IA. Dizemos isso claramente, porque um projeto que promete mostrar o seu trabalho não pode ser vago sobre quem fez o trabalho. Este artigo explica como uma frase é redigida, o que você pode ver dela, onde a redação por IA deixa a desejar e o que precisa acontecer antes que qualquer frase seja chamada de revisada.

## Como uma frase é redigida

Tome Filipenses 4:6–7, uma longa frase grega sobre a preocupação e a oração. Ela passa por quatro etapas.

**1. A fonte é carregada, não digitada.** Um script lê os dados-fonte fixos, o SBL Greek New Testament com os dados palavra por palavra do MACULA para o Novo Testamento e o Códice de Leningrado de Westminster para o Antigo. Ele divide o texto onde a edição termina uma frase e escreve um registro vazio para cada uma, com a identificação de cada palavra grega e o próprio texto grego. Ninguém, nem humano nem IA, digita o original. Veja [Por que nunca digitamos grego ou hebraico à mão](/articles/never-typed-by-hand/).

**2. A IA escreve um rascunho.** Trabalhando a partir do grego, dos dados das palavras e de um guia de estilo escrito, um modelo de IA preenche o registro: uma glosa literal na ordem das palavras gregas, a tradução em três níveis em cada língua e as decisões por trás deles. O guia de estilo define as regras: quais palavras são termos-chave já fixados, como cada nível se diferencia, o que pode ir entre colchetes, quais configurações de leitura se aplicam e onde. Para alguns livros há uma lista à parte de termos fixados, para que a mesma palavra hebraica não saia de três maneiras diferentes ao longo dos sessenta e seis capítulos de Isaías.

**3. O software confere as regras.** Um validador roda em cada registro. Ele rejeita qualquer palavra grega ou hebraica que não seja, letra por letra, uma forma ou uma palavra de dicionário dos dados-fonte. Ele confere se cada termo-chave usa a sua palavra fixada em todos os níveis, a não ser que uma decisão explique por que não. Ele confere se cada registro tem os três níveis, se um registro termina onde termina uma frase e se as decisões de sentido não contêm formulações próprias de uma só língua. Um registro que quebra uma regra não entra.

**4. A mudança é feita em público.** Cada nova passagem chega como uma proposta de mudança no GitHub, onde os testes e a geração do site rodam antes de ela ser incorporada. Todo o seu histórico fica ali para ser lido.

## O que o registro contém

Este é o nível Equilibrada da frase que saiu dessas etapas:

> {{OWB:PHP.4.6.s1:B}}

O seu registro contém o grego, que começa com {{GREEK:PHP.4.6:1-2}}, "com nada fiquem ansiosos"; uma glosa literal; os níveis Literal, Equilibrada e Acessível em inglês; e os mesmos três níveis em outras línguas, à medida que são redigidos. Ele também contém doze decisões. Sete são decisões de sentido, comuns a todas as línguas. Uma diz que {{LEMMA:PHP.4.6:2}} significa aqui a preocupação ansiosa, a palavra que Jesus usa em Mateus 6, e não a boa preocupação pelos outros para a qual Paulo a usa em 2:20. Outra diz que o verbo para "guardar" é o que faz uma guarnição, uma imagem que o povo de Filipos, uma colônia romana com soldados aposentados entre os seus cidadãos, teria sentido. As outras cinco são decisões de formulação, cada uma para uma língua. Uma decisão do inglês, por exemplo, explica por que a Equilibrada diz que a paz vai "stand guard over" os corações: ela mantém a imagem do soldado sem o antiquado "keep". O português faz a mesma escolha, "montará guarda sobre", e registra isso numa decisão própria.

Duas decisões deste registro estão marcadas como incertas. Uma é sobre o sentido: a paz que "supera todo entendimento" pode ser a paz que vai além do que a mente consegue compreender, ou a paz que consegue mais do que qualquer plano humano conseguiria. O registro segue a leitura mais comum e dá a outra numa nota de rodapé. A segunda é sobre a formulação em inglês. O nível Acessível diz que a paz guarda vocês "porque vocês estão unidos a Cristo Jesus", onde o grego diz só "em". A decisão de formulação diz claramente que isso acrescenta uma razão que o grego deixa implícita, e que os revisores devem conferi-la. O português Acessível diz o mesmo:

> {{OWB:PHP.4.6.s1:R}}

Esse é o padrão em toda parte. Nos rascunhos feitos até agora, uma frase traz em média cerca de quatro decisões, e cerca de uma decisão em cada doze está marcada como incerta. A IA é instruída a marcar uma decisão apertada como incerta, em vez de apresentá-la como resolvida, e o leitor mostra a etiqueta.

## O que a IA não faz

Ela não decide que o seu próprio trabalho está correto. **Nada é marcado como revisado por uma IA.** Toda frase começa com o status *rascunho feito com ajuda de IA* e continua assim até que um revisor humano identificado a aprove. No banco de dados do projeto, cada etapa do histórico de revisão de uma frase pertence à conta de uma pessoa identificada; a IA não tem como aprovar os seus próprios rascunhos.

Ela também não usa outras traduções como base. As Bíblias inglesas de domínio público podem ser consultadas para conferir um rascunho, nunca para fornecer a sua formulação, e a formulação de traduções protegidas por direitos autorais nunca é reproduzida.

## Os limites da redação por IA

Um leitor tem razão em perguntar o que uma IA erra. Já vimos vários tipos de erro, e o processo foi construído em torno deles.

**A formulação conhecida puxa com força.** Um modelo de IA leu muitas Bíblias. Os primeiros rascunhos de Filipenses 4:6–8 saíram quase palavra por palavra como traduções existentes e tiveram de ser reescritos a partir do grego. O guia de estilo agora manda que todo rascunho comece pelo grego e pela glosa, compare depois e reescreva qualquer frase que coincida com uma versão conhecida por mais do que uma expressão curta e comum.

**Os fatos podem ser lembrados errado.** Quando um registro descreve as evidências dos manuscritos, a leitura de um rolo hebraico ou um escritor da Igreja antiga, ele se baseia no que o modelo aprendeu, não numa biblioteca aberta diante dele. Os registros são instruídos a dizer isso. Muitas decisões sobre variantes textuais terminam com uma observação de que um revisor precisa conferir as evidências com o aparato, a lista acadêmica das leituras dos manuscritos. Alguns dos registros de Isaías vão além e marcam uma leitura como "de memória; a ser conferida". Veja [Quando os manuscritos divergem](/articles/when-manuscripts-disagree/).

**Fluência não é discernimento.** Um rascunho pode ser lido com facilidade e ainda assim estar errado, ou estar certo por razões que não são exatamente as declaradas. O tom confiante de uma frase não é prova a seu favor.

**A formulação natural precisa de falantes nativos.** Uma IA consegue escrever espanhol, francês, suaíli, vietnamita, coreano, português, amárico, híndi ou russo gramaticalmente corretos. Se uma frase soa natural para um leitor que cresceu com a língua é outra questão. O registro em espanhol de João 1:1, por exemplo, escolhe *el Verbo* em vez de *la Palabra* para "o Verbo" e assinala a escolha para a revisão de um falante nativo.

**A coerência entre os livros é difícil.** Milhares de frases redigidas em momentos diferentes podem se desviar umas das outras. Os termos-chave conferidos por software, as listas de termos dos livros longos e as decisões que citam decisões anteriores trabalham contra isso, mas algum desvio vai restar para os revisores encontrarem.

## Por que usar IA?

Um cético atento poderia dizer que as Escrituras são importantes demais para serem redigidas por uma máquina. Levamos o argumento a sério. A nossa resposta é que a IA não substitui os estudiosos; ela muda o que se pede a eles.

Escrever as razões de cada frase da Bíblia, em linguagem simples, com as alternativas consideradas, é mais trabalho do que a maioria das equipes de tradução jamais teve tempo de fazer. Um rascunho com o seu raciocínio exposto dá ao revisor algo definido para conferir: uma escolha declarada, as opções deixadas de lado e uma razão que é sólida ou não. Ele também dá a cada leitor a mesma visão que o revisor tem. Se o raciocínio é fraco, qualquer pessoa pode ver que é fraco.

O que a redação por IA não pode dar é confiança. Essa precisa ser conquistada por pessoas que leem as línguas originais e assinam o seu trabalho.

## As etapas da revisão

Uma frase passa por estes status:

- **Rascunho, ainda não revisado.** Escrita com IA, conferida por software, ainda não lida por um revisor.
- **Sentido revisado.** Um revisor acadêmico que lê a língua original, o grego para o Novo Testamento e o hebraico para o Antigo, conferiu as decisões de sentido: o que o texto diz.
- **Revisado.** Um revisor de língua, um leitor fluente da língua para a qual a frase é traduzida, também conferiu a formulação.
- **Corrigido após a revisão.** A frase foi alterada depois da revisão, com a razão registrada.

Cada etapa é registrada com o nome do revisor, a data e uma observação, de modo que o histórico de cada frase pode ser rastreado. Um revisor também pode assinalar um problema ou deixar um comentário sem aprovar nada. Importar novos rascunhos nunca zera o status de revisão de uma frase.

## Em que pé as coisas estão hoje

Os registros de revisão e as funções de revisor já existem no banco de dados do projeto, mas as ferramentas que os revisores vão usar ainda estão sendo construídas. Até que fiquem prontas, os arquivos no GitHub são a cópia principal da tradução, e cada frase mantém ali o seu status, nos dados abertos.

Hoje nenhuma frase deste site foi revisada. Todas elas, em todas as línguas, são rascunhos feitos com ajuda de IA.

## Como você pode conferir o trabalho

Você não precisa esperar os revisores para testar o que lê.

- **Abra o registro.** Toque em qualquer versículo para ver a sua glosa, os seus três níveis e cada decisão, com as alternativas que o registro considerou.
- **Olhe o grego ou o hebraico.** Toque numa palavra no painel para ver a sua forma de dicionário, a sua gramática e uma glosa dos dados-fonte.
- **Encontre as decisões apertadas.** O leitor pode marcar onde o sentido é incerto, para que você veja num relance quais decisões são questões de discernimento.
- **Compare os níveis.** A Literal mostra a forma do original; a Acessível mostra onde a tradução explicitou alguma coisa. Veja [Três níveis, um sentido](/articles/three-levels-one-meaning/).
- **Leia o histórico.** Cada registro e cada mudança nele estão no GitHub.

## Ajude a revisar

Se você lê grego ou hebraico, ou é falante nativo de espanhol, francês, suaíli, vietnamita, coreano, português, amárico, híndi ou russo e consegue avaliar se uma frase soa natural, a sua ajuda será muito bem-vinda. Tudo está aberto no [GitHub](https://github.com/jdegreef/open-word-bible), inclusive cada decisão e o seu raciocínio, e o link "Relatar um problema", no rodapé de cada página, abre uma *issue* ali. Discordar de uma decisão, e dizer por quê, é exatamente o tipo de ajuda de que o projeto precisa.
