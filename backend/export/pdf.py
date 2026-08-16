from datetime import datetime


def build_pdf(entries: list[dict]) -> bytes:
    """
    Renders the audit session output panel as a styled PDF.
    Each entry: { question, answer, sources, response_type, timestamp }
    """
    rows = ""
    for e in entries:
        sources_html = "".join(
            f"<li>{s}</li>" for s in (e.get("sources") or [])
        )
        answer_clean = (
            (e.get("answer") or "")
            .replace("OUT_OF_CONTEXT: ", "")
            .replace("NOT_FOUND: ", "")
        )
        badge_color = {
            "answer":          "#238636",
            "not_found":       "#9a6700",
            "out_of_context":  "#1f6feb",
        }.get(e.get("response_type", ""), "#444")

        rows += f"""
        <div class="entry">
            <div class="entry-header">
                <span class="badge" style="background:{badge_color}">
                    {e.get("response_type", "").replace("_", " ").upper()}
                </span>
                <span class="timestamp">{e.get("timestamp", "")}</span>
            </div>
            <p class="question">{e["question"]}</p>
            <hr/>
            <div class="answer">{answer_clean}</div>
            {"<div class='sources'><strong>Sources:</strong><ul>" + sources_html + "</ul></div>" if sources_html else ""}
        </div>
        """

    html = f"""
    <html>
    <head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500&family=IBM+Plex+Mono:wght@400&display=swap');
        body {{
            font-family: 'IBM Plex Sans', Arial, sans-serif;
            font-size: 11px;
            margin: 40px;
            color: #1a1a2e;
            line-height: 1.6;
        }}
        h1 {{
            font-size: 16px;
            font-weight: 500;
            color: #0a0e13;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 8px;
            margin-bottom: 24px;
        }}
        .meta {{
            font-size: 10px;
            color: #666;
            margin-bottom: 32px;
        }}
        .entry {{
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 16px 20px;
            margin-bottom: 16px;
            page-break-inside: avoid;
        }}
        .entry-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 10px;
        }}
        .badge {{
            color: white;
            font-size: 8px;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: 3px;
            letter-spacing: 0.08em;
            font-family: 'IBM Plex Mono', monospace;
        }}
        .timestamp {{
            font-size: 9px;
            color: #888;
            font-family: 'IBM Plex Mono', monospace;
        }}
        .question {{
            font-size: 13px;
            font-weight: 500;
            margin: 0 0 10px 0;
            color: #0a0e13;
        }}
        hr {{
            border: none;
            border-top: 1px solid #e8e8e8;
            margin: 10px 0;
        }}
        .answer {{
            font-size: 11px;
            line-height: 1.7;
            white-space: pre-wrap;
            color: #2a2a3e;
        }}
        .sources {{
            margin-top: 12px;
            font-size: 10px;
            color: #555;
        }}
        .sources ul {{
            margin: 4px 0 0 16px;
            padding: 0;
        }}
        .sources li {{
            margin-bottom: 2px;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 9px;
        }}
    </style>
    </head>
    <body>
        <h1>Pharmaceutical SOP Audit Session</h1>
        <p class="meta">
            Exported: {datetime.now().strftime("%d %b %Y %H:%M")} &nbsp;·&nbsp;
            {len(entries)} entr{"y" if len(entries) == 1 else "ies"} &nbsp;·&nbsp;
            Powered by RAG · Claude · pgvector
        </p>
        {rows}
    </body>
    </html>
    """
    # Lazy-import WeasyPrint so missing system libraries don't crash app at import-time
    try:
        from weasyprint import HTML
    except Exception as exc:
        raise RuntimeError("WeasyPrint is not available in this environment") from exc

    return HTML(string=html).write_pdf()
