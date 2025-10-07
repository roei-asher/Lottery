"""
Mega Millions Number Predictor

This module generates optimized Mega Millions ticket combinations based on historical
drawing data using frequency analysis, recency weighting, and pair correlation.
"""

import pandas as pd
import numpy as np
from collections import Counter
import itertools
import random
from pathlib import Path
from typing import List, Tuple


class MegaMillionsPredictor:
    """
    Generates optimized Mega Millions tickets based on historical data analysis.

    Mega Millions draws 5 regular numbers (1-70) and 1 Mega Ball number (1-25).
    This predictor uses three main strategies:
    1. Frequency + Recency analysis
    2. Tiered selection
    3. Pair correlation analysis
    """

    REGULAR_NUMBERS_MIN = 1
    REGULAR_NUMBERS_MAX = 70
    MEGABALL_MIN = 1
    MEGABALL_MAX = 25
    NUMBERS_PER_TICKET = 5

    def __init__(self, csv_file: str, lookback_draws: int = 200):
        """
        Initialize the predictor with historical Mega Millions data.

        Args:
            csv_file: Path to CSV file containing historical Mega Millions data
            lookback_draws: Number of recent draws to analyze (default: 200)
        """
        self.csv_file = Path(csv_file)
        self.lookback_draws = lookback_draws
        self.df = None
        self.regular_scores = {}
        self.megaball_scores = {}
        self.pair_frequency = {}

        self._load_and_prepare_data()
        self._analyze_data()

    def _load_and_prepare_data(self) -> None:
        """Load and prepare the Mega Millions data from CSV."""
        if not self.csv_file.exists():
            raise FileNotFoundError(f"Data file not found: {self.csv_file}")

        self.df = pd.read_csv(self.csv_file)
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        self.df = self.df.sort_values('Date', ascending=False)

    def _analyze_data(self) -> None:
        """Analyze historical data to compute scores and frequencies."""
        recent_df = self.df.head(self.lookback_draws)

        self._analyze_regular_numbers(recent_df)
        self._analyze_megaball_numbers(recent_df)
        self._analyze_pair_frequency(recent_df)

    def _analyze_regular_numbers(self, df: pd.DataFrame) -> None:
        """Analyze regular numbers (1-70) for frequency and recency."""
        # Calculate frequency
        regular_counts = Counter()
        for col in ['Number1', 'Number2', 'Number3', 'Number4', 'Number5']:
            regular_counts.update(df[col].astype(int))

        # Calculate recency weights (more recent = higher weight)
        recency_weights = {num: 0 for num in range(self.REGULAR_NUMBERS_MIN,
                                                    self.REGULAR_NUMBERS_MAX + 1)}

        for i, (idx, row) in enumerate(df.iterrows()):
            weight = np.exp(-0.02 * i)  # Exponential decay
            for col in ['Number1', 'Number2', 'Number3', 'Number4', 'Number5']:
                recency_weights[int(row[col])] += weight

        # Combine frequency and recency (60% frequency, 40% recency)
        max_freq = max(regular_counts.values()) if regular_counts else 1
        max_recency = max(recency_weights.values()) if recency_weights else 1

        for num in range(self.REGULAR_NUMBERS_MIN, self.REGULAR_NUMBERS_MAX + 1):
            norm_freq = regular_counts.get(num, 0) / max_freq
            norm_recency = recency_weights.get(num, 0) / max_recency
            self.regular_scores[num] = (0.6 * norm_freq) + (0.4 * norm_recency)

    def _analyze_megaball_numbers(self, df: pd.DataFrame) -> None:
        """Analyze Mega Ball numbers (1-25) for frequency and recency."""
        megaball_counts = Counter(df['MegaBall'].astype(int))
        megaball_recency = {num: 0 for num in range(self.MEGABALL_MIN,
                                                     self.MEGABALL_MAX + 1)}

        for i, (idx, row) in enumerate(df.iterrows()):
            weight = np.exp(-0.03 * i)
            megaball_recency[int(row['MegaBall'])] += weight

        # Combine frequency and recency
        max_freq = max(megaball_counts.values()) if megaball_counts else 1
        max_recency = max(megaball_recency.values()) if megaball_recency else 1

        for num in range(self.MEGABALL_MIN, self.MEGABALL_MAX + 1):
            norm_freq = megaball_counts.get(num, 0) / max_freq
            norm_recency = megaball_recency.get(num, 0) / max_recency
            self.megaball_scores[num] = (0.6 * norm_freq) + (0.4 * norm_recency)

    def _analyze_pair_frequency(self, df: pd.DataFrame) -> None:
        """Analyze how often number pairs appear together."""
        # Initialize all possible pairs
        for i in range(self.REGULAR_NUMBERS_MIN, self.REGULAR_NUMBERS_MAX + 1):
            for j in range(i + 1, self.REGULAR_NUMBERS_MAX + 1):
                self.pair_frequency[(i, j)] = 0

        # Count pair occurrences
        for _, row in df.iterrows():
            numbers = [int(row['Number1']), int(row['Number2']), int(row['Number3']),
                      int(row['Number4']), int(row['Number5'])]

            for i, j in itertools.combinations(numbers, 2):
                if i > j:
                    i, j = j, i
                self.pair_frequency[(i, j)] += 1

    def generate_tickets(self, num_tickets: int = 12) -> List[Tuple[List[int], int]]:
        """
        Generate optimized Mega Millions ticket combinations.

        Args:
            num_tickets: Number of ticket combinations to generate

        Returns:
            List of tuples, each containing (regular_numbers_list, megaball_number)
        """
        tickets = []
        top_regular = sorted(self.regular_scores.items(), key=lambda x: x[1], reverse=True)

        # Strategy 1: Core set with weighted selection (4 tickets)
        tickets.extend(self._generate_core_tickets(top_regular, 4))

        # Strategy 2: Tiered selection (4 tickets)
        tickets.extend(self._generate_tiered_tickets(top_regular, 4))

        # Strategy 3: Pair correlation (4 tickets)
        tickets.extend(self._generate_pair_based_tickets(top_regular, 4))

        # Filter and ensure uniqueness
        valid_tickets = self._validate_and_deduplicate(tickets)

        # Fill up to requested number if needed
        while len(valid_tickets) < num_tickets:
            new_ticket = self._generate_mixed_strategy_ticket(top_regular)
            if new_ticket not in valid_tickets:
                valid_tickets.append(new_ticket)

        return valid_tickets[:num_tickets]

    def _generate_core_tickets(self, top_regular: List[Tuple[int, float]],
                               count: int) -> List[Tuple[List[int], int]]:
        """Generate tickets using core top-scoring numbers."""
        tickets = []
        core_set = [num for num, _ in top_regular[:20]]

        for _ in range(count):
            ticket_numbers = []
            remaining = core_set.copy()

            # Pick 3 top numbers with weighted selection
            for _ in range(3):
                if remaining:
                    weights = [self.regular_scores[num] for num in remaining]
                    total = sum(weights)
                    if total > 0:
                        weights = [w/total for w in weights]
                        chosen = np.random.choice(remaining, p=weights)
                    else:
                        chosen = random.choice(remaining)
                    ticket_numbers.append(chosen)
                    remaining.remove(chosen)

            # Add 2 more with increased randomness
            if remaining:
                weights = [self.regular_scores[num] * (0.7 + 0.3 * random.random())
                          for num in remaining]
                total = sum(weights)
                if total > 0:
                    weights = [w/total for w in weights]
                    chosen = np.random.choice(remaining, size=min(2, len(remaining)),
                                            replace=False, p=weights)
                    ticket_numbers.extend(chosen)

            # Ensure 5 numbers
            while len(ticket_numbers) < self.NUMBERS_PER_TICKET:
                all_nums = list(range(self.REGULAR_NUMBERS_MIN,
                                    self.REGULAR_NUMBERS_MAX + 1))
                available = [n for n in all_nums if n not in ticket_numbers]
                ticket_numbers.append(random.choice(available))

            ticket_numbers.sort()
            megaball_num = self._select_megaball_number()
            tickets.append((ticket_numbers, megaball_num))

        return tickets

    def _generate_tiered_tickets(self, top_regular: List[Tuple[int, float]],
                                 count: int) -> List[Tuple[List[int], int]]:
        """Generate tickets using tiered selection strategy."""
        tickets = []
        tiers = [
            [num for num, _ in top_regular[:15]],
            [num for num, _ in top_regular[15:30]],
            [num for num, _ in top_regular[30:45]]
        ]

        for _ in range(count):
            ticket_numbers = []
            ticket_numbers.extend(random.sample(tiers[0], 2))  # 2 from top tier
            ticket_numbers.extend(random.sample(tiers[1], 2))  # 2 from middle tier
            ticket_numbers.append(random.choice(tiers[2]))      # 1 from lower tier
            ticket_numbers.sort()

            megaball_num = self._select_megaball_number()
            tickets.append((ticket_numbers, megaball_num))

        return tickets

    def _generate_pair_based_tickets(self, top_regular: List[Tuple[int, float]],
                                     count: int) -> List[Tuple[List[int], int]]:
        """Generate tickets using pair correlation analysis."""
        tickets = []
        top_pairs = sorted(self.pair_frequency.items(), key=lambda x: x[1],
                          reverse=True)[:50]

        for _ in range(count):
            ticket_numbers = set()
            pairs_to_use = random.sample(top_pairs[:20], 2)

            for (i, j), _ in pairs_to_use:
                ticket_numbers.add(i)
                ticket_numbers.add(j)

            # Fill to 5 numbers if needed
            while len(ticket_numbers) < self.NUMBERS_PER_TICKET:
                candidates = [num for num, _ in top_regular if num not in ticket_numbers]
                if candidates:
                    ticket_numbers.add(candidates[0])
                else:
                    break

            ticket_numbers = sorted(list(ticket_numbers))[:self.NUMBERS_PER_TICKET]

            megaball_num = self._select_megaball_number()
            tickets.append((ticket_numbers, megaball_num))

        return tickets

    def _generate_mixed_strategy_ticket(self,
                                       top_regular: List[Tuple[int, float]]) -> Tuple[List[int], int]:
        """Generate a single ticket using mixed strategies."""
        regular_nums = set()

        # Add top-scoring numbers
        for _ in range(3):
            candidates = [num for num, _ in top_regular[:30] if num not in regular_nums]
            if candidates:
                weights = [self.regular_scores[num] for num in candidates]
                total = sum(weights)
                weights = [w/total for w in weights]
                chosen = np.random.choice(candidates, p=weights)
                regular_nums.add(chosen)

        # Fill with pair-based selection
        top_pairs = sorted(self.pair_frequency.items(), key=lambda x: x[1],
                          reverse=True)[:30]

        while len(regular_nums) < self.NUMBERS_PER_TICKET:
            relevant_pairs = [(p, f) for (p, f) in top_pairs
                            if (p[0] in regular_nums) != (p[1] in regular_nums)]

            if relevant_pairs:
                weights = [f for _, f in relevant_pairs]
                total = sum(weights)
                weights = [w/total for w in weights]
                chosen_pair, _ = relevant_pairs[np.random.choice(len(relevant_pairs),
                                                                p=weights)]
                regular_nums.add(chosen_pair[0] if chosen_pair[0] not in regular_nums
                               else chosen_pair[1])
            else:
                candidates = list(range(self.REGULAR_NUMBERS_MIN,
                                      self.REGULAR_NUMBERS_MAX + 1))
                available = [n for n in candidates if n not in regular_nums]
                if available:
                    weights = [self.regular_scores.get(n, 0.01) for n in available]
                    total = sum(weights)
                    weights = [w/total for w in weights]
                    chosen = np.random.choice(available, p=weights)
                    regular_nums.add(chosen)
                else:
                    break

        regular_nums = sorted(list(regular_nums))
        megaball_num = self._select_megaball_number()

        return (regular_nums, megaball_num)

    def _select_megaball_number(self) -> int:
        """Select a Mega Ball number using weighted probability."""
        weights = [self.megaball_scores[i] for i in range(self.MEGABALL_MIN,
                                                          self.MEGABALL_MAX + 1)]
        total = sum(weights)
        weights = [w/total for w in weights]
        return np.random.choice(range(self.MEGABALL_MIN,
                                     self.MEGABALL_MAX + 1), p=weights)

    def _validate_and_deduplicate(self,
                                 tickets: List[Tuple[List[int], int]]) -> List[Tuple[List[int], int]]:
        """Validate tickets and remove duplicates."""
        valid_tickets = []

        for regular, megaball in tickets:
            # Validate ticket
            if len(regular) != self.NUMBERS_PER_TICKET:
                continue
            if len(set(regular)) != self.NUMBERS_PER_TICKET:
                continue
            if not all(self.REGULAR_NUMBERS_MIN <= num <= self.REGULAR_NUMBERS_MAX
                      for num in regular):
                continue
            if not (self.MEGABALL_MIN <= megaball <= self.MEGABALL_MAX):
                continue

            # Add if unique
            ticket = (regular, megaball)
            if ticket not in valid_tickets:
                valid_tickets.append(ticket)

        return valid_tickets


def main():
    """Example usage of the Mega Millions Predictor."""
    import sys

    csv_file = 'datasets/mega_millions_lottery_data.csv'

    try:
        predictor = MegaMillionsPredictor(csv_file)
        tickets = predictor.generate_tickets(num_tickets=12)

        print("=" * 60)
        print("MEGA MILLIONS - OPTIMIZED TICKET PREDICTIONS")
        print("=" * 60)
        print(f"Based on analysis of {predictor.lookback_draws} recent draws")
        print(f"Regular numbers: {predictor.REGULAR_NUMBERS_MIN}-{predictor.REGULAR_NUMBERS_MAX}")
        print(f"Mega Ball: {predictor.MEGABALL_MIN}-{predictor.MEGABALL_MAX}")
        print("-" * 60)

        for i, (regular, megaball) in enumerate(tickets, 1):
            regular_str = " ".join(f"{n:2d}" for n in regular)
            print(f"Ticket {i:2d}: [{regular_str}] | Mega Ball: {megaball:2d}")

        print("=" * 60)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
