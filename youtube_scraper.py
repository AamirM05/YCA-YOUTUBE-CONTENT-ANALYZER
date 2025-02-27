from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeScraper:
    def __init__(self):
        self.setup_driver()
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # New headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
        chrome_options.add_argument("--window-size=1920,1080")  # Set window size
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            # Try using ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.error(f"Error with ChromeDriverManager: {e}")
            try:
                # Fallback to direct Chrome instantiation
                self.driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                logger.error(f"Error creating Chrome driver: {e}")
                raise
        
    def get_channel_videos(self, channel_url, months_back=2):
        """Scrape videos from a channel for the specified number of months"""
        try:
            # Handle channel URL formatting
            if not channel_url.endswith('/videos'):
                videos_url = f"{channel_url.rstrip('/')}/videos"
            else:
                videos_url = channel_url
                
            logger.info(f"Accessing channel videos at: {videos_url}")
            self.driver.get(videos_url)
            
            # Wait for content to load and log page title
            time.sleep(5)
            logger.info(f"Page title: {self.driver.title}")
            
            # Calculate the date threshold
            threshold_date = datetime.now() - timedelta(days=30 * months_back)
            
            videos_data = []
            last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            
            while True:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                time.sleep(2)
                
                # Get video elements
                video_elements = self.driver.find_elements(By.TAG_NAME, "ytd-rich-grid-media")
                
                for element in video_elements:
                    try:
                        video_data = self._extract_video_data(element)
                        if video_data:
                            upload_date = self._parse_upload_date(video_data['upload_date'])
                            if upload_date < threshold_date:
                                return videos_data
                            videos_data.append(video_data)
                    except Exception as e:
                        logger.error(f"Error extracting video data: {e}")
                
                # Check if we've reached the end
                new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            return videos_data
            
        except Exception as e:
            logger.error(f"Error scraping channel videos: {e}")
            return []
            
    def _extract_video_data(self, video_element):
        """Extract metadata from a video element"""
        try:
            # Get video title and URL
            try:
                # First try to find the video URL from any anchor tag
                links = video_element.find_elements(By.TAG_NAME, "a")
                video_url = None
                title_element = None
                
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/watch?v=" in href:
                        video_url = href
                        title_element = link
                        break
                
                if not video_url or not title_element:
                    logger.error("Could not find video URL")
                    return None
                
                if video_url:
                    # Convert relative URL to absolute URL if needed
                    if not video_url.startswith('http'):
                        video_url = f"https://www.youtube.com{video_url}"
                    
                # Try multiple methods to get the video title
                video_title = None
                
                # Method 1: Try aria-label attribute which often contains the full title
                aria_label = title_element.get_attribute("aria-label")
                if aria_label:
                    # Extract title from aria-label (usually in format "Title by Channel X views Y ago Duration")
                    title_parts = aria_label.split(" by ")
                    if title_parts:
                        video_title = title_parts[0]
                
                # Method 2: Try title attribute
                if not video_title:
                    video_title = title_element.get_attribute("title")
                
                # Method 3: Try finding specific title elements
                if not video_title:
                    title_spans = video_element.find_elements(By.CSS_SELECTOR, "#video-title, #video-title-link")
                    for span in title_spans:
                        title = span.get_attribute("title") or span.text
                        if title and not title.isdigit() and ':' not in title:
                            video_title = title
                            break
                
                # Clean up the title
                if video_title:
                    video_title = video_title.strip()
                
                if not video_title:
                    logger.error("Could not find video title")
                    return None
                logger.info(f"Found video: {video_title} - {video_url}")
            except Exception as e:
                logger.error(f"Error extracting video URL: {e}")
                return None
            
            # Get video metadata (views, upload date)
            metadata = video_element.find_element(By.ID, "metadata-line")
            metadata_items = metadata.find_elements(By.CLASS_NAME, "inline-metadata-item")
            
            views = "0"
            upload_date = "Unknown"
            
            for item in metadata_items:
                text = item.text.lower()
                if "views" in text:
                    views = text.replace("views", "").strip()
                elif "ago" in text:
                    upload_date = text
                    
            # Get video duration
            try:
                # Try multiple methods to get duration
                duration = ""
                
                # Method 1: Try badge-shape text
                try:
                    duration_element = video_element.find_element(
                        By.CSS_SELECTOR, 
                        ".badge-shape-wiz--thumbnail-badge .badge-shape-wiz__text"
                    )
                    duration = duration_element.text.strip()
                except:
                    pass
                
                # Method 2: Try time status renderer
                if not duration:
                    try:
                        duration_element = video_element.find_element(
                            By.CSS_SELECTOR,
                            "ytd-thumbnail-overlay-time-status-renderer"
                        )
                        duration = duration_element.text.strip()
                    except:
                        pass
                
                # Method 3: Try aria-label
                if not duration:
                    try:
                        duration_element = video_element.find_element(
                            By.CSS_SELECTOR,
                            "[aria-label*='minutes'], [aria-label*='seconds']"
                        )
                        aria_label = duration_element.get_attribute("aria-label")
                        if aria_label:
                            duration = aria_label.split(" ", 1)[0].strip()
                    except:
                        pass
                            
            except Exception as e:
                logger.error(f"Error extracting duration: {e}")
                duration = ""
            
            # Get thumbnail URL
            thumbnail = video_element.find_element(By.TAG_NAME, "img")
            thumbnail_url = thumbnail.get_attribute("src")
            
            return {
                "title": video_title,
                "url": video_url,
                "views": views,
                "upload_date": upload_date,
                "duration": duration,
                "thumbnail_url": thumbnail_url
            }
            
        except Exception as e:
            logger.error(f"Error extracting video data: {e}")
            return None
            
    def _parse_upload_date(self, date_str):
        """Convert relative date string to datetime object"""
        try:
            number = int(''.join(filter(str.isdigit, date_str)))
            if "year" in date_str:
                return datetime.now() - timedelta(days=number * 365)
            elif "month" in date_str:
                return datetime.now() - timedelta(days=number * 30)
            elif "week" in date_str:
                return datetime.now() - timedelta(weeks=number)
            elif "day" in date_str:
                return datetime.now() - timedelta(days=number)
            elif "hour" in date_str:
                return datetime.now() - timedelta(hours=number)
            else:
                return datetime.now()
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return datetime.now()
            
    def close(self):
        """Close the WebDriver"""
        self.driver.quit()

if __name__ == "__main__":
    # Example usage
    scraper = YouTubeScraper()
    channel_url = "https://www.youtube.com/@example"
    videos = scraper.get_channel_videos(channel_url, months_back=2)
    
    # Convert to DataFrame and save
    if videos:
        df = pd.DataFrame(videos)
        df.to_csv("youtube_data.csv", index=False)
        print(f"Saved {len(videos)} videos to youtube_data.csv")
    
    scraper.close()
