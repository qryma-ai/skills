#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qryma Search Core Logic
"""
import os
import re
import json
import urllib.request
import sys
from typing import Optional

def detect_user_language() -> str:
    """
    自动检测用户的语言设置。
    首先尝试从环境变量读取，然后通过IP地址定位检测，默认返回 'en'。
    """
    # 1. 尝试从环境变量读取
    lang_env = os.environ.get("QRYMA_LANG")
    if lang_env:
        return lang_env.strip()

    try:
        # 2. 通过IP地址定位服务检测语言
        # 使用免费的ipapi.co服务
        with urllib.request.urlopen("https://ipapi.co/json/", timeout=5) as response:
            ip_data = json.loads(response.read().decode("utf-8"))
            country_code = ip_data.get("country_code")

            # 根据国家代码映射到语言
            lang_map = {
                "CN": "zh-CN",  # 中国（简体中文）
                "TW": "zh-TW",  # 台湾（繁体中文）
                "HK": "zh-TW",  # 香港（繁体中文）
                "SG": "zh-CN",  # 新加坡（简体中文）
                "JP": "ja",     # 日本
                "KR": "ko",     # 韩国
                "FR": "fr",     # 法国
                "DE": "de",     # 德国
                "IT": "it",     # 意大利
                "ES": "es",     # 西班牙
                "PT": "pt-PT",  # 葡萄牙
                "BR": "pt-BR",  # 巴西（葡萄牙语）
                "RU": "ru",     # 俄罗斯
                "AR": "ar",     # 阿拉伯语
                "GB": "en-GB",  # 英国（英式英语）
                "US": "en",     # 美国（英语）
                "CA": "fr-CA",  # 加拿大（法语）
                "IN": "hi",     # 印度（印地语）
                "ID": "id",     # 印度尼西亚
                "MY": "ms",     # 马来西亚（马来语）
                "PH": "fil",    # 菲律宾（菲律宾语）
                "TH": "th",     # 泰国
                "VI": "vi",     # 越南
                "TR": "tr",     # 土耳其
                "GR": "el",     # 希腊
                "NL": "nl",     # 荷兰
                "SE": "sv",     # 瑞典
                "NO": "no",     # 挪威
                "FI": "fi",     # 芬兰
                "DK": "da",     # 丹麦
                "PL": "pl",     # 波兰
                "CZ": "cs",     # 捷克
                "HU": "hu",     # 匈牙利
                "RO": "ro",     # 罗马尼亚
                "BG": "bg",     # 保加利亚
                "HU": "hu",     # 匈牙利
                "SK": "sk",     # 斯洛伐克
                "SI": "sl",     # 斯洛文尼亚
                "EE": "et",     # 爱沙尼亚
                "LV": "lv",     # 拉脱维亚
                "LT": "lt",     # 立陶宛
                "IE": "en-GB",  # 爱尔兰
                "AT": "de",     # 奥地利（德语）
                "CH": "de",     # 瑞士（德语）
                "BE": "fr",     # 比利时（法语）
            }

            return lang_map.get(country_code, "en")  # 默认英语

    except Exception as e:
        print(f"自动语言检测失败: {e}", file=sys.stderr)
        return "en"  # 失败时默认英语

# Backward compatibility
QRYMA_URL = "https://search.qryma.com/api/web"


def load_key() -> Optional[str]:
    """Load Qryma API key"""
    # Load from environment variable
    key = os.environ.get("QRYMA_API_KEY")
    if key:
        return key.strip()

    # Load from environment variable for endpoint
    endpoint = os.environ.get("QRYMA_ENDPOINT")
    if endpoint:
        pass  # just for loading, we'll handle it in the core

    # Load from config file
    env_path = os.path.expanduser("~/.qryma/.env")
    if not os.path.exists(env_path):
        env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            m = re.search(r"^\s*QRYMA_API_KEY\s*=\s*(.+?)\s*$", txt, re.M)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v:
                    return v
        except Exception:
            pass

    return None


def load_endpoint() -> str:
    """Load Qryma API endpoint"""
    # Load from environment variable
    endpoint = os.environ.get("QRYMA_ENDPOINT")
    if endpoint:
        return endpoint.strip()

    # Load from config file
    env_path = os.path.expanduser("~/.qryma/.env")
    if not os.path.exists(env_path):
        env_path = ".env"
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            m = re.search(r"^\s*QRYMA_ENDPOINT\s*=\s*(.+?)\s*$", txt, re.M)
            if m:
                v = m.group(1).strip().strip('"').strip("'")
                if v:
                    return v
        except Exception:
            pass

    # Default to the old endpoint for backward compatibility
    return "https://search.qryma.com/api/web"


class QrymaSearchCore:
    """Qryma search core class"""

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None):
        self.api_key = api_key or load_key()
        self.endpoint = endpoint or load_endpoint()

    def search(
        self,
        query: str,
        max_results: int = 10,
        lang: Optional[str] = None,
        start: int = 0,
        safe: bool = False,
        detail: bool = True,
    ) -> dict:
        """Execute search"""
        if not self.api_key:
            raise ValueError("QRYMA_API_KEY not found")

        # 如果没有指定语言，则自动检测
        if lang is None:
            lang = detect_user_language()

        # Backend API parameters: query, lang, start, safe, detail
        payload = {
            "query": query,
            "lang": lang,
            "start": start,
            "safe": safe,
            "detail": detail,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "X-Api-Key": self.api_key,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")

        try:
            obj = json.loads(body)
        except json.JSONDecodeError as e:
            raise ValueError(f"Response parsing failed: {e}") from e

        # Format response
        out = {
            "query": query,
            "results": [],
        }
        # Process result format returned by backend
        # max_results is applied locally by truncating results array
        organic_results = obj.get("organic") or []
        for r in organic_results[:max_results]:
            out["results"].append(
                {
                    "title": r.get("title"),
                    "url": r.get("link"),  # API returns link field
                    "content": r.get("text"),
                }
            )

        return out
