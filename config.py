"""
Configuration settings for the Lottery Analysis toolkit
"""

from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).parent
DATASETS_DIR = BASE_DIR / "datasets"
DOCS_DIR = BASE_DIR / "docs"
EXAMPLES_DIR = BASE_DIR / "examples"

# Ensure directories exist
DATASETS_DIR.mkdir(exist_ok=True)
DOCS_DIR.mkdir(exist_ok=True)
EXAMPLES_DIR.mkdir(exist_ok=True)

# Israeli Lottery Configuration
ISRAELI_LOTTERY = {
    "name": "Israeli Lottery (Lotto)",
    "regular_numbers": {
        "min": 1,
        "max": 37,
        "count": 6
    },
    "special_number": {
        "min": 1,
        "max": 7,
        "count": 1
    },
    "data_file": DATASETS_DIR / "cleaned_israeli_lottery_data.csv",
    "drawing_days": [1, 4]  # Tuesday, Friday
}

# Powerball Configuration
POWERBALL = {
    "name": "Powerball",
    "regular_numbers": {
        "min": 1,
        "max": 69,
        "count": 5
    },
    "special_number": {
        "min": 1,
        "max": 26,
        "count": 1,
        "name": "Powerball"
    },
    "data_file": DATASETS_DIR / "powerball_lottery_data.csv",
    "drawing_days": [0, 2, 5],  # Monday, Wednesday, Saturday
    "url": "https://www.powerball.com/previous-results"
}

# Mega Millions Configuration
MEGA_MILLIONS = {
    "name": "Mega Millions",
    "regular_numbers": {
        "min": 1,
        "max": 70,
        "count": 5
    },
    "special_number": {
        "min": 1,
        "max": 25,
        "count": 1,
        "name": "Mega Ball"
    },
    "data_file": DATASETS_DIR / "mega_millions_lottery_data.csv",
    "drawing_days": [1, 4],  # Tuesday, Friday
    "api_url": "https://www.masslottery.com/api/v1/draw-results/mega_millions"
}

# Scraper Configuration
SCRAPER_CONFIG = {
    "default_years": 10,
    "interval_weeks": 10,
    "request_delay": 2,  # seconds between requests
    "timeout": 30,  # request timeout in seconds
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    "lookback_draws": 200,  # number of recent draws to analyze
    "frequency_weight": 0.6,  # weight for frequency in scoring (0-1)
    "recency_weight": 0.4,  # weight for recency in scoring (0-1)
    "hot_cold_threshold": 0.2,  # top/bottom 20% for hot/cold classification
    "rolling_window": 20,  # window size for trend analysis
    "figure_dpi": 300  # DPI for saved figures
}

# Prediction Configuration
PREDICTION_CONFIG = {
    "default_tickets": 12,  # default number of tickets to generate
    "frequency_decay": 0.02,  # exponential decay factor for regular numbers
    "special_decay": 0.03,  # exponential decay factor for special numbers
    "random_seed": None  # set to integer for reproducible results
}

# Visualization Configuration
VIZ_CONFIG = {
    "style": "seaborn-v0_8-darkgrid",
    "color_palette": "husl",
    "figure_size": (15, 7),
    "font_size": 10,
    "title_size": 14
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S"
}
