from flask import Flask, render_template, request, jsonify
from youtube_scraper import YouTubeScraper
from subtitle_downloader import SubtitleDownloader
from idea_generator import IdeaGenerator
import pandas as pd
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize components
OPENAI_API_KEY = ""
# Configure to include all videos and full subtitle text
MAX_VIDEOS_WITH_SUBTITLES = 100  # Set high to include all videos
SUBTITLE_CHARS_PER_VIDEO = 1000000  # Set high to include full subtitle text
idea_generator = IdeaGenerator(OPENAI_API_KEY, max_videos=MAX_VIDEOS_WITH_SUBTITLES, subtitle_chars=SUBTITLE_CHARS_PER_VIDEO)
subtitle_downloader = SubtitleDownloader()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_channel():
    try:
        data = request.get_json()
        channel_url = data.get('channel_url')
        months_back = int(data.get('months_back', 2))
        
        logger.info(f"Analyzing channel: {channel_url} for past {months_back} months")
        
        if not channel_url:
            logger.error("Channel URL is missing")
            return jsonify({'error': 'Channel URL is required'}), 400
            
        # Initialize scraper and get videos
        logger.info("Starting video scraping...")
        scraper = YouTubeScraper()
        videos = scraper.get_channel_videos(channel_url, months_back)
        scraper.close()
        logger.info(f"Found {len(videos)} videos")
        
        if not videos:
            logger.error("No videos found for the channel")
            return jsonify({'error': 'No videos found'}), 404
            
        # Download subtitles for videos
        logger.info("Starting subtitle downloads...")
        subtitles_data = {}
        for i, video in enumerate(videos, 1):
            logger.info(f"Processing video {i}/{len(videos)}: {video['title']}")
            subtitle_path = subtitle_downloader.download_subtitle(video['url'])
            if subtitle_path:
                subtitle_text = subtitle_downloader.get_subtitle_text(subtitle_path)
                subtitles_data[video['url']] = subtitle_text
                logger.info(f"Successfully downloaded subtitles for video {i}")
            else:
                logger.warning(f"No subtitles found for video {i}")
                
        # Generate content ideas
        logger.info("Generating content ideas...")
        ideas = idea_generator.analyze_video_data(videos, subtitles_data)
        
        # Save analysis results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = {
            'channel_url': channel_url,
            'analysis_date': timestamp,
            'videos_analyzed': len(videos),
            'videos_with_subtitles': len(subtitles_data),
            'video_data': videos,
            'generated_ideas': ideas
        }
        
        # Save to CSV for video data
        logger.info("Saving results to files...")
        df = pd.DataFrame(videos)
        csv_path = f'static/results/videos_{timestamp}.csv'
        df.to_csv(csv_path, index=False)
        logger.info(f"Saved video data to {csv_path}")
        
        # Save complete results to JSON
        json_path = f'static/results/analysis_{timestamp}.json'
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved analysis results to {json_path}")
            
        return jsonify({
            'success': True,
            'video_count': len(videos),
            'subtitle_count': len(subtitles_data),
            'ideas': ideas,
            'csv_file': f'videos_{timestamp}.csv',
            'json_file': f'analysis_{timestamp}.json'
        })
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create results directory if it doesn't exist
    os.makedirs('static/results', exist_ok=True)
    app.run(debug=True)
