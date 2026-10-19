#!/usr/bin/env python3
"""
Agentic Video Studio ? Scrapling B-Roll Provider
Autonomous, zero-API-key scraper for copyright-free stock footage using Scrapling.
Sources high-definition vertical (9:16) and horizontal (16:9) clips from Pexels & Coverr.
"""

import os
import sys
import re
import json
import argparse
import subprocess
from pathlib import Path
from urllib.parse import quote
from dataclasses import dataclass, asdict
import requests

try:
    from scrapling import Fetcher, StealthyFetcher
    SCRAPLING_AVAILABLE = True
except ImportError:
    SCRAPLING_AVAILABLE = False

try:
    import imageio_ffmpeg
    FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_BIN = "ffmpeg"


@dataclass
class BrollClip:
    id: str
    title: str
    query: str
    source: str
    page_url: str
    download_url: str
    thumbnail_url: str
    orientation: str
    license: str
    local_path: str = ""
    resolution: str = ""
    duration: float = 0.0


def sanitise_slug(name: str) -> str:
    cleaned = re.sub(r'[^\w\-_\.]', '_', name)
    return re.sub(r'_+', '_', cleaned).strip('_')[:60]


def probe_video(video_path: str) -> dict:
    """Probe video file for resolution and duration using ffmpeg/ffprobe."""
    info = {"resolution": "unknown", "duration": 0.0}
    try:
        # Run ffmpeg -i to parse duration and resolution from stderr
        cmd = [FFMPEG_BIN, "-i", video_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        err = res.stderr

        # Extract duration: Duration: 00:00:15.24
        dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", err)
        if dur_match:
            h, m, s = float(dur_match.group(1)), float(dur_match.group(2)), float(dur_match.group(3))
            info["duration"] = round(h * 3600 + m * 60 + s, 2)

        # Extract resolution: Stream #0:0: Video: ... 1080x1920 or 2160x3840
        res_match = re.search(r"Stream.*Video:.*?(\d{3,4})x(\d{3,4})", err)
        if res_match:
            info["resolution"] = f"{res_match.group(1)}x{res_match.group(2)}"
    except Exception as e:
        print(f"  [Probe Warning] Could not probe video: {e}")
    return info


def search_pexels_scrapling(query: str, orientation: str = "portrait", limit: int = 3, exclude_ids: set | None = None) -> list[BrollClip]:
    """
    Search Pexels Videos using Scrapling without requiring an API key.
    orientation: 'portrait' (9:16 vertical), 'landscape' (16:9), or None (all)
    exclude_ids: set of video IDs to exclude (ensuring visual diversity across slots)
    """
    if not SCRAPLING_AVAILABLE:
        print("  [Scrapling] Scrapling library not installed. Run 'pip install scrapling'")
        return []

    if exclude_ids is None:
        exclude_ids = set()

    encoded_query = quote(query)
    url = f"https://www.pexels.com/search/videos/{encoded_query}/"
    if orientation in ["portrait", "landscape"]:
        url += f"?orientation={orientation}"

    print(f"  [Scrapling] Fetching Pexels videos: {url}")
    try:
        response = Fetcher.get(url, timeout=15)
    except Exception as e:
        print(f"  [Scrapling Fetcher Error] Retrying with StealthyFetcher: {e}")
        try:
            response = StealthyFetcher.fetch(url, headless=True)
        except Exception as e2:
            print(f"  [Scrapling Error] Could not fetch Pexels: {e2}")
            return []

    if response.status != 200:
        print(f"  [Scrapling Warning] HTTP {response.status} from Pexels")
        return []

    clips = []
    seen_ids = set(exclude_ids)

    # Pexels embeds video articles with detail links and direct download links
    articles = response.css("article")
    for article in articles:
        a_tags = article.css("a")
        page_url = ""
        download_url = ""
        vid_id = ""
        title = ""

        for a in a_tags:
            href = a.attrib.get("href", "")
            if not href:
                continue
            # Detail page: /video/slug-name-12345/
            m_page = re.search(r"/video/([^/]+)-(\d+)/", href)
            if m_page:
                title = m_page.group(1).replace("-", " ").title()
                vid_id = m_page.group(2)
                page_url = f"https://www.pexels.com{href}"

            # Download link: https://www.pexels.com/download/video/12345/
            m_dl = re.search(r"/download/video/(\d+)/", href)
            if m_dl:
                vid_id = m_dl.group(1)
                download_url = f"https://www.pexels.com/download/video/{vid_id}/"

        if not vid_id:
            # Fallback regex search on article HTML
            m_id = re.search(r"/download/video/(\d+)/", article.text or "")
            if m_id:
                vid_id = m_id.group(1)
                download_url = f"https://www.pexels.com/download/video/{vid_id}/"

        if vid_id and vid_id not in seen_ids:
            seen_ids.add(vid_id)
            if not download_url:
                download_url = f"https://www.pexels.com/download/video/{vid_id}/"
            if not page_url:
                page_url = f"https://www.pexels.com/video/{vid_id}/"
            if not title:
                title = f"Pexels Video {vid_id}"

            # Extract thumbnail
            img = article.css("img")
            thumb_url = img[0].attrib.get("src", "") if img else ""

            clip = BrollClip(
                id=vid_id,
                title=title,
                query=query,
                source="pexels",
                page_url=page_url,
                download_url=download_url,
                thumbnail_url=thumb_url,
                orientation=orientation,
                license="Pexels License (100% Free for commercial use, no attribution required)"
            )
            clips.append(clip)
            if len(clips) >= limit:
                break

    print(f"  [Scrapling] Found {len(clips)} matching clips on Pexels")
    return clips


def download_broll_clip(clip: BrollClip, dest_dir: Path, filename_prefix: str = "") -> str | None:
    """Download the actual MP4 file via stream and probe its metadata."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    slug = sanitise_slug(f"{filename_prefix}_{clip.source}_{clip.id}_{clip.title}")
    out_file = dest_dir / f"{slug}.mp4"

    if out_file.exists() and out_file.stat().st_size > 500000:
        print(f"  [Cache HIT] Already downloaded: {out_file.name}")
        info = probe_video(str(out_file))
        clip.local_path = str(out_file)
        clip.resolution = info["resolution"]
        clip.duration = info["duration"]
        return str(out_file)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://www.pexels.com/"
    }

    print(f"  [Downloading] {clip.title} ({clip.source} #{clip.id})...")
    try:
        with requests.get(clip.download_url, stream=True, headers=headers, timeout=60, allow_redirects=True) as r:
            r.raise_for_status()
            content_length = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(out_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 512):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

        if out_file.exists() and out_file.stat().st_size > 50000:
            info = probe_video(str(out_file))
            clip.local_path = str(out_file)
            clip.resolution = info["resolution"]
            clip.duration = info["duration"]
            size_mb = round(out_file.stat().st_size / (1024 * 1024), 2)
            print(f"  [OK] Saved: {out_file.name} ({size_mb} MB, {clip.resolution}, {clip.duration}s)")
            return str(out_file)
        else:
            print(f"  [Error] Downloaded file was too small or empty.")
            return None
    except Exception as e:
        print(f"  [Error] Failed to download clip: {e}")
        return None


def search_and_download_broll(
    query: str,
    dest_dir: Path,
    orientation: str = "portrait",
    limit: int = 1,
    prefix: str = "broll",
    exclude_ids: set | None = None
) -> list[BrollClip]:
    """High-level function: search, download best match, and return populated BrollClip list."""
    clips = search_pexels_scrapling(query, orientation=orientation, limit=limit, exclude_ids=exclude_ids)
    downloaded_clips = []

    for i, clip in enumerate(clips):
        filename_prefix = f"{prefix}_{i+1:02d}"
        local_path = download_broll_clip(clip, dest_dir, filename_prefix=filename_prefix)
        if local_path:
            downloaded_clips.append(clip)

    return downloaded_clips


def main():
    parser = argparse.ArgumentParser(description="Scrapling Autonomous B-Roll Downloader")
    parser.add_argument("--query", "-q", required=True, help="Search query (e.g., 'money counting', 'credit card')")
    parser.add_argument("--orientation", "-o", default="portrait", choices=["portrait", "landscape", "all"], help="Video orientation")
    parser.add_argument("--limit", "-l", type=int, default=2, help="Number of clips to download")
    parser.add_argument("--dest", "-d", default="assets/broll/test_downloads", help="Destination directory")
    args = parser.parse_args()

    orientation = None if args.orientation == "all" else args.orientation
    dest_path = Path(args.dest)

    print(f"\n============================================================")
    print(f"  Agentic Video Studio ? Scrapling B-Roll Provider")
    print(f"  Query       : {args.query}")
    print(f"  Orientation : {args.orientation} ({'9:16 Vertical' if args.orientation == 'portrait' else '16:9 Landscape'})")
    print(f"  Limit       : {args.limit}")
    print(f"  Destination : {dest_path.resolve()}")
    print(f"============================================================\n")

    clips = search_and_download_broll(
        query=args.query,
        dest_dir=dest_path,
        orientation=orientation,
        limit=args.limit,
        prefix=sanitise_slug(args.query)
    )

    print(f"\n[Summary] Successfully sourced and verified {len(clips)} clip(s):")
    for c in clips:
        print(f" - {c.title}: {c.local_path} ({c.resolution}, {c.duration}s)")
        print(f"   License: {c.license}")
        print(f"   Source : {c.page_url}\n")


if __name__ == "__main__":
    main()
