# YCA-YOUTUBE-CONTENT-ANALYZER

![Project Banner](https://raw.githubusercontent.com/AamirM05/YCA-YOUTUBE-CONTENT-ANALYZER/refs/heads/main/IMAGES/screencapture-127-0-0-1-5000-2025-02-26-23_56_39.png)

A powerful data engineering tool that extracts, transforms, and analyzes YouTube channel data to generate content insights, visualize trends, and provide strategic recommendations for content creators. This project implements a complete ETL (Extract, Transform, Load) pipeline for YouTube content analysis.

## 🚀 Features

- **Channel Analysis**: Analyze any YouTube channel by URL
- **Content Insights**: AI-powered content ideas generation based on channel performance
- **Data Visualization**: Interactive charts and graphs to visualize channel performance
- **Video Metrics**: Detailed metrics for each video including views, duration, and upload date
- **Filtering & Sorting**: Advanced filtering and sorting options for video data
- **Export Options**: Download analysis results in multiple formats

## 📋 Table of Contents

- [Installation](#-installation)
- [Usage](#-usage)
- [UI Components](#-ui-components)
- [Data Engineering Aspects](#-data-engineering-aspects)
- [Upcoming Features](#-upcoming-features)
- [Technical Details](#-technical-details)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-channel-analyzer.git
cd youtube-channel-analyzer
```

2. Install the required dependencies:
```bash
python install_requirements.py
```

3. Set up your environment variables in `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to:
```
http://localhost:5000
```

## 🎮 Usage

1. Enter a YouTube channel URL in the format `https://www.youtube.com/@channelname`
2. Select the time period to analyze (1-12 months)
3. Click "Analyze Channel" and wait for the analysis to complete
4. Explore the generated insights, charts, and data visualizations
5. Use filtering and sorting options to find specific videos
6. Download the analysis results in your preferred format

## 🖥️ UI Components

### Input Form

![Input Form](https://raw.githubusercontent.com/AamirM05/YCA-YOUTUBE-CONTENT-ANALYZER/refs/heads/main/IMAGES/1.png)

The input form allows you to specify:
- **Channel URL**: The YouTube channel to analyze (must be in the format `https://www.youtube.com/@channelname`)
- **Time Period**: How far back to analyze videos (1, 2, 3, 6, or 12 months)

### Stats Cards
The stats cards provide a quick overview of the analysis results:
- **Videos Analyzed**: Total number of videos analyzed in the selected time period
- **Videos with Subtitles**: Number of videos that have subtitles available
- **Total Views**: Cumulative views across all analyzed videos

### Charts and Visualizations

![Charts](https://raw.githubusercontent.com/AamirM05/YCA-YOUTUBE-CONTENT-ANALYZER/refs/heads/main/IMAGES/Screenshot%202025-02-26%20235318.png)

The application provides multiple interactive charts:

1. **Video Views Comparison**: Bar chart showing views for each video
2. **Upload Timeline**: Line chart showing video upload frequency over time
3. **Video Duration Distribution**: Pie chart categorizing videos by duration (short, medium, long)
4. **Top Engaging Videos**: Bar chart showing the most engaging videos based on views per minute

### Content Ideas

![Content Ideas](https://raw.githubusercontent.com/AamirM05/YCA-YOUTUBE-CONTENT-ANALYZER/refs/heads/main/IMAGES/Screenshot%202025-02-26%20235401.png)

The AI-powered content ideas section provides:
- Analysis of top-performing content patterns and themes
- Explanation of what makes successful videos work
- Specific content ideas based on channel performance
- Suggested video titles, descriptions, and key points
- Strategic recommendations for video duration and upload timing

### Video List with Filtering

![Video List](https://raw.githubusercontent.com/AamirM05/YCA-YOUTUBE-CONTENT-ANALYZER/refs/heads/main/IMAGES/Screenshot%202025-02-26%20235453.png)

The video list displays all analyzed videos with:
- Thumbnail image
- Video title
- View count
- Video duration
- Upload date

**Filtering and Sorting Options**:
- Search videos by title
- Sort by views (high to low or low to high)
- Sort by date (newest first or oldest first)
- Sort by duration (longest first or shortest first)

### Advanced Features

![Advanced Features](https://raw.githubusercontent.com/AamirM05/YCA-YOUTUBE-CONTENT-ANALYZER/refs/heads/main/IMAGES/bottom.png)

The advanced features section includes:
- **Content Analysis**: Deeper analysis of content patterns and success factors
- **Channel Comparison**: Compare the analyzed channel with another YouTube channel

### Download Options
The download section allows you to export analysis results in multiple formats:
- **CSV**: Download video data in CSV format
- **JSON**: Download complete analysis results in JSON format
- **PDF**: Export a comprehensive report in PDF format

## 💾 Data Engineering Aspects

This project incorporates several key data engineering components:

### Data Extraction (Ingestion)
- **Web Scraping**: Custom YouTube scraper to extract channel and video metadata
- **Subtitle Extraction**: Specialized component using youtube-transcript-api for downloading and processing video subtitles
- **ETL Process**: Complete Extract, Transform, Load pipeline for YouTube data

### Data Processing (Transformation)
- **Data Cleaning**: Processing raw YouTube data into structured formats
- **Metric Calculation**: Computing engagement metrics, view rates, and performance indicators
- **AI-Powered Enrichment**: Using OpenAI to transform raw content data into actionable insights

### Data Storage & Management
- **Structured Storage**: Organized storage of processed data in CSV and JSON formats
- **Results Management**: Timestamped analysis results for historical comparison
- **Data Versioning**: Maintaining multiple analysis runs with consistent naming conventions

### Data Visualization (Pipeline Output)
- **Interactive Dashboards**: Dynamic charts and visualizations of processed data
- **Metric Comparison**: Visual tools for comparing performance across videos
- **Trend Analysis**: Timeline and distribution visualizations for pattern recognition

![Data Pipeline](https://raw.githubusercontent.com/AamirM05/YCA-YOUTUBE-CONTENT-ANALYZER/refs/heads/main/IMAGES/Screenshot%20(46)%20(1)%20(2)%20(1).png)

## 🔮 Upcoming Features

The following features are currently in development and will be available soon:

1. **Content Pattern Analysis**: Advanced AI analysis of content patterns that drive engagement
2. **Channel Comparison**: Compare metrics between multiple YouTube channels
3. **PDF Export**: Generate comprehensive PDF reports of the analysis
4. **Keyword Analysis**: Identify trending keywords and topics in your niche
5. **Audience Demographics**: Analyze viewer demographics and preferences
6. **Thumbnail Analysis**: AI-powered analysis of thumbnail effectiveness
7. **Scheduling Recommendations**: Optimal posting schedule based on audience activity
8. **Competitor Analysis**: Analyze and compare with competitor channels

## 🔧 Technical Details

This application is built using:

- **Backend**: Python with Flask for API endpoints and data processing
- **ETL Pipeline**: Custom extraction, transformation, and loading processes
- **Frontend**: HTML, CSS, JavaScript for the user interface
- **Data Visualization**: Chart.js for interactive data visualizations
- **AI Integration**: OpenAI API for advanced content analysis and insights generation
- **YouTube Data**: Custom scraping solution for metadata extraction
- **Subtitle Extraction**: youtube-transcript-api for reliable subtitle downloading
- **Styling**: Bootstrap 5 with custom CSS for responsive design
- **Icons**: Font Awesome for UI elements

The application follows a modular architecture with the following components:

- `app.py`: Main Flask application and API endpoints
- `youtube_scraper.py`: ETL component for YouTube channel and video data extraction
- `subtitle_downloader.py`: Specialized ETL component for subtitle processing using youtube-transcript-api
- `idea_generator.py`: AI-powered data transformation and insights generation
- `static/js/main.js`: Frontend data processing and visualization logic
- `static/css/style.css`: Custom styling for the data dashboard
- `templates/index.html`: Main application template and visualization container
- `static/results/`: Data storage for processed analysis results

## 🚀 Future Enhancements

Based on data engineering best practices, the following enhancements could further strengthen the project:

### Database Integration
- Implement a proper database (PostgreSQL, MongoDB, or BigQuery) instead of file-based storage
- Create data models and schemas for efficient querying and analysis
- Implement data versioning and historical tracking

### Pipeline Automation
- Integrate Apache Airflow for workflow orchestration and scheduling
- Create DAGs (Directed Acyclic Graphs) for automated data processing
- Implement error handling and retry mechanisms

### Scalability Improvements
- Implement a queue system like Kafka for handling multiple channel processing
- Add distributed processing capabilities for large-scale data analysis
- Implement caching mechanisms for frequently accessed data

### Monitoring and Logging
- Add comprehensive logging throughout the data pipeline
- Implement monitoring for pipeline health and performance
- Create alerting for pipeline failures or data quality issues

Created with ❤️ by [MOHAMMAD AAMIR]
