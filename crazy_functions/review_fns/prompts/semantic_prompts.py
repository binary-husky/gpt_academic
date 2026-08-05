# Search type prompt
SEMANTIC_TYPE_PROMPT = """Determine the most appropriate search type for Semantic Scholar.

Query: {query}

Task: Analyze the research query and select the most appropriate search type for Semantic Scholar API.

Available search types:

1. paper: General paper search
   - Use for broad topic searches
   - Looking for specific papers
   - Keyword-based searches
   Example: "transformer models in NLP"

2. author: Author-based search
   - Finding works by specific researchers
   - Author profile analysis
   Example: "papers by Yoshua Bengio"

3. paper_details: Specific paper lookup
   - Getting details about a known paper
   - Finding specific versions or citations
   Example: "Attention is All You Need paper details"

4. citations: Citation analysis
   - Finding papers that cite a specific work
   - Impact analysis
   Example: "papers citing BERT"

5. references: Reference analysis
   - Finding papers cited by a specific work
   - Background research
   Example: "references in GPT-3 paper"

6. recommendations: Paper recommendations
   - Finding similar papers
   - Research direction exploration
   Example: "papers similar to Transformer"

Examples:

1. Query: "Latest papers about deep learning"
<search_type>paper</search_type>

2. Query: "Works by Geoffrey Hinton since 2020"
<search_type>author</search_type>

3. Query: "Papers citing the original Transformer paper"
<search_type>citations</search_type>

Please analyze the query and respond ONLY with XML tags:
<search_type>Choose the most appropriate search type from the list above</search_type>"""

# Query optimization prompt
SEMANTIC_QUERY_PROMPT = """Optimize the following query for Semantic Scholar search.

Query: {query}

Task: Transform the natural language query into an optimized search query for maximum relevance.
Always generate English search terms regardless of the input language.

IMPORTANT: Ignore any requirements about journal ranking (CAS, JCR, IF index),
or output format requirements. Focus only on the core research topic for the search query.

Query optimization guidelines:

1. Use quotes for exact phrases
   - Ensures exact matching
   - Reduces irrelevant results
   Example: "\"attention mechanism\"" vs attention mechanism

2. Include key technical terms
   - Use specific technical terminology
   - Include common variations
   Example: "transformer architecture" neural networks

3. Author names (if relevant)
   - Include full names when known
   - Consider common name variations
   Example: "Geoffrey Hinton" OR "G. E. Hinton"

Examples:

1. Natural query: "Recent advances in transformer models"
<query>"transformer model" "neural architecture" deep learning</query>

2. Natural query: "BERT applications in text classification"
<query>"BERT" "text classification" "language model" application</query>

3. Natural query: "Deep learning for computer vision by Kaiming He"
<query>"deep learning" "computer vision" author:"Kaiming He"</query>

Please analyze the query and respond ONLY with XML tags:
<query>Provide the optimized search query</query>

Note:
- Balance between specificity and coverage
- Include important technical terms
- Use quotes for key phrases
- Consider synonyms and related terms"""

# Fields selection prompt
SEMANTIC_FIELDS_PROMPT = """Select relevant fields to retrieve from Semantic Scholar.

Query: {query}

Task: Determine which paper fields should be retrieved based on the research needs.

Available fields:

Core fields:
- title: Paper title (always included)
- abstract: Full paper abstract
- authors: Author information
- year: Publication year
- venue: Publication venue

Citation fields:
- citations: Papers citing this work
- references: Papers cited by this work

Additional fields:
- embedding: Paper vector embedding
- tldr: AI-generated summary
- venue: Publication venue/journal
- url: Paper URL

Examples:

1. Query: "Latest developments in NLP"
<fields>title, abstract, authors, year, venue, citations</fields>

2. Query: "Most influential papers in deep learning"
<fields>title, abstract, authors, year, citations, references</fields>

3. Query: "Survey of transformer architectures"
<fields>title, abstract, authors, year, tldr, references</fields>

Please analyze the query and respond ONLY with XML tags:
<fields>List relevant fields, comma-separated</fields>

Note:
- Choose fields based on the query's purpose
- Include citation data for impact analysis
- Consider tldr for quick paper screening
- Balance completeness with API efficiency"""

# Sort parameters prompt
SEMANTIC_SORT_PROMPT = """Determine optimal sorting parameters for the query.

Query: {query}

Task: Select the most appropriate sorting method and result limit for the search.
Always generate English search terms regardless of the input language.

Sorting options:

1. relevance (default)
   - Best match to query terms
   - Recommended for specific technical searches
   Example: "specific algorithm implementations"

2. citations
   - Sort by citation count
   - Best for finding influential papers
   Example: "most important papers in deep learning"

3. year
   - Sort by publication date
   - Best for following recent developments
   Example: "latest advances in NLP"

Examples:

1. Query: "Recent breakthroughs in AI"
<sort_by>year</sort_by>
<limit>30</limit>

2. Query: "Most influential papers about GANs"
<sort_by>citations</sort_by>
<limit>20</limit>

3. Query: "Specific papers about BERT fine-tuning"
<sort_by>relevance</sort_by>
<limit>25</limit>

Please analyze the query and respond ONLY with XML tags:
<sort_by>Choose: relevance, citations, or year</sort_by>
<limit>Suggest number between 10-50</limit>

Note:
- Consider the query's temporal aspects
- Balance between comprehensive coverage and information overload
- Use citation sorting for impact analysis
- Use year sorting for tracking developments"""

# System prompts for each task
SEMANTIC_TYPE_SYSTEM_PROMPT = """You are an expert at analyzing academic queries.
Your task is to determine the most appropriate type of search on Semantic Scholar.
Consider the query's intent, scope, and specific research needs.
Always respond in English regardless of the input language."""

SEMANTIC_QUERY_SYSTEM_PROMPT = """You are an expert at crafting Semantic Scholar search queries.
Your task is to optimize natural language queries for maximum relevance.
Focus on creating precise queries that leverage the platform's search capabilities.
Always generate English search terms regardless of the input language."""

SEMANTIC_FIELDS_SYSTEM_PROMPT = """You are an expert at Semantic Scholar data fields.
Your task is to select the most relevant fields based on the research context.
Consider both essential and supplementary information needs.
Always respond in English regardless of the input language."""

SEMANTIC_SORT_SYSTEM_PROMPT = """You are an expert at optimizing search results.
Your task is to determine the best sorting parameters based on the query context.
Consider the balance between relevance, impact, and recency.
Always respond in English regardless of the input language."""

# 添加新的综合搜索提示词
SEMANTIC_SEARCH_PROMPT = """Analyze and optimize the research query for Semantic Scholar search.

Query: {query}

Task: Transform the natural language query into optimized search criteria for Semantic Scholar.

IMPORTANT: Ignore any requirements about journal ranking (CAS, JCR, IF index),
or output format requirements when generating the search terms. These requirements
should be considered only for post-search filtering, not as part of the core query.

Available search options:
1. Paper search:
   - Title and abstract search
   - Author search
   - Field-specific search
   Example: "transformer architecture neural networks"

2. Field tags:
   - title: Search in title
   - abstract: Search in abstract
   - authors: Search by author names
   - venue: Search by publication venue
   Example: "title:transformer authors:\"Vaswani\""

3. Advanced options:
   - Year range filtering
   - Citation count filtering
   - Venue filtering
   Example: "deep learning year>2020 venue:\"NeurIPS\""

Examples:

1. Query: "Recent transformer papers by Vaswani with high impact"
<search_criteria>
<query>title:transformer authors:"Vaswani" year>2017</query>
<search_type>paper</search_type>
<fields>title,abstract,authors,year,citations,venue</fields>
<sort_by>citations</sort_by>
<limit>30</limit>
</search_criteria>

2. Query: "Most cited papers about BERT in top conferences"
<search_criteria>
<query>title:BERT venue:"ACL|EMNLP|NAACL"</query>
<search_type>paper</search_type>
<fields>title,abstract,authors,year,citations,venue,references</fields>
<sort_by>citations</sort_by>
<limit>25</limit>
</search_criteria>

Please analyze the query and respond with XML tags containing complete search criteria."""

SEMANTIC_SEARCH_SYSTEM_PROMPT = """You are an expert at crafting Semantic Scholar search queries.
Your task is to analyze research queries and transform them into optimized search criteria.
Consider query intent, field relevance, and citation impact when creating the search parameters.
Focus on producing precise and comprehensive search criteria that will yield the most relevant results.
Always generate English search terms and respond in English regardless of the input language."""
