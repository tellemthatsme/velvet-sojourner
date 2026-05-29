MODEL_RATES = {
    "gpt-4": {"input": 30.0, "output": 60.0},
    "gpt-4-turbo": {"input": 10.0, "output": 30.0},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "claude-3-opus": {"input": 15.0, "output": 75.0},
    "claude-3-sonnet": {"input": 3.0, "output": 15.0},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "gemini-pro": {"input": 0.50, "output": 1.50},
    "o1": {"input": 15.0, "output": 60.0},
    "o3": {"input": 10.0, "output": 40.0},
}


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def estimate_cost(text: str, model: str) -> float:
    rates = MODEL_RATES.get(model)
    if not rates:
        return 0.0
    tokens = estimate_tokens(text)
    input_tokens = int(tokens * 0.67)
    output_tokens = tokens - input_tokens
    cost = (input_tokens / 1_000_000) * rates["input"] + (output_tokens / 1_000_000) * rates["output"]
    return round(cost, 6)


class CostAnalyzer:
    def analyze_conversation(self, conv: dict) -> dict:
        content = ""
        for msg in conv.get("messages", []):
            content += msg.get("content", "") + " "
        tokens = estimate_tokens(content)
        costs = {m: estimate_cost(content, m) for m in MODEL_RATES}
        return {"tokens": tokens, "costs": costs, "message_count": len(conv.get("messages", []))}

    def analyze_batch(self, convs: list) -> dict:
        by_model = {}
        by_source = {}
        details = []
        total_tokens = 0
        for conv in convs:
            result = self.analyze_conversation(conv)
            total_tokens += result["tokens"]
            source = conv.get("source", "unknown")
            by_source[source] = by_source.get(source, 0) + 1
            for model, cost in result["costs"].items():
                if model not in by_model:
                    by_model[model] = {"count": 0, "total_cost": 0.0, "total_tokens": 0}
                by_model[model]["count"] += 1
                by_model[model]["total_cost"] += cost
                by_model[model]["total_tokens"] += result["tokens"]
            details.append(result)
        total_cost = sum(max(c["costs"].values()) for c in details)
        return {
            "total": len(convs),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 6),
            "by_model": by_model,
            "by_source": by_source,
            "details": details,
        }
