# Euclides

Euclides e uma aplicacao web em Streamlit para estudo de artigos em PDF. A proposta e oferecer uma experiencia parecida com um notebook de pesquisa: o usuario adiciona fontes, visualiza os documentos carregados e usa uma area de chat e ferramentas de estudo para explorar o conteudo.

## Endpoint publicado

A aplicacao esta publicada no Streamlit Cloud:

```text
https://euclides.streamlit.app/
```

Esse endpoint e a versao publica usada para avaliacao. A versao local pode ser executada com o comando abaixo.

## Como executar

```powershell
streamlit run app.py
```

Depois acesse:

```text
http://localhost:8501
```

## 1. Descricao do problema e da solucao proposta

O problema principal e que estudantes e pesquisadores normalmente precisam ler varios artigos em PDF, comparar ideias, extrair informacoes e transformar o conteudo em resumos, mapas mentais ou tabelas. Esse processo costuma ser manual, demorado e disperso entre muitas ferramentas.

O Euclides propoe centralizar esse fluxo em uma unica interface:

- uma area de **Fontes**, onde o usuario carrega ate 3 documentos em PDF;
- uma lista visivel dos arquivos carregados;
- um **chat** para fazer perguntas sobre os artigos;
- ferramentas de estudo para gerar **resumo**, **mapa mental** e **tabela de dados**;
- uma area de configuracao futura para modelo, prompt, modo de ensino e ferramentas ativas.

Nesta primeira versao, a aplicacao ainda nao usa uma LLM real. As respostas e acoes de IA sao simuladas para validar a experiencia de uso. Futuramente, a IA sera integrada por meio de um fluxo RAG: os PDFs serao lidos, divididos em trechos, indexados em uma base vetorial e consultados por um modelo de linguagem. O chat e as ferramentas de resumo, mapa mental e tabela usarao esses trechos para responder com base nas fontes carregadas.

## 2. Escolhas de design

O projeto foi desenvolvido em **Streamlit** porque a prioridade era construir rapidamente uma interface web funcional, navegavel e facil de testar. Streamlit permite criar upload de arquivos, abas, formularios, chat e componentes interativos com pouco codigo, o que combina bem com um prototipo academico.

A interface foi organizada em duas areas principais:

- **Barra lateral**: concentra fontes e configuracoes. Essa escolha deixa o espaco principal livre para o estudo e segue o padrao de ferramentas como notebooks de IA, onde o contexto fica separado da conversa.
- **Area principal**: exibe o logo, o chat e as funcoes de estudo. O usuario consegue conversar com os documentos e alternar entre resumo, mapa mental e tabela sem sair da tela.

Tambem foram adicionados paineis de configuracao inspirados em interfaces de LLM:

- **Model settings** para provedor, modelo, temperatura e max tokens;
- **Model config** para opcoes futuras de recuperacao e citacao;
- **Teaching mode** para definir o estilo pedagogico da resposta;
- **Active tools** para visualizar quais funcoes estarao disponiveis;
- **Final system prompt preview** para mostrar como o prompt final sera montado.
- **Arquitetura futura de IA** para demonstrar o fluxo planejado: PDF, extracao de texto, RAG, orquestracao, modelo e resposta com evidencias.

Esses componentes ainda nao executam IA, mas tornam clara a arquitetura futura. A alternativa seria criar apenas um chat simples, mas isso deixaria o projeto menos ambicioso e menos preparado para agentes, ferramentas e modelos. Outra alternativa seria integrar LangChain desde o inicio, mas isso aumentaria a complexidade antes de validar a interface. Por isso, a primeira etapa foca em UI e fluxo de usuario.

## 3. O que funcionou

O agente de codificacao gerou bem a estrutura inicial do projeto. A partir de prompts em linguagem natural, ele criou uma aplicacao Streamlit com upload de PDF, limite de 3 arquivos, lista de fontes, chat simulado e abas para resumo, mapa mental e tabela de dados.

Exemplo de prompt que funcionou bem:

```text
o projeto vai ser uma aplicacao para estudo que vai ser tipo notebook klm...
preciso uma area de Fontes, onde vou adicionar so artigos em pdf...
so vai recever 3 arquivos como maximo...
vai ter um chat...
uma de resumo... mapa mental... tabela de dados
```

Esse prompt funcionou porque descreveu claramente o objetivo, o estilo de produto e os fluxos principais da interface. O agente conseguiu transformar a descricao em componentes concretos do Streamlit.

Outro prompt que gerou bons resultados foi:

```text
minha interface pode ter esas carateristicas...
Model settings, Model config, Teaching mode, Active tools e Final system prompt preview
Ainda nao precisso nada de agentes e ferramentas, so preciso deixar pronto a visualizacao
```

Esse pedido foi efetivo porque definiu exatamente o escopo: adicionar visualizacao e preparacao futura, sem implementar agentes ou modelos reais. O resultado foi uma barra lateral com configuracoes editaveis e preview do system prompt.

Tambem funcionou bem a verificacao do endpoint. O servidor Streamlit respondeu com status HTTP 200 em `http://localhost:8501`, indicando que a aplicacao estava acessivel.

## 4. O que nao funcionou

Algumas limitacoes apareceram durante o processo.

Primeiro, o comando `python` do ambiente nao estava funcionando corretamente. Ao tentar validar a sintaxe com `python -m py_compile app.py`, o sistema retornou erro de sessao. O comando `py` tambem nao encontrou uma instalacao Python valida. A solucao foi usar diretamente o executavel do Streamlit, que ja estava instalado e respondeu corretamente.

Segundo, na primeira criacao dos arquivos, `app.py` e `requirements.txt` foram adicionados na raiz do usuario em vez da pasta do projeto. Isso precisou ser corrigido movendo os arquivos para `C:\Users\BEIKER\Downloads\Notebook_Euclides`.

Terceiro, a validacao visual pelo navegador integrado nao ficou disponivel nesta sessao. A aplicacao foi verificada por resposta HTTP 200 e por revisao do codigo, mas uma validacao completa de clique em cada componente no navegador ainda deve ser feita manualmente ou com uma ferramenta de browser funcional.

Quarto, a aplicacao ainda nao processa o conteudo real dos PDFs. Ela armazena os arquivos na sessao e simula respostas. Isso e suficiente para validar o fluxo de interface, mas nao para responder perguntas reais sobre os artigos.

Quinto, foi identificado um problema nos campos de texto das funcoes de estudo: o input de "Topico para resumir" nao permitia digitacao corretamente. A causa provavel era o uso de HTML customizado envolvendo widgets nativos do Streamlit. A correcao substituiu esses wrappers por `st.container(border=True)`, mantendo o visual de painel sem bloquear a interacao.

Se o projeto fosse refeito, uma melhoria seria criar desde o inicio uma estrutura de pastas separada, por exemplo:

```text
services/
  pdf_loader.py
  rag_service.py
  llm_service.py
components/
  sources.py
  chat.py
  settings.py
```

Essa separacao facilitaria a proxima etapa, quando forem adicionados extracao de texto dos PDFs, embeddings, busca semantica e conexao com uma LLM.

## 5. Uso efetivo do agente de codificacao

A maior parte do codigo inicial foi gerada com apoio do agente de codificacao, a partir de prompts em linguagem natural e iteracoes sucessivas. O estudante atuou definindo o escopo, revisando os criterios da rubrica, solicitando ajustes e validando se a interface correspondia ao objetivo do projeto.

Principais iteracoes realizadas:

1. **Criacao da aplicacao base**

Prompt usado:

```text
agora vou comecar um novo rpojeto, o projeto vai ser uma aplicacao para estudo
que vai ser tipo notebook klm... vai ser desenvolvida em streamlit...
preciso uma area de Fontes... adicionar fontes... artigos ou documentos em pdf...
so vai recever 3 arquivos como maximo...
vai ter um chat... uma de resumo... mapa mental... tabela de dados...
```

Resultado gerado pelo agente:

- `app.py` com interface Streamlit;
- logo textual do Euclides no topo;
- upload de PDFs;
- limite de 3 arquivos;
- lista de fontes carregadas;
- chat simulado;
- abas para resumo, mapa mental e tabela.

2. **Expansao da interface para configuracoes futuras de IA**

Prompt usado:

```text
minha interface pode ter esas carateristicas...
Model settings, Model config, Teaching mode, Active tools e Final system prompt preview...
Ainda nao precisso nada de agentes e ferramentas,
so preciso deixar pronto a visualizacao para em uma etapa futura
```

Resultado gerado pelo agente:

- paineis de configuracao na barra lateral;
- selecao visual de provedor/modelo;
- temperatura e max tokens;
- modo de ensino;
- ferramentas ativas;
- preview do system prompt final com placeholders.
- pipeline visual de IA futura;
- simulador de execucao para chat, resumo, mapa mental e tabela.

3. **Avaliacao dos criterios da rubrica**

Prompts usados:

```text
preciso que avalie se o aplicativo cumpre os proximos criterios:
1. Endpoint Funcional
```

```text
2. Complexidade e Ambicao do Problema
```

```text
4. README — Documentacao do Processo
```

Resultado gerado pelo agente:

- avaliacao do endpoint funcional;
- avaliacao da complexidade e ambicao;
- criacao deste README com os blocos exigidos pela rubrica;
- verificacao de que o servidor Streamlit respondia em `http://localhost:8501` com status HTTP 200.

4. **Intervencoes e supervisao**

O agente nao trabalhou de forma totalmente autonoma sem direcao. O estudante supervisionou o processo, corrigiu o rumo do projeto e pediu explicitamente que agentes e ferramentas reais ainda nao fossem implementados. Essa decisao manteve o escopo adequado para a etapa atual: uma interface funcional e preparada para evolucao futura.

Tambem houve ajustes tecnicos durante a execucao:

- os arquivos `app.py` e `requirements.txt` foram movidos para a pasta correta do projeto;
- o app foi executado com `streamlit run app.py`;
- o endpoint foi verificado por resposta HTTP 200;
- o README foi criado depois da revisao dos criterios da rubrica.
- a simulacao visual de pipeline foi adicionada para evidenciar a preparacao futura para IA sem criar dependencias externas.
- um bug de interacao nos campos das funcoes de estudo foi corrigido depois de teste manual da interface.

Essa sequencia demonstra uso extensivo do agente, com varias iteracoes, prompts documentados e codigo gerado a partir de supervisao humana.

## Estado atual

O Euclides atualmente entrega uma interface web funcional e navegavel, com dados simulados. A arquitetura visual ja mostra como a IA sera integrada futuramente, mas a camada real de processamento de documentos e modelos ainda sera implementada em uma proxima etapa.
