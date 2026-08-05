# Crossref query optimization prompt
CROSSREF_QUERY_PROMPT = """Analyze and optimize the query for Crossref search.

Query: {query}

Task: Transform the natural language query into an optimized Crossref search query.
Always generate English search terms regardless of the input language.

IMPORTANT: Ignore any requirements about journal ranking (CAS, JCR, IF index),
or output format requirements. Focus only on the core research topic for the search query.

Available search fields and filters:
1. Basic fields:
   - title: Search in title
   - abstract: Search in abstract
   - author: Search for author names
   - container-title: Search in journal/conference name
   - publisher: Search by publisher name
   - type: Filter by work type (journal-article, book-chapter, etc.)
   - year: Filter by publication year

2. Boolean operators:
   - AND: Both terms must appear
   - OR: Either term can appear
   - NOT: Exclude terms
   - "": Exact phrase match

3. Special filters:
   - is-referenced-by-count: Filter by citation count
   - from-pub-date: Filter by publication date
   - has-abstract: Filter papers with abstracts

Examples:

1. Query: "Machine learning in healthcare after 2020"
<query>title:"machine learning" AND title:healthcare AND from-pub-date:2020</query>

2. Query: "Papers by Geoffrey Hinton about deep learning"
<query>author:"Hinton, Geoffrey" AND (title:"deep learning" OR abstract:"deep learning")</query>

3. Query: "Most cited papers about transformers in Nature"
<query>title:transformer AND container-title:Nature AND is-referenced-by-count:[100 TO *]</query>

4. Query: "Recent BERT applications in medical domain"
<query>title:BERT AND abstract:medical AND from-pub-date:2020 AND type:journal-article</query>

Please analyze the query and respond ONLY with XML tags:
<query>Provide the optimized Crossref search query using appropriate fields and operators</query>"""

# System prompt
CROSSREF_QUERY_SYSTEM_PROMPT = """You are an expert at crafting Crossref search queries.
Your task is to optimize natural language queries for Crossref's API.
Focus on creating precise queries that will return relevant results.
Always generate English search terms regardless of the input language.
Consider using field-specific search terms and appropriate filters to improve search accuracy."""
