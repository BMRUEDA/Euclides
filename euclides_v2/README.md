# Euclides v2

Esta pasta e uma evolucao separada do projeto atual. O objetivo e permitir o desenvolvimento em fases sem modificar o `app.py` original da raiz do repositorio.

## Objetivo

Transformar o Euclides de um prototipo visual em uma aplicacao funcional para estudo com PDFs, chat e ferramentas academicas.

## Fases sugeridas

1. **Extracao de PDF**
   - Ler arquivos PDF carregados pelo usuario.
   - Separar texto por pagina.
   - Guardar metadados como nome do arquivo e numero da pagina.

2. **Busca inicial**
   - Implementar uma busca simples por palavras-chave.
   - Retornar trechos relevantes antes de adicionar embeddings.

3. **Chat com contexto**
   - Usar os trechos recuperados para montar o prompt.
   - Conectar uma LLM por meio de um servico isolado.

4. **Ferramentas de estudo**
   - Resumo.
   - Mapa mental.
   - Tabela de dados.
   - Todas usando a mesma base de contexto dos PDFs.

5. **RAG vetorial**
   - Adicionar embeddings.
   - Criar indice vetorial.
   - Melhorar recuperacao semantica.

## Estrutura

```text
euclides_v2/
  README.md
  app.py
  requirements.txt
  components/
    chat.py
    sidebar.py
    study_tools.py
  models/
    source.py
  services/
    llm_service.py
    pdf_loader.py
    retrieval.py
    tool_service.py
```

## Como executar futuramente

```powershell
streamlit run euclides_v2/app.py
```

