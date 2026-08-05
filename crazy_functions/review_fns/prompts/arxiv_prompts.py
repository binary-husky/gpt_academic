# Basic type analysis prompt
ARXIV_TYPE_PROMPT = """Analyze the research query and determine if arXiv search is needed and its type.

Query: {query}

Task 1: Determine if this query requires arXiv search
- arXiv is suitable for:
  * Computer science and AI/ML
  * Physics and mathematics
  * Quantitative biology and finance
  * Electrical engineering
  * Recent preprints in these fields
- arXiv is NOT needed for:
  * Medical research (unless ML/AI applications)
  * Social sciences
  * Business studies
  * Humanities
  * Industry reports

Task 2: If arXiv search is needed, determine the most appropriate search type
Available types:
1. basic: Keyword-based search across all fields
   - For specific technical queries
   - When looking for particular methods or applications
2. category: Category-based search within specific fields
   - For broad topic exploration
   - When surveying a research area
3. none: arXiv search not needed for this query
   - When topic is outside arXiv's scope
   - For non-technical or clinical research

Examples:

1. Query: "BERT transformer architecture"
<search_type>basic</search_type>

2. Query: "latest developments in machine learning"
<search_type>category</search_type>

3. Query: "COVID-19 clinical trials"
<search_type>none</search_type>

4. Query: "psychological effects of social media"
<search_type>none</search_type>

Please analyze the query and respond ONLY with XML tags:
<search_type>Choose either 'basic', 'category', or 'none'</search_type>"""

# Query optimization prompt
ARXIV_QUERY_PROMPT = """Optimize the following query for arXiv search.

Query: {query}

Task: Transform the natural language query into an optimized arXiv search query using boolean operators and field tags.
Always generate English search terms regardless of the input language.

IMPORTANT: Ignore any requirements about journal ranking (CAS, JCR, IF index),
or output format requirements. Focus only on the core research topic for the search query.

Available field tags:
- ti: Search in title
- abs: Search in abstract
- au: Search for author
- all: Search in all fields (default)

Boolean operators:
- AND: Both terms must appear
- OR: Either term can appear
- NOT: Exclude terms
- (): Group terms
- "": Exact phrase match

Examples:

1. Natural query: "Recent papers about transformer models by Vaswani"
<query>ti:"transformer model" AND au:Vaswani AND year:[2017 TO 2024]</query>

2. Natural query: "Deep learning for computer vision, excluding surveys"
<query>ti:(deep learning AND "computer vision") NOT (ti:survey OR ti:review)</query>

3. Natural query: "Attention mechanism in language models"
<query>ti:(attention OR "attention mechanism") AND abs:"language model"</query>

4. Natural query: "GANs or generative adversarial networks for image generation"
<query>(ti:GAN OR ti:"generative adversarial network") AND abs:"image generation"</query>

Please analyze the query and respond ONLY with XML tags:
<query>Provide the optimized search query using appropriate operators and tags</query>

Note:
- Use quotes for exact phrases
- Combine multiple conditions with boolean operators
- Consider both title and abstract for important concepts
- Include author names when relevant
- Use parentheses for complex logical groupings"""

# Sort parameters prompt
ARXIV_SORT_PROMPT = """Determine optimal sorting parameters for the research query.

Query: {query}

Task: Select the most appropriate sorting parameters to help users find the most relevant papers.

Available sorting options:

1. Sort by:
   - relevance: Best match to query terms (default)
   - lastUpdatedDate: Most recently updated papers
   - submittedDate: Most recently submitted papers

2. Sort order:
   - descending: Newest/Most relevant first (default)
   - ascending: Oldest/Least relevant first

3. Result limit:
   - Minimum: 10 papers
   - Maximum: 50 papers
   - Recommended: 20-30 papers for most queries

Examples:

1. Query: "Latest developments in transformer models"
<sort_by>submittedDate</sort_by>
<sort_order>descending</sort_order>
<limit>30</limit>

2. Query: "Foundational papers about neural networks"
<sort_by>relevance</sort_by>
<sort_order>descending</sort_order>
<limit>20</limit>

3. Query: "Evolution of deep learning since 2012"
<sort_by>submittedDate</sort_by>
<sort_order>ascending</sort_order>
<limit>50</limit>

Please analyze the query and respond ONLY with XML tags:
<sort_by>Choose: relevance, lastUpdatedDate, or submittedDate</sort_by>
<sort_order>Choose: ascending or descending</sort_order>
<limit>Suggest number between 10-50</limit>

Note:
- Choose relevance for specific technical queries
- Use lastUpdatedDate for tracking paper revisions
- Use submittedDate for following recent developments
- Consider query context when setting the limit"""

# System prompts for each task
ARXIV_TYPE_SYSTEM_PROMPT = """You are an expert at analyzing academic queries.
Your task is to determine whether the query is better suited for keyword search or category-based search.
Consider the query's specificity, scope, and intended search area when making your decision.
Always respond in English regardless of the input language."""

ARXIV_QUERY_SYSTEM_PROMPT = """You are an expert at crafting arXiv search queries.
Your task is to optimize natural language queries using boolean operators and field tags.
Focus on creating precise, targeted queries that will return the most relevant results.
Always generate English search terms regardless of the input language."""

ARXIV_CATEGORIES_SYSTEM_PROMPT = """You are an expert at arXiv category classification.
Your task is to select the most relevant categories for the given research query.
Consider both primary and related interdisciplinary categories, while maintaining focus on the main research area.
Always respond in English regardless of the input language."""

ARXIV_SORT_SYSTEM_PROMPT = """You are an expert at optimizing search results.
Your task is to determine the best sorting parameters based on the query context.
Consider the user's likely intent and temporal aspects of the research topic.
Always respond in English regardless of the input language."""

# 添加新的搜索提示词
ARXIV_SEARCH_PROMPT = """Analyze and optimize the research query for arXiv search.

Query: {query}

Task: Transform the natural language query into an optimized arXiv search query.

Available search options:
1. Basic search with field tags:
   - ti: Search in title
   - abs: Search in abstract
   - au: Search for author
   Example: "ti:transformer AND abs:attention"

2. Category-based search:
   - Use specific arXiv categories
   Example: "cat:cs.AI AND neural networks"

3. Date range:
   - Specify date range using submittedDate
   Example: "deep learning AND submittedDate:[20200101 TO 20231231]"

Examples:

1. Query: "Recent papers about transformer models by Vaswani"
<search_criteria>
<query>ti:"transformer model" AND au:Vaswani AND submittedDate:[20170101 TO 99991231]</query>
<categories>cs.CL, cs.AI, cs.LG</categories>
<sort_by>submittedDate</sort_by>
<sort_order>descending</sort_order>
<limit>30</limit>
</search_criteria>

2. Query: "Latest developments in computer vision"
<search_criteria>
<query>cat:cs.CV AND submittedDate:[20220101 TO 99991231]</query>
<categories>cs.CV, cs.AI, cs.LG</categories>
<sort_by>submittedDate</sort_by>
<sort_order>descending</sort_order>
<limit>25</limit>
</search_criteria>

Please analyze the query and respond with XML tags containing search criteria."""

ARXIV_SEARCH_SYSTEM_PROMPT = """You are an expert at crafting arXiv search queries.
Your task is to analyze research queries and transform them into optimized arXiv search criteria.
Consider query intent, relevant categories, and temporal aspects when creating the search parameters.
Always generate English search terms and respond in English regardless of the input language."""

# Categories selection prompt
ARXIV_CATEGORIES_PROMPT = """Select the most relevant arXiv categories for the research query.

Query: {query}

Task: Choose 2-4 most relevant categories that best match the research topic.

Available Categories:

Computer Science (cs):
- cs.AI: Artificial Intelligence (neural networks, machine learning, NLP)
- cs.CL: Computation and Language (NLP, machine translation)
- cs.CV: Computer Vision and Pattern Recognition
- cs.LG: Machine Learning (deep learning, reinforcement learning)
- cs.NE: Neural and Evolutionary Computing
- cs.RO: Robotics
- cs.IR: Information Retrieval
- cs.SE: Software Engineering
- cs.DB: Databases
- cs.DC: Distributed Computing
- cs.CY: Computers and Society
- cs.HC: Human-Computer Interaction

Mathematics (math):
- math.OC: Optimization and Control
- math.PR: Probability
- math.ST: Statistics
- math.NA: Numerical Analysis
- math.DS: Dynamical Systems

Statistics (stat):
- stat.ML: Machine Learning
- stat.ME: Methodology
- stat.TH: Theory
- stat.AP: Applications

Physics (physics):
- physics.comp-ph: Computational Physics
- physics.data-an: Data Analysis
- physics.soc-ph: Physics and Society

Electrical Engineering (eess):
- eess.SP: Signal Processing
- eess.AS: Audio and Speech Processing
- eess.IV: Image and Video Processing
- eess.SY: Systems and Control

Examples:

1. Query: "Deep learning for computer vision"
<categories>cs.CV, cs.LG, stat.ML</categories>

2. Query: "Natural language processing with transformers"
<categories>cs.CL, cs.AI, cs.LG</categories>

3. Query: "Reinforcement learning for robotics"
<categories>cs.RO, cs.AI, cs.LG</categories>

4. Query: "Statistical methods in machine learning"
<categories>stat.ML, cs.LG, math.ST</categories>

Please analyze the query and respond ONLY with XML tags:
<categories>List 2-4 most relevant categories, comma-separated</categories>

Note:
- Choose primary categories first, then add related ones
- Limit to 2-4 most relevant categories
- Order by relevance (most relevant first)
- Use comma and space between categories (e.g., "cs.AI, cs.LG")"""

# 在文件末尾添加新的 prompt
ARXIV_LATEST_PROMPT = """Determine if the query is requesting latest papers from arXiv.

Query: {query}

Task: Analyze if the query is specifically asking for recent/latest papers from arXiv.

IMPORTANT RULE:
- The query MUST explicitly mention "arXiv" or "arxiv" to be considered a latest arXiv papers request
- Queries only asking for recent/latest papers WITHOUT mentioning arXiv should return false

Indicators for latest papers request:
1. MUST HAVE keywords about arXiv:
   - "arxiv"
   - "arXiv"
   AND

2. Keywords about recency:
   - "latest"
   - "recent"
   - "new"
   - "newest"
   - "just published"
   - "this week/month"

Examples:

1. Latest papers request (Valid):
Query: "Show me the latest AI papers on arXiv"
<is_latest_request>true</is_latest_request>

2. Latest papers request (Valid):
Query: "What are the recent papers about transformers on arxiv"
<is_latest_request>true</is_latest_request>

3. Not a latest papers request (Invalid - no mention of arXiv):
Query: "Show me the latest papers about BERT"
<is_latest_request>false</is_latest_request>

4. Not a latest papers request (Invalid - no recency):
Query: "Find papers on arxiv about transformers"
<is_latest_request>false</is_latest_request>

Please analyze the query and respond ONLY with XML tags:
<is_latest_request>true/false</is_latest_request>

Note: The response should be true ONLY if both conditions are met:
1. Query explicitly mentions arXiv/arxiv
2. Query asks for recent/latest papers"""

ARXIV_LATEST_SYSTEM_PROMPT = """You are an expert at analyzing academic queries.
Your task is to determine if the query is specifically requesting latest/recent papers from arXiv.
Remember: The query MUST explicitly mention arXiv to be considered valid, even if it asks for recent papers.
Always respond in English regardless of the input language."""
