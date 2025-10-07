"""
Powerball Lottery Data Scraper

This module fetches historical Powerball lottery data from the official website.
Powerball draws 5 regular numbers (1-69) and 1 Powerball number (1-26).
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
from pathlib import Path
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PowerballScraper:
    """
    Scraper for fetching Powerball lottery historical data.

    Powerball drawings occur on Monday, Wednesday, and Saturday.
    """

    BASE_URL = "https://www.powerball.com/previous-results"
    DRAWING_DAYS = [0, 2, 5]  # Monday, Wednesday, Saturday
    DEFAULT_YEARS = 10
    DEFAULT_INTERVAL_WEEKS = 10

    def __init__(self, output_dir: str = "datasets"):
        """
        Initialize the Powerball scraper.

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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": self.BASE_URL,
        })

    def _get_next_drawing_date(self, date: datetime) -> datetime:
        """Get the next valid Powerball drawing date (Mon, Wed, or Sat)."""
        while date.weekday() not in self.DRAWING_DAYS:
            date += timedelta(days=1)
        return date

    def _get_previous_drawing_date(self, date: datetime) -> datetime:
        """Get the previous valid Powerball drawing date (Mon, Wed, or Sat)."""
        while date.weekday() not in self.DRAWING_DAYS:
            date -= timedelta(days=1)
        return date

    def fetch_data(self, start_date: str, end_date: str) -> List[List]:
        """
        Fetch Powerball data for a specific date range.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format

        Returns:
            List of draw results, each containing [date, num1-5, powerball, powerplay]
        """
        # Validate date range
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")

        if start_dt > end_dt:
            logger.warning(f"Invalid date range: {start_date} to {end_date}")
            return []

        params = {"gc": "powerball", "sd": start_date, "ed": end_date}

        try:
            logger.info(f"Fetching data from {start_date} to {end_date}")
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = []

            # Find all card elements containing draw results
            cards = soup.find_all("a", class_="card")

            for card in cards:
                try:
                    # Extract draw date
                    date_elem = card.find("h5", class_="card-title")
                    if not date_elem:
                        continue

                    date_text = date_elem.text.strip()
                    draw_date = datetime.strptime(date_text, "%a, %b %d, %Y").strftime("%Y-%m-%d")

                    # Extract winning numbers
                    number_elements = card.find_all("div", class_="white-balls")
                    numbers = [elem.text.strip() for elem in number_elements]

                    if len(numbers) != 5:
                        logger.warning(f"Unexpected number count for {draw_date}: {len(numbers)}")
                        continue

                    # Extract Powerball number
                    powerball_elem = card.find("div", class_="powerball")
                    if not powerball_elem:
                        logger.warning(f"No Powerball number found for {draw_date}")
                        continue

                    powerball = powerball_elem.text.strip()

                    # Extract Power Play multiplier
                    multiplier_elem = card.find("span", class_="multiplier")
                    multiplier = multiplier_elem.text.strip().replace("x", "") if multiplier_elem else None

                    # Create result row
                    row = [draw_date] + numbers + [powerball, multiplier]
                    results.append(row)
                    logger.debug(f"Successfully processed draw: {draw_date}")

                except Exception as e:
                    logger.error(f"Error processing card: {e}")
                    continue

            logger.info(f"Fetched {len(results)} draws from {start_date} to {end_date}")
            return results

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout for date range {start_date} to {end_date}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def scrape_historical_data(self, years: int = DEFAULT_YEARS,
                               interval_weeks: int = DEFAULT_INTERVAL_WEEKS) -> Optional[pd.DataFrame]:
        """
        Scrape historical Powerball data for the specified number of years.

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
            # Start from January 1st of the year
            current_date = self._get_next_drawing_date(datetime(year, 1, 1))

            # End at December 31st of the year or today for current year
            year_end = min(datetime(year, 12, 31), today)
            year_end = self._get_previous_drawing_date(year_end)

            while current_date <= year_end:
                # Calculate end date for current interval
                interval_end = min(current_date + interval, year_end)
                interval_end = self._get_previous_drawing_date(interval_end)

                # Only proceed if we have a valid date range
                if current_date <= interval_end:
                    start_date_str = current_date.strftime("%Y-%m-%d")
                    end_date_str = interval_end.strftime("%Y-%m-%d")

                    interval_data = self.fetch_data(start_date_str, end_date_str)

                    if interval_data:
                        all_results.extend(interval_data)
                        logger.info(f"Added {len(interval_data)} records")
                    else:
                        logger.warning(f"No data found for {start_date_str} to {end_date_str}")

                    # Move to the next interval
                    current_date = self._get_next_drawing_date(interval_end + timedelta(days=1))

                    # Polite delay between requests
                    time.sleep(2)
                else:
                    break

        if not all_results:
            logger.error("No data was collected")
            return None

        # Create DataFrame
        columns = ["Date", "Number1", "Number2", "Number3", "Number4", "Number5",
                  "Powerball", "PowerPlay"]
        df = pd.DataFrame(all_results, columns=columns)

        # Convert and sort
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date", ascending=False)

        return df

    def save_data(self, df: pd.DataFrame, filename: str = "powerball_lottery_data.csv") -> None:
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
    """Main function to run the Powerball scraper."""
    scraper = PowerballScraper()

    logger.info("Starting Powerball data scraping...")
    df = scraper.scrape_historical_data(years=10)

    if df is not None:
        scraper.save_data(df)
        print("\n" + "=" * 60)
        print("Powerball Data Scraping Completed")
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
