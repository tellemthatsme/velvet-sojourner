#!/usr/bin/env python3
import sys
import os

try:
    from PyQt6.QtWidgets import QApplication
    from src.gui import ExportGUI
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

if __name__ == "__main__":
    if "--cli" in sys.argv or not HAS_GUI:
        import argparse

        parser = argparse.ArgumentParser(
            description="ChatGPT Exporter - Export, organize, and analyze AI conversations",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""Examples:
  python main.py --cli                              CLI mode with defaults
  python main.py --cli --input ./downloads --output ./exports
  python main.py --cli --analytics                  Show analytics report
  python main.py --cli --cost                       Show cost estimation
  python main.py --cli --serve                      Start web dashboard
  python main.py --cli --report html                Generate HTML report
  python main.py --cli --stats                      Show file statistics
  python main.py --cli --dedupe                     Deduplicate exports
  python main.py --cli --merge file1.txt file2.txt --output merged.md
  python main.py                                   Launch GUI (if PyQt6 installed)
            """,
        )
        parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
        parser.add_argument("--analytics", action="store_true", help="Show analytics report")
        parser.add_argument("--cost", action="store_true", help="Show cost estimation")
        parser.add_argument("--serve", action="store_true", help="Start web dashboard server")
        parser.add_argument("--report", choices=["html", "csv"], default=None, help="Generate analytics report (html/csv)")
        parser.add_argument("--port", type=int, default=8766, help="Web dashboard port (default: 8766)")
        parser.add_argument("--input", "-i", type=str, default="downloads", help="Input directory (default: downloads)")
        parser.add_argument("--output", "-o", type=str, default="exports", help="Output directory (default: exports)")
        parser.add_argument("--stats", action="store_true", help="Show file statistics")
        parser.add_argument("--dedupe", action="store_true", help="Remove duplicates")
        parser.add_argument("--merge", nargs="+", help="Merge conversation files into one")
        parser.add_argument("--format", choices=["md", "html", "pdf"], default="md", help="Output format (default: md)")
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        args, remaining = parser.parse_known_args()

        if args.analytics or args.cost or args.serve or args.report:
            from src.export_sorter import ExportSorter
            from pathlib import Path
            from src.analyzers.session_stats import compute
            from src.analyzers.trend_analyzer import TrendAnalyzer
            from src.analyzers.cost_tracker import CostAnalyzer
            from src.analyzers.model_detector import ModelDetector
            from src.exporters.analytics_report import AnalyticsReport
            from src.exporters.csv_export import export_conversations_csv
            from src.knowledge_base import KnowledgeBase
            import json

            input_dir = Path(args.input or "downloads")
            output_dir = Path(args.output or "exports")
            sorter = ExportSorter(input_dir, output_dir)
            files = sorter.scan_input()
            conversations = []
            detector = ModelDetector()
            for fpath in files:
                chat = sorter.parser.parse_file(fpath)
                if chat:
                    conv = {
                        "id": fpath.stem,
                        "title": chat.title,
                        "date": chat.date or "",
                        "source": chat.source,
                        "model": chat.model or detector.detect_source_model(chat.source),
                        "topic": sorter.organizer._classify_type(chat),
                        "messages": chat.messages,
                        "metadata": chat.metadata,
                    }
                    conversations.append(conv)

            if args.analytics:
                stats = compute(conversations)
                trend = TrendAnalyzer().analyze(conversations)
                costs = CostAnalyzer().analyze_batch(conversations)
                print("\n=== ANALYTICS REPORT ===")
                print(f"Total Conversations: {stats.total_conversations}")
                print(f"Total Messages:      {stats.total_messages}")
                print(f"Avg Msgs/Conv:       {stats.avg_messages_per_conv}")
                print(f"Avg Length (chars):  {stats.avg_length_chars}")
                print(f"Avg Length (tokens): {stats.avg_length_tokens}")
                print(f"Most Active Source:  {stats.most_active_source}")
                print(f"\nTop Topics:")
                for topic, count in stats.most_common_topics[:5]:
                    print(f"  - {topic}: {count}")
                print(f"\nTop Keywords:")
                for word, count in stats.top_keywords[:10]:
                    print(f"  - {word}: {count}")
                print(f"\nTrends: {len(trend.get('daily', []))} days of data")
                print(f"Date Range: {trend.get('date_range', {}).get('start', 'N/A')} to {trend.get('date_range', {}).get('end', 'N/A')}")
                print(f"Peak Days: {trend.get('peak_days', [])}")
                print(f"\nEstimated Cost (GPT-4): ${costs.get('total_cost', 0):.4f}")

            if args.cost:
                costs = CostAnalyzer().analyze_batch(conversations)
                print("\n=== COST ESTIMATION ===")
                print(f"Total Conversations: {costs['total']}")
                print(f"Total Tokens:        {costs['total_tokens']:,}")
                print(f"Total Cost (max):    ${costs['total_cost']:.4f}")
                print(f"\nBreakdown by Model:")
                for model, data in sorted(costs["by_model"].items()):
                    print(f"  {model}: ${data['total_cost']:.4f} ({data['count']} convs, {data['total_tokens']:,} tokens)")
                print(f"\nBreakdown by Source:")
                for src, count in sorted(costs["by_source"].items()):
                    print(f"  {src}: {count} conversations")

            if args.report == "html":
                stats = compute(conversations)
                trend = TrendAnalyzer().analyze(conversations)
                costs = CostAnalyzer().analyze_batch(conversations)
                report = AnalyticsReport()
                html = report.generate_html(
                    {k: v for k, v in stats.__dict__.items()},
                    trend, costs,
                )
                out_path = Path("analytics_report.html")
                out_path.write_text(html, encoding="utf-8")
                print(f"\nHTML report saved to {out_path.resolve()}")
            elif args.report == "csv":
                stats = compute(conversations)
                report = AnalyticsReport()
                csv_data = report.generate_csv({k: v for k, v in stats.__dict__.items()})
                out_path = Path("analytics_report.csv")
                out_path.write_text(csv_data, encoding="utf-8")
                print(f"\nCSV report saved to {out_path.resolve()}")

            if args.serve:
                port = args.port
                kb = KnowledgeBase()
                from src.api.routes import init as api_init
                api_init(conversations, kb)
                try:
                    from src.web.app import serve as web_serve
                    web_serve(host="0.0.0.0", port=port)
                except ImportError:
                    from fastapi import FastAPI
                    import uvicorn
                    app = FastAPI(title="ChatGPT Export Dashboard")
                    from src.api.routes import router as api_router
                    app.include_router(api_router)
                    import webbrowser
                    webbrowser.open(f"http://localhost:{port}")
                    print(f"\nDashboard: http://localhost:{port}")
                    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

        else:
            sys.argv = [arg for arg in sys.argv if arg not in ("--cli",)]
            from src.export_sorter import main as cli_main
            cli_main()
    else:
        from PyQt6.QtWidgets import QApplication
        from src.gui import ExportGUI
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        window = ExportGUI()
        window.show()
        sys.exit(app.exec())
