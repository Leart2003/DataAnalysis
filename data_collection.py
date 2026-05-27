from __future__ import annotations

import csv
import json
from pathlib import Path

from models import AttackRecord, ScrapedAdvisory


class CSVDataCollector:
    fieldnames = [
        "Attack category",
        "Attack subcategory",
        "Protocol",
        "Source IP",
        "Source Port",
        "Destination IP",
        "Destination Port",
        "Attack Name",
        "Attack Reference",
        ".",
        "Time",
    ]

    def read_csv(self, csv_path: str | Path) -> list[AttackRecord]:
        records: list[AttackRecord] = []
        with Path(csv_path).open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                records.append(AttackRecord.from_csv_row(row))
        return records

    def write_csv(self, csv_path: str | Path, records: list[AttackRecord]) -> None:
        path = Path(csv_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=self.fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record.to_csv_row())

    def write_json(self, json_path: str | Path, payload: object) -> None:
        path = Path(json_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)

    def advisories_to_payload(self, advisories: list[ScrapedAdvisory]) -> list[dict[str, str]]:
        return [{"title": advisory.title, "url": advisory.url} for advisory in advisories]

