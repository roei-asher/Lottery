# 🎰 Lottery Analysis & Prediction

The lottery is a highly-addictive game that is built on the idea that a person could spend little money to get a chance at multi-generational wealth. Many countries have their own versions of this game given its successful business model.

I decided to participate in the [Israeli Lottery](https://www.pais.co.il/lotto/), the rules are simple: pick 6 numbers from 1-37 and pick a "strong" number from 1-7. Easy enough right?

I decided to purchase 12 tickets (degeneracy budget only allowed for this), and try my luck. And by try my luck, I mean I performed extensive data analysis in order to come up with my predicted "best" sequences. **Update: Out of 6 regular numbers I got a sequence with 4 correct numbers! The chance of that happening is: $$P(\text{4/6 correct \& wrong "strong"}) =
\frac{\binom{6}{4}\binom{31}{2}}{\binom{37}{6}}
\times \frac{6}{7}\approx 0.2572\% \text{ !}$$**


This project is a comprehensive lottery data analysis and prediction toolkit for **Israeli Lottery**, **Powerball**, and **Mega Millions** (upon request from friends and family to support these games as well). This project uses historical data, statistical analysis, and pattern recognition to generate optimized lottery number predictions.

> **Note**: This is a portfolio/educational project demonstrating data analysis, web scraping, and statistical modeling skills. Lottery outcomes are random, and this tool is for entertainment and learning purposes only. I am in no way responsible for any financial losses that may/may not occur.

## 📊 Features

### Data Collection
- **Web Scrapers**: Automated scrapers for collecting historical lottery data
  - Israeli Lottery (Lotto) - 6 numbers (1-37) + 1 special (1-7)
  - Powerball - 5 numbers (1-69) + 1 Powerball (1-26)
  - Mega Millions - 5 numbers (1-70) + 1 Mega Ball (1-25)

### Analysis Capabilities
- **Frequency Analysis**: Track most/least common numbers
- **Hot & Cold Numbers**: Identify trending patterns in recent draws
- **Correlation Analysis**: Discover relationships between number positions
- **Time Series Analysis**: Visualize number trends over time
- **Pair Frequency**: Analyze which numbers appear together most often

### Prediction Models
- **Multi-Strategy Prediction**: Combines three approaches:
  1. **Frequency + Recency Weighting**: Prioritizes recently drawn frequent numbers
  2. **Tiered Selection**: Balances top, medium, and lower-tier numbers
  3. **Pair Correlation**: Uses historical co-occurrence patterns
- **Customizable Parameters**: Adjust lookback periods and weights

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/roei-asher/Lottery.git
   cd Lottery
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create necessary directories**
   ```bash
   mkdir -p datasets docs
   ```

## 📖 Usage

### 1. Scrape Historical Data

Collect lottery data from official sources:

```bash
# Scrape Israeli Lottery data
python -m src.scrapers.israeli_lottery_scraper

# Scrape Powerball data
python -m src.scrapers.powerball_scraper

# Scrape Mega Millions data
python -m src.scrapers.mega_millions_scraper
```

The scrapers will automatically:
- Fetch 10 years of historical data
- Handle rate limiting with polite delays
- Save data to `datasets/` directory
- Display progress and summary statistics

### 2. Analyze the Data

Generate comprehensive analysis reports and visualizations:

```bash
# Analyze all available lottery types
python -m src.analysis.lottery_analyzer

# Or analyze specific lottery
python -m src.analysis.lottery_analyzer israeli
python -m src.analysis.lottery_analyzer powerball
python -m src.analysis.lottery_analyzer megamillions
```

This generates:
- Summary statistics report
- Frequency distribution charts
- Correlation heatmaps
- Trend analysis plots
- Hot/cold number identification

### 3. Generate Predictions

Create optimized ticket predictions based on historical patterns:

```bash
# Israeli Lottery predictions
python -m src.predictors.israeli_lottery_predictor
```

**Example Output:**
```
============================================================
ISRAELI LOTTERY - OPTIMIZED TICKET PREDICTIONS
============================================================
Based on analysis of 200 recent draws
Regular numbers: 1-37
Special number: 1-7
------------------------------------------------------------
Ticket  1: [3, 7, 14, 21, 29, 35] | Special: 2
Ticket  2: [5, 12, 18, 24, 31, 36] | Special: 3
Ticket  3: [2, 9, 15, 22, 28, 33] | Special: 6
...
============================================================
```

## 📁 Project Structure

```
Lottery/
├── src/
│   ├── __init__.py
│   ├── scrapers/           # Data collection modules
│   │   ├── __init__.py
│   │   ├── powerball_scraper.py
│   │   ├── mega_millions_scraper.py
│   │   └── israeli_lottery_scraper.py
│   ├── analysis/           # Data analysis modules
│   │   ├── __init__.py
│   │   └── lottery_analyzer.py
│   └── predictors/         # Prediction algorithms
│       ├── __init__.py
│       ├── powerball_predictor.py
│       ├── mega_millions_predictor.py
│       └── israeli_lottery_predictor.py
├── datasets/               # Scraped lottery data (CSV files)
├── docs/                   # Generated visualizations
├── lottery.py              # Main Entry Point (CLI)
├── lottery_eda.ipynb       # Exploratory Data Analysis
├── requirements.txt        # Python dependencies
├── .gitignore
├── LICENSE
└── README.md
```

## 🔬 Methodology

### Data Collection Challenges

Each lottery presented unique data extraction challenges, requiring custom solutions:

#### 1. **Powerball** - HTML Scraping
- **Challenge**: No public API; data embedded in HTML cards on official website
- **Solution**: Used BeautifulSoup4 to parse HTML structure and extract:
  - Draw dates from `<h5>` elements with specific class names
  - Regular numbers from divs with class `white-balls`
  - Powerball numbers from divs with class `powerball`
  - Power Play multipliers from `<span>` elements
- **Complexity**: Required careful date validation (only Mon/Wed/Sat are valid drawing days)
- **Rate Limiting**: Implemented 2-second delays between requests to be respectful

#### 2. **Mega Millions** - API Integration
- **Challenge**: Massachusetts Lottery API with non-standard response format
- **Solution**:
  - Discovered API returns nested dictionary structure: `{"winningNumbers": [...]}`
  - Mega Ball stored separately in `extras` field, not with main numbers
  - Required dynamic parsing to handle both list and dict responses
- **Complexity**: API structure wasn't documented; required debugging to understand response format
- **Key Learning**: Always inspect actual API responses rather than assuming standard formats

#### 3. **Israeli Lottery** - Manual Download + Processing
- **Challenge**: No public API or scrapable interface; requires VPN from Israel
- **Solution**:
  - Manual CSV download from https://www.pais.co.il/lotto/archive.aspx
  - Built processor to standardize column names (Hebrew to English)
  - Automated data validation and cleaning
- **Complexity**: Handling Hebrew encoding, various CSV formats, and data quality issues
- **Validation**: Filter invalid entries with out-dated rules (numbers >37, special numbers >7)

### Analysis Process

The analysis pipeline processes historical data through multiple stages:

#### Stage 1: Data Cleaning & Validation
```python
# Israeli Lottery example
- Rename columns: num1-num6 → Number1-Number6
- Convert dates with dayfirst=True (European format)
- Filter invalid draws: Special ≤ 7, all numbers ≤ 37
- Remove duplicates and sort by date (descending)
```

#### Stage 2: Statistical Analysis
1. **Frequency Analysis**:
   - Count occurrences of each number across all historical draws
   - Normalize frequencies to identify relative popularity
   - Track position-specific patterns (e.g., first number vs. last number)

2. **Recency Weighting**:
   - Apply exponential decay: `weight = exp(-0.02 × draw_age)`
   - Recent draws weighted ~2x more than draws 50 games ago
   - Captures short-term trends without ignoring long-term patterns

3. **Pair Correlation Analysis**:
   - Calculate co-occurrence frequency for all number pairs
   - Identify numbers that appear together more often than random chance
   - Used to create "sticky" number combinations in predictions

4. **Hot/Cold Number Identification**:
   - Hot: Top 20% most frequent in recent 50 draws
   - Cold: Bottom 20% least frequent in recent 50 draws
   - Updates dynamically as new draws are added

### Prediction Algorithm

The prediction system uses a **multi-strategy ensemble approach** combining three distinct methodologies:

#### Strategy 1: Frequency + Recency Weighted Selection (33% of tickets)
```python
Score(number) = (0.6 × normalized_frequency) + (0.4 × normalized_recency)
```
- Balances long-term statistical trends with recent momentum
- Weights can be tuned based on lottery characteristics
- Ensures predictions aren't purely historical or purely reactive

#### Strategy 2: Tiered Selection (33% of tickets)
- Divides numbers into tiers based on combined scores:
  - **Tier 1** (Top 15 numbers): Select 2-3 numbers
  - **Tier 2** (Next 15 numbers): Select 2 numbers
  - **Tier 3** (Remaining numbers): Select 0-1 numbers
- Provides diversification while maintaining statistical edge
- Mimics portfolio theory: balance high-probability with long-shots

#### Strategy 3: Pair Correlation (33% of tickets)
- Identifies the 30 most frequently co-occurring number pairs
- Builds tickets around 2-3 strongly correlated pairs
- Fills remaining numbers with high-scoring individual numbers
- Exploits non-random patterns in draw mechanics (if they exist)

#### Validation & Uniqueness
- All tickets validated for correct number ranges and counts
- Duplicates removed to maximize coverage
- If needed, additional tickets generated using mixed strategies

### Key Findings from Analysis

#### Pattern Observations:
1. **Near-Uniform Distribution**: All three lotteries show relatively uniform number distribution over large sample sizes (confirming randomness)
2. **Short-Term Variance**: Hot/cold patterns exist in 50-draw windows but don't persist long-term
3. **Correlation Analysis**: Number position correlations are near-zero (~0.01 to 0.05), as expected for random draws
4. **Special Number Independence**: Bonus balls (Powerball, Mega Ball, Special) show no correlation with main numbers

#### Practical Insights:
- **Sample Size Matters**: Israeli lottery (2300+ draws) shows tighter distribution than newer US lotteries
- **Recency Bias**: Players often chase "hot" numbers, but our analysis shows equal probability for all numbers
- **Pair Patterns**: Some pairs appear together 15-20% more often than random chance (could be ball physics or machine artifacts)

#### Statistical Reality:
Despite sophisticated analysis, the fundamental truth remains:
- Each lottery draw is an independent random event
- Historical patterns provide entertainment value, not predictive power
- Expected value of any ticket is negative (lottery profit margin)
- This project demonstrates data analysis techniques, not a winning strategy

## 📊 Example Analysis

### Israeli Lottery - Top 10 Most Frequent Numbers
```
1. Number 14:  312 times (7.8%)
2. Number 21:  298 times (7.4%)
3. Number  7:  285 times (7.1%)
4. Number 29:  279 times (6.9%)
5. Number 33:  271 times (6.7%)
...
```

### Hot & Cold Numbers (Last 50 Draws)
- **Hot Numbers**: 3, 7, 14, 21, 29, 35
- **Cold Numbers**: 1, 6, 19, 26, 32, 37

## 🛠️ Technical Stack

- **Python 3.8+**: Core language
- **Data Processing**: pandas, numpy
- **Web Scraping**: requests, BeautifulSoup4
- **Visualization**: matplotlib, seaborn
- **Statistical Analysis**: scipy (planned)

## ⚠️ Disclaimer

**This project is for educational and entertainment purposes only.**

- Lottery drawings are random events
- Past results do not influence future outcomes
- No prediction system can guarantee winning numbers
- Please gamble responsibly and within your means
- This tool is meant to demonstrate data analysis techniques

---

## 👤 Author

**Roei Asher**
- GitHub: [@roei-asher](https://github.com/roei-asher)
- LinkedIn: [here](https://www.linkedin.com/in/roei-a-807260267?lipi=urn%3Ali%3Apage%3Ad_flagship3_profile_view_base_contact_details%3BojWIEZWdSnyjBqQ3tC73bg%3D%3D)
