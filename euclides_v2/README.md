# Euclides v2

Esta pasta contem uma evolucao separada do Euclides original. A proposta e continuar o desenvolvimento em fases, sem modificar o `app.py` da raiz do repositorio.

O Euclides original funciona como prototipo visual. A `euclides_v2` comeca a transformar esse prototipo em uma aplicacao funcional para estudo com PDFs, busca de trechos, chat com contexto e ferramentas academicas.

## Regra de colaboracao

Antes de qualquer modificacao em arquivos do projeto, o agente deve:

1. Informar quais arquivos pretende modificar.
2. Explicar o motivo da mudanca.
3. Aguardar confirmacao explicita do usuario.
4. Aplicar somente as mudancas aprovadas.

Esta regra vale para codigo, README, configuracoes e comandos que alterem arquivos.

## Estado atual

Fases implementadas ate agora:

- Fase 1: leitura real de PDFs e diagnostico das fontes.
- Fase 2: busca lexical simples com expansao academica portugues-ingles.
- Fase 3: chat com contexto recuperado.
- Fase 4: ferramentas de estudo com contexto.
- Fase 5: modelo real minimo via Gemini.
- Fase 6: RAG vetorial inicial com embeddings Gemini, indice em memoria e busca hibrida.
- Fase 7: ferramentas academicas extras e controle real de `Active tools`.
- Fase 8C: OpenAI como segundo provedor real via API.

O modo padrao continua `Placeholder` e `Lexical`, para evitar custo de API por acidente. Para usar Gemini real ou embeddings, e necessario configurar `GEMINI_API_KEY`.

Escopo final definido:

- Gemini continua como provedor real ja implementado.
- OpenAI esta implementado como segundo provedor real via API.
- Ollama e modelos locais nao serao implementados por questoes tecnicas e porque o projeto nao precisa rodar modelo local.
- O projeto sera considerado concluido depois da Fase 8A, exportacao de materiais de estudo em TXT.

## Objetivo da v2

Construir uma arquitetura simples e expansivel para:

- carregar ate 3 PDFs;
- extrair texto real dos arquivos;
- diagnosticar se o PDF foi lido corretamente;
- buscar trechos relevantes dentro dos textos;
- responder no chat usando contexto recuperado;
- gerar ferramentas de resumo, mapa mental, tabela, citas, flashcards e quiz;
- manter provedores por API com Gemini e OpenAI.

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
 Chat  Resumo  Mapa mental  Tabela  Citas  Flashcards  Quiz
   |     |        |            |
   +-----+--------+------------+
         |
   +--------+--------+
   |        |        |
 Gemini   OpenAI  Placeholder
   |        |        |
   +--------+--------+
         |
  Resposta final
```

O app ja possui modo simulado (`Placeholder`) e chamadas reais ao Gemini e a OpenAI. O foco final e exportar materiais de estudo em TXT para tornar o projeto pratico e concluido.

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
    embedding_service.py
    export_service.py
    llm_service.py
    pdf_loader.py
    retrieval.py
    tool_service.py
    vector_retrieval.py
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
- renderiza ferramentas de estudo;
- permite exportar chat e ferramentas em TXT;
- respeita a selecao de `Active tools` para exibir ou ocultar o chat.

### `components/sidebar.py`

Controla a barra lateral.

Inclui:

- upload de PDFs;
- limite de 3 fontes;
- lista de arquivos carregados;
- remocao de arquivos;
- configuracao de modelos;
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
- usa a recuperacao configurada na sidebar para recuperar trechos;
- envia os trechos para `llm_service.py`;
- responde com `Placeholder`, Gemini ou OpenAI;
- permite exportar a conversa em TXT.

### `components/study_tools.py`

Interface das ferramentas de estudo.

Inclui:

- resumo;
- mapa mental;
- tabela de dados.
- citas;
- flashcards;
- quiz.

As ferramentas usam a mesma busca ranqueada do chat e podem retornar saidas simuladas ou respostas reais via provedor de modelo selecionado.

Cada ferramenta tambem mostra o prompt enviado ou preparado para a LLM e permite exportar o resultado em TXT.

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

Servico de busca lexical.

Implementa a recuperacao local baseada em palavras, usada diretamente no modo `Lexical` e como fallback/complemento dos modos `Vetorial` e `Hibrida`.

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

Essa expansao acontece antes da etapa de LLM. Ela serve apenas para recuperar trechos melhores. A LLM recebe os trechos encontrados como contexto; ela nao precisa saber que a busca expandiu os termos.

Na versao com RAG vetorial, a busca semantica deve ser a estrategia principal. A busca lexical com expansao pode continuar como complemento ou fallback para nomes, siglas, termos tecnicos e palavras exatas.

### `services/llm_service.py`

Servico central para respostas com modelo.

Atualmente mantem o modo `Placeholder` simulado e ja chama Gemini ou OpenAI via API quando um desses provedores esta selecionado. Ollama nao faz parte do escopo final.

Esse isolamento e intencional: provedores reais devem ser conectados principalmente neste arquivo, sem espalhar chamadas de API pelos componentes.

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

### `services/export_service.py`

Servico de exportacao TXT.

Ele:

- monta TXT para conversa do chat;
- monta TXT para resultados das ferramentas;
- inclui data, topico, conteudo e fontes usadas;
- gera nomes de arquivo seguros;
- nao adiciona dependencias externas.

## Decisoes de engenharia de LLM

Esta secao resume as decisoes tecnicas relacionadas ao uso de IA generativa no Euclides v2.

### Framework escolhido

O projeto usa chamadas REST diretas para Gemini e OpenAI, usando bibliotecas padrao do Python.

Decisao:

- nao usar SDKs oficiais neste fechamento;
- nao usar LangChain ou LangGraph;
- nao usar framework de agentes.

Motivos:

- o fluxo do app e simples e controlado: upload de PDFs, recuperacao de trechos, montagem de prompt e chamada ao modelo;
- chamadas REST reduzem dependencias externas;
- o codigo fica mais facil de auditar para fins academicos;
- o isolamento em `llm_service.py` permite trocar ou adicionar provedores sem espalhar logica de API pela interface.

Trade-off:

- SDKs poderiam simplificar alguns recursos avancados;
- LangChain ou LangGraph poderiam ajudar em fluxos agenticos maiores;
- para este projeto, a complexidade adicional nao se justifica.

### Provedores e modelos

Provedores disponiveis:

- `Placeholder`: modo simulado, sem custo e sem chamada externa;
- `Gemini`: provedor real via API;
- `OpenAI`: segundo provedor real via API.

Modelos padrao:

- Gemini: `gemini-3.1-flash-lite`;
- OpenAI: `gpt-5`;
- Embeddings: `gemini-embedding-001`.

Decisoes:

- `Placeholder` fica como padrao para evitar custo acidental;
- Gemini foi usado primeiro por ser adequado para chamadas REST simples e embeddings;
- OpenAI foi adicionado como segundo provedor para cumprir o requisito de IA generativa com alternativa de modelo;
- Ollama e modelos locais ficaram fora do escopo por limitacoes tecnicas da maquina e porque o projeto nao precisa rodar LLM local.

### Modelos pagos vs. modelos locais

Escolha atual:

- o projeto usa provedores pagos/externos por API: Gemini e OpenAI;
- o projeto tambem mantem `Placeholder` para testar fluxo, RAG, prompts e exportacao sem custo;
- nenhum modelo local foi integrado.

Por que escolher Gemini e OpenAI:

- qualidade de resposta maior para tarefas academicas;
- melhor capacidade de seguir instrucoes de citacao e contexto;
- menor exigencia de hardware local;
- configuracao simples por variaveis de ambiente;
- disponibilidade de embeddings via Gemini para RAG vetorial;
- menor risco de travamento em uma maquina com pouca RAM;
- comparacao entre dois provedores reais sem mudar a arquitetura do app.

Limitacoes dos provedores pagos/externos:

- exigem internet;
- podem gerar custo por uso;
- podem sofrer rate limit ou limite gratuito;
- dependem da disponibilidade do provedor;
- PDFs e trechos recuperados sao enviados para uma API externa;
- mudancas futuras de modelo, preco ou endpoint podem exigir ajustes;
- tool calling nativo nao foi usado, entao as ferramentas sao controladas pela aplicacao.

Seria viavel rodar com modelo local?

- Tecnicamente sim, desde que a maquina tenha RAM, CPU/GPU e armazenamento suficientes;
- no ambiente atual, Ollama/modelo local ficou fora do escopo por limitacao tecnica e por nao ser necessario para o objetivo do projeto;
- a arquitetura permitiria adicionar um adaptador local em `llm_service.py` no futuro, mantendo o mesmo contrato `generate_response(prompt, settings)`.

O que se ganharia com modelo local:

- maior privacidade, pois os trechos dos PDFs nao sairiam da maquina;
- funcionamento offline depois de baixar o modelo;
- custo variavel menor por chamada;
- mais controle sobre o ambiente de execucao.

O que se perderia com modelo local nesta aplicacao:

- qualidade potencialmente menor em respostas academicas, dependendo do modelo;
- maior latencia em maquina sem GPU;
- menor janela de contexto em modelos pequenos;
- maior consumo de RAM e disco;
- configuracao mais complexa para o usuario;
- embeddings e tool calling poderiam exigir componentes adicionais;
- manutencao local de modelos, quantizacao e servidor.

Trade-off final:

- Gemini e OpenAI foram escolhidos para priorizar qualidade, simplicidade de uso e menor dependencia de hardware;
- o custo e a privacidade sao mitigados com `Placeholder`, modo `Lexical` sem API e limite de ate 3 PDFs;
- modelo local seria uma boa evolucao para privacidade/offline, mas nao para o escopo final deste projeto.

### System prompt

O system prompt base fica em `components/sidebar.py` como `DEFAULT_SYSTEM_PROMPT`.

Ele foi projetado para controlar comportamento, escopo e rastreabilidade da resposta.

Estrutura logica do prompt:

```text
Papel
  -> Euclides, assistente de estudo academico
Restricao principal
  -> usar apenas PDFs carregados pelo usuario
Comportamento esperado
  -> explicar com clareza
  -> citar documento quando possivel
  -> avisar quando algo nao estiver nas fontes
Configuracoes dinamicas
  -> modo de ensino
  -> fontes carregadas
  -> estilo de citacao
  -> estrategia de resposta
```

Elementos definidos:

- identidade do assistente: Euclides, assistente de estudo academico;
- regra principal: usar apenas PDFs carregados pelo usuario;
- obrigacao de clareza;
- orientacao para citar documentos quando possivel;
- aviso quando a informacao nao estiver nas fontes;
- formato esperado de resposta no prompt de tarefa:
  - resposta direta;
  - evidencias com citacoes;
  - indicacao clara quando a informacao nao aparece nos PDFs;
- placeholders configuraveis:
  - `[[TEACHING_MODE]]`;
  - `[[SOURCES]]`;
  - `[[CITATION_STYLE]]`;
  - `[[ANSWER_STRATEGY]]`.

Decisao:

- manter o prompt visivel e editavel na sidebar;
- mostrar o preview final do prompt para auditoria;
- separar prompt base, contexto recuperado e instrucao da tarefa.

Motivo:

- facilita demonstrar como o comportamento da LLM e controlado;
- permite testar modos de ensino sem alterar codigo;
- reduz risco de respostas fora do contexto.

Iteracao e refinamento:

1. Prompt inicial: persona academica e regra de usar PDFs.
2. Problema identificado: respostas poderiam ficar genericas ou nao indicar limites do contexto.
3. Refinamento: adicao de regra para avisar quando a informacao nao estiver nas fontes.
4. Refinamento: inclusao de placeholders para modo de ensino, fontes, citacao e estrategia.
5. Refinamento: `context_builder.py` passou a montar um prompt de tarefa com pergunta, contexto recuperado e formato esperado.
6. Refinamento: `tool_service.py` passou a criar prompts especificos para resumo, mapa mental, tabela, citas, flashcards e quiz.

Exemplo de prompt final montado pelo app:

```text
Voce e o Euclides, um assistente de estudo academico.
Use apenas as fontes em PDF carregadas pelo usuario.
Explique com clareza, cite o documento quando possivel e avise quando algo nao estiver nas fontes.
Modo de ensino: Explicacao direta
Fontes carregadas: artigo.pdf
Estilo de citacao: Arquivo + pagina
Estrategia de resposta: Responder somente com as fontes

Instrucao da tarefa:
Responda usando apenas o contexto recuperado abaixo. Comece com uma resposta direta.
Em seguida, apresente evidencias com citacoes. Use citacoes no formato (arquivo, p. numero).
Se o contexto nao trouxer a resposta, escreva claramente:
'Nao encontrei essa informacao nos PDFs carregados.'

Pergunta do usuario:
Quais foram os participantes do estudo?

Contexto recuperado:
[Fonte 1] artigo.pdf, p. 3
Score: 0.84
Termos encontrados: participants, study
Trecho: The study enrolled 120 undergraduate students...

Resposta:
```

### Parametros do modelo

Parametros configuraveis na sidebar:

- provedor;
- modelo;
- temperatura;
- max tokens;
- quantidade de trechos recuperados por pergunta.

Valores iniciais:

- provedor: `Placeholder`;
- temperatura: `0.2`;
- max tokens: `1200`;
- trechos recuperados: `5`;
- modo de busca: `Lexical`.

Decisao:

- temperatura baixa para priorizar respostas mais estaveis e menos criativas;
- max tokens controlavel para reduzir custo e evitar respostas longas demais;
- modelo editavel para permitir testes sem mudar codigo;
- `Lexical` como busca padrao para funcionar sem custo de embeddings.

Tabela de decisao:

| Parametro | Valor final/padrao | Valores considerados | Justificativa |
| --- | --- | --- | --- |
| Provedor | `Placeholder` | `Placeholder`, `Gemini`, `OpenAI` | evita custo acidental e permite testar interface/RAG sem API |
| Modelo Gemini | `gemini-3.1-flash-lite` | modelos Gemini mais leves e modelos maiores | prioriza latencia, custo e integracao REST simples |
| Modelo OpenAI | `gpt-5` | modelo padrao OpenAI configuravel pelo usuario | oferece segundo provedor de maior capacidade sem mudar arquitetura |
| Temperatura | `0.2` | `0.0`, `0.2`, `0.7` | `0.0` ficou rigido demais; `0.7` aumenta variacao; `0.2` equilibra estabilidade e linguagem natural |
| Max tokens | `1200` | `800`, `1200`, `2000` | `800` pode cortar respostas; `2000` aumenta custo; `1200` basta para respostas academicas curtas |
| `retrieval_k` | `5` | `3`, `5`, `8` | `3` pode perder contexto; `8` aumenta prompt/custo; `5` equilibra cobertura e concisao |
| Modo de busca | `Lexical` | `Lexical`, `Vetorial`, `Hibrida` | `Lexical` funciona sem API; `Vetorial` e `Hibrida` ficam disponiveis quando ha chave Gemini |
| Embeddings | `gemini-embedding-001` | embeddings por API vs. semantica local | evita exigir modelo local e melhora consultas multilingues |
| `top-p` | padrao do provedor | expor na UI vs. manter implicito | nao foi exposto para reduzir complexidade e evitar ajuste redundante com temperatura |

Evidencia de experimentacao e refinamento:

- `Placeholder` foi mantido como padrao apos testes de fluxo para evitar chamadas pagas durante desenvolvimento;
- `Lexical` foi mantido como padrao porque funcionou bem para termos exatos, nomes, siglas e validacao sem chave de API;
- `Hibrida` foi adicionada depois da busca lexical para combinar significado semantico com termos exatos;
- `retrieval_k=5` foi escolhido como equilibrio entre contexto suficiente e prompt curto;
- temperatura baixa foi adotada porque o caso de uso exige respostas rastreaveis, nao criatividade;
- max tokens foi mantido em `1200` para limitar custo e ainda permitir resposta com evidencias;
- OpenAI e Gemini usam a mesma interface `LlmSettings`, permitindo comparar provedores sem alterar componentes.

Parametros deliberadamente nao expostos:

- `top-p` nao foi exposto na interface para manter a configuracao simples;
- penalidades de frequencia/presenca nao foram expostas porque o app nao gera texto criativo longo;
- seed nao foi exposta porque a prioridade e rastreabilidade por fonte, nao reproducibilidade exata de cada token;
- caso seja necessario, esses campos podem ser adicionados ao mesmo objeto `LlmSettings`.

### Estrategia de prompting

O projeto usa prompting instrucional com RAG e prompts especificos por tarefa.

Padrao usado:

```text
system prompt configuravel
  -> instrucao da tarefa
  -> pergunta/topico do usuario
  -> contexto recuperado dos PDFs
  -> regras de citacao
  -> formato esperado da resposta
```

Decisoes:

- nao usar few-shot prompting nesta versao;
- nao solicitar chain-of-thought;
- nao usar XML tags formais;
- usar delimitadores textuais simples como `Instrucao da tarefa`, `Pergunta do usuario`, `Contexto recuperado` e `Resposta`;
- exigir resposta direta seguida de evidencias;
- exigir citacoes no formato `(arquivo, p. numero)`;
- instruir a LLM a dizer quando a informacao nao foi encontrada nos PDFs.

Motivo:

- o objetivo e estudo academico com rastreabilidade;
- a resposta deve ser verificavel nas fontes;
- chain-of-thought nao e necessario para o usuario final e poderia expor raciocinio intermediario desnecessario;
- few-shot aumentaria o prompt e o custo sem necessidade clara neste escopo.

Tecnicas usadas:

- RAG com contexto explicitamente delimitado;
- instrucao negativa contra invencao de autores, numeros, resultados e conclusoes;
- formato de resposta definido por tarefa;
- prompts especializados para ferramentas;
- citacao obrigatoria por fonte e pagina;
- fallback textual quando a informacao nao aparece no contexto;
- temperatura baixa para reduzir variacao.

Few-shot:

- nao foi usado porque as tarefas dependem fortemente do conteudo recuperado dos PDFs;
- exemplos fixos poderiam enviesar respostas para formatos ou dominios que nao aparecem no documento do usuario;
- a decisao foi priorizar instrucao clara + contexto recuperado.

Chain-of-thought:

- nao foi solicitado;
- o app pede resposta direta e evidencias, nao raciocinio interno passo a passo;
- isso reduz verbosidade e evita expor raciocinio intermediario desnecessario.

XML tags:

- nao foram usadas tags XML formais;
- o projeto usa secoes textuais claras porque sao suficientes para Gemini e OpenAI neste fluxo;
- se o projeto exigisse parsing automatico rigido, XML ou JSON estruturado seriam considerados.

Formato de saida por tipo de tarefa:

- Chat: resposta direta, evidencias citadas e limites do contexto;
- Resumo: ideia central, pontos principais, evidencias e limites;
- Mapa mental: conceito central, ramos, evidencias e fontes;
- Tabela: campos extraidos com documento, pagina e observacao;
- Citas: citacao, documento, pagina e relevancia;
- Flashcards: frente e verso com fonte;
- Quiz: pergunta, resposta correta e justificativa citada.

### RAG

O projeto usa RAG para responder com base nos PDFs carregados.

Etapas:

1. Upload de ate 3 PDFs.
2. Extracao de texto com `pypdf`.
3. Divisao em chunks.
4. Recuperacao de trechos.
5. Montagem de contexto.
6. Chamada ao provedor selecionado.
7. Resposta com citacoes.

Modos de recuperacao:

- `Lexical`: busca local por termos, sem API;
- `Vetorial`: embeddings Gemini e similaridade por cosseno;
- `Hibrida`: combina busca lexical e semantica.

Decisoes:

- manter busca lexical como padrao e fallback;
- usar embeddings Gemini somente quando o usuario escolhe `Vetorial` ou `Hibrida`;
- usar indice vetorial em memoria/cache do Streamlit;
- nao usar FAISS, Chroma ou pgvector neste fechamento.

Motivo:

- o app precisa funcionar sem custo e sem chave de embeddings;
- busca lexical e forte para nomes, siglas, termos tecnicos e palavras exatas;
- busca vetorial melhora perguntas em portugues sobre textos em ingles;
- indice em memoria e suficiente para ate 3 PDFs e reduz complexidade operacional.

### Ferramentas disponibilizadas

Ferramentas da aplicacao:

| Ferramenta | Entrada principal | Saida | Usa RAG | Usa LLM real | Justificativa |
| --- | --- | --- | --- | --- | --- |
| Chat | pergunta do usuario | resposta direta com evidencias | sim | opcional | permitir perguntas livres sobre os PDFs |
| Resumo | topico | resumo academico curto | sim | opcional | condensar conteudo para estudo |
| Mapa mental | tema | estrutura hierarquica | sim | opcional | organizar conceitos e relacoes |
| Tabela de dados | campos/dados desejados | linhas tabulares | sim | opcional | transformar trechos em dados comparaveis |
| Citas | tema | citacoes relevantes com fonte | sim | opcional | apoiar escrita academica e revisao |
| Flashcards | tema | frente e verso | sim | opcional | apoiar memorizacao ativa |
| Quiz | tema | perguntas e gabarito | sim | opcional | apoiar autoavaliacao |
| Exportacao TXT | conteudo gerado | arquivo `.txt` | nao | nao | salvar materiais de estudo fora do app |

Decisao importante:

- essas ferramentas sao ferramentas da aplicacao, nao tools/function calling nativas da LLM.

Motivo:

- o controle do fluxo fica no codigo Python;
- a LLM recebe prompts especificos e contexto recuperado;
- evita depender de formatos proprietarios de function calling;
- facilita manter o mesmo comportamento em Gemini, OpenAI e Placeholder.

Contrato geral das ferramentas:

```text
entrada do usuario
  -> validacao de PDFs e texto extraivel
  -> recuperacao de trechos com retrieve_chunks_with_status
  -> montagem de prompt especifico
  -> Placeholder ou provedor real
  -> exibicao na interface
  -> exportacao TXT quando aplicavel
```

Parametros usados pelas ferramentas:

| Parametro | Tipo | Origem | Uso |
| --- | --- | --- | --- |
| `topic` / pergunta | `str` | campo de texto ou chat | direciona recuperacao e prompt |
| `retrieval_mode` | `str` | sidebar | escolhe `Lexical`, `Vetorial` ou `Hibrida` |
| `retrieval_k` | `int` | sidebar | controla quantos trechos entram no contexto |
| `model_provider` | `str` | sidebar | escolhe `Placeholder`, `Gemini` ou `OpenAI` |
| `model_name` | `str` | sidebar | define modelo do provedor |
| `temperature` | `float` | sidebar | controla variacao da resposta |
| `max_tokens` | `int` | sidebar | limita tamanho da resposta |
| `system_prompt` | `str` | sidebar/context_builder | define comportamento geral |
| `RetrievedChunk[]` | lista tipada | RAG | contem chunk, score e termos encontrados |

Contratos de saida:

| Ferramenta | Formato esperado |
| --- | --- |
| Chat | texto com resposta direta, evidencias e citacoes |
| Resumo | Markdown/texto com ideia central, pontos principais e limites |
| Mapa mental | Markdown/texto hierarquico |
| Tabela de dados | dataframe no modo Placeholder ou Markdown/texto no modo LLM |
| Citas | lista de citacoes com arquivo e pagina |
| Flashcards | dataframe no modo Placeholder ou Markdown/texto no modo LLM |
| Quiz | Markdown/texto com perguntas, respostas e justificativas |
| Exportacao TXT | texto simples com data, topico, conteudo e fontes |

Quando um provedor real esta ativo:

- a ferramenta monta um prompt especifico;
- envia o prompt para `generate_response`;
- recebe texto final do modelo.

Quando `Placeholder` esta ativo:

- a ferramenta gera saida simulada baseada nos trechos recuperados;
- isso permite testar RAG, interface e exportacao sem custo de API.

Tratamento de erros e estados vazios:

- se nao houver PDF carregado, a ferramenta pede para carregar pelo menos um PDF;
- se o PDF nao tiver texto extraivel, a ferramenta mostra aviso e recomenda verificar o diagnostico;
- se nenhum trecho relevante for encontrado, a ferramenta nao chama LLM e avisa o usuario;
- se `GEMINI_API_KEY` estiver ausente em modo vetorial/hibrido, a recuperacao volta para lexical;
- se `GEMINI_API_KEY` ou `OPENAI_API_KEY` estiver ausente no provedor real, `llm_service.py` retorna erro amigavel;
- timeouts, modelo inexistente, permissao invalida e rate limit tambem recebem mensagens amigaveis;
- exportacao TXT funciona sem API, pois usa o conteudo ja gerado.

Descricao das ferramentas para a LLM:

- `build_summary_prompt`: pede resumo academico curto com ideia central, pontos principais, evidencias e limites do contexto;
- `build_mind_map_prompt`: pede estrutura hierarquica com conceito central, ramos, evidencias e limites;
- `build_table_prompt`: pede tabela Markdown com documento, pagina, campo, valor extraido, citacao e observacao;
- `build_citations_prompt`: pede citacoes uteis, documento, pagina, motivo de relevancia e limite de uso;
- `build_flashcards_prompt`: pede flashcards com frente e verso, baseados no contexto e com citacao;
- `build_quiz_prompt`: pede quiz curto com resposta correta e justificativa citada.

Por que nao usar tools/function calling nativas:

- as ferramentas nao precisam que a LLM decida quando chamar funcoes;
- o usuario escolhe explicitamente a ferramenta na interface;
- o fluxo fica deterministico e mais facil de avaliar;
- Gemini e OpenAI podem receber o mesmo prompt, mantendo portabilidade;
- parametros e erros ficam controlados no codigo Python.

### Structured outputs, agentes e multi-agente

Structured outputs:

- nao foram usados como recurso nativo dos provedores;
- tabelas e flashcards usam estruturas Python internas quando em modo `Placeholder`;
- quando a LLM real e usada, a saida e texto/Markdown orientado por prompt.

Agentes:

- nao foram implementados;
- nao ha planejamento autonomo, chamadas iterativas de ferramentas pela LLM ou memoria agentica.

Multi-agente:

- nao foi implementado;
- o projeto usa um fluxo unico e deterministico.

Motivo:

- o requisito principal e uma aplicacao funcional com IA generativa e decisoes de LLM documentadas;
- RAG simples e ferramentas controladas atendem melhor ao escopo;
- agentes aumentariam custo, latencia e complexidade sem necessidade para estudar PDFs.

### Tratamento de erros e seguranca

Decisoes:

- chaves de API nao ficam no codigo;
- `GEMINI_API_KEY` e `OPENAI_API_KEY` sao lidas de variaveis de ambiente;
- erros de chave ausente, permissao, modelo inexistente, timeout e limite de uso retornam mensagens amigaveis;
- PDFs sem texto extraivel geram aviso;
- respostas devem usar apenas os trechos recuperados.

Limitacoes aceitas:

- PDFs escaneados sem OCR nao sao lidos;
- o indice vetorial nao e persistente;
- nao ha avaliacao automatica de qualidade das respostas;
- nao ha banco de conversas;
- a citacao depende da qualidade do texto extraido e dos chunks recuperados.

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
11. Chat e ferramentas passaram a usar `retrieval_k` da configuracao.

Decisao tecnica:

- A expansao portugues-ingles foi mantida porque melhora o uso do app antes da busca semantica.
- Ela nao substitui embeddings.
- Ela nao atrapalha a LLM, pois atua somente na etapa de recuperacao.
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
7. Cada ferramenta passou a exibir o prompt preparado para a LLM.

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
  -> prompt preparado para LLM
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
- prepara um prompt para a LLM extrair campos estruturados.

Decisao tecnica:

- As ferramentas continuam simuladas para manter controle da arquitetura antes da LLM.
- A camada de recuperacao ja esta integrada.
- A chamada real fica concentrada em `tool_service.py` e no servico de modelo.
- O usuario ja consegue validar se as ferramentas usam trechos reais dos PDFs.

Como testar:

1. Carregar um PDF com texto extraivel.
2. Abrir uma das ferramentas: `Resumo`, `Mapa mental` ou `Tabela de dados`.
3. Informar um topico presente no artigo.
4. Verificar se a saida usa trechos reais dos PDFs.
5. Verificar se aparecem fontes, paginas, scores ou termos encontrados.
6. Abrir `Prompt preparado para a LLM` para conferir o contexto enviado ao modelo.

## Fase 5 - Modelo real

Status: minimo funcional implementado com Gemini.

Objetivo: conectar um provedor de LLM.

Provedores implementados para o fechamento do projeto:

- Gemini como provedor real inicial via API;
- OpenAI como segundo provedor real via API;
- Placeholder como modo local simulado, sem custo e sem chamada externa.

Ollama e modelos locais ficam fora do escopo final por questoes tecnicas da maquina e porque o projeto nao precisa executar LLM localmente.

O design final deve manter a selecao visual na sidebar com `Placeholder`, `OpenAI` e `Gemini`.

Preparacao ja feita:

- o chat ja monta o prompt final com o contexto recuperado;
- as ferramentas ja montam prompts especificos com o mesmo contexto recuperado;
- o `Final system prompt preview` da sidebar ja e aplicado ao chat e aos prompts das ferramentas;
- `llm_service.py` concentra a resposta simulada, as configuracoes de modelo e as chamadas reais ao Gemini e a OpenAI;
- `tool_service.py` concentra os prompts das ferramentas e reutiliza o mesmo servico de modelo.

Adaptador Gemini inicial:

- modelo padrao: `gemini-3.1-flash-lite`;
- provedor padrao do app: `Placeholder`, para evitar chamadas de API por acidente;
- chave esperada: `GEMINI_API_KEY`;
- chamada feita via REST para a API `generateContent`;
- usa `temperature` e `max tokens` da sidebar;
- mostra erro amigavel quando a chave esta ausente, o modelo nao existe, a conexao falha ou o limite gratuito e atingido;
- mantem `Placeholder` como modo simulado para testar a aplicacao sem API.

Adaptador OpenAI:

- modelo padrao: `gpt-5`;
- chave esperada: `OPENAI_API_KEY`;
- chamada feita via REST para a Responses API;
- usa `temperature` e `max tokens` da sidebar;
- mostra erro amigavel quando a chave esta ausente, o modelo nao existe, a conexao falha ou o limite de uso e atingido;
- reutiliza o mesmo prompt com contexto recuperado usado por Gemini e Placeholder.

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
- exibir erros amigaveis quando chave de API, modelo de API ou conexao nao estiverem disponiveis.

Arquitetura proposta para a Fase 5:

```text
chat.py / study_tools.py
  -> retrieval.py
  -> context_builder.py
  -> llm_service.py
  -> provider selecionado
       -> Gemini
       -> OpenAI
       -> Placeholder
  -> resposta final
```

Como sera feita:

1. Criar uma interface comum em `llm_service.py`, por exemplo `generate_response(prompt, settings)`. Implementado.
2. Criar adaptadores internos para cada provedor:
   - `call_gemini`: implementado;
   - `call_openai`: implementado;
   - `Placeholder`: implementado como modo simulado.
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
   - timeout;
   - limite de tokens.

Estrategia recomendada:

- Usar Gemini como provedor inicial.
- Manter `Placeholder` como modo sem custo para testes de interface e recuperacao.
- Usar OpenAI como segundo provedor por API.
- Nao implementar Ollama nem outro modelo local neste projeto.
- Nao colocar chaves de API no codigo.
- Manter a resposta sempre baseada nos trechos recuperados, nao em conhecimento solto do modelo.

Variaveis de ambiente usadas:

```text
OPENAI_API_KEY
GEMINI_API_KEY
```

Resultado esperado da Fase 5:

O usuario podera carregar PDFs, perguntar no chat ou usar uma ferramenta, e receber uma resposta real de LLM baseada no contexto recuperado dos documentos.

## Fase 6 - RAG vetorial

Status: prototipo inicial implementado.

Objetivo: substituir ou complementar a busca lexical por recuperacao semantica.

O que foi implementado nesta primeira versao:

1. Reaproveitamento do chunking ja existente.
2. Criacao de `embedding_service.py` para gerar embeddings via Gemini.
3. Criacao de `vector_retrieval.py` para busca vetorial, indice em memoria e busca hibrida.
4. Similaridade por cosseno em memoria, sem FAISS ou Chroma.
5. Modo de busca selecionavel na sidebar:
   - `Lexical`;
   - `Vetorial`;
   - `Hibrida`.
6. Fallback automatico para busca lexical quando embeddings falham ou `GEMINI_API_KEY` nao esta configurada.
7. Aviso visual na sidebar quando o modo vetorial/hibrido esta ativo sem chave de embeddings.
8. Aviso no chat, no painel de busca e nas ferramentas quando a recuperacao vetorial/hibrida falha e volta para lexical.

Uso recomendado:

- `Lexical`: melhor escolha quando o objetivo e custo zero, velocidade e termos exatos;
- `Vetorial`: util para comparar a recuperacao semantica isolada;
- `Hibrida`: melhor escolha quando o usuario aceita usar embeddings, pois combina significado com termos exatos e reduz custo ao gerar embeddings somente dos melhores candidatos lexicais.

O que esta fase deve entregar:

- dividir paginas longas em chunks menores: implementado;
- gerar embeddings dos chunks: implementado via Gemini quando ativado;
- armazenar embeddings em um indice vetorial: implementado em memoria/cache do Streamlit para prototipo;
- buscar trechos por similaridade semantica: implementado;
- melhorar perguntas em portugues sobre artigos em ingles: em validacao;
- combinar busca semantica com busca lexical quando for util: implementado no modo `Hibrida`.

Por que essa fase e importante:

A busca atual ainda depende de palavras ou equivalentes simples. Ela funciona para termos diretos, mas pode falhar quando o usuario pergunta com palavras diferentes das usadas no artigo.

Exemplo:

```text
Usuario: Quais foram os participantes do estudo?
Artigo: The study enrolled 120 undergraduate students...
```

Uma busca lexical pode nao encontrar bem essa relacao se os termos nao estiverem no dicionario. Uma busca semantica multilingue tende a encontrar porque compara significado, nao apenas palavras.

Como sera feita:

1. Reaproveitar ou ajustar o servico `chunking.py`: implementado.
2. Gerar embeddings dos chunks: implementado com `gemini-embedding-001`.
3. Criar um servico de embeddings: implementado em `embedding_service.py`.
4. Escolher um modelo de embeddings: Gemini via API, porque a maquina tem pouca RAM.
5. Criar um indice vetorial local: prototipo em memoria/cache do Streamlit.
6. Implementar `semantic_retrieve`: implementado em `vector_retrieval.py`.
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
  -> modo selecionado na sidebar
  -> busca semantica se modo Vetorial/Hibrida e GEMINI_API_KEY existir
  -> busca lexical como fallback/complemento
  -> remover duplicados
  -> ordenar melhores trechos
  -> enviar contexto para a LLM
```

Motivo:

- busca semantica entende melhor significado entre idiomas;
- busca lexical ainda e forte para termos tecnicos, siglas, nomes de autores, datasets e palavras exatas;
- combinar as duas tende a recuperar contexto mais confiavel do que usar apenas uma;
- no modo `Hibrida`, a busca lexical primeiro limita os candidatos e a busca semantica reordena esse subconjunto, reduzindo chamadas de embeddings.

Resultado esperado da Fase 6:

O usuario podera fazer perguntas naturais em portugues mesmo quando o artigo estiver em ingles, e o sistema devera recuperar trechos relevantes por significado, nao apenas por palavras iguais.

Observacao de custo:

- o modo padrao continua `Lexical`, sem chamadas de embeddings;
- `Vetorial` e `Hibrida` podem chamar a API de embeddings do Gemini;
- `Vetorial` pode gerar embeddings para todos os chunks;
- `Hibrida` gera embeddings apenas para os melhores candidatos lexicais, o que tende a custar menos em PDFs maiores;
- os embeddings sao cacheados pelo Streamlit para reduzir chamadas repetidas no mesmo conjunto de textos.

## Fase 7 - Ferramentas academicas extras

Status: implementada em versao inicial.

Objetivo: transformar a lista `Active tools` da sidebar em controle real da interface e adicionar ferramentas de estudo adicionais usando o mesmo contexto recuperado pelo RAG.

O que foi feito:

1. `Active tools` passou a controlar se o chat fica visivel.
2. `Active tools` passou a controlar quais abas aparecem em `Ferramentas de estudo`.
3. Adicionada ferramenta `Citas`.
4. Adicionada ferramenta `Flashcards`.
5. Adicionada ferramenta `Quiz`.
6. As novas ferramentas usam `retrieve_chunks_with_status`, respeitando `Lexical`, `Vetorial` e `Hibrida`.
7. As novas ferramentas mostram fallback quando embeddings falham.
8. As novas ferramentas funcionam em modo `Placeholder` com saida simulada.
9. Quando um provedor real esta selecionado, as novas ferramentas enviam prompts especificos para a LLM.

Fluxo das ferramentas:

```text
topico do usuario
  -> recuperacao configurada na sidebar
  -> trechos ranqueados
  -> prompt especifico da ferramenta
  -> saida simulada ou LLM real
```

Como testar:

1. Abrir `Active tools` na sidebar.
2. Marcar ou desmarcar `Chat`, `Resumo`, `Mapa mental`, `Tabela de dados`, `Citas`, `Flashcards` e `Quiz`.
3. Confirmar que as abas mudam conforme a selecao.
4. Carregar um PDF com texto extraivel.
5. Informar um topico em uma ferramenta.
6. Testar em modo `Placeholder` e depois com `Gemini`.
7. Testar `Vetorial` ou `Hibrida` para confirmar que as ferramentas usam a mesma recuperacao do chat.

## Fase 8C - OpenAI

Status: implementada.

Objetivo: adicionar OpenAI como segundo provedor real por API, mantendo a mesma arquitetura usada pelo Gemini.

O que foi feito:

1. Adicionado `DEFAULT_OPENAI_MODEL`.
2. Adicionado `call_openai` em `llm_service.py`.
3. A chamada usa REST para a Responses API.
4. A chave esperada e `OPENAI_API_KEY`.
5. `generate_response` passou a rotear `OpenAI`.
6. A sidebar passou a mostrar apenas `Placeholder`, `Gemini` e `OpenAI`.
7. Ollama foi removido da selecao visual e permanece fora do escopo final.
8. Erros de chave ausente, modelo invalido, conexao, timeout e limite de uso recebem mensagens amigaveis.

Como testar:

1. Definir `OPENAI_API_KEY` no PowerShell.
2. Rodar o app.
3. Selecionar `OpenAI` na sidebar.
4. Carregar um PDF com texto extraivel.
5. Perguntar no chat ou gerar uma ferramenta.
6. Verificar se a resposta usa fontes e paginas dos PDFs.

## Fase 8A - Exportacao TXT

Status: implementada.

Objetivo: permitir que o usuario salve os materiais de estudo gerados pelo Euclides em arquivos `.txt`, sem dependencias novas.

O que foi feito:

1. Criado `export_service.py`.
2. Adicionado exportador TXT do chat.
3. Adicionado exportador TXT para `Resumo`.
4. Adicionado exportador TXT para `Mapa mental`.
5. Adicionado exportador TXT para `Tabela de dados`.
6. Adicionado exportador TXT para `Citas`.
7. Adicionado exportador TXT para `Flashcards`.
8. Adicionado exportador TXT para `Quiz`.
9. Os arquivos exportados incluem data, topico, conteudo e fontes usadas.
10. Tabelas e flashcards sao convertidos para texto simples.

Como testar:

1. Carregar um PDF.
2. Fazer uma pergunta no chat e clicar em `Exportar chat TXT`.
3. Gerar cada ferramenta de estudo.
4. Clicar no botao `Exportar ... TXT`.
5. Abrir o arquivo baixado e conferir conteudo, topico e fontes.

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

Nenhuma dependencia nova foi adicionada para Gemini ou OpenAI. As chamadas usam bibliotecas padrao do Python via REST.

Variaveis de ambiente para usar provedores reais:

```text
GEMINI_API_KEY
OPENAI_API_KEY
```

Em PowerShell:

```powershell
$env:GEMINI_API_KEY="SUA_CHAVE_AQUI"
$env:OPENAI_API_KEY="SUA_CHAVE_AQUI"
```

Dependencias futuras so devem entrar se houver necessidade real de recursos avancados. O fechamento atual evita SDKs externos.

## Fluxo atual da aplicacao

1. Usuario carrega PDFs na sidebar.
2. O app guarda os arquivos em `st.session_state.sources`.
3. O diagnostico chama `load_pdf_corpus`.
4. `pdf_loader.py` extrai texto, divide em chunks, cacheia o corpus e gera diagnosticos.
5. O teste de busca chama `retrieve_chunks_with_status`.
6. Chat usa `retrieve_chunks_with_status`, respeitando o modo `Lexical`, `Vetorial` ou `Hibrida`.
7. Ferramentas usam a mesma recuperacao configurada na sidebar para montar resumo, mapa mental, tabela, citas, flashcards, quiz e prompts.
8. A resposta final usa Gemini quando o provedor esta selecionado e `GEMINI_API_KEY` existe.
9. A resposta final usa OpenAI quando o provedor esta selecionado e `OPENAI_API_KEY` existe.
10. O modo `Placeholder` continua simulado e sem custo.

## Limitacoes atuais

- As LLMs reais por API sao Gemini e OpenAI.
- Ollama e modelos locais nao fazem parte do escopo final.
- Embeddings existem via Gemini, mas dependem de `GEMINI_API_KEY`.
- O indice vetorial ainda e um prototipo em memoria/cache do Streamlit, nao um banco vetorial persistente como FAISS, Chroma ou pgvector.
- PDFs escaneados sem OCR nao terao texto extraivel.
- O modo padrao ainda e lexical, mas ja existe busca vetorial e busca hibrida selecionavel na sidebar.
- A expansao portugues-ingles cobre apenas termos comuns; nao e uma traducao completa da pergunta.
- O chunking atual ainda e baseado em tamanho de texto; futuramente pode ser refinado por secoes, titulos e estrutura do artigo.

## O que funcionou

Decisoes que deram bons resultados no escopo do projeto:

1. **Placeholder como modo padrao**
   - Permitiu testar interface, RAG, prompts, ferramentas e exportacao sem custo de API.
   - Reduziu risco de chamadas acidentais para Gemini ou OpenAI.

2. **RAG antes da chamada ao modelo**
   - Melhorou a rastreabilidade das respostas.
   - Permitiu exigir citacoes por arquivo e pagina.
   - Reduziu dependencia de conhecimento geral solto do modelo.

3. **Busca lexical como padrao e fallback**
   - Funcionou bem para nomes, siglas, termos tecnicos e palavras exatas.
   - Manteve o app funcional mesmo sem `GEMINI_API_KEY`.

4. **Busca hibrida**
   - Melhorou a recuperacao quando o usuario pergunta em portugues sobre artigos em ingles.
   - Combinou a precisao de termos exatos com similaridade semantica.

5. **Prompts especificos por ferramenta**
   - Resumo, mapa mental, tabela, citas, flashcards e quiz passaram a ter instrucoes proprias.
   - Isso deixou as saidas mais alinhadas ao objetivo de cada ferramenta.

6. **Regra de citacao e limite de contexto**
   - A instrucao para citar `(arquivo, p. numero)` ajudou a tornar as respostas verificaveis.
   - A regra de dizer quando a informacao nao aparece nos PDFs reduziu extrapolacoes.

7. **Chamadas REST diretas**
   - Mantiveram o projeto simples e com poucas dependencias.
   - Facilitaram auditar onde cada provedor e chamado.

8. **Exportacao TXT**
   - Entregou utilidade pratica para estudo.
   - Evitou dependencias extras e formatos complexos.

## O que nao funcionou e ajustes feitos

Problemas encontrados, limitacoes e ajustes:

1. **PDFs escaneados sem OCR**
   - Problema: `pypdf` nao extrai texto de PDFs compostos por imagem.
   - Ajuste: foi criado diagnostico de fontes para avisar quando nao ha texto extraivel.
   - Decisao: OCR ficou fora do escopo final.

2. **Modelo local/Ollama**
   - Problema: a maquina tinha limitacoes tecnicas para rodar modelo local com qualidade aceitavel.
   - Ajuste: Ollama foi removido do escopo final.
   - Decisao: usar Gemini e OpenAI por API.

3. **Busca lexical isolada**
   - Problema: busca por palavras pode falhar quando pergunta e artigo usam termos diferentes ou idiomas diferentes.
   - Ajuste: foi adicionada expansao portugues-ingles para termos academicos.
   - Ajuste posterior: foi adicionada busca vetorial e modo hibrido.

4. **Busca vetorial com custo e dependencia de chave**
   - Problema: embeddings dependem de `GEMINI_API_KEY` e podem gerar custo.
   - Ajuste: `Lexical` continua como padrao.
   - Ajuste: modos `Vetorial` e `Hibrida` fazem fallback para lexical quando embeddings falham.

5. **Risco de respostas genericas da LLM**
   - Problema: modelos podem responder com conhecimento geral sem usar os PDFs.
   - Ajuste: prompts passaram a exigir uso apenas do contexto recuperado.
   - Ajuste: prompts passaram a pedir citacoes e aviso quando a resposta nao estiver nos PDFs.

6. **Function calling nativo**
   - Problema: usar tools nativas de cada provedor aumentaria acoplamento e complexidade.
   - Ajuste: as ferramentas foram implementadas como ferramentas da aplicacao.
   - Decisao: a LLM recebe prompts especificos, mas nao decide autonomamente qual ferramenta chamar.

7. **Banco vetorial persistente**
   - Problema: FAISS, Chroma ou pgvector adicionariam dependencia e configuracao.
   - Ajuste: foi usado indice em memoria/cache do Streamlit.
   - Decisao: suficiente para ate 3 PDFs no escopo atual.

8. **Prompt inicial pouco restritivo**
   - Problema: um prompt apenas com persona academica nao documentava formato de resposta nem limites.
   - Ajuste: o prompt foi refinado com restricao de fonte, citacao, modo de ensino, estrategia de resposta e aviso de ausencia de contexto.

## Status final

O projeto esta concluido dentro do escopo definido.

Checklist de validacao:

1. Testar chat com `Placeholder`, `Gemini` e `OpenAI`.
2. Testar busca `Lexical`, `Vetorial` e `Hibrida`.
3. Confirmar fallback para lexical quando `GEMINI_API_KEY` estiver ausente ou embeddings falharem.
4. Testar ferramentas `Resumo`, `Mapa mental`, `Tabela de dados`, `Citas`, `Flashcards` e `Quiz`.
5. Conferir se as respostas citam arquivo e pagina.
6. Exportar chat e ferramentas em TXT.

Encerramento do projeto:

O projeto e considerado concluido porque:

1. Gemini e OpenAI estiverem disponiveis como provedores por API.
2. O modo `Placeholder` continuar funcionando para testes sem custo.
3. As ferramentas de estudo puderem exportar materiais em TXT.
4. O README documentar como configurar `GEMINI_API_KEY` e `OPENAI_API_KEY`.

Fora do escopo final:

- Fase 8B: persistencia local de PDFs, conversas e resultados.
- Fase 8D: OCR para PDFs escaneados.
- Fase 8E: indice vetorial persistente com FAISS, Chroma ou pgvector.
- Ollama ou qualquer outro modelo local.

## Comandos de Git sugeridos

Para salvar as mudancas:

```powershell
git add euclides_v2
git commit -m "Prepare Euclides v2 for real LLM integration"
git push origin main
```
