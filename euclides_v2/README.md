# Euclides v2

Esta pasta contem uma evolucao separada do Euclides original. A proposta e continuar o desenvolvimento em fases, sem modificar o `app.py` da raiz do repositorio.

O Euclides original funciona como prototipo visual. A `euclides_v2` comeca a transformar esse prototipo em uma aplicacao funcional para estudo com PDFs, busca de trechos, chat com contexto e ferramentas academicas.

## Objetivo da v2

Construir uma arquitetura simples e expansivel para:

- carregar ate 3 PDFs;
- extrair texto real dos arquivos;
- diagnosticar se o PDF foi lido corretamente;
- buscar trechos relevantes dentro dos textos;
- preparar o chat para responder usando contexto recuperado;
- preparar ferramentas de resumo, mapa mental e tabela;
- manter a escolha futura entre provedores como Ollama, OpenAI e Gemini.

## Arquitetura planejada

```text
Euclides

        PDFs
         |
    Extracao de texto
         |
   Divisao em trechos
         |
   Busca / Recuperacao
         |
   +-----+--------+------------+
   |     |        |            |
 Chat  Resumo  Mapa mental  Tabela
   |     |        |            |
   +-----+--------+------------+
         |
   +-----+--------+
   |     |        |
 Ollama OpenAI  Gemini
   |     |        |
   +-----+--------+
         |
  Resposta final
```

Nesta etapa, a parte de modelo ainda e simulada. O foco atual e garantir que o PDF seja lido e que a busca inicial consiga encontrar trechos uteis.

## Estrutura de pastas

```text
euclides_v2/
  README.md
  app.py
  requirements.txt
  components/
    chat.py
    retrieval_preview.py
    sidebar.py
    source_diagnostics.py
    study_tools.py
  models/
    source.py
  services/
    chunking.py
    context_builder.py
    llm_service.py
    pdf_loader.py
    retrieval.py
    tool_service.py
```

## Responsabilidade dos arquivos

### `app.py`

Arquivo principal da aplicacao Streamlit v2.

Ele:

- inicializa o estado da sessao;
- carrega a sidebar;
- renderiza chat;
- renderiza diagnostico das fontes;
- renderiza painel de teste de busca;
- renderiza ferramentas de estudo.

### `components/sidebar.py`

Controla a barra lateral.

Inclui:

- upload de PDFs;
- limite de 3 fontes;
- lista de arquivos carregados;
- remocao de arquivos;
- configuracao futura de modelos;
- preview do prompt final.

Paineis disponiveis:

- `Model settings`;
- `Model config`;
- `Teaching mode`;
- `Active tools`;
- `Final system prompt preview`.

### `components/source_diagnostics.py`

Painel de diagnostico dos PDFs.

Ele mostra:

- quantidade de fontes;
- total de paginas;
- paginas com texto extraido;
- quantidade de trechos;
- preview curto do texto extraido;
- aviso quando o PDF parece escaneado ou composto por imagens;
- erro amigavel quando o arquivo nao pode ser lido.

Este painel e principalmente util durante o desenvolvimento. Na versao final, pode continuar como uma area avancada ou de diagnostico.

### `components/retrieval_preview.py`

Painel de teste da busca inicial.

Permite digitar uma consulta e visualizar:

- trechos encontrados;
- arquivo de origem;
- pagina;
- score da busca;
- termos encontrados;
- preview do trecho.

Esse painel valida a Fase 2 antes de conectar uma LLM real.

### `components/chat.py`

Interface do chat.

Atualmente:

- recebe perguntas do usuario;
- valida se ha PDF carregado;
- valida se ha texto extraivel;
- usa a busca simples para recuperar trechos;
- envia os trechos para uma resposta simulada em `llm_service.py`.

Na proxima fase, este componente deve passar a montar um prompt com contexto real e enviar para um provedor de modelo.

### `components/study_tools.py`

Interface das ferramentas de estudo.

Inclui:

- resumo;
- mapa mental;
- tabela de dados.

Atualmente, as ferramentas usam a mesma busca ranqueada do chat e retornam saidas simuladas baseadas nos trechos recuperados.

Cada ferramenta tambem mostra o prompt preparado para uma LLM futura.

### `models/source.py`

Modelos de dados principais.

Contem:

- `SourceFile`: representa um PDF carregado.
- `DocumentChunk`: representa um trecho extraido de uma pagina.
- `RetrievedChunk`: representa um trecho recuperado pela busca, com score e termos encontrados.
- `PdfDiagnostic`: representa o diagnostico de um PDF.
- `PdfCorpus`: junta todos os trechos e diagnosticos de uma colecao de PDFs.

### `services/pdf_loader.py`

Servico de leitura dos PDFs.

Responsabilidades:

- abrir PDFs a partir dos bytes carregados;
- extrair texto pagina por pagina com `pypdf`;
- limpar espacos repetidos;
- criar `DocumentChunk` com nome do arquivo, pagina e trecho controlado;
- gerar diagnostico tecnico do PDF;
- usar cache do Streamlit para evitar reprocessar os mesmos PDFs a cada painel;
- tratar erros de leitura sem quebrar a aplicacao.

### `services/chunking.py`

Servico de divisao de texto em trechos menores.

Ele:

- recebe o texto extraido de uma pagina;
- limpa espacos repetidos;
- divide textos longos em chunks com tamanho controlado;
- preserva uma pequena sobreposicao entre chunks;
- tenta cortar em fim de frase ou espaco quando possivel.

### `services/retrieval.py`

Servico de busca inicial.

Ainda nao usa embeddings. A busca atual e lexical, baseada em palavras.

Ela faz:

- normalizacao de acentos;
- conversao para minusculas;
- tokenizacao por termos com 3 ou mais caracteres;
- remocao de palavras comuns;
- expansao simples de termos academicos em portugues para equivalentes em ingles;
- calculo de score por frequencia de termos inteiros e cobertura da consulta;
- ordenacao dos trechos mais relevantes.

A expansao portugues-ingles foi adicionada porque muitos artigos academicos estao em ingles, mas o usuario pode fazer perguntas em portugues. Exemplo:

```text
metodologia -> methodology, methods
resultados -> results, findings
amostra -> sample
participantes -> participants
```

Essa expansao acontece antes da etapa de LLM. Ela serve apenas para recuperar trechos melhores. A LLM futura recebera os trechos encontrados como contexto; ela nao precisa saber que a busca expandiu os termos.

Na versao com RAG vetorial, a busca semantica deve ser a estrategia principal. A busca lexical com expansao pode continuar como complemento ou fallback para nomes, siglas, termos tecnicos e palavras exatas.

### `services/llm_service.py`

Servico placeholder para resposta com modelo.

Atualmente nao chama OpenAI, Gemini nem Ollama. Ele apenas monta uma resposta simulada usando os trechos recuperados.

Esse isolamento e intencional: quando um modelo real for conectado, a mudanca principal deve acontecer neste arquivo.

### `services/context_builder.py`

Servico responsavel por montar o contexto que sera enviado ao modelo.

Ele:

- formata citacoes por arquivo e pagina;
- monta um bloco de contexto com score, termos encontrados e trecho;
- monta um prompt final com pergunta do usuario, prompt base da sidebar e contexto recuperado;
- gera um resumo das fontes consultadas.

### `services/tool_service.py`

Servico placeholder para ferramentas academicas.

Contem funcoes para:

- gerar resumo simulado;
- gerar mapa mental simulado;
- gerar tabela de dados simulada.
- montar prompts especificos para cada ferramenta.

As ferramentas ja usam os resultados ranqueados da busca, incluindo fonte, pagina, score e termos encontrados. Na fase de LLM, essas funcoes devem trocar a simulacao por chamadas reais ao provedor selecionado.

## Fases de desenvolvimento

## Fase 1 - PDF funcional

Status: implementada.

Objetivo: garantir que o app consiga receber PDFs e extrair texto de forma confiavel.

O que foi feito:

1. Criada a pasta `euclides_v2` para nao alterar o app original.
2. Criada estrutura modular com `components/`, `services/` e `models/`.
3. Adicionado `pypdf` em `requirements.txt`.
4. Criado `SourceFile` para representar os arquivos carregados.
5. Criado `DocumentChunk` para representar texto extraido por pagina e dividido em trechos.
6. Criado `PdfDiagnostic` para registrar paginas, trechos, preview e erros.
7. Criado `PdfCorpus` para reunir trechos e diagnosticos.
8. Implementado `pdf_loader.py` para extrair texto dos PDFs.
9. Criado painel `Diagnostico das fontes`.
10. Adicionado preview do texto extraido.
11. Adicionados avisos para PDFs sem texto extraivel.
12. Adicionado tratamento de erro para PDF invalido.
13. Chat e ferramentas passaram a validar se existem PDFs e texto antes de executar.

Como testar:

1. Rodar a aplicacao.
2. Carregar um PDF pela sidebar.
3. Abrir `Diagnostico das fontes`.
4. Verificar paginas, paginas com texto, trechos e preview.
5. Testar tambem um PDF escaneado para confirmar o aviso de texto nao extraivel.

## Fase 2 - Busca simples

Status: implementada.

Objetivo: encontrar trechos relevantes nos PDFs sem ainda usar embeddings ou banco vetorial.

O que foi feito:

1. Criado `RetrievedChunk` para guardar trecho, score e termos encontrados.
2. Melhorado `retrieval.py` com normalizacao de texto.
3. Adicionada remocao basica de acentos.
4. Adicionada remocao de palavras comuns.
5. Adicionada expansao simples de termos academicos em portugues para ingles.
6. Criado calculo de score por frequencia de termos inteiros.
7. Adicionado bonus por cobertura da consulta.
8. Ordenacao dos resultados por relevancia.
9. Criado painel `Teste de busca`.
10. O painel mostra score, termos encontrados, arquivo, pagina e preview.
11. Chat e ferramentas passaram a usar `retrieval_k` da configuracao futura.

Decisao tecnica:

- A expansao portugues-ingles foi mantida porque melhora o uso do app antes da busca semantica.
- Ela nao substitui embeddings.
- Ela nao deve atrapalhar uma LLM futura, pois atua somente na etapa de recuperacao.
- Quando houver RAG vetorial, a recuperacao semantica deve ser a principal.
- A busca lexical pode continuar como fallback para casos em que palavras exatas importam.

Como testar:

1. Carregar um PDF com texto extraivel.
2. Abrir `Teste de busca`.
3. Digitar termos como `metodologia`, `resultados`, `amostra` ou um conceito do artigo.
4. Clicar em `Buscar trechos`.
5. Verificar se os trechos retornados pertencem as paginas corretas.
6. Testar consultas em portugues contra artigos em ingles, por exemplo `metodologia`, `resultados` e `participantes`.

## Fase 3 - Chat com contexto

Status: implementada com resposta simulada.

Objetivo: fazer o chat usar os trechos recuperados para montar uma resposta mais proxima de uma resposta real.

O que foi feito:

1. Criado `context_builder.py`.
2. Criada funcao para formatar citacoes por arquivo e pagina.
3. Criada montagem de bloco de contexto com score, termos encontrados e trecho.
4. Criada montagem de prompt final com pergunta, prompt base e contexto.
5. `llm_service.py` passou a receber resultados ranqueados da busca.
6. A resposta simulada passou a mostrar sintese preliminar, evidencia principal e fontes usadas.
7. O chat passou a preservar metadados da busca, como score e termos encontrados.

Como testar:

1. Carregar um PDF com texto extraivel.
2. Fazer uma pergunta no chat usando termos presentes no artigo.
3. Verificar se a resposta mostra a evidencia principal.
4. Verificar se a resposta mostra `Fontes usadas`.
5. Verificar se o prompt de contexto aparece no final da resposta simulada.

## Fase 4 - Ferramentas com contexto

Status: implementada com saidas simuladas.

Objetivo: fazer resumo, mapa mental e tabela usarem o mesmo contexto recuperado pelo RAG.

O que foi feito:

1. `study_tools.py` passou a usar `retrieve_ranked_chunks`.
2. As ferramentas passaram a receber `RetrievedChunk`, preservando score, termos encontrados, arquivo e pagina.
3. `tool_service.py` passou a montar prompts especificos para resumo, mapa mental e tabela.
4. O resumo simulado passou a exibir evidencias recuperadas e fontes usadas.
5. O mapa mental simulado passou a organizar ramos a partir dos termos e trechos recuperados.
6. A tabela passou a incluir documento, pagina, campo, score, termos e trecho.
7. Cada ferramenta passou a exibir o prompt preparado para uma LLM futura.

Detalhamento tecnico:

As ferramentas deixaram de receber somente `DocumentChunk` e passaram a receber `RetrievedChunk`. Isso e importante porque `RetrievedChunk` preserva informacoes da recuperacao:

- `chunk`: trecho original extraido do PDF;
- `score`: pontuacao da busca;
- `matched_terms`: termos encontrados;
- `source_name`: arquivo de origem;
- `page_number`: pagina de origem.

Com isso, as ferramentas nao trabalham mais apenas com texto bruto. Elas tambem sabem por que aquele trecho foi selecionado e de onde ele veio.

Fluxo atual das ferramentas:

```text
topico informado pelo usuario
  -> load_pdf_corpus()
  -> retrieve_ranked_chunks()
  -> tool_service.py
  -> saida simulada estruturada
  -> prompt preparado para LLM futura
```

Resumo:

- recebe os trechos ranqueados;
- seleciona evidencias principais;
- exibe uma sintese simulada;
- mostra as fontes usadas;
- prepara um prompt para a LLM gerar um resumo academico real.

Mapa mental:

- recebe os trechos ranqueados;
- usa os termos encontrados como ramos iniciais;
- adiciona evidencias de cada trecho;
- mostra fonte e pagina;
- prepara um prompt para a LLM organizar o mapa de forma mais inteligente.

Tabela de dados:

- recebe os trechos ranqueados;
- monta linhas com documento, pagina, campo, score, termos e trecho;
- prepara um prompt para a LLM extrair campos estruturados futuramente.

Decisao tecnica:

- As ferramentas continuam simuladas para manter controle da arquitetura antes da LLM.
- A camada de recuperacao ja esta integrada.
- A troca futura sera concentrada em `tool_service.py` e no servico de modelo.
- O usuario ja consegue validar se as ferramentas usam trechos reais dos PDFs.

Como testar:

1. Carregar um PDF com texto extraivel.
2. Abrir uma das ferramentas: `Resumo`, `Mapa mental` ou `Tabela de dados`.
3. Informar um topico presente no artigo.
4. Verificar se a saida usa trechos reais dos PDFs.
5. Verificar se aparecem fontes, paginas, scores ou termos encontrados.
6. Abrir `Prompt preparado para a LLM` para conferir o contexto enviado futuramente ao modelo.

## Fase 5 - Modelo real

Status: minimo funcional implementado com Gemini.

Objetivo: conectar um provedor de LLM.

Provedores planejados:

- Gemini como provedor real inicial via API;
- OpenAI como proximo provedor via API, ainda nao implementado;
- Ollama adiado para esta maquina por limitacao de RAM.

O design atual ja deixa a selecao visual na sidebar com `Placeholder`, `Ollama`, `OpenAI` e `Gemini`. O primeiro provedor real conectado e o Gemini.

Preparacao ja feita:

- o chat ja monta o prompt final com o contexto recuperado;
- as ferramentas ja montam prompts especificos com o mesmo contexto recuperado;
- o `Final system prompt preview` da sidebar ja e aplicado ao chat e aos prompts das ferramentas;
- `llm_service.py` concentra a resposta simulada, as configuracoes de modelo e a chamada real ao Gemini;
- `tool_service.py` concentra os prompts das ferramentas e reutiliza o mesmo servico de modelo.

Adaptador Gemini inicial:

- modelo padrao: `gemini-3.1-flash-lite`;
- provedor padrao do app: `Placeholder`, para evitar chamadas de API por acidente;
- chave esperada: `GEMINI_API_KEY`;
- chamada feita via REST para a API `generateContent`;
- usa `temperature` e `max tokens` da sidebar;
- mostra erro amigavel quando a chave esta ausente, o modelo nao existe, a conexao falha ou o limite gratuito e atingido;
- mantem `Placeholder` como modo simulado para testar a aplicacao sem API.

Refinamento de respostas:

- o chat pede resposta direta seguida de evidencias;
- cada afirmacao baseada nos documentos deve citar arquivo e pagina;
- quando o contexto nao tiver a informacao, a resposta deve dizer que ela nao foi encontrada nos PDFs carregados;
- resumo, mapa mental e tabela usam prompts especificos, mas seguem a mesma regra de citacao e contexto obrigatorio.

O que esta fase deve entregar:

- substituir respostas simuladas por respostas geradas por modelo;
- manter o uso dos trechos recuperados como contexto obrigatorio;
- aplicar o `Final system prompt preview` na montagem da chamada;
- respeitar configuracoes da sidebar, como provedor, modelo, temperatura e max tokens;
- usar o mesmo servico de modelo para chat e ferramentas;
- exibir erros amigaveis quando chave de API, modelo local ou conexao nao estiverem disponiveis.

Arquitetura proposta para a Fase 5:

```text
chat.py / study_tools.py
  -> retrieval.py
  -> context_builder.py
  -> llm_service.py
  -> provider selecionado
       -> Ollama
       -> OpenAI
       -> Gemini
  -> resposta final
```

Como sera feita:

1. Criar uma interface comum em `llm_service.py`, por exemplo `generate_response(prompt, settings)`. Implementado.
2. Criar adaptadores internos para cada provedor:
   - `call_gemini`: implementado;
   - `call_openai`: planejado;
   - `call_ollama`: adiado por limitacao de RAM nesta maquina.
3. Ler da sidebar:
   - provedor;
   - nome do modelo;
   - temperatura;
   - max tokens.
4. Montar o prompt usando `context_builder.py`.
5. Enviar o prompt para o provedor escolhido.
6. Retornar resposta para chat ou ferramentas.
7. Tratar erros de forma clara:
   - modelo nao encontrado;
   - API key ausente;
   - Ollama desligado;
   - timeout;
   - limite de tokens.

Estrategia recomendada:

- Usar Gemini como provedor inicial, porque funciona nesta maquina com pouca RAM.
- Manter `Placeholder` como modo sem custo para testes de interface e recuperacao.
- Adicionar OpenAI futuramente se for necessario comparar qualidade ou custo.
- Adiar Ollama local enquanto a maquina tiver cerca de 4 GB de RAM.
- Nao colocar chaves de API no codigo.
- Manter a resposta sempre baseada nos trechos recuperados, nao em conhecimento solto do modelo.

Exemplo de variaveis futuras:

```text
OPENAI_API_KEY
GEMINI_API_KEY
OLLAMA_BASE_URL
```

Resultado esperado da Fase 5:

O usuario podera carregar PDFs, perguntar no chat ou usar uma ferramenta, e receber uma resposta real de LLM baseada no contexto recuperado dos documentos.

## Fase 6 - RAG vetorial

Status: planejada.

Objetivo: substituir ou complementar a busca lexical por recuperacao semantica.

Passos sugeridos:

1. Dividir textos em chunks menores e controlados.
2. Gerar embeddings.
3. Salvar vetores em uma base local ou em memoria.
4. Buscar por similaridade semantica.
5. Comparar resultado vetorial com a busca simples atual.

O que esta fase deve entregar:

- dividir paginas longas em chunks menores;
- gerar embeddings dos chunks;
- armazenar embeddings em um indice vetorial;
- buscar trechos por similaridade semantica;
- melhorar perguntas em portugues sobre artigos em ingles;
- combinar busca semantica com busca lexical quando for util.

Por que essa fase e importante:

A busca atual ainda depende de palavras ou equivalentes simples. Ela funciona para termos diretos, mas pode falhar quando o usuario pergunta com palavras diferentes das usadas no artigo.

Exemplo:

```text
Usuario: Quais foram os participantes do estudo?
Artigo: The study enrolled 120 undergraduate students...
```

Uma busca lexical pode nao encontrar bem essa relacao se os termos nao estiverem no dicionario. Uma busca semantica multilingue tende a encontrar porque compara significado, nao apenas palavras.

Como sera feita:

1. Reaproveitar ou ajustar o servico `chunking.py`.
2. Gerar embeddings dos chunks.
3. Criar um servico de embeddings, por exemplo `embedding_service.py`.
4. Escolher um modelo de embeddings:
   - local, se a prioridade for estudo/offline;
   - via API, se a prioridade for qualidade e simplicidade.
5. Criar um indice vetorial local:
   - em memoria para prototipo;
   - FAISS, Chroma ou alternativa similar em fase mais madura.
6. Implementar `semantic_retrieve`.
7. Combinar resultados:
   - busca semantica principal;
   - busca lexical como fallback;
   - remocao de duplicados;
   - ordenacao final.

Arquitetura proposta para a Fase 6:

```text
PDFs
  -> extracao de texto
  -> chunking
  -> embeddings
  -> indice vetorial
  -> busca semantica
  -> combinacao com busca lexical
  -> contexto para LLM
```

Estrategia recomendada:

```text
consulta do usuario
  -> busca semantica multilingue como principal
  -> busca lexical como fallback/complemento
  -> remover duplicados
  -> ordenar melhores trechos
  -> enviar contexto para a LLM
```

Motivo:

- busca semantica entende melhor significado entre idiomas;
- busca lexical ainda e forte para termos tecnicos, siglas, nomes de autores, datasets e palavras exatas;
- combinar as duas tende a recuperar contexto mais confiavel do que usar apenas uma.

Resultado esperado da Fase 6:

O usuario podera fazer perguntas naturais em portugues mesmo quando o artigo estiver em ingles, e o sistema devera recuperar trechos relevantes por significado, nao apenas por palavras iguais.

## Como executar

Dentro da raiz do repositorio:

```powershell
streamlit run euclides_v2/app.py
```

Se estiver usando a `.venv` da pasta `euclides_v2`, o comando pode ser executado com o Streamlit instalado nesse ambiente.

## Dependencias

Arquivo:

```text
euclides_v2/requirements.txt
```

Dependencias atuais:

```text
streamlit>=1.36.0
pypdf>=5.0.0
```

Nenhuma dependencia nova foi adicionada para o Gemini inicial. A chamada usa bibliotecas padrao do Python via REST.

Variavel de ambiente necessaria para usar Gemini:

```text
GEMINI_API_KEY
```

Em PowerShell:

```powershell
$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
```

Dependencias futuras podem entrar junto com outros adaptadores da Fase 5, por exemplo:

- Ollama: cliente HTTP, como `requests` ou `httpx`;
- OpenAI: SDK oficial `openai` ou cliente HTTP;
- Gemini avancado: SDK do Google, se for necessario usar recursos alem da chamada REST atual.

## Fluxo atual da aplicacao

1. Usuario carrega PDFs na sidebar.
2. O app guarda os arquivos em `st.session_state.sources`.
3. O diagnostico chama `load_pdf_corpus`.
4. `pdf_loader.py` extrai texto, divide em chunks, cacheia o corpus e gera diagnosticos.
5. O teste de busca chama `retrieve_ranked_chunks`.
6. Chat usa os resultados ranqueados para montar contexto e resposta simulada.
7. Ferramentas usam os resultados ranqueados para montar resumo, mapa mental, tabela e prompts simulados.
8. A resposta final usa Gemini quando o provedor esta selecionado e `GEMINI_API_KEY` existe; caso contrario, o modo `Placeholder` continua simulado.

## Limitacoes atuais

- A LLM real inicial e Gemini; Ollama e OpenAI ainda nao foram conectados.
- Ainda nao ha embeddings.
- Ainda nao ha banco vetorial.
- PDFs escaneados sem OCR nao terao texto extraivel.
- A busca simples ainda e lexical, mas ja possui uma expansao limitada de termos academicos portugues-ingles.
- A expansao portugues-ingles cobre apenas termos comuns; nao e uma traducao completa da pergunta.
- O chunking atual ainda e baseado em tamanho de texto; futuramente pode ser refinado por secoes, titulos e estrutura do artigo.

## Comandos de Git sugeridos

Para salvar as mudancas:

```powershell
git add euclides_v2
git commit -m "Prepare Euclides v2 for real LLM integration"
git push origin main
```
