# 新建文件，添加论文识别提示
PAPER_IDENTIFY_PROMPT = """Analyze the query to identify paper details.

Query: {query}

Task: Extract paper identification information from the query.
Always generate English search terms regardless of the input language.

IMPORTANT: Ignore any requirements about journal ranking (CAS, JCR, IF index),
or output format requirements. Focus only on identifying paper details.

Possible paper identifiers:
1. arXiv ID (e.g., 2103.14030, arXiv:2103.14030)
2. DOI (e.g., 10.1234/xxx.xxx)
3. Paper title (e.g., "Attention is All You Need")

Examples:

1. Query with arXiv ID:
Query: "Analyze paper 2103.14030"
<paper_info>
<paper_source>arxiv</paper_source>
<paper_id>2103.14030</paper_id>
<paper_title></paper_title>
</paper_info>

2. Query with DOI:
Query: "Review the paper with DOI 10.1234/xxx.xxx"
<paper_info>
<paper_source>doi</paper_source>
<paper_id>10.1234/xxx.xxx</paper_id>
<paper_title></paper_title>
</paper_info>

3. Query with paper title:
Query: "Analyze 'Attention is All You Need' paper"
<paper_info>
<paper_source>title</paper_source>
<paper_id></paper_id>
<paper_title>Attention is All You Need</paper_title>
</paper_info>

Please analyze the query and respond ONLY with XML tags containing paper information."""

PAPER_IDENTIFY_SYSTEM_PROMPT = """You are an expert at identifying academic paper references.
Your task is to extract paper identification information from queries.
Look for arXiv IDs, DOIs, and paper titles."""
