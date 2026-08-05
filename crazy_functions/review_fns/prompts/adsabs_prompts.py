# ADS query optimization prompt
ADSABS_QUERY_PROMPT = """Analyze and optimize the following query for NASA ADS search.
If the query is not related to astronomy, astrophysics, or physics, return <query>none</query>.
If the query contains non-English terms, translate them to English first.

Query: {query}

Task: Transform the natural language query into an optimized ADS search query.
Always generate English search terms regardless of the input language.

IMPORTANT: Ignore any requirements about journal ranking (CAS, JCR, IF index),
or output format requirements. Focus only on the core research topic for the search query.

Relevant research areas for ADS:
- Astronomy and astrophysics
- Physics (theoretical and experimental)
- Space science and exploration
- Planetary science
- Cosmology
- Astrobiology
- Related instrumentation and methods

Available search fields and filters:
1. Basic fields:
   - title: Search in title (title:"term")
   - abstract: Search in abstract (abstract:"term")
   - author: Search for author names (author:"lastname, firstname")
   - year: Filter by year (year:2020-2023)
   - bibstem: Search by journal abbreviation (bibstem:ApJ)

2. Boolean operators:
   - AND
   - OR
   - NOT
   - (): Group terms
   - "": Exact phrase match

3. Special filters:
   - citations(identifier:paper): Papers citing a specific paper
   - references(identifier:paper): References of a specific paper
   - citation_count: Filter by citation count
   - database: Filter by database (database:astronomy)

Examples:

1. Query: "Black holes in galaxy centers after 2020"
<query>title:"black hole" AND abstract:"galaxy center" AND year:2020-</query>

2. Query: "Papers by Neil deGrasse Tyson about exoplanets"
<query>author:"Tyson, Neil deGrasse" AND title:exoplanet</query>

3. Query: "Most cited papers about dark matter in ApJ"
<query>title:"dark matter" AND bibstem:ApJ AND citation_count:[100 TO *]</query>

4. Query: "Latest research on diabetes treatment"
<query>none</query>

5. Query: "Machine learning for galaxy classification"
<query>title:("machine learning" OR "deep learning") AND (title:galaxy OR abstract:galaxy) AND abstract:classification</query>

Please analyze the query and respond ONLY with XML tags:
<query>Provide the optimized ADS search query using appropriate fields and operators, or "none" if not relevant</query>"""

# System prompt
ADSABS_QUERY_SYSTEM_PROMPT = """You are an expert at crafting NASA ADS search queries.
Your task is to:
1. First determine if the query is relevant to astronomy, astrophysics, or physics research
2. If relevant, optimize the natural language query for the ADS API
3. If not relevant, return "none" to indicate the query should be handled by other databases

Focus on creating precise queries that will return relevant astronomical and physics literature.
Always generate English search terms regardless of the input language.
Consider using field-specific search terms and appropriate filters to improve search accuracy.

Remember: ADS is specifically for astronomy, astrophysics, and physics research.
Medical, biological, or general research queries should return "none"."""
