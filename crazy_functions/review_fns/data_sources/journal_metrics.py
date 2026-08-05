import json
import os
from typing import Dict, Optional

class JournalMetrics:
    """期刊指标管理类"""

    def __init__(self):
        self.journal_data: Dict = {}  # 期刊名称到指标的映射
        self.issn_map: Dict = {}      # ISSN到指标的映射
        self.name_map: Dict = {}      # 标准化名称到指标的映射
        self._load_journal_data()

    def _normalize_journal_name(self, name: str) -> str:
        """标准化期刊名称

        Args:
            name: 原始期刊名称

        Returns:
            标准化后的期刊名称
        """
        if not name:
            return ""

        # 转换为小写
        name = name.lower()

        # 移除常见的前缀和后缀
        prefixes = ['the ', 'proceedings of ', 'journal of ']
        suffixes = [' journal', ' proceedings', ' magazine', ' review', ' letters']

        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):]

        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]

        # 移除特殊字符，保留字母、数字和空格
        name = ''.join(c for c in name if c.isalnum() or c.isspace())

        # 移除多余的空格
        name = ' '.join(name.split())

        return name

    def _convert_if_value(self, if_str: str) -> Optional[float]:
        """转换IF值为float，处理特殊情况"""
        try:
            if if_str.startswith('<'):
                # 对于<0.1这样的值，返回0.1
                return float(if_str.strip('<'))
            return float(if_str)
        except (ValueError, AttributeError):
            return None

    def _load_journal_data(self):
        """加载期刊数据"""
        try:
            file_path = os.path.join(os.path.dirname(__file__), 'cas_if.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 建立期刊名称到指标的映射
            for journal in data:
                # 准备指标数据
                metrics = {
                    'if_factor': self._convert_if_value(journal.get('IF')),
                    'jcr_division': journal.get('Q'),
                    'cas_division': journal.get('B')
                }

                # 存储期刊名称映射（使用标准化名称）
                if journal.get('journal'):
                    normalized_name = self._normalize_journal_name(journal['journal'])
                    self.journal_data[normalized_name] = metrics
                    self.name_map[normalized_name] = metrics

                # 存储期刊缩写映射
                if journal.get('jabb'):
                    normalized_abbr = self._normalize_journal_name(journal['jabb'])
                    self.journal_data[normalized_abbr] = metrics
                    self.name_map[normalized_abbr] = metrics

                # 存储ISSN映射
                if journal.get('issn'):
                    self.issn_map[journal['issn']] = metrics
                if journal.get('eissn'):
                    self.issn_map[journal['eissn']] = metrics

        except Exception as e:
            print(f"加载期刊数据时出错: {str(e)}")
            self.journal_data = {}
            self.issn_map = {}
            self.name_map = {}

    def get_journal_metrics(self, venue_name: str, venue_info: dict) -> dict:
        """获取期刊指标

        Args:
            venue_name: 期刊名称
            venue_info: 期刊详细信息

        Returns:
            包含期刊指标的字典
        """
        try:
            metrics = {}

            # 1. 首先尝试通过ISSN匹配
            if venue_info and 'issn' in venue_info:
                issn_value = venue_info['issn']
                # 处理ISSN可能是列表的情况
                if isinstance(issn_value, list):
                    # 尝试每个ISSN
                    for issn in issn_value:
                        metrics = self.issn_map.get(issn, {})
                        if metrics:  # 如果找到匹配的指标，就停止搜索
                            break
                else:  # ISSN是字符串的情况
                    metrics = self.issn_map.get(issn_value, {})

            # 2. 如果ISSN匹配失败，尝试通过期刊名称匹配
            if not metrics and venue_name:
                # 标准化期刊名称
                normalized_name = self._normalize_journal_name(venue_name)
                metrics = self.name_map.get(normalized_name, {})

                # 如果完全匹配失败，尝试部分匹配
                # if not metrics:
                #     for db_name, db_metrics in self.name_map.items():
                #         if normalized_name in db_name:
                #             metrics = db_metrics
                #             break

            return metrics

        except Exception as e:
            print(f"获取期刊指标时出错: {str(e)}")
            return {}
