from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, Response
from typing import Optional
from collections import defaultdict

router = APIRouter()

_conversations = []
_knowledge_base = None


def init(data: list, kb=None):
    global _conversations, _knowledge_base
    _conversations = data
    _knowledge_base = kb


@router.get("/stats")
async def get_stats():
    from ..analyzers.session_stats import compute
    return compute(_conversations)


@router.get("/trends")
async def get_trends():
    from ..analyzers.trend_analyzer import TrendAnalyzer
    analyzer = TrendAnalyzer()
    return analyzer.analyze(_conversations)


@router.get("/topics")
async def get_topics():
    from collections import Counter
    topics = Counter()
    for conv in _conversations:
        topic = conv.get("topic", "general")
        topics[topic] += 1
    return topics.most_common(50)


@router.get("/costs")
async def get_costs():
    from ..analyzers.cost_tracker import CostAnalyzer
    analyzer = CostAnalyzer()
    return analyzer.analyze_batch(_conversations)


@router.get("/costs/monthly")
async def get_monthly_costs():
    from ..analyzers.cost_tracker import CostAnalyzer
    analyzer = CostAnalyzer()
    monthly = defaultdict(lambda: {"count": 0, "total_cost": 0.0, "total_tokens": 0})
    for conv in _conversations:
        date_str = conv.get("date", "")
        if not date_str:
            continue
        month = date_str[:7]
        result = analyzer.analyze_conversation(conv)
        monthly[month]["count"] += 1
        monthly[month]["total_tokens"] += result["tokens"]
        monthly[month]["total_cost"] += max(result["costs"].values()) if result["costs"] else 0
    return [{"month": k, "count": v["count"], "total_tokens": v["total_tokens"], "total_cost": round(v["total_cost"], 4)}
            for k, v in sorted(monthly.items())]


@router.get("/search")
async def search(q: str = Query(""), limit: int = Query(50)):
    if not q or not _knowledge_base:
        return []
    return _knowledge_base.search(q, limit=limit)


@router.get("/conversations")
async def list_conversations(page: int = Query(1, ge=1), per_page: int = Query(50, ge=1, le=200)):
    start = (page - 1) * per_page
    end = start + per_page
    items = _conversations[start:end]
    return {
        "items": items,
        "total": len(_conversations),
        "page": page,
        "per_page": per_page,
        "total_pages": max(1, (len(_conversations) + per_page - 1) // per_page),
    }


@router.get("/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    for conv in _conversations:
        if conv.get("id") == conv_id:
            return conv
    return {"error": "not found"}


@router.get("/export/csv")
async def export_csv():
    import csv
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "title", "date", "source", "model", "topic", "tokens", "estimated_cost", "message_count"])
    for conv in _conversations:
        content = " ".join(m.get("content", "") for m in conv.get("messages", []))
        tokens = max(1, len(content) // 4)
        writer.writerow([
            conv.get("id", ""),
            conv.get("title", ""),
            conv.get("date", ""),
            conv.get("source", ""),
            conv.get("model", ""),
            conv.get("topic", ""),
            tokens,
            round(tokens * 0.00003 * 30.0, 4),
            len(conv.get("messages", [])),
        ])
    return Response(content=output.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=conversations.csv"})


@router.get("/export/report")
async def export_report():
    from ..analyzers.session_stats import compute
    from ..analyzers.trend_analyzer import TrendAnalyzer
    from ..analyzers.cost_tracker import CostAnalyzer
    from ..exporters.analytics_report import AnalyticsReport
    stats = compute(_conversations)
    trend = TrendAnalyzer().analyze(_conversations)
    costs = CostAnalyzer().analyze_batch(_conversations)
    report = AnalyticsReport()
    html = report.generate_html({k: v for k, v in stats.__dict__.items()}, trend, costs)
    return HTMLResponse(content=html)


@router.get("/export/data")
async def export_data(format: str = Query("csv"), start: str = Query(""), end: str = Query("")):
    filtered = _conversations
    if start:
        filtered = [c for c in filtered if c.get("date", "") >= start]
    if end:
        filtered = [c for c in filtered if c.get("date", "") <= end]

    if format == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "title", "date", "source", "model", "topic", "tokens", "estimated_cost", "message_count"])
        for conv in filtered:
            content = " ".join(m.get("content", "") for m in conv.get("messages", []))
            tokens = max(1, len(content) // 4)
            writer.writerow([
                conv.get("id", ""), conv.get("title", ""), conv.get("date", ""),
                conv.get("source", ""), conv.get("model", ""), conv.get("topic", ""),
                tokens, round(tokens * 0.00003 * 30.0, 4), len(conv.get("messages", [])),
            ])
        return Response(content=output.getvalue(), media_type="text/csv",
                        headers={"Content-Disposition": "attachment; filename=export.csv"})
    elif format == "html":
        from ..analyzers.session_stats import compute
        from ..analyzers.trend_analyzer import TrendAnalyzer
        from ..analyzers.cost_tracker import CostAnalyzer
        from ..exporters.analytics_report import AnalyticsReport
        stats = compute(filtered)
        trend = TrendAnalyzer().analyze(filtered)
        costs = CostAnalyzer().analyze_batch(filtered)
        report = AnalyticsReport()
        html = report.generate_html({k: v for k, v in stats.__dict__.items()}, trend, costs)
        return HTMLResponse(content=html)
    else:
        items = []
        for c in filtered:
            items.append({
                "id": c.get("id"), "title": c.get("title"), "date": c.get("date"),
                "source": c.get("source"), "model": c.get("model"), "topic": c.get("topic"),
                "message_count": len(c.get("messages", [])),
            })
        return items
