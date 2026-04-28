"""
Generate the daily Markdown report from stock data and news articles.
"""
import os
from datetime import datetime


def _format_article(article: dict) -> str:
    title = article.get("title", "").strip()
    url = article.get("url", "").strip()
    summary = article.get("summary", "").strip()
    is_important = article.get("is_important", False)

    link_md = f"[{title}]({url})" if url else title
    if is_important:
        line = f"⭐ **[重要]** **{link_md}**"
    else:
        line = f"**{link_md}**"

    if summary:
        return f"{line}\n> {summary}\n"
    return f"{line}\n"


def _stock_section(date_str: str, rows: list[dict]) -> str:
    lines = [
        f"## 📈 美股昨日收盤（{date_str}）\n",
        "| 指數／標的 | 收盤價 | 漲跌 | 漲跌幅 |",
        "|-----------|--------|------|--------|",
    ]
    for row in rows:
        close = row["close"]
        arrow = row["arrow"]
        change = row["change"]
        pct = row["pct"]
        if close == "N/A":
            lines.append(f"| {row['name']} | N/A | ─ N/A | N/A |")
        else:
            lines.append(f"| {row['name']} | {close} | {arrow} {change} | {pct} |")
    return "\n".join(lines) + "\n"


def _news_section(
    emoji: str,
    section_title: str,
    scraper_results: list[dict],
) -> str:
    lines = [f"## {emoji} {section_title}\n"]
    for result in scraper_results:
        site_name = result.get("site_name", "Unknown")
        articles = result.get("articles", [])
        status = result.get("status", "unknown")
        message = result.get("message", "")
        http_status = result.get("http_status")
        final_url = result.get("final_url", "")
        lines.append(f"### {site_name}\n")
        if not articles:
            if status == "empty":
                lines.append("_（本次爬取未取得任何文章）_\n")
            else:
                detail_parts = []
                if http_status is not None:
                    detail_parts.append(f"HTTP {http_status}")
                if message:
                    detail_parts.append(message)
                if final_url:
                    detail_parts.append(f"final_url={final_url}")
                detail = " | ".join(detail_parts) if detail_parts else "未知錯誤"
                lines.append(f"_（本次爬取失敗：{detail}）_\n")
        else:
            for a in articles:
                lines.append(_format_article(a))
    return "\n".join(lines)


def generate_report(
    stock_date: str,
    stock_rows: list[dict],
    international: list[tuple[str, list[dict]]],
    taiwan: list[tuple[str, list[dict]]],
    output_dir: str = "output",
) -> str:
    """Build the Markdown report and save it. Returns the file path."""
    today = datetime.now().strftime("%Y%m%d")
    report_date = datetime.now().strftime("%Y-%m-%d")

    sections = [
        f"# 📰 每日財經摘要 — {report_date}\n",
        "---\n",
        _stock_section(stock_date, stock_rows),
        "\n---\n",
        _news_section("🌍", "國際財經新聞", international),
        "\n---\n",
        _news_section("🇹🇼", "台灣財經新聞", taiwan),
    ]

    content = "\n".join(sections)

    os.makedirs(output_dir, exist_ok=True)
    filename = f"daily_finance_news_{today}.md"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath
