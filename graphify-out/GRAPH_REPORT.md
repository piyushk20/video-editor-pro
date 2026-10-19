# Graph Report - .  (2026-10-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 143 nodes · 241 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a3563604`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- search_and_download_broll
- studio_server.py
- app.js
- phase4_editor.py
- remove_silences
- generate_chasing_money_graphics.py
- generate_debt_graphics.py
- phase1_analyser.py
- render_chasing_money_master.py
- render_master
- generate_motion_graphics.py
- phase2_director.py
- find_image
- run_pipeline.py

## God Nodes (most connected - your core abstractions)
1. `search_and_download_broll()` - 9 edges
2. `draw_rounded_card()` - 7 edges
3. `source_broll()` - 7 edges
4. `main()` - 7 edges
5. `download_broll_clip()` - 7 edges
6. `remove_silences()` - 7 edges
7. `get_fonts()` - 6 edges
8. `main()` - 6 edges
9. `get_font()` - 6 edges
10. `draw_card_base()` - 6 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `remove_silences()`  [EXTRACTED]
  agentic-video-studio/tools/phase0_input_handler.py → agentic-video-studio/tools/silence_remover.py
- `source_broll()` --calls--> `search_and_download_broll()`  [EXTRACTED]
  agentic-video-studio/tools/phase3_broll_sourcer.py → agentic-video-studio/tools/scrapling_broll_provider.py

## Import Cycles
- None detected.

## Communities (14 total, 1 thin omitted)

### Community 0 - "search_and_download_broll"
Cohesion: 0.19
Nodes (19): download_clip(), main(), Path, sanitise_filename(), search_pexels(), search_pixabay(), source_broll(), BrollClip (+11 more)

### Community 1 - "studio_server.py"
Cohesion: 0.13
Nodes (16): get_project_details(), get_projects(), open_explorer(), process_url(), List all completed projects in output/ directory., Return all deliverables, files, and scores for a specific project., Handle drag & drop file upload and start pipeline., Handle URL media ingestion and start pipeline. (+8 more)

### Community 2 - "app.js"
Cohesion: 0.26
Nodes (12): initExplorerButtons(), initLaunchButton(), loadProject(), loadProjectsList(), logTerminal(), onJobCompleted(), onJobFailed(), resetStepper() (+4 more)

### Community 3 - "phase4_editor.py"
Cohesion: 0.27
Nodes (13): consolidate_project_folder(), ffmpeg_run(), get_broll_timeline(), get_graphics_timeline(), load_manifest(), load_plan(), main(), Render highlight short clips directly from the fully composited master video. (+5 more)

### Community 4 - "remove_silences"
Cohesion: 0.24
Nodes (11): detect_input_type(), handle_local(), handle_url(), main(), detect_silences(), get_media_duration(), main(), Return total media duration in seconds via FFmpeg probe. (+3 more)

### Community 5 - "generate_chasing_money_graphics.py"
Cohesion: 0.53
Nodes (9): create_card_1_intro(), create_card_2_speakers(), create_card_3_myth(), create_card_4_behaviors(), create_card_5_outro(), draw_rounded_card(), get_fonts(), main() (+1 more)

### Community 6 - "generate_debt_graphics.py"
Cohesion: 0.64
Nodes (8): draw_card_base(), get_font(), main(), make_baby_steps_card(), make_intro_title(), make_lower_third(), make_outro_card(), make_rainy_day_card()

### Community 7 - "phase1_analyser.py"
Cohesion: 0.33
Nodes (8): analyse_content(), extract_audio(), load_manifest(), main(), Semantic analysis: filler words, key moments, chapter points, highlights., Extract audio from video for transcription., Word-level transcription with faster-whisper., transcribe()

### Community 8 - "render_chasing_money_master.py"
Cohesion: 0.52
Nodes (6): copy_project_assets(), main(), render_16x9_companion(), render_9x16_master(), render_highlight_shorts(), write_delivery_report()

### Community 9 - "render_master"
Cohesion: 0.57
Nodes (6): ensure_brolls(), ensure_motion_graphics(), main(), probe_video(), Path, render_master()

### Community 10 - "generate_motion_graphics.py"
Cohesion: 0.60
Nodes (5): draw_card_base(), generate_graphics(), get_font(), load_project_meta(), main()

### Community 11 - "phase2_director.py"
Cohesion: 0.70
Nodes (4): build_edit_plan(), load_analysis(), load_transcript(), main()

### Community 12 - "find_image"
Cohesion: 0.67
Nodes (3): find_image(), main(), Path

## Knowledge Gaps
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Should `studio_server.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1286549707602339 - nodes in this community are weakly interconnected._