from __future__ import annotations

from pathlib import Path

from data_cleaning import AttackDataCleaner
from data_collection import CSVDataCollector


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    collector = CSVDataCollector()
    cleaner = AttackDataCleaner()

    records = collector.read_csv(base_dir / "Cybersecurity_attacks.csv")
    before_missing = cleaner.summarize_missing_values(records)
    cleaned_records = cleaner.clean(records)
    after_missing = cleaner.summarize_missing_values(cleaned_records)

    print("Para mbushjes se qelizave boshe:")
    print(before_missing)
    print("Pas mbushjes se qelizave boshe:")
    print(after_missing)
    print(f"Rreshta pas pastrimit: {len(cleaned_records)}")


if __name__ == "__main__":
    main()
