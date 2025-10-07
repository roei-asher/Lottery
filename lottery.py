#!/usr/bin/env python3
"""
Lottery Analysis & Prediction - Main Entry Point

A comprehensive command-line interface for lottery data scraping,
analysis, and prediction.
"""

import sys
import argparse
from pathlib import Path


def print_banner():
    """Print the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🎰  LOTTERY ANALYSIS & PREDICTION TOOLKIT  🎰        ║
    ║                                                              ║
    ║     Analyze and predict lottery numbers using statistical    ║
    ║     analysis and pattern recognition techniques              ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def scrape_data(lottery_type: str):
    """
    Scrape historical lottery data.

    Args:
        lottery_type: Type of lottery (israeli, powerball, megamillions, all)
    """
    print(f"\n📥 Scraping {lottery_type} lottery data...")
    print("-" * 60)

    if lottery_type in ["israeli", "all"]:
        try:
            print("\n🇮🇱 Israeli Lottery:")
            # Note: Israeli lottery scraper would need to be implemented
            print("   ⚠️  Israeli lottery scraper not yet implemented")
            print("   Please use existing CSV data in datasets/")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    if lottery_type in ["powerball", "all"]:
        try:
            print("\n🇺🇸 Powerball:")
            from src.scrapers.powerball_scraper import main

            main()
            print("   ✅ Powerball data scraped successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    if lottery_type in ["megamillions", "all"]:
        try:
            print("\n💰 Mega Millions:")
            from src.scrapers.mega_millions_scraper import main

            main()
            print("   ✅ Mega Millions data scraped successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def analyze_data(lottery_type: str):
    """
    Analyze lottery data and generate reports.

    Args:
        lottery_type: Type of lottery (israeli, powerball, megamillions, all)
    """
    print(f"\n📊 Analyzing {lottery_type} lottery data...")
    print("-" * 60)

    if lottery_type in ["israeli", "all"]:
        try:
            print("\n🇮🇱 Israeli Lottery Analysis:")
            from src.analysis.lottery_analyzer import analyze_israeli_lottery

            analyze_israeli_lottery()
        except FileNotFoundError:
            print("   ⚠️  Data file not found. Run scraper first.")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    if lottery_type in ["powerball", "all"]:
        try:
            print("\n🇺🇸 Powerball Analysis:")
            from src.analysis.lottery_analyzer import analyze_powerball

            analyze_powerball()
        except FileNotFoundError:
            print("   ⚠️  Data file not found. Run scraper first.")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    if lottery_type in ["megamillions", "all"]:
        try:
            print("\n💰 Mega Millions Analysis:")
            from src.analysis.lottery_analyzer import analyze_mega_millions

            analyze_mega_millions()
        except FileNotFoundError:
            print("   ⚠️  Data file not found. Run scraper first.")
        except Exception as e:
            print(f"   ❌ Error: {e}")


def generate_predictions(lottery_type: str, num_tickets: int = 12):
    """
    Generate lottery number predictions.

    Args:
        lottery_type: Type of lottery (israeli, powerball, megamillions)
        num_tickets: Number of ticket combinations to generate
    """
    print(f"\n🎲 Generating {lottery_type} lottery predictions...")
    print("-" * 60)

    if lottery_type == "israeli":
        try:
            from src.predictors.israeli_lottery_predictor import IsraeliLotteryPredictor

            predictor = IsraeliLotteryPredictor(
                "datasets/cleaned_israeli_lottery_data.csv"
            )
            tickets = predictor.generate_tickets(num_tickets=num_tickets)

            print("\n" + "=" * 60)
            print("ISRAELI LOTTERY - OPTIMIZED PREDICTIONS")
            print("=" * 60)
            print(f"Based on {predictor.lookback_draws} recent draws")
            print("Numbers: 6 regular (1-37) + 1 special (1-7)")
            print("-" * 60)

            for i, (regular, special) in enumerate(tickets, 1):
                regular_str = ", ".join(f"{n:2d}" for n in regular)
                print(f"Ticket {i:2d}: [{regular_str}] | Special: {special}")

            print("=" * 60)
            print("\n⚠️  Disclaimer: These predictions are for entertainment only.")
            print("   Lottery outcomes are random and unpredictable.\n")

        except FileNotFoundError:
            print("   ❌ Data file not found. Run scraper and ensure data exists.")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    elif lottery_type in ["powerball", "megamillions"]:
        print(f"   ⚠️  {lottery_type.title()} predictor not yet implemented")
        print("   Currently only Israeli lottery predictions are available")

    else:
        print("   ❌ Invalid lottery type for predictions")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Lottery Analysis & Prediction Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all lottery data
  python lottery.py scrape --all

  # Scrape specific lottery
  python lottery.py scrape --lottery powerball

  # Analyze all available data
  python lottery.py analyze --all

  # Generate Israeli lottery predictions
  python lottery.py predict --lottery israeli --tickets 12

For more information, visit: https://github.com/roei-asher/Lottery
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape lottery data")
    scrape_group = scrape_parser.add_mutually_exclusive_group(required=True)
    scrape_group.add_argument(
        "--lottery",
        choices=["israeli", "powerball", "megamillions"],
        help="Lottery type to scrape",
    )
    scrape_group.add_argument(
        "--all", action="store_true", help="Scrape all lottery types"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze lottery data")
    analyze_group = analyze_parser.add_mutually_exclusive_group(required=True)
    analyze_group.add_argument(
        "--lottery",
        choices=["israeli", "powerball", "megamillions"],
        help="Lottery type to analyze",
    )
    analyze_group.add_argument(
        "--all", action="store_true", help="Analyze all lottery types"
    )

    # Predict command
    predict_parser = subparsers.add_parser(
        "predict", help="Generate lottery predictions"
    )
    predict_parser.add_argument(
        "--lottery",
        required=True,
        choices=["israeli", "powerball", "megamillions"],
        help="Lottery type for predictions",
    )
    predict_parser.add_argument(
        "--tickets",
        type=int,
        default=12,
        help="Number of ticket combinations (default: 12)",
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Check if datasets directory exists
    datasets_dir = Path("datasets")
    if not datasets_dir.exists():
        datasets_dir.mkdir(parents=True)
        print("📁 Created datasets directory\n")

    # Execute command
    if args.command == "scrape":
        lottery_type = "all" if args.all else args.lottery
        scrape_data(lottery_type)

    elif args.command == "analyze":
        lottery_type = "all" if args.all else args.lottery
        analyze_data(lottery_type)

    elif args.command == "predict":
        generate_predictions(args.lottery, args.tickets)

    else:
        parser.print_help()
        return 1

    print("\n✨ Done!\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
