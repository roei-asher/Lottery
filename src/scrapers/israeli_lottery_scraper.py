"""
Israeli Lottery Data Processor

This script processes the manually downloaded Israeli Lottery CSV file.
The Israeli Lottery (Pais) does not provide a public API, so data must be
downloaded from their website: https://www.pais.co.il/lotto/archive.aspx
Note: An Israeli VPN might be needed to access this site.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IsraeliLotteryProcessor:
    """
    Processes and cleans Israeli Lottery CSV data.

    Expected raw CSV format:
    - Lottery, Date, num1, num2, num3, num4, num5, num6, Special
    """

    def __init__(
        self,
        input_file: str = "datasets/israeli_lottery.csv",
        output_file: str = "datasets/cleaned_israeli_lottery_data.csv",
    ):
        """
        Initialize the processor.

        Args:
            input_file: Path to the raw CSV file
            output_file: Path for the cleaned output file
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

    def process(self) -> pd.DataFrame:
        """
        Process the Israeli lottery CSV file.

        Returns:
            Cleaned DataFrame
        """
        if not self.input_file.exists():
            raise FileNotFoundError(
                f"Israeli lottery data not found at: {self.input_file}\n"
                f"Please download it from: https://www.pais.co.il/lotto/archive.aspx"
            )

        logger.info(f"Reading data from {self.input_file}")

        # Read the CSV file
        df = pd.read_csv(self.input_file)

        logger.info(f"Loaded {len(df)} rows")
        logger.info(f"Columns: {list(df.columns)}")

        # Fill NaN values
        df.fillna(1.0, inplace=True)

        # Rename columns from num1-num6 to Number1-Number6
        rename_dict = {f"num{i}": f"Number{i}" for i in range(1, 7)}
        df.rename(columns=rename_dict, inplace=True)

        logger.info("Renamed columns to standard format")

        # Convert date column
        df["Draw Date"] = pd.to_datetime(df["Date"], dayfirst=True)

        # Filter out invalid data
        # Remove rows where Special number is > 7
        before_filter = len(df)
        df = df[df["Special"] <= 7]

        # Remove rows where any regular number is > 37
        number_cols = ["Number1", "Number2", "Number3", "Number4", "Number5", "Number6"]
        df = df[~(df[number_cols] > 37).any(axis=1)]

        after_filter = len(df)
        if before_filter != after_filter:
            logger.info(f"Filtered out {before_filter - after_filter} invalid rows")

        # Set Draw Date as index
        df.set_index("Draw Date", inplace=True)
        df.index = pd.to_datetime(df.index)

        # Drop the original Date column
        if "Date" in df.columns:
            df.drop(["Date"], axis=1, inplace=True)

        # Sort by date descending (most recent first)
        df = df.sort_index(ascending=False)

        # Save cleaned data
        df.to_csv(self.output_file)
        logger.info(f"Saved cleaned data to {self.output_file}")
        logger.info(f"Total valid draws: {len(df)}")

        if len(df) > 0:
            logger.info(f"Date range: {df.index.min()} to {df.index.max()}")

        return df


def main():
    """Main function to run the Israeli lottery processor."""
    print("\n" + "=" * 70)
    print("ISRAELI LOTTERY DATA PROCESSOR")
    print("=" * 70)

    processor = IsraeliLotteryProcessor()

    try:
        df = processor.process()

        print("\n" + "=" * 70)
        print("Processing Complete!")
        print("=" * 70)
        print(f"Total draws: {len(df)}")
        print(f"Date range: {df.index.min().date()} to {df.index.max().date()}")
        print("\nFirst 5 rows:")
        print(df.head())
        print("\n" + "=" * 70)

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nSteps to get the data:")
        print("1. Visit: https://www.pais.co.il/lotto/results.aspx")
        print("2. Download the historical results CSV")
        print("3. Save it as: datasets/israeli_lottery.csv")
        print("4. Run this script again")
        return 1

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.exception("Error details:")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
