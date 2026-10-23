#!/usr/bin/env python3
"""
Agentic Video Studio — Interactive EDL (Edit Decision List) Review Generator
Ported & enhanced from Nate Herk's herk-edit-kit (scripts/build-edl-review.mjs).

Builds a self-contained, responsive dark-glass HTML review dashboard for an EDL.
Visualizes:
- Kept regions (emerald green) vs Cut regions (crimson red / amber)
- Interactive timeline scrubber bar where clicking any cut plays what was removed
- Detailed statistics: source duration, edited duration, seconds saved, cut types breakdown
- Top Cuts table with timecodes, reasons, and 1-click jump buttons
- Embeds both original and edited video players side-by-side
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


def fmt_time(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - (m * 60)
    return f"{m:02d}:{s:05.2f}"


def generate_edl_html(
    edl_data: Dict[str, Any],
    original_video_url: Optional[str] = None,
    edited_video_url: Optional[str] = None,
    title: str = "Edit Decision List Review"
) -> str:
    dur = float(edl_data.get("source_duration", 60.0))
    if dur <= 0:
        dur = 60.0
    edited_dur = float(edl_data.get("edited_duration", dur))
    removed = float(edl_data.get("removed", max(0.0, dur - edited_dur)))
    pct_saved = round((removed / dur) * 100, 1) if dur > 0 else 0.0

    keeps = edl_data.get("keep_ranges", [])
    deletes = edl_data.get("delete_ranges", [])

    # If no keeps provided, synthesize from deletes
    if not keeps and deletes:
        keeps = []
        cur = 0.0
        for d in sorted(deletes, key=lambda x: x["start"]):
            if d["start"] > cur + 0.05:
                keeps.append({"start": cur, "end": d["start"]})
            cur = max(cur, d["end"])
        if cur < dur - 0.05:
            keeps.append({"start": cur, "end": dur})

    def pct(s: float) -> float:
        return max(0.0, min(100.0, (s / dur) * 100.0))

    # Segment HTML
    keep_segments_html = []
    for k in keeps:
        st, en = float(k["start"]), float(k["end"])
        left = pct(st)
        width = max(0.1, pct(en - st))
        keep_segments_html.append(
            f'<div class="seg keep" style="left:{left:.2f}%; width:{width:.2f}%;" '
            f'title="Keep: {fmt_time(st)} - {fmt_time(en)} ({en-st:.2f}s)"></div>'
        )

    cut_segments_html = []
    top_cuts = []
    for idx, d in enumerate(deletes):
        st, en = float(d["start"]), float(d["end"])
        length = en - st
        reason = d.get("reason") or d.get("type") or "Cut"
        left = pct(st)
        width = max(0.2, pct(length))
        cut_segments_html.append(
            f'<div class="seg cut" style="left:{left:.2f}%; width:{width:.2f}%;" '
            f'data-start="{st:.2f}" data-len="{length:.2f}" '
            f'title="Cut #{idx+1}: {fmt_time(st)} - {fmt_time(en)} ({length:.2f}s) - {reason}"></div>'
        )
        top_cuts.append({"idx": idx + 1, "start": st, "end": en, "len": length, "reason": reason})

    # Sort top cuts by length
    top_cuts_sorted = sorted(top_cuts, key=lambda x: x["len"], reverse=True)

    table_rows = []
    for c in top_cuts_sorted[:25]:
        table_rows.append(
            f'<tr>'
            f'<td><span class="cut-num">#{c["idx"]}</span></td>'
            f'<td><button class="jump-btn" data-time="{c["start"]:.2f}">▶ {fmt_time(c["start"])}</button></td>'
            f'<td>{fmt_time(c["end"])}</td>'
            f'<td><strong class="cut-duration">-{c["len"]:.2f}s</strong></td>'
            f'<td><span class="cut-reason-tag">{c["reason"]}</span></td>'
            f'</tr>'
        )

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — Video Editor Pro</title>
  <style>
    :root {{
      --bg: #0b0f17;
      --card-bg: rgba(22, 27, 34, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --text: #f0f6fc;
      --text-muted: #8b949e;
      --emerald: #10b981;
      --crimson: #ef4444;
      --amber: #f59e0b;
      --cyan: #06b6d4;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
      padding: 24px;
      line-height: 1.5;
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }}
    .header-left h1 {{
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .header-left p {{
      color: var(--text-muted);
      font-size: 13px;
      margin-top: 4px;
    }}
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .stat-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      backdrop-filter: blur(10px);
    }}
    .stat-card span {{
      display: block;
      color: var(--text-muted);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }}
    .stat-card strong {{
      font-size: 24px;
      font-weight: 800;
      color: var(--text);
    }}
    .stat-card.emerald strong {{ color: var(--emerald); }}
    .stat-card.crimson strong {{ color: var(--crimson); }}
    .stat-card.cyan strong {{ color: var(--cyan); }}

    /* Timeline Scrubber Container */
    .timeline-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      margin-bottom: 24px;
    }}
    .timeline-title {{
      font-size: 14px;
      font-weight: 700;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .timeline-legend {{
      display: flex;
      gap: 16px;
      font-size: 12px;
      color: var(--text-muted);
    }}
    .legend-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .legend-box {{
      width: 12px;
      height: 12px;
      border-radius: 3px;
    }}
    .legend-box.keep {{ background: var(--emerald); }}
    .legend-box.cut {{ background: var(--crimson); }}

    .scrubber-track {{
      position: relative;
      height: 48px;
      background: #161b22;
      border-radius: 8px;
      overflow: hidden;
      cursor: pointer;
      border: 1px solid rgba(255,255,255,0.06);
    }}
    .seg {{
      position: absolute;
      top: 0;
      bottom: 0;
      transition: opacity 0.2s;
    }}
    .seg.keep {{
      background: var(--emerald);
      opacity: 0.85;
    }}
    .seg.cut {{
      background: var(--crimson);
      opacity: 0.95;
      z-index: 2;
    }}
    .seg.cut:hover {{
      opacity: 1;
      filter: brightness(1.3);
      cursor: pointer;
    }}
    .playhead {{
      position: absolute;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #fff;
      box-shadow: 0 0 8px rgba(255,255,255,0.8);
      z-index: 10;
      pointer-events: none;
      left: 0%;
    }}

    /* Media Comparison */
    .player-comparison {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }}
    .player-box {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }}
    .player-box h4 {{
      font-size: 13px;
      font-weight: 700;
      color: var(--text-muted);
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    video {{
      width: 100%;
      border-radius: 8px;
      background: #000;
      max-height: 380px;
    }}

    /* Cuts Table */
    .table-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
    }}
    .table-card h3 {{
      font-size: 15px;
      font-weight: 700;
      margin-bottom: 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }}
    th {{
      text-align: left;
      padding: 10px 14px;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
      font-weight: 600;
      font-size: 12px;
      text-transform: uppercase;
    }}
    td {{
      padding: 12px 14px;
      border-bottom: 1px solid rgba(255,255,255,0.04);
    }}
    tr:hover td {{
      background: rgba(255,255,255,0.02);
    }}
    .jump-btn {{
      background: rgba(6, 182, 212, 0.15);
      color: var(--cyan);
      border: 1px solid rgba(6, 182, 212, 0.3);
      padding: 4px 10px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 12px;
      font-weight: 600;
      transition: all 0.2s;
    }}
    .jump-btn:hover {{
      background: var(--cyan);
      color: #000;
    }}
    .cut-duration {{
      color: var(--crimson);
      font-weight: 700;
    }}
    .cut-reason-tag {{
      background: rgba(239, 68, 68, 0.15);
      color: #fca5a5;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
    }}
  </style>
</head>
<body>

  <div class="header">
    <div class="header-left">
      <h1>✂️ {title}</h1>
      <p>Precision Edit Decision List Visualizer & Audio-Video Cut Audit</p>
    </div>
    <div class="badge" style="background: rgba(16,185,129,0.15); color: var(--emerald); padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 12px; border: 1px solid rgba(16,185,129,0.3);">
      ✓ Review Ready
    </div>
  </div>

  <div class="stats-grid">
    <div class="stat-card">
      <span>Original Duration</span>
      <strong>{fmt_time(dur)}</strong>
    </div>
    <div class="stat-card emerald">
      <span>Tightened Duration</span>
      <strong>{fmt_time(edited_dur)}</strong>
    </div>
    <div class="stat-card crimson">
      <span>Dead Air & Mistakes Cut</span>
      <strong>-{removed:.2f}s</strong>
    </div>
    <div class="stat-card cyan">
      <span>Time Saved</span>
      <strong>{pct_saved}%</strong>
    </div>
    <div class="stat-card">
      <span>Cuts Count</span>
      <strong>{len(deletes)}</strong>
    </div>
  </div>

  <div class="timeline-card">
    <div class="timeline-title">
      <span>Multi-Track Cut Timeline (Click on any red cut to scrub)</span>
      <div class="timeline-legend">
        <div class="legend-item"><div class="legend-box keep"></div> Kept Spoken Content ({dur - removed:.1f}s)</div>
        <div class="legend-item"><div class="legend-box cut"></div> Removed Pauses & Mistakes ({removed:.1f}s)</div>
      </div>
    </div>
    <div class="scrubber-track" id="timeline-track">
      {''.join(keep_segments_html)}
      {''.join(cut_segments_html)}
      <div class="playhead" id="playhead"></div>
    </div>
  </div>

  {f'''<div class="player-comparison">
    <div class="player-box">
      <h4>Raw Source Video (Before Cuts)</h4>
      <video id="vid-raw" controls src="{original_video_url or ''}"></video>
    </div>
    <div class="player-box">
      <h4>Tightened Master Video (After Cuts)</h4>
      <video id="vid-tight" controls src="{edited_video_url or ''}"></video>
    </div>
  </div>''' if original_video_url or edited_video_url else ''}

  <div class="table-card">
    <h3>Top Cuts by Duration ({len(top_cuts_sorted)} Total)</h3>
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Cut Start Time</th>
          <th>Cut End Time</th>
          <th>Duration Saved</th>
          <th>Reason & Mistake Type</th>
        </tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
  </div>

  <script>
    const dur = {dur};
    const vidRaw = document.getElementById("vid-raw");
    const playhead = document.getElementById("playhead");
    const track = document.getElementById("timeline-track");

    // Click jump buttons
    document.querySelectorAll(".jump-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        const t = parseFloat(btn.dataset.time);
        if (vidRaw) {{
          vidRaw.currentTime = Math.max(0, t - 0.5);
          vidRaw.play();
        }}
        updatePlayhead(t);
      }});
    }});

    // Click cut rectangles
    document.querySelectorAll(".seg.cut").forEach(seg => {{
      seg.addEventListener("click", (e) => {{
        e.stopPropagation();
        const st = parseFloat(seg.dataset.start);
        if (vidRaw) {{
          vidRaw.currentTime = Math.max(0, st - 0.3);
          vidRaw.play();
        }}
        updatePlayhead(st);
      }});
    }});

    // Click on track
    if (track) {{
      track.addEventListener("click", (e) => {{
        const rect = track.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const frac = Math.max(0, Math.min(1, clickX / rect.width));
        const t = frac * dur;
        if (vidRaw) {{
          vidRaw.currentTime = t;
          vidRaw.play();
        }}
        updatePlayhead(t);
      }});
    }}

    function updatePlayhead(timeSec) {{
      if (playhead && dur > 0) {{
        const pctVal = (timeSec / dur) * 100;
        playhead.style.left = pctVal + "%";
      }}
    }}

    if (vidRaw) {{
      vidRaw.addEventListener("timeupdate", () => {{
        updatePlayhead(vidRaw.currentTime);
      }});
    }}
  </script>
</body>
</html>
"""
    return html_content


def build_edl_review(
    edl_path: str,
    output_html_path: Optional[str] = None,
    original_video_url: Optional[str] = None,
    edited_video_url: Optional[str] = None
) -> str:
    path = Path(edl_path).resolve()
    with open(path, "r", encoding="utf-8") as f:
        edl_data = json.load(f)

    title = f"EDL Cut Review — {path.stem.replace('_edl', '').replace('_', ' ').title()}"
    html = generate_edl_html(edl_data, original_video_url, edited_video_url, title)

    out_file = Path(output_html_path).resolve() if output_html_path else path.parent / f"{path.stem}_review.html"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[EDL Review OK] Generated interactive visual review: {out_file}")
    return str(out_file)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_edl_review.py <edl.json> [--output review.html] [--raw video.mp4] [--cut video.mp4]")
        sys.exit(1)
    
    edl_file = sys.argv[1]
    out_html = None
    raw_v = None
    cut_v = None
    
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            out_html = sys.argv[i + 1]
        elif sys.argv[i] == "--raw" and i + 1 < len(sys.argv):
            raw_v = sys.argv[i + 1]
        elif sys.argv[i] == "--cut" and i + 1 < len(sys.argv):
            cut_v = sys.argv[i + 1]

    build_edl_review(edl_file, out_html, raw_v, cut_v)
