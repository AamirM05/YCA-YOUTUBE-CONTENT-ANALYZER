import openai
import pandas as pd
import json
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IdeaGenerator:
    def __init__(self, api_key: str, max_videos: int = 3, subtitle_chars: int = 1000):
        """
        Initialize OpenAI client with API key
        
        Args:
            api_key: OpenAI API key
            max_videos: Maximum number of videos to include subtitles for
            subtitle_chars: Maximum number of characters to include from each subtitle
        """
        openai.api_key = api_key
        self.max_videos = max_videos
        self.subtitle_chars = subtitle_chars
        
    def analyze_video_data(self, videos_data: List[Dict], subtitles_data: Dict[str, str]) -> str:
        """
        Analyze video data and subtitles to generate content ideas
        
        Args:
            videos_data: List of video metadata dictionaries
            subtitles_data: Dictionary mapping video URLs to subtitle text
        """
        try:
            # Log received data
            logger.info(f"Analyzing {len(videos_data)} videos")
            logger.info(f"Have subtitles for {len(subtitles_data)} videos")
            
            # Log video titles and their subtitle availability
            for video in videos_data:
                has_subtitles = video['url'] in subtitles_data
                logger.info(f"Video: {video['title']}")
                logger.info(f"  URL: {video['url']}")
                logger.info(f"  Views: {video['views']}")
                logger.info(f"  Has subtitles: {has_subtitles}")
                if has_subtitles:
                    subtitle_length = len(subtitles_data[video['url']])
                    logger.info(f"  Subtitle length: {subtitle_length} chars")
            
            # Prepare data for GPT analysis
            analysis_prompt = self._prepare_analysis_prompt(videos_data, subtitles_data)
            
            # Log the prompt before sending to GPT
            logger.info("\nSending prompt to GPT:\n%s", analysis_prompt)
            
            # Get response from GPT-4
            response = openai.ChatCompletion.create(
                model="chatgpt-4o-latest",
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ]
            )
            
            # Log the response
            response_content = response.choices[0].message['content']
            logger.info("\nGPT Response:\n%s", response_content)
            
            # Log token usage
            tokens_used = response.usage.total_tokens
            logger.info(f"Total tokens used: {tokens_used}")
            
            return response_content
            
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            return "Error generating ideas"
            
    def _prepare_analysis_prompt(self, videos_data: List[Dict], subtitles_data: Dict[str, str]) -> str:
        """Prepare prompt for GPT analysis"""
        # Convert views to numeric format
        for video in videos_data:
            views_str = video['views'].lower().replace('k', '000').replace('m', '000000')
            views_str = ''.join(filter(str.isdigit, views_str))
            video['views_count'] = int(views_str) if views_str else 0
            
        # Sort videos by views
        sorted_videos = sorted(videos_data, key=lambda x: x['views_count'], reverse=True)
        
        # Prepare video performance summary
        video_summary = "\n".join([
            f"Title: {v['title']}\n"
            f"Views: {v['views']}\n"
            f"Duration: {v['duration']}\n"
            f"Upload Date: {v['upload_date']}\n"
            f"Has Subtitles: {'Yes' if v['url'] in subtitles_data else 'No'}\n"
            for v in sorted_videos
        ])
        
        # Add subtitle analysis for top performing videos
        subtitle_analysis = ""
        videos_with_subtitles = 0
        
        for video in sorted_videos:
            if videos_with_subtitles >= self.max_videos:
                break
                
            if video['url'] in subtitles_data:
                subtitle_text = subtitles_data[video['url']]
                subtitle_analysis += f"\nSubtitle content for '{video['title']}':\n"
                
                # Include specified amount of subtitle text
                if len(subtitle_text) > self.subtitle_chars:
                    subtitle_analysis += f"{subtitle_text[:self.subtitle_chars]}...\n"
                else:
                    subtitle_analysis += f"{subtitle_text}\n"
                    
                videos_with_subtitles += 1
                
        logger.info(f"Including subtitles for {videos_with_subtitles} videos")
        
        prompt = f"""
        Analyze this YouTube channel's content performance and generate strategic content ideas.

        Video Performance Data:
        {video_summary}

        Key Content Analysis from Top Performing Videos:
        {subtitle_analysis}

        Based on this data, please provide:
        1. Top performing content patterns and themes
        2. Analysis of what makes the successful videos work
        3. 5 specific content ideas that could perform well
        4. Suggested video titles, descriptions, and key points to cover
        5. Strategic recommendations for video duration and upload timing

        Focus on actionable insights and specific ideas that build on proven success patterns.
        """
        
        return prompt

if __name__ == "__main__":
    # Example usage
    api_key = "your-api-key"
    generator = IdeaGenerator(api_key)
    
    # Example data
    videos_data = [
        {
            "title": "Example Video",
            "views": "100K",
            "duration": "10:00",
            "upload_date": "1 month ago",
            "url": "https://youtube.com/watch?v=example"
        }
    ]
    
    subtitles_data = {
        "https://youtube.com/watch?v=example": "Example subtitle text..."
    }
    
    ideas = generator.analyze_video_data(videos_data, subtitles_data)
    print(ideas)
