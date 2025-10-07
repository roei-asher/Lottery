"""
Mega Millions Lottery Data Scraper

This module fetches historical Mega Millions lottery data from the Massachusetts Lottery API.
Mega Millions draws 5 regular numbers (1-70) and 1 Mega Ball number (1-25).
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MegaMillionsScraper:
    """
    Scraper for fetching Mega Millions lottery historical data.

    Uses the Massachusetts Lottery API which provides comprehensive Mega Millions data.
    Drawings occur on Tuesday and Friday.
    """

    API_URL = "https://www.masslottery.com/api/v1/draw-results/mega_millions"
    DRAWING_DAYS = [1, 4]  # Tuesday, Friday
    DEFAULT_YEARS = 10
    DEFAULT_INTERVAL_WEEKS = 10

    def __init__(self, output_dir: str = "datasets"):
        """
        Initialize the Mega Millions scraper.

        Args:
            output_dir: Directory to save the scraped data
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self._setup_session()

    def _setup_session(self) -> None:
        """Configure the requests session with appropriate headers."""
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                         "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.masslottery.com/tools/past-results/mega-millions",
            "Origin": "https://www.masslottery.com",
        })

    def fetch_data(self, start_date: str, end_date: str) -> List[List]:
        """
        Fetch Mega Millions data for a specific date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of draw results, each containing [date, num1-5, megaball, jackpot, multiplier]
        """
        params = {"draw_date_min": start_date, "draw_date_max": end_date}

        try:
            logger.info(f"Fetching data from {start_date} to {end_date}")
            response = self.session.get(self.API_URL, params=params, timeout=30)

            logger.debug(f"Status Code: {response.status_code}")

            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: Failed to fetch data")
                return []

            try:
                data = response.json()
                logger.debug(f"Response type: {type(data)}, keys/length: {list(data.keys()) if isinstance(data, dict) else len(data)}")

                # Handle both list and dictionary responses
                if isinstance(data, dict):
                    # If it's a dict, look for common keys that contain the draw data
                    if 'draws' in data:
                        data = data['draws']
                    elif 'results' in data:
                        data = data['results']
                    elif 'data' in data:
                        data = data['data']
                    elif 'winningNumbers' in data:
                        # The winningNumbers field might contain the list of draws
                        winning_numbers = data['winningNumbers']
                        logger.debug(f"winningNumbers type: {type(winning_numbers)}")
                        if isinstance(winning_numbers, list):
                            data = winning_numbers
                        else:
                            # Single draw result wrapped in a dict
                            data = [data]
                    else:
                        logger.error(f"Unexpected dict format. Keys: {list(data.keys())}")
                        logger.debug(f"Response preview: {str(response.text)[:500]}")
                        return []

                if not isinstance(data, list):
                    logger.error(f"Unexpected data format. Expected list, got {type(data)}")
                    logger.debug(f"Response preview: {str(response.text)[:500]}")
                    return []

                results = []
                for draw in data:
                    try:
                        draw_result = self._parse_draw(draw)
                        if draw_result:
                            results.append(draw_result)
                    except Exception as e:
                        logger.error(f"Error parsing draw: {e}")
                        continue

                logger.info(f"Successfully fetched {len(results)} draws")
                return results

            except ValueError as e:
                logger.error(f"JSON parsing error: {e}")
                logger.debug(f"Response content: {response.text[:200]}")
                return []

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for date range {start_date} to {end_date}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def _parse_draw(self, draw: Dict[str, Any]) -> Optional[List]:
        """
        Parse a single draw result from the API response.

        Args:
            draw: Dictionary containing draw information

        Returns:
            List with draw data or None if parsing fails
        """
        try:
            # Log available keys for debugging
            logger.debug(f"Draw keys: {list(draw.keys())}")

            # Try different date field names
            draw_date = draw.get("drawDate") or draw.get("draw_date") or draw.get("date") or draw.get("Date")
            if not draw_date:
                logger.warning(f"Draw missing date field. Available keys: {list(draw.keys())}")
                return None

            winning_numbers = draw.get("winningNumbers", [])

            # Extract Mega Ball from extras field
            extras = draw.get("extras", {})
            mega_ball = None
            multiplier = None

            # Try to get Mega Ball from extras
            if isinstance(extras, dict):
                mega_ball = extras.get("megaBall") or extras.get("MegaBall") or extras.get("megaball")
                multiplier = extras.get("megaplier") or extras.get("Megaplier") or extras.get("multiplier")

            # If not in extras, try as direct field
            if mega_ball is None:
                mega_ball = draw.get("megaBall") or draw.get("MegaBall")

            if len(winning_numbers) < 5:
                logger.warning(f"Draw {draw_date}: insufficient regular numbers ({len(winning_numbers)})")
                return None

            if mega_ball is None:
                logger.warning(f"Draw {draw_date}: missing Mega Ball. Extras: {extras}")
                return None

            # First 5 numbers are regular numbers (should be sorted)
            regular_numbers = sorted(winning_numbers[:5])

            # Extract additional information
            jackpot = draw.get("jackpot")

            # Format numbers with leading zeros
            formatted_numbers = [str(num).zfill(2) for num in regular_numbers]
            formatted_mega_ball = str(mega_ball).zfill(2)

            row = [draw_date] + formatted_numbers + [formatted_mega_ball, jackpot, multiplier]

            logger.debug(f"Parsed draw: {draw_date}")
            return row

        except Exception as e:
            logger.error(f"Error parsing draw data: {e}")
            return None

    def scrape_historical_data(self, years: int = DEFAULT_YEARS,
                               interval_weeks: int = DEFAULT_INTERVAL_WEEKS) -> Optional[pd.DataFrame]:
        """
        Scrape historical Mega Millions data for the specified number of years.

        Args:
            years: Number of years of historical data to scrape
            interval_weeks: Number of weeks per request interval

        Returns:
            DataFrame containing all scraped data, or None if scraping failed
        """
        today = datetime.today()
        current_year = today.year
        all_results = []
        interval = timedelta(weeks=interval_weeks)

        years_to_scrape = range(current_year, current_year - years, -1)

        for year in years_to_scrape:
            start_date = datetime(year, 1, 1)
            end_of_year = datetime(year, 12, 31) if year < current_year else today

            while start_date < end_of_year:
                end_date = min(start_date + interval, end_of_year)

                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")

                interval_data = self.fetch_data(start_date_str, end_date_str)

                if interval_data:
                    all_results.extend(interval_data)
                    logger.info(f"Added {len(interval_data)} records")
                else:
                    logger.warning(f"No data found for {start_date_str} to {end_date_str}")

                # Move to the next interval
                start_date = end_date + timedelta(days=1)

                # Polite delay between requests
                time.sleep(2)

        if not all_results:
            logger.error("No data was collected")
            return None

        # Create DataFrame
        columns = ["Date", "Number1", "Number2", "Number3", "Number4", "Number5",
                  "MegaBall", "Jackpot", "Multiplier"]
        df = pd.DataFrame(all_results, columns=columns)

        # Convert and sort
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date", ascending=False)

        return df

    def save_data(self, df: pd.DataFrame, filename: str = "mega_millions_lottery_data.csv") -> None:
        """
        Save the scraped data to CSV.

        Args:
            df: DataFrame containing the lottery data
            filename: Output filename
        """
        output_file = self.output_dir / filename
        df.to_csv(output_file, index=False)
        logger.info(f"Data saved to {output_file}")
        logger.info(f"Total records: {len(df)}")


def main():
    """Main function to run the Mega Millions scraper."""
    scraper = MegaMillionsScraper()

    logger.info("Starting Mega Millions data scraping...")
    df = scraper.scrape_historical_data(years=10)

    if df is not None:
        scraper.save_data(df)
        print("\n" + "=" * 60)
        print("Mega Millions Data Scraping Completed")
        print("=" * 60)
        print(f"Total draws collected: {len(df)}")
        print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        print("\nFirst 5 draws:")
        print(df.head())
        print("=" * 60)
    else:
        logger.error("Scraping failed. Please check the error messages above.")


if __name__ == "__main__":
    main()
