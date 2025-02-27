// Chart objects
let viewsChart = null;
let uploadTimelineChart = null;
let durationChart = null;
let engagementChart = null;

// Store the video data globally for filtering and sorting
let globalVideoData = [];

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('analyzeForm');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    const error = document.getElementById('error');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Get form values
        const channelUrl = document.getElementById('channelUrl').value;
        const monthsBack = document.getElementById('monthsBack').value;
        
        // Show loading, hide results and error
        loading.style.display = 'block';
        results.style.display = 'none';
        error.style.display = 'none';
        
        try {
            // Make API request
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    channel_url: channelUrl,
                    months_back: monthsBack
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'An error occurred during analysis');
            }
            
            // Fetch the full analysis data from the JSON file
            const analysisResponse = await fetch(`/static/results/${data.json_file}`);
            const analysisData = await analysisResponse.json();
            
            // Update basic stats
            document.getElementById('videoCount').textContent = data.video_count;
            document.getElementById('subtitleCount').textContent = data.subtitle_count;
            document.getElementById('ideasText').textContent = data.ideas;
            
            // Calculate and display total views
            const totalViews = calculateTotalViews(analysisData.video_data);
            document.getElementById('totalViews').textContent = formatNumber(totalViews);
            
            // Update download links
            document.getElementById('csvDownload').href = `/static/results/${data.csv_file}`;
            document.getElementById('jsonDownload').href = `/static/results/${data.json_file}`;
            
            // Store video data globally
            globalVideoData = analysisData.video_data;
            
            // Populate video table
            populateVideoTable(globalVideoData);
            
            // Create charts
            createViewsChart(globalVideoData);
            createUploadTimelineChart(globalVideoData);
            createDurationChart(globalVideoData);
            createEngagementChart(globalVideoData);
            
            // Show results
            results.style.display = 'block';
            
        } catch (err) {
            // Show error message
            error.textContent = err.message;
            error.style.display = 'block';
        } finally {
            // Hide loading spinner
            loading.style.display = 'none';
        }
    });
    
    // Set up event listeners for filtering and sorting
    document.getElementById('videoSearch').addEventListener('input', function() {
        filterAndSortVideos();
    });
    
    document.getElementById('videoSort').addEventListener('change', function() {
        filterAndSortVideos();
    });
    
    // Set up event listeners for advanced features
    document.getElementById('contentAnalysisBtn').addEventListener('click', function() {
        alert('Content pattern analysis feature coming soon!');
    });
    
    document.getElementById('compareChannelBtn').addEventListener('click', function() {
        const compareUrl = document.getElementById('compareChannelUrl').value;
        if (compareUrl) {
            alert(`Channel comparison with ${compareUrl} feature coming soon!`);
        } else {
            alert('Please enter a channel URL to compare with.');
        }
    });
    
    document.getElementById('exportPdfBtn').addEventListener('click', function() {
        alert('PDF export feature coming soon!');
    });
    
    // Input validation
    const channelUrlInput = document.getElementById('channelUrl');
    channelUrlInput.addEventListener('input', function() {
        const url = this.value.trim();
        const isValid = url.match(/^https:\/\/(www\.)?youtube\.com\/@[\w-]+$/);
        
        if (url && !isValid) {
            this.setCustomValidity('Please enter a valid YouTube channel URL (e.g., https://www.youtube.com/@channelname)');
        } else {
            this.setCustomValidity('');
        }
    });
});

// Helper function to format numbers
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// Calculate total views from video data
function calculateTotalViews(videoData) {
    return videoData.reduce((total, video) => {
        // Parse the views string (e.g., "1.3m", "215k") to a number
        const viewsStr = video.views || "0";
        let multiplier = 1;
        
        if (viewsStr.toLowerCase().includes('k')) {
            multiplier = 1000;
        } else if (viewsStr.toLowerCase().includes('m')) {
            multiplier = 1000000;
        }
        
        // Extract the numeric part and multiply
        const numericPart = parseFloat(viewsStr.replace(/[^0-9.]/g, ''));
        const views = isNaN(numericPart) ? 0 : numericPart * multiplier;
        
        return total + views;
    }, 0);
}

// Filter and sort videos based on search input and sort selection
function filterAndSortVideos() {
    const searchTerm = document.getElementById('videoSearch').value.toLowerCase();
    const sortOption = document.getElementById('videoSort').value;
    
    // Filter videos based on search term
    let filteredVideos = globalVideoData.filter(video => 
        video.title.toLowerCase().includes(searchTerm)
    );
    
    // Sort videos based on selected option
    switch(sortOption) {
        case 'views-desc':
            filteredVideos.sort((a, b) => parseViewsString(b.views) - parseViewsString(a.views));
            break;
        case 'views-asc':
            filteredVideos.sort((a, b) => parseViewsString(a.views) - parseViewsString(b.views));
            break;
        case 'date-desc':
            filteredVideos.sort((a, b) => compareDates(b.upload_date, a.upload_date));
            break;
        case 'date-asc':
            filteredVideos.sort((a, b) => compareDates(a.upload_date, b.upload_date));
            break;
        case 'duration-desc':
            filteredVideos.sort((a, b) => parseDuration(b.duration) - parseDuration(a.duration));
            break;
        case 'duration-asc':
            filteredVideos.sort((a, b) => parseDuration(a.duration) - parseDuration(b.duration));
            break;
    }
    
    // Update the table with filtered and sorted videos
    populateVideoTable(filteredVideos);
}

// Helper function to parse views string to number for sorting
function parseViewsString(viewsStr) {
    if (!viewsStr) return 0;
    
    let multiplier = 1;
    if (viewsStr.toLowerCase().includes('k')) {
        multiplier = 1000;
    } else if (viewsStr.toLowerCase().includes('m')) {
        multiplier = 1000000;
    }
    
    const numericPart = parseFloat(viewsStr.replace(/[^0-9.]/g, ''));
    return isNaN(numericPart) ? 0 : numericPart * multiplier;
}

// Helper function to compare dates for sorting
function compareDates(dateA, dateB) {
    // Convert relative dates to a numeric value for comparison
    function dateToValue(dateStr) {
        if (!dateStr) return 0;
        
        const now = new Date();
        
        if (dateStr.includes('day')) {
            const days = parseInt(dateStr);
            return now - (days * 24 * 60 * 60 * 1000);
        } else if (dateStr.includes('week')) {
            const weeks = parseInt(dateStr);
            return now - (weeks * 7 * 24 * 60 * 60 * 1000);
        } else if (dateStr.includes('month')) {
            const months = parseInt(dateStr);
            return now - (months * 30 * 24 * 60 * 60 * 1000);
        } else if (dateStr.includes('year')) {
            const years = parseInt(dateStr);
            return now - (years * 365 * 24 * 60 * 60 * 1000);
        }
        
        return 0;
    }
    
    return dateToValue(dateA) - dateToValue(dateB);
}

// Helper function to parse duration string to seconds for sorting
function parseDuration(durationStr) {
    if (!durationStr) return 0;
    
    const parts = durationStr.split(':');
    if (parts.length === 2) {
        // MM:SS format
        return parseInt(parts[0]) * 60 + parseInt(parts[1]);
    } else if (parts.length === 3) {
        // HH:MM:SS format
        return parseInt(parts[0]) * 3600 + parseInt(parts[1]) * 60 + parseInt(parts[2]);
    }
    
    return 0;
}

// Populate video table with data
function populateVideoTable(videoData) {
    const tableBody = document.getElementById('videoTable');
    tableBody.innerHTML = '';
    
    videoData.forEach(video => {
        const row = document.createElement('tr');
        
        // Thumbnail cell
        const thumbnailCell = document.createElement('td');
        const thumbnail = document.createElement('img');
        thumbnail.src = video.thumbnail_url || '';
        thumbnail.alt = video.title;
        thumbnail.style.width = '120px';
        thumbnail.style.borderRadius = '8px';
        thumbnailCell.appendChild(thumbnail);
        
        // Title cell
        const titleCell = document.createElement('td');
        titleCell.textContent = video.title;
        titleCell.style.fontWeight = '500';
        
        // Views cell
        const viewsCell = document.createElement('td');
        viewsCell.textContent = video.views || '0';
        
        // Duration cell
        const durationCell = document.createElement('td');
        durationCell.textContent = video.duration || 'Unknown';
        
        // Upload date cell
        const dateCell = document.createElement('td');
        dateCell.textContent = video.upload_date || 'Unknown';
        
        // Append cells to row
        row.appendChild(thumbnailCell);
        row.appendChild(titleCell);
        row.appendChild(viewsCell);
        row.appendChild(durationCell);
        row.appendChild(dateCell);
        
        // Append row to table
        tableBody.appendChild(row);
    });
}

// Create views chart
function createViewsChart(videoData) {
    // Destroy existing chart if it exists
    if (viewsChart) {
        viewsChart.destroy();
    }
    
    const ctx = document.getElementById('viewsChart').getContext('2d');
    
    // Prepare data
    const labels = videoData.map(video => {
        // Truncate long titles
        const title = video.title;
        return title.length > 20 ? title.substring(0, 20) + '...' : title;
    });
    
    // Parse views from the views string instead of using views_count
    const viewsData = videoData.map(video => {
        // Parse the views string (e.g., "1.3m", "215k") to a number
        const viewsStr = video.views || "0";
        let multiplier = 1;
        
        if (viewsStr.toLowerCase().includes('k')) {
            multiplier = 1000;
        } else if (viewsStr.toLowerCase().includes('m')) {
            multiplier = 1000000;
        }
        
        // Extract the numeric part and multiply
        const numericPart = parseFloat(viewsStr.replace(/[^0-9.]/g, ''));
        return isNaN(numericPart) ? 0 : numericPart * multiplier;
    });
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, '#03C0C1');
    gradient.addColorStop(1, '#007F80');
    
    viewsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Views',
                data: viewsData,
                backgroundColor: gradient,
                borderColor: '#009C9D',
                borderWidth: 1,
                borderRadius: 5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Video Views Comparison',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#007F80'
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatNumber(context.raw) + ' views';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// Create upload timeline chart
function createUploadTimelineChart(videoData) {
    // Destroy existing chart if it exists
    if (uploadTimelineChart) {
        uploadTimelineChart.destroy();
    }
    
    const ctx = document.getElementById('uploadTimelineChart').getContext('2d');
    
    // Process data to group by upload time
    const uploadGroups = {};
    
    videoData.forEach(video => {
        const uploadDate = video.upload_date || 'Unknown';
        if (!uploadGroups[uploadDate]) {
            uploadGroups[uploadDate] = 0;
        }
        uploadGroups[uploadDate]++;
    });
    
    const labels = Object.keys(uploadGroups);
    const counts = Object.values(uploadGroups);
    
    // Create gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(3, 253, 252, 0.8)');
    gradient.addColorStop(1, 'rgba(0, 127, 128, 0.2)');
    
    uploadTimelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Videos',
                data: counts,
                backgroundColor: gradient,
                borderColor: '#00D8D8',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#007F80',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Upload Timeline',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#007F80'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Create duration chart
function createDurationChart(videoData) {
    // Destroy existing chart if it exists
    if (durationChart) {
        durationChart.destroy();
    }
    
    const ctx = document.getElementById('durationChart').getContext('2d');
    
    // Process data to categorize durations
    const durationCategories = {
        'Short (< 10 min)': 0,
        'Medium (10-20 min)': 0,
        'Long (> 20 min)': 0
    };
    
    videoData.forEach(video => {
        const duration = parseDuration(video.duration);
        
        if (duration < 600) { // Less than 10 minutes
            durationCategories['Short (< 10 min)']++;
        } else if (duration < 1200) { // 10-20 minutes
            durationCategories['Medium (10-20 min)']++;
        } else { // More than 20 minutes
            durationCategories['Long (> 20 min)']++;
        }
    });
    
    const labels = Object.keys(durationCategories);
    const data = Object.values(durationCategories);
    
    // Create chart
    durationChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#03FDFC',
                    '#00D8D8',
                    '#007F80'
                ],
                borderColor: '#fff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Video Duration Distribution',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#007F80'
                },
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${context.label}: ${value} videos (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Create engagement chart (views per video duration)
function createEngagementChart(videoData) {
    // Destroy existing chart if it exists
    if (engagementChart) {
        engagementChart.destroy();
    }
    
    const ctx = document.getElementById('engagementChart').getContext('2d');
    
    // Calculate engagement (views per minute) for each video
    const engagementData = videoData.map(video => {
        const views = parseViewsString(video.views);
        const duration = parseDuration(video.duration) / 60; // Convert to minutes
        
        // Avoid division by zero
        const engagement = duration > 0 ? views / duration : 0;
        
        return {
            title: video.title,
            engagement: engagement,
            views: views,
            duration: duration
        };
    });
    
    // Sort by engagement and take top 5
    const topEngagement = engagementData
        .sort((a, b) => b.engagement - a.engagement)
        .slice(0, 5);
    
    // Create chart
    engagementChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topEngagement.map(item => {
                const title = item.title;
                return title.length > 20 ? title.substring(0, 20) + '...' : title;
            }),
            datasets: [{
                label: 'Views per Minute',
                data: topEngagement.map(item => Math.round(item.engagement)),
                backgroundColor: '#009C9D',
                borderColor: '#007F80',
                borderWidth: 1,
                borderRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top Engaging Videos (Views per Minute)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#007F80'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const item = topEngagement[index];
                            return [
                                `Views per Minute: ${formatNumber(item.engagement)}`,
                                `Total Views: ${formatNumber(item.views)}`,
                                `Duration: ${Math.round(item.duration)} minutes`
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Views per Minute'
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}
