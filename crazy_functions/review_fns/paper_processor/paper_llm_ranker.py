from typing import List, Dict
from crazy_functions.review_fns.data_sources.base_source import PaperMetadata
from request_llms.embed_models.bge_llm import BGELLMRanker
from crazy_functions.review_fns.query_analyzer import SearchCriteria
import random
from crazy_functions.review_fns.data_sources.journal_metrics import JournalMetrics

class PaperLLMRanker:
    """使用LLM进行论文重排序"""

    def __init__(self, llm_kwargs: Dict = None):
        self.ranker = BGELLMRanker(llm_kwargs=llm_kwargs)
        self.journal_metrics = JournalMetrics()

    def _update_paper_metrics(self, papers: List[PaperMetadata]) -> None:
        """更新论文的期刊指标"""
        for paper in papers:
            # 跳过arXiv来源的论文
            if getattr(paper, 'source', '') == 'arxiv':
                continue

            if hasattr(paper, 'venue_name') or hasattr(paper, 'venue_info'):
                # 获取venue_name和venue_info
                venue_name = getattr(paper, 'venue_name', '')
                venue_info = getattr(paper, 'venue_info', {})

                # 使用改进的匹配逻辑获取指标
                metrics = self.journal_metrics.get_journal_metrics(venue_name, venue_info)

                # 更新论文的指标
                paper.if_factor = metrics.get('if_factor')
                paper.jcr_division = metrics.get('jcr_division')
                paper.cas_division = metrics.get('cas_division')

    def _get_year_as_int(self, paper) -> int:
        """统一获取论文年份为整数格式

        Args:
            paper: 论文对象或直接是年份值

        Returns:
            整数格式的年份，如果无法转换则返回0
        """
        try:
            # 如果输入直接是年份而不是论文对象
            if isinstance(paper, int):
                return paper
            elif isinstance(paper, str):
                try:
                    return int(paper)
                except ValueError:
                    import re
                    year_match = re.search(r'\d{4}', paper)
                    if year_match:
                        return int(year_match.group())
                    return 0
            elif isinstance(paper, float):
                return int(paper)

            # 处理论文对象
            year = getattr(paper, 'year', None)
            if year is None:
                return 0

            # 如果是字符串，尝试转换为整数
            if isinstance(year, str):
                # 首先尝试直接转换整个字符串
                try:
                    return int(year)
                except ValueError:
                    # 如果直接转换失败，尝试提取第一个数字序列
                    import re
                    year_match = re.search(r'\d{4}', year)
                    if year_match:
                        return int(year_match.group())
                    return 0
            # 如果是浮点数，转换为整数
            elif isinstance(year, float):
                return int(year)
            # 如果已经是整数，直接返回
            elif isinstance(year, int):
                return year
            return 0
        except (ValueError, TypeError):
            return 0

    def rank_papers(
        self,
        query: str,
        papers: List[PaperMetadata],
        search_criteria: SearchCriteria = None,
        top_k: int = 40,
        use_rerank: bool = False,
        pre_filter_ratio: float = 0.5,
        max_papers: int = 150
    ) -> List[PaperMetadata]:
        """对论文进行重排序"""
        initial_count = len(papers) if papers else 0
        stats = {'initial': initial_count}

        if not papers or not query:
            return []

        # 更新论文的期刊指标
        self._update_paper_metrics(papers)

        # 构建增强查询
        # enhanced_query = self._build_enhanced_query(query, search_criteria) if search_criteria else query
        enhanced_query = query
        # 首先过滤不满足年份要求的论文
        if search_criteria and search_criteria.start_year and search_criteria.end_year:
            before_year_filter = len(papers)
            filtered_papers = []
            start_year = int(search_criteria.start_year)
            end_year = int(search_criteria.end_year)

            for paper in papers:
                paper_year = self._get_year_as_int(paper)
                if paper_year == 0 or start_year <= paper_year <= end_year:
                    filtered_papers.append(paper)

            papers = filtered_papers
            stats['after_year_filter'] = len(papers)

        if not papers:  # 如果过滤后没有论文，直接返回空列表
            return []

        # 新增：对少量论文的快速处理
        SMALL_PAPER_THRESHOLD = 10  # 定义"少量"论文的阈值
        if len(papers) <= SMALL_PAPER_THRESHOLD:
            # 对于少量论文，直接根据查询类型进行简单排序
            if search_criteria:
                if search_criteria.query_type == "latest":
                    papers.sort(key=lambda x: getattr(x, 'year', 0) or 0, reverse=True)
                elif search_criteria.query_type == "recommend":
                    papers.sort(key=lambda x: getattr(x, 'citations', 0) or 0, reverse=True)
                elif search_criteria.query_type == "review":
                    papers.sort(key=lambda x:
                        1 if any(keyword in (getattr(x, 'title', '') or '').lower() or
                                keyword in (getattr(x, 'abstract', '') or '').lower()
                                for keyword in ['review', 'survey', 'overview'])
                        else 0,
                        reverse=True
                    )
            return papers[:top_k]

        # 1. 优先处理最新的论文
        if search_criteria and search_criteria.query_type == "latest":
            papers = sorted(papers, key=lambda x: self._get_year_as_int(x), reverse=True)

        # 2. 如果是综述类查询，优先处理可能的综述论文
        if search_criteria and search_criteria.query_type == "review":
            papers = sorted(papers, key=lambda x:
                1 if any(keyword in (getattr(x, 'title', '') or '').lower() or
                        keyword in (getattr(x, 'abstract', '') or '').lower()
                        for keyword in ['review', 'survey', 'overview'])
                else 0,
                reverse=True
            )

        # 3. 如果论文数量超过限制，采用分层采样而不是完全随机
        if len(papers) > max_papers:
            before_max_limit = len(papers)
            papers = self._select_papers_strategically(papers, search_criteria, max_papers)
            stats['after_max_limit'] = len(papers)

        try:
            paper_texts = []
            valid_papers = []  # 4. 跟踪有效论文

            for paper in papers:
                if paper is None:
                    continue
                # 5. 预先过滤明显不相关的论文
                if search_criteria and search_criteria.start_year:
                    if getattr(paper, 'year', 0) and self._get_year_as_int(paper.year) < search_criteria.start_year:
                        continue

                doc = self._build_enhanced_document(paper, search_criteria)
                paper_texts.append(doc)
                valid_papers.append(paper)  # 记录对应的论文

            stats['after_valid_check'] = len(valid_papers)

            if not paper_texts:
                return []

            # 使用LLM判断相关性
            relevance_results = self.ranker.batch_check_relevance(
                query=enhanced_query,  # 使用增强的查询
                paper_texts=paper_texts,
                show_progress=True
            )

            # 6. 优化相关论文的选择策略
            relevant_papers = []
            for paper, is_relevant in zip(valid_papers, relevance_results):
                if is_relevant:
                    relevant_papers.append(paper)

            stats['after_llm_filter'] = len(relevant_papers)

            # 打印统计信息
            print(f"论文筛选统计: 初始数量={stats['initial']}, " +
                  f"年份过滤后={stats.get('after_year_filter', stats['initial'])}, " +
                  f"数量限制后={stats.get('after_max_limit', stats.get('after_year_filter', stats['initial']))}, " +
                  f"有效性检查后={stats['after_valid_check']}, " +
                  f"LLM筛选后={stats['after_llm_filter']}")

            # 7. 改进回退策略
            if len(relevant_papers) < min(5, len(papers)):
                # 如果相关论文太少，返回按引用量排序的论文
                return sorted(
                    papers[:top_k],
                    key=lambda x: getattr(x, 'citations', 0) or 0,
                    reverse=True
                )

            # 8. 对最终结果进行排序
            if search_criteria:
                if search_criteria.query_type == "latest":
                    # 最新论文优先，但同年份按IF排序
                    relevant_papers.sort(key=lambda x: (
                        self._get_year_as_int(x),
                        getattr(x, 'if_factor', 0) or 0
                    ), reverse=True)
                elif search_criteria.query_type == "recommend":
                    # IF指数优先，其次是引用量
                    relevant_papers.sort(key=lambda x: (
                        getattr(x, 'if_factor', 0) or 0,
                        getattr(x, 'citations', 0) or 0
                    ), reverse=True)
                else:
                    # 默认按IF指数排序
                    relevant_papers.sort(key=lambda x: getattr(x, 'if_factor', 0) or 0, reverse=True)

            return relevant_papers[:top_k]

        except Exception as e:
            print(f"论文排序时出错: {str(e)}")
            # 9. 改进错误处理的回退策略
            try:
                return sorted(
                    papers[:top_k],
                    key=lambda x: getattr(x, 'citations', 0) or 0,
                    reverse=True
                )
            except:
                return papers[:top_k] if papers else []

    def _build_enhanced_query(self, query: str, criteria: SearchCriteria) -> str:
        """构建增强的查询文本"""
        components = []

        # 强调这是用户的原始查询，是最重要的匹配依据
        components.append(f"Original user query that must be primarily matched: {query}")

        if criteria:
            # 添加主题（如果与原始查询不同）
            if criteria.main_topic and criteria.main_topic != query:
                components.append(f"Additional context - The main topic is about: {criteria.main_topic}")

            # 添加子主题
            if criteria.sub_topics:
                components.append(f"Secondary aspects to consider: {', '.join(criteria.sub_topics)}")

            # 添加查询类型相关信息
            if criteria.query_type == "review":
                components.append("Paper type preference: Looking for comprehensive review papers, survey papers, or overview papers")
            elif criteria.query_type == "latest":
                components.append("Temporal preference: Focus on the most recent developments and latest papers")
            elif criteria.query_type == "recommend":
                components.append("Impact preference: Consider influential and fundamental papers")

        # 直接连接所有组件，保持语序
        enhanced_query = ' '.join(components)

        # 限制长度但不打乱顺序
        if len(enhanced_query) > 1000:
            enhanced_query = enhanced_query[:997] + "..."

        return enhanced_query

    def _build_enhanced_document(self, paper: PaperMetadata, criteria: SearchCriteria) -> str:
        """构建增强的文档表示"""
        components = []

        # 基本信息
        title = getattr(paper, 'title', '')
        authors = ', '.join(getattr(paper, 'authors', []))
        abstract = getattr(paper, 'abstract', '')
        year = getattr(paper, 'year', '')
        venue = getattr(paper, 'venue', '')

        components.extend([
            f"Title: {title}",
            f"Authors: {authors}",
            f"Year: {year}",
            f"Venue: {venue}",
            f"Abstract: {abstract}"
        ])

        # 根据查询类型添加额外信息
        if criteria:
            if criteria.query_type == "review":
                # 对于综述类查询，强调论文的综述性质
                title_lower = (title or '').lower()
                abstract_lower = (abstract or '').lower()
                if any(keyword in title_lower or keyword in abstract_lower
                      for keyword in ['review', 'survey', 'overview']):
                    components.append("This is a review/survey paper")

            elif criteria.query_type == "latest":
                # 对于最新论文查询，强调时间信息
                if year and int(year) >= criteria.start_year:
                    components.append(f"This is a recent paper from {year}")

            elif criteria.query_type == "recommend":
                # 对于推荐类查询，添加主题相关性信息
                if criteria.main_topic:
                    title_lower = (title or '').lower()
                    abstract_lower = (abstract or '').lower()
                    topic_relevance = any(topic.lower() in title_lower or topic.lower() in abstract_lower
                                        for topic in [criteria.main_topic] + (criteria.sub_topics or []))
                    if topic_relevance:
                        components.append(f"This paper is directly related to {criteria.main_topic}")

        return '\n'.join(components)

    def _select_papers_strategically(
        self,
        papers: List[PaperMetadata],
        search_criteria: SearchCriteria,
        max_papers: int = 150
    ) -> List[PaperMetadata]:
        """战略性地选择论文子集，优先选择非Crossref来源的论文，
        当ADS论文充足时排除arXiv论文"""
        if len(papers) <= max_papers:
            return papers

        # 1. 首先按来源分组
        papers_by_source = {
            'crossref': [],
            'adsabs': [],
            'arxiv': [],
            'others': []  # semantic, pubmed等其他来源
        }

        for paper in papers:
            source = getattr(paper, 'source', '')
            if source == 'crossref':
                papers_by_source['crossref'].append(paper)
            elif source == 'adsabs':
                papers_by_source['adsabs'].append(paper)
            elif source == 'arxiv':
                papers_by_source['arxiv'].append(paper)
            else:
                papers_by_source['others'].append(paper)

        # 2. 计算分数的通用函数
        def calculate_paper_score(paper):
            score = 0
            title = (getattr(paper, 'title', '') or '').lower()
            abstract = (getattr(paper, 'abstract', '') or '').lower()
            year = self._get_year_as_int(paper)
            citations = getattr(paper, 'citations', 0) or 0

            # 安全地获取搜索条件
            main_topic = (getattr(search_criteria, 'main_topic', '') or '').lower()
            sub_topics = getattr(search_criteria, 'sub_topics', []) or []
            query_type = getattr(search_criteria, 'query_type', '')
            start_year = getattr(search_criteria, 'start_year', 0) or 0

            # 主题相关性得分
            if main_topic and main_topic in title:
                score += 10
            if main_topic and main_topic in abstract:
                score += 5

            # 子主题相关性得分
            for sub_topic in sub_topics:
                if sub_topic and sub_topic.lower() in title:
                    score += 5
                if sub_topic and sub_topic.lower() in abstract:
                    score += 2.5

            # 根据查询类型调整分数
            if query_type == "review":
                review_keywords = ['review', 'survey', 'overview']
                if any(keyword in title for keyword in review_keywords):
                    score *= 1.5
                if any(keyword in abstract for keyword in review_keywords):
                    score *= 1.2
            elif query_type == "latest":
                if year and start_year:
                    year_int = year if isinstance(year, int) else self._get_year_as_int(paper)
                    start_year_int = start_year if isinstance(start_year, int) else int(start_year)
                    if year_int >= start_year_int:
                        recency_bonus = min(5, (year_int - start_year_int))
                        score += recency_bonus * 2
            elif query_type == "recommend":
                citation_score = min(10, citations / 100)
                score += citation_score

            return score

        result = []

        # 3. 处理ADS和arXiv论文
        non_crossref_papers = papers_by_source['others']  # 首先添加其他来源的论文

        # 添加ADS论文
        if papers_by_source['adsabs']:
            non_crossref_papers.extend(papers_by_source['adsabs'])

        # 只有当ADS论文不足20篇时，才添加arXiv论文
        if len(papers_by_source['adsabs']) <= 20:
            non_crossref_papers.extend(papers_by_source['arxiv'])
        elif not papers_by_source['adsabs'] and papers_by_source['arxiv']:
            # 如果没有ADS论文但有arXiv论文，也使用arXiv论文
            non_crossref_papers.extend(papers_by_source['arxiv'])

        # 4. 对非Crossref论文评分和排序
        scored_non_crossref = [(p, calculate_paper_score(p)) for p in non_crossref_papers]
        scored_non_crossref.sort(key=lambda x: x[1], reverse=True)

        # 5. 先添加高分的非Crossref论文
        non_crossref_limit = max_papers * 0.9  # 90%的配额给非Crossref论文
        if len(scored_non_crossref) >= non_crossref_limit:
            result.extend([p[0] for p in scored_non_crossref[:int(non_crossref_limit)]])
        else:
            result.extend([p[0] for p in scored_non_crossref])

        # 6. 如果还有剩余空间，考虑添加Crossref论文
        remaining_slots = max_papers - len(result)
        if remaining_slots > 0 and papers_by_source['crossref']:
            # 计算Crossref论文的最大数量（不超过总数的10%）
            max_crossref = min(remaining_slots, max_papers * 0.1)

            # 对Crossref论文评分和排序
            scored_crossref = [(p, calculate_paper_score(p)) for p in papers_by_source['crossref']]
            scored_crossref.sort(key=lambda x: x[1], reverse=True)

            # 添加最高分的Crossref论文
            result.extend([p[0] for p in scored_crossref[:int(max_crossref)]])

        # 7. 如果使用了Crossref论文后还有空位，继续使用非Crossref论文填充
        if len(result) < max_papers and len(scored_non_crossref) > len(result):
            remaining_non_crossref = [p[0] for p in scored_non_crossref[len(result):]]
            result.extend(remaining_non_crossref[:max_papers - len(result)])

        return result
