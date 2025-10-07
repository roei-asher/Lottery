"""
Lottery Data Analysis Module

This module provides comprehensive analysis and visualization capabilities
for lottery data including frequency analysis, correlation, and trend analysis.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
from pathlib import Path
from typing import List, Optional, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LotteryAnalyzer:
    """
    Comprehensive lottery data analyzer with visualization capabilities.

    Supports analysis of various lottery types with customizable number ranges.
    """

    def __init__(
        self,
        csv_file: str,
        number_columns: List[str],
        special_column: Optional[str] = None,
    ):
        """
        Initialize the lottery analyzer.

        Args:
            csv_file: Path to the lottery data CSV file
            number_columns: List of column names containing the drawn numbers
            special_column: Optional column name for special/bonus number
        """
        self.csv_file = Path(csv_file)
        self.number_columns = number_columns
        self.special_column = special_column
        self.df = None

        self._load_data()

    def _load_data(self) -> None:
        """Load and prepare the lottery data."""
        if not self.csv_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.csv_file}")

        self.df = pd.read_csv(self.csv_file)

        # Convert date column to datetime if it exists
        date_columns = ["Date", "Draw Date", "DrawDate"]
        for col in date_columns:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col])
                self.df = self.df.sort_values(col, ascending=False)
                break

        logger.info(f"Loaded {len(self.df)} lottery draws from {self.csv_file}")

    def get_summary_statistics(self) -> Dict[str, any]:
        """
        Get summary statistics for the lottery data.

        Returns:
            Dictionary containing summary statistics
        """
        all_numbers = pd.concat([self.df[col] for col in self.number_columns])

        stats = {
            "total_draws": len(self.df),
            "date_range": (
                self.df[self._get_date_column()].min(),
                self.df[self._get_date_column()].max(),
            ),
            "number_range": (int(all_numbers.min()), int(all_numbers.max())),
            "most_common_numbers": Counter(all_numbers).most_common(10),
            "least_common_numbers": Counter(all_numbers).most_common()[-10:],
        }

        if self.special_column and self.special_column in self.df.columns:
            stats["most_common_special"] = Counter(
                self.df[self.special_column]
            ).most_common(5)

        return stats

    def _get_date_column(self) -> str:
        """Find the date column in the DataFrame."""
        date_columns = ["Date", "Draw Date", "DrawDate"]
        for col in date_columns:
            if col in self.df.columns:
                return col
        return self.df.columns[0]  # Fallback to first column

    def plot_number_frequency(
        self, save_path: Optional[str] = None, top_n: Optional[int] = None
    ) -> None:
        """
        Plot the frequency distribution of all drawn numbers.

        Args:
            save_path: Optional path to save the figure
            top_n: If specified, only plot the top N most frequent numbers
        """
        all_numbers = pd.concat([self.df[col] for col in self.number_columns])
        number_counts = Counter(all_numbers)

        plt.figure(figsize=(15, 7))

        if top_n:
            top_numbers = dict(number_counts.most_common(top_n))
            plt.bar(top_numbers.keys(), top_numbers.values())
            plt.title(f"Top {top_n} Most Frequent Numbers")
        else:
            numbers_sorted = sorted(number_counts.items())
            plt.bar([n for n, _ in numbers_sorted], [c for _, c in numbers_sorted])
            plt.title("Frequency Distribution of All Numbers")

        plt.xlabel("Number")
        plt.ylabel("Frequency")
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved frequency plot to {save_path}")

        plt.close()

    def plot_special_frequency(self, save_path: Optional[str] = None) -> None:
        """
        Plot the frequency distribution of special/bonus numbers.

        Args:
            save_path: Optional path to save the figure
        """
        if not self.special_column or self.special_column not in self.df.columns:
            logger.warning("No special number column available")
            return

        plt.figure(figsize=(12, 6))
        special_counts = Counter(self.df[self.special_column])
        numbers_sorted = sorted(special_counts.items())

        plt.bar([n for n, _ in numbers_sorted], [c for _, c in numbers_sorted])
        plt.title(f"Frequency Distribution of {self.special_column}")
        plt.xlabel(self.special_column)
        plt.ylabel("Frequency")
        plt.xticks(rotation=0)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved special number frequency plot to {save_path}")

        plt.close()

    def plot_correlation_matrix(self, save_path: Optional[str] = None) -> None:
        """
        Plot correlation matrix between number positions.

        Args:
            save_path: Optional path to save the figure
        """
        correlation_matrix = self.df[self.number_columns].corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(
            correlation_matrix,
            annot=True,
            cmap="coolwarm",
            center=0,
            fmt=".2f",
            square=True,
        )
        plt.title("Correlation Between Number Positions")
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved correlation matrix to {save_path}")

        plt.close()

    def plot_number_trends(
        self, window_size: int = 20, save_path: Optional[str] = None
    ) -> None:
        """
        Plot rolling average trends for number frequencies.

        Args:
            window_size: Size of the rolling window
            save_path: Optional path to save the figure
        """
        date_col = self._get_date_column()
        df_sorted = self.df.sort_values(date_col)

        # Calculate rolling average for top 5 most common numbers
        all_numbers = pd.concat([self.df[col] for col in self.number_columns])
        top_5_numbers = [num for num, _ in Counter(all_numbers).most_common(5)]

        plt.figure(figsize=(15, 8))

        for number in top_5_numbers:
            # Create binary series for number appearance
            appearances = (
                df_sorted[self.number_columns]
                .apply(lambda row: number in row.values, axis=1)
                .astype(int)
            )

            # Calculate rolling average
            rolling_avg = appearances.rolling(window=window_size).mean()

            plt.plot(df_sorted[date_col], rolling_avg, label=f"Number {number}")

        plt.xlabel("Date")
        plt.ylabel(f"Frequency (Rolling {window_size}-draw average)")
        plt.title("Top 5 Number Trends Over Time")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Saved trends plot to {save_path}")

        plt.close()

    def analyze_hot_cold_numbers(
        self, recent_draws: int = 50
    ) -> Tuple[List[int], List[int]]:
        """
        Identify hot (frequent) and cold (infrequent) numbers in recent draws.

        Args:
            recent_draws: Number of recent draws to analyze

        Returns:
            Tuple of (hot_numbers, cold_numbers)
        """
        recent_df = self.df.head(recent_draws)
        all_numbers = pd.concat([recent_df[col] for col in self.number_columns])

        number_counts = Counter(all_numbers)
        sorted_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)

        # Top 20% are "hot", bottom 20% are "cold"
        cutoff = max(1, len(sorted_numbers) // 5)
        hot_numbers = [num for num, _ in sorted_numbers[:cutoff]]
        cold_numbers = [num for num, _ in sorted_numbers[-cutoff:]]

        return hot_numbers, cold_numbers

    def print_summary_report(self) -> None:
        """Print a comprehensive summary report of the lottery data."""
        stats = self.get_summary_statistics()

        print("\n" + "=" * 70)
        print("LOTTERY DATA ANALYSIS REPORT")
        print("=" * 70)
        print(f"Data file: {self.csv_file}")
        print(f"Total draws: {stats['total_draws']}")
        print(f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}")
        print(f"Number range: {stats['number_range'][0]} to {stats['number_range'][1]}")
        print("\n" + "-" * 70)
        print("TOP 10 MOST FREQUENT NUMBERS:")
        print("-" * 70)
        for i, (num, count) in enumerate(stats["most_common_numbers"], 1):
            percentage = (
                count / (stats["total_draws"] * len(self.number_columns))
            ) * 100
            print(f"{i:2d}. Number {num:2d}: {count:4d} times ({percentage:.2f}%)")

        if "most_common_special" in stats:
            print("\n" + "-" * 70)
            print(f"MOST FREQUENT {self.special_column.upper()}:")
            print("-" * 70)
            for i, (num, count) in enumerate(stats["most_common_special"], 1):
                percentage = (count / stats["total_draws"]) * 100
                print(
                    f"{i}. {self.special_column} {num}: {count} times ({percentage:.2f}%)"
                )

        # Hot and cold numbers analysis
        hot, cold = self.analyze_hot_cold_numbers()
        print("\n" + "-" * 70)
        print("HOT NUMBERS (Last 50 draws):")
        print("-" * 70)
        print(", ".join(str(n) for n in sorted(hot)))

        print("\n" + "-" * 70)
        print("COLD NUMBERS (Last 50 draws):")
        print("-" * 70)
        print(", ".join(str(n) for n in sorted(cold)))

        print("\n" + "=" * 70)


def analyze_israeli_lottery(
    csv_file: str = "datasets/cleaned_israeli_lottery_data.csv",
):
    """Analyze Israeli lottery data."""
    number_columns = ["Number1", "Number2", "Number3", "Number4", "Number5", "Number6"]
    analyzer = LotteryAnalyzer(csv_file, number_columns, special_column="Special")

    analyzer.print_summary_report()
    analyzer.plot_number_frequency(save_path="docs/israeli_frequency.png")
    analyzer.plot_special_frequency(save_path="docs/israeli_special.png")
    analyzer.plot_correlation_matrix(save_path="docs/israeli_correlation.png")


def analyze_powerball(csv_file: str = "datasets/powerball_lottery_data.csv"):
    """Analyze Powerball lottery data."""
    number_columns = ["Number1", "Number2", "Number3", "Number4", "Number5"]
    analyzer = LotteryAnalyzer(csv_file, number_columns, special_column="Powerball")

    analyzer.print_summary_report()
    analyzer.plot_number_frequency(save_path="docs/powerball_frequency.png")
    analyzer.plot_special_frequency(save_path="docs/powerball_special.png")
    analyzer.plot_correlation_matrix(save_path="docs/powerball_correlation.png")


def analyze_mega_millions(csv_file: str = "datasets/mega_millions_lottery_data.csv"):
    """Analyze Mega Millions lottery data."""
    number_columns = ["Number1", "Number2", "Number3", "Number4", "Number5"]
    analyzer = LotteryAnalyzer(csv_file, number_columns, special_column="MegaBall")

    analyzer.print_summary_report()
    analyzer.plot_number_frequency(save_path="docs/megamillions_frequency.png")
    analyzer.plot_special_frequency(save_path="docs/megamillions_special.png")
    analyzer.plot_correlation_matrix(save_path="docs/megamillions_correlation.png")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        lottery_type = sys.argv[1].lower()
        if lottery_type == "israeli":
            analyze_israeli_lottery()
        elif lottery_type == "powerball":
            analyze_powerball()
        elif lottery_type == "megamillions":
            analyze_mega_millions()
        else:
            print("Usage: python lottery_analyzer.py [israeli|powerball|megamillions]")
            sys.exit(1)
    else:
        print("Analyzing all available lottery types...")
        print("\n" + "=" * 70)
        print("ISRAELI LOTTERY")
        try:
            analyze_israeli_lottery()
        except FileNotFoundError:
            logger.warning("Israeli lottery data not found")

        print("\n" + "=" * 70)
        print("POWERBALL")
        try:
            analyze_powerball()
        except FileNotFoundError:
            logger.warning("Powerball data not found")

        print("\n" + "=" * 70)
        print("MEGA MILLIONS")
        try:
            analyze_mega_millions()
        except FileNotFoundError:
            logger.warning("Mega Millions data not found")
