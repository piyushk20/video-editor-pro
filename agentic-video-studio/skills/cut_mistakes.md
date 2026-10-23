# Cut Mistakes & Repeats (Herk Style)

Autonomous transcript-driven mistake cutter:
- Scans word-level timestamps for immediate word repeats and stutters.
- Uses Jaccard similarity across speech segments to identify re-recorded lines (retakes) and keep only the best clean take.
- Retimes word-level transcripts for subsequent B-roll, motion graphics, and subtitle synchronization.
- Generates interactive visual EDL (Edit Decision List) review dashboards.
