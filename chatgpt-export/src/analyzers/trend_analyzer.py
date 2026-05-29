from collections import defaultdict
from datetime import datetime


class TrendAnalyzer:
    def analyze(self, conversations: list) -> dict:
        daily_counts = defaultdict(int)
        weekly_counts = defaultdict(int)
        source_daily = defaultdict(lambda: defaultdict(int))
        topic_daily = defaultdict(lambda: defaultdict(int))
        model_daily = defaultdict(lambda: defaultdict(int))

        for conv in conversations:
            date_str = conv.get("date", "")
            if not date_str:
                continue
            try:
                dt = datetime.fromisoformat(date_str) if "T" in date_str else datetime.strptime(date_str, "%Y-%m-%d")
            except (ValueError, TypeError):
                continue
            day_key = dt.strftime("%Y-%m-%d")
            week_key = dt.strftime("%Y-W%W")
            daily_counts[day_key] += 1
            weekly_counts[week_key] += 1
            source = conv.get("source", "unknown")
            source_daily[source][day_key] += 1
            topic = conv.get("topic", "general")
            topic_daily[topic][day_key] += 1
            model = conv.get("model", "unknown") or "unknown"
            model_daily[model][day_key] += 1

        peak_days = sorted(daily_counts.items(), key=lambda x: x[1], reverse=True)[:5] if daily_counts else []

        weekly_data = [{"week": k, "count": v} for k, v in sorted(weekly_counts.items())]
        daily_data = [{"date": k, "count": v} for k, v in sorted(daily_counts.items())]

        topic_drift = self._detect_topic_drift(topic_daily)

        source_timeline = {}
        for src, days in source_daily.items():
            source_timeline[src] = [{"date": k, "count": v} for k, v in sorted(days.items())]

        return {
            "daily": daily_data,
            "weekly": weekly_data,
            "peak_days": peak_days,
            "source_timeline": source_timeline,
            "topic_drift": topic_drift,
            "total_conversations": len(conversations),
            "date_range": self._date_range(daily_data),
        }

    def _detect_topic_drift(self, topic_daily: dict) -> list:
        drifts = []
        for topic, days in topic_daily.items():
            sorted_days = sorted(days.items())
            if len(sorted_days) < 2:
                continue
            mid = len(sorted_days) // 2
            first_half = sum(v for _, v in sorted_days[:mid])
            second_half = sum(v for _, v in sorted_days[mid:])
            total = first_half + second_half
            if total == 0:
                continue
            change_pct = ((second_half - first_half) / total) * 100
            drifts.append({"topic": topic, "change_pct": round(change_pct, 1), "first_half": first_half, "second_half": second_half})
        return sorted(drifts, key=lambda x: abs(x["change_pct"]), reverse=True)

    def _date_range(self, daily_data: list) -> dict:
        if not daily_data:
            return {"start": None, "end": None}
        return {"start": daily_data[0]["date"], "end": daily_data[-1]["date"]}
