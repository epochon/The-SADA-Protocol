"""
YouTube Transcript Fetcher Service
Extracts transcripts from YouTube videos for analysis
"""

import re
from typing import Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable
)
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

# Import centralized config and cache
from app.core.config import settings
from app.core.cache import transcript_cache


def extract_video_id(url: str) -> Optional[str]:
    """
    Extract YouTube video ID from various URL formats.
    Supports: youtube.com/watch?v=, youtu.be/, youtube.com/embed/
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'(?:youtube\.com\/watch\?.*v=)([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def fetch_transcript(video_url: str) -> Dict[str, Any]:
    """
    Fetch transcript from a YouTube video with caching and timeout.
    
    Args:
        video_url: Full YouTube URL
        
    Returns:
        dict: {
            "status": "success" | "error",
            "video_id": str,
            "transcript": str (full text),
            "segments": list (timestamped segments),
            "language": str,
            "error": str (if failed)
        }
    """
    video_id = extract_video_id(video_url)
    
    if not video_id:
        return {
            "status": "error",
            "video_id": None,
            "transcript": None,
            "error": "Invalid YouTube URL. Could not extract video ID."
        }
    
    # Check cache first
    cache_key = f"transcript:{video_id}"
    cached = transcript_cache.get(cache_key)
    if cached:
        print(f"📦 Transcript Cache HIT for {video_id}")
        return cached
    
    # Fetch with timeout protection
    def _fetch_inner():
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Priority: Manual English > Auto-generated English > Any translated
        transcript = None
        language = "en"
        
        try:
            # Try manual English first
            transcript = transcript_list.find_transcript(['en'])
        except NoTranscriptFound:
            try:
                # Try auto-generated English
                transcript = transcript_list.find_generated_transcript(['en'])
            except NoTranscriptFound:
                # Get any available and translate to English
                for t in transcript_list:
                    transcript = t.translate('en')
                    language = f"{t.language_code} -> en (translated)"
                    break
        
        if transcript is None:
            return {
                "status": "error",
                "video_id": video_id,
                "transcript": None,
                "error": "No transcript available for this video."
            }
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        # Combine all segments into full text
        full_text = " ".join([segment['text'] for segment in transcript_data])
        
        return {
            "status": "success",
            "video_id": video_id,
            "transcript": full_text,
            "segments": transcript_data,  # Contains timestamp info
            "language": language,
            "word_count": len(full_text.split())
        }
    
    # Execute with timeout
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_fetch_inner)
            result = future.result(timeout=settings.youtube_timeout)
            
            # Cache successful results
            if result.get("status") == "success":
                transcript_cache.set(cache_key, result)
                print(f"🔄 Transcript Cache MISS for {video_id} - fetched fresh")
            
            return result
            
    except FuturesTimeoutError:
        return {
            "status": "error",
            "video_id": video_id,
            "transcript": None,
            "error": f"Timeout: YouTube transcript fetch exceeded {settings.youtube_timeout}s"
        }
    except TranscriptsDisabled:
        return {
            "status": "error",
            "video_id": video_id,
            "transcript": None,
            "error": "Transcripts are disabled for this video."
        }
    except VideoUnavailable:
        return {
            "status": "error",
            "video_id": video_id,
            "transcript": None,
            "error": "Video is unavailable or private."
        }
    except Exception as e:
        return {
            "status": "error",
            "video_id": video_id,
            "transcript": None,
            "error": f"Failed to fetch transcript: {str(e)}"
        }

