from datetime import datetime


class AnalyticsReport:
    def generate_html(self, stats: dict, trends: dict, costs: dict) -> str:
        total = stats.get("total_conversations", 0)
        total_msgs = stats.get("total_messages", 0)
        avg_msgs = stats.get("avg_messages_per_conv", 0)
        avg_len = stats.get("avg_length_chars", 0)
        total_cost = costs.get("total_cost", 0)
        source = stats.get("most_active_source", "N/A")

        topic_rows = ""
        for topic, count in stats.get("most_common_topics", []):
            topic_rows += f"<tr><td>{topic}</td><td>{count}</td></tr>\n"

        daily_data = trends.get("daily", [])
        daily_labels = json_escape([d["date"] for d in daily_data])
        daily_counts = json_escape([d["count"] for d in daily_data])

        cost_by_model = costs.get("by_model", {})
        cost_labels = json_escape(list(cost_by_model.keys()))
        cost_values = json_escape([v["total_cost"] for v in cost_by_model.values()])

        topic_labels = json_escape([t for t, _ in stats.get("most_common_topics", [])])
        topic_values = json_escape([c for _, c in stats.get("most_common_topics", [])])

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Analytics Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; color: #333; padding: 20px; }}
  h1 {{ margin-bottom: 20px; color: #1a1a2e; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
  .card {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .card h3 {{ font-size: 0.85em; text-transform: uppercase; color: #888; margin-bottom: 5px; }}
  .card .value {{ font-size: 2em; font-weight: 700; color: #1a1a2e; }}
  .charts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 30px; }}
  .chart-box {{ background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  .chart-box h3 {{ margin-bottom: 15px; color: #444; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
  th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }}
  th {{ background: #f8f9fa; font-weight: 600; color: #555; }}
  tr:last-child td {{ border-bottom: none; }}
  .section {{ margin-bottom: 30px; }}
  .section h2 {{ margin-bottom: 15px; color: #1a1a2e; }}
</style>
</head>
<body>
<h1>Analytics Report</h1>
<p style="color:#888;margin-bottom:20px;">Generated {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>

<div class="cards">
  <div class="card"><h3>Conversations</h3><div class="value">{total}</div></div>
  <div class="card"><h3>Total Messages</h3><div class="value">{total_msgs}</div></div>
  <div class="card"><h3>Avg Messages/Conv</h3><div class="value">{avg_msgs}</div></div>
  <div class="card"><h3>Avg Length</h3><div class="value">{avg_len} chars</div></div>
  <div class="card"><h3>Est. Cost (GPT-4)</h3><div class="value">${total_cost:.2f}</div></div>
  <div class="card"><h3>Most Active Source</h3><div class="value">{source}</div></div>
</div>

<div class="charts">
  <div class="chart-box">
    <h3>Daily Activity</h3>
    <canvas id="dailyChart"></canvas>
  </div>
  <div class="chart-box">
    <h3>Cost by Model</h3>
    <canvas id="costChart"></canvas>
  </div>
  <div class="chart-box">
    <h3>Topics</h3>
    <canvas id="topicChart"></canvas>
  </div>
</div>

<div class="section">
  <h2>Topic Distribution</h2>
  <table>
    <thead><tr><th>Topic</th><th>Count</th></tr></thead>
    <tbody>{topic_rows}</tbody>
  </table>
</div>

<script>
new Chart(document.getElementById('dailyChart'), {{
  type: 'line',
  data: {{
    labels: {daily_labels},
    datasets: [{{ label: 'Conversations', data: {daily_counts}, borderColor: '#4f46e5', fill: true, tension: 0.3 }}]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});
new Chart(document.getElementById('costChart'), {{
  type: 'bar',
  data: {{
    labels: {cost_labels},
    datasets: [{{ label: 'Cost ($)', data: {cost_values}, backgroundColor: '#10b981' }}]
  }},
  options: {{ responsive: true, plugins: {{ legend: {{ display: false }} }} }}
}});
new Chart(document.getElementById('topicChart'), {{
  type: 'pie',
  data: {{
    labels: {topic_labels},
    datasets: [{{ data: {topic_values}, backgroundColor: ['#4f46e5','#10b981','#f59e0b','#ef4444','#8b5cf6','#ec4899','#14b8a6','#f97316'] }}]
  }},
  options: {{ responsive: true }}
}});
</script>
</body>
</html>"""
        return html

    def generate_csv(self, stats: dict) -> str:
        lines = ["metric,value"]
        for key, val in stats.items():
            if isinstance(val, (str, int, float)):
                lines.append(f"{key},{val}")
            elif isinstance(val, list) and val and isinstance(val[0], tuple):
                for k, v in val:
                    lines.append(f"{key}_{k},{v}")
        return "\n".join(lines)


def json_escape(obj):
    import json
    return json.dumps(obj)
