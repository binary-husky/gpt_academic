# PubMed search type prompt
PUBMED_TYPE_PROMPT = """Analyze the research query and determine the appropriate PubMed search type.

Query: {query}

Available search types:
1. basic: General keyword search for medical/biomedical topics
2. author: Search by author name
3. journal: Search within specific journals
4. none: Query not related to medical/biomedical research

Examples:

1. Query: "COVID-19 treatment outcomes"
<search_type>basic</search_type>

2. Query: "Papers by Anthony Fauci"
<search_type>author</search_type>

3. Query: "Recent papers in Nature about CRISPR"
<search_type>journal</search_type>

4. Query: "Deep learning for computer vision"
<search_type>none</search_type>

5. Query: "Transformer architecture for NLP"
<search_type>none</search_type>

Please analyze the query and respond ONLY with XML tags:
<search_type>Choose: basic, author, journal, or none</search_type>"""

# PubMed query optimization prompt
PUBMED_QUERY_PROMPT = """Optimize the following query for PubMed search.

Query: {query}

Task: Transform the natural language query into an optimized PubMed search query.
Requirements:
- Always generate English search terms regardless of input language
- Translate any non-English terms to English before creating the query
- Never include non-English characters in the final query

IMPORTANT: Ignore any requirements about journal ranking (CAS, JCR, IF index),
or output format requirements. Focus only on the core medical/biomedical topic for the search query.

Available field tags:
- [Title] - Search in title
- [Author] - Search for author
- [Journal] - Search in journal name
- [MeSH Terms] - Search using MeSH terms

Boolean operators:
- AND
- OR
- NOT

Examples:

1. Query: "COVID-19 treatment in elderly patients"
<query>COVID-19[Title] AND treatment[Title/Abstract] AND elderly[Title/Abstract]</query>

2. Query: "Cancer immunotherapy review articles"
<query>cancer immunotherapy[Title/Abstract] AND review[Publication Type]</query>

Please analyze the query and respond ONLY with XML tags:
<query>Provide the optimized PubMed search query</query>"""

# PubMed sort parameters prompt
PUBMED_SORT_PROMPT = """Determine optimal sorting parameters for PubMed results.

Query: {query}

Task: Select the most appropriate sorting method and result limit.

Available sort options:
- relevance: Best match to query
- date: Most recent first
- journal: Sort by journal name

Examples:

1. Query: "Latest developments in gene therapy"
<sort_by>date</sort_by>
<limit>30</limit>

2. Query: "Classic papers about DNA structure"
<sort_by>relevance</sort_by>
<limit>20</limit>

Please analyze the query and respond ONLY with XML tags:
<sort_by>Choose: relevance, date, or journal</sort_by>
<limit>Suggest number between 10-50</limit>"""

# System prompts
PUBMED_TYPE_SYSTEM_PROMPT = """You are an expert at analyzing medical and scientific queries.
Your task is to determine the most appropriate PubMed search type.
Consider the query's focus and intended search scope.
Always respond in English regardless of the input language."""

PUBMED_QUERY_SYSTEM_PROMPT = """You are an expert at crafting PubMed search queries.
Your task is to optimize natural language queries using PubMed's search syntax.
Focus on creating precise, targeted queries that will return relevant medical literature.
Always generate English search terms regardless of the input language."""

PUBMED_SORT_SYSTEM_PROMPT = """You are an expert at optimizing PubMed search results.
Your task is to determine the best sorting parameters based on the query context.
Consider the balance between relevance and recency.
Always respond in English regardless of the input language."""
