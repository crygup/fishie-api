import secrets
from typing import Any, Dict

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from yt_dlp import YoutubeDL

from .vars import SOUNDCLOUD_RE, TIKTOK_RE, VIDEOS_RE

ytdl = APIRouter(prefix="/ytdl")


def match_filter(info: Dict[Any, Any]):
    if info.get("live_status", None) == "is_live":
        raise HTTPException(
            status_code=401, detail="Live videos are blacklisted from being downloaded."
        )


@ytdl.get("/download")
def disp(url: str, audio: bool = False, format: str = "mp4"):
    name = secrets.token_urlsafe(8)
    video_match = VIDEOS_RE.search(url)

    if video_match is None or video_match and video_match.group(0) == "":
        raise HTTPException(
            status_code=401,
            detail={
                "error": "Unaccepted website. TikTok, Twitch, Instagram, YouTube, Reddit and Soundcloud are only accepted right now."
            },
        )

    video = video_match.group(0)

    options = {
        "outtmpl": rf"u\{name}.%(ext)s",
        "quiet": True,
        "max_filesize": 100_000_000,
        "match_filter": match_filter,
    }

    if TIKTOK_RE.search(video):
        options["format_sort"] = ["vcodec:h264"]

    if SOUNDCLOUD_RE.search(video) or audio:
        format = "mp3"

    if audio:
        options["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": format,
                "preferredquality": "192",
            }
        ]
        options["format"] = "bestaudio/best"
    else:
        options["format"] = f"bestvideo+bestaudio[ext={format}]/best"

    with YoutubeDL(options) as ydl:
        try:
            ydl.download(video)
        except ValueError as e:
            return {"error": str(e)}

    return FileResponse(rf"u\{name}.{format}")


@ytdl.get("/info")
def get_info(url: str):
    with YoutubeDL() as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                return {"error": "Could not extract info."}
            return info
        except ValueError as e:
            return {"error": str(e)}
