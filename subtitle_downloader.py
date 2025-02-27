from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import logging
import os
import re
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SubtitleDownloader:
    def __init__(self, output_dir: str = "subtitles"):
        """Initialize the subtitle downloader with output directory"""
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def download_subtitle(self, video_url: str) -> Optional[str]:
        """Download subtitle for a given YouTube video URL"""
        if not video_url:
            logger.error("Received empty video URL")
            return None
            
        logger.info(f"Attempting to download subtitles for: {video_url}")
        try:
            # Extract video ID from URL
            video_id = self._extract_video_id(video_url)
            if not video_id:
                logger.error(f"Could not extract video ID from URL: {video_url}")
                return None
                
            logger.info(f"Video ID: {video_id}")
            
            # Get available transcript list
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                # Get available languages without accessing private attributes
                available_languages = []
                for transcript in transcript_list:
                    available_languages.append(transcript.language_code)
                logger.info(f"Available transcripts: {available_languages}")
            except (TranscriptsDisabled, NoTranscriptFound) as e:
                logger.info(f"No transcripts available for video: {video_id}. Error: {str(e)}")
                return None
                
            # Try to get English transcript
            transcript = None
            try:
                # First try to get manual English transcript
                transcript = transcript_list.find_transcript(['en'])
                logger.info("Found manual English transcript")
            except NoTranscriptFound:
                try:
                    # Then try to get auto-generated English transcript
                    transcript = transcript_list.find_transcript(['en-US', 'en-GB'])
                    logger.info("Found auto-generated English transcript")
                except NoTranscriptFound:
                    try:
                        # Try to get any transcript and translate it to English
                        transcript = transcript_list.find_transcript(['es', 'fr', 'de', 'it', 'pt'])
                        transcript = transcript.translate('en')
                        logger.info(f"Translated transcript from another language to English")
                    except (NoTranscriptFound, Exception) as e:
                        logger.info(f"Could not find or translate any transcript: {str(e)}")
                        return None
            
            if not transcript:
                logger.info("No English transcript found")
                return None
                
            # Fetch the transcript data
            transcript_data = transcript.fetch()
            logger.info(f"Successfully fetched transcript with {len(transcript_data)} entries")
            
            # Convert transcript to plain text
            text_content = self._convert_transcript_to_text(transcript_data)
            
            # Save to file
            txt_path = os.path.join(self.output_dir, f"{video_id}.en.txt")
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text_content)
                
            logger.info(f"Successfully saved transcript to: {txt_path}")
            return txt_path
                
        except Exception as e:
            logger.error(f"Error downloading subtitles for {video_url}: {e}")
            return None
            
    def _extract_video_id(self, video_url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        if not video_url:
            return None
            
        # Try different URL patterns
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard YouTube URL
            r'(?:embed\/)([0-9A-Za-z_-]{11})',  # Embed URL
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'  # Short URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
                
        return None
            
    def _convert_transcript_to_text(self, transcript_data: list) -> str:
        """Convert transcript data to plain text"""
        # Sort by start time to ensure correct order
        transcript_data.sort(key=lambda x: x['start'])
        
        # Extract text from each entry
        text_parts = []
        for entry in transcript_data:
            text = entry.get('text', '').strip()
            if text:
                text_parts.append(text)
                
        # Join all parts with proper spacing
        return ' '.join(text_parts)
        
    def get_subtitle_text(self, subtitle_path: str) -> str:
        """Read text content from subtitle file"""
        try:
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                return f.read()
            
        except Exception as e:
            logger.error(f"Error reading subtitle file {subtitle_path}: {e}")
            return ""

if __name__ == "__main__":
    # Example usage
    downloader = SubtitleDownloader()
    video_url = "https://www.youtube.com/watch?v=example"
    subtitle_path = downloader.download_subtitle(video_url)
    
    if subtitle_path:
        text = downloader.get_subtitle_text(subtitle_path)
        print(f"Subtitle text length: {len(text)} characters")
