from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class AttackRecord:
    attack_category: str
    attack_subcategory: str
    protocol: str
    source_ip: str
    source_port: str
    destination_ip: str
    destination_port: str
    attack_name: str
    attack_reference: str
    marker: str
    time_range: str

    @classmethod
    def from_csv_row(cls, row: dict[str, str]) -> "AttackRecord":
        return cls(
            attack_category=row.get("Attack category", ""),
            attack_subcategory=row.get("Attack subcategory", ""),
            protocol=row.get("Protocol", ""),
            source_ip=row.get("Source IP", ""),
            source_port=row.get("Source Port", ""),
            destination_ip=row.get("Destination IP", ""),
            destination_port=row.get("Destination Port", ""),
            attack_name=row.get("Attack Name", ""),
            attack_reference=row.get("Attack Reference", ""),
            marker=row.get(".", ""),
            time_range=row.get("Time", ""),
        )

    def to_csv_row(self) -> dict[str, str]:
        return {
            "Attack category": self.attack_category,
            "Attack subcategory": self.attack_subcategory,
            "Protocol": self.protocol,
            "Source IP": self.source_ip,
            "Source Port": self.source_port,
            "Destination IP": self.destination_ip,
            "Destination Port": self.destination_port,
            "Attack Name": self.attack_name,
            "Attack Reference": self.attack_reference,
            ".": self.marker,
            "Time": self.time_range,
        }

    def dedupe_key(self) -> tuple[str, ...]:
        row = self.to_csv_row()
        return tuple(row.values())

    def start_year(self) -> int | None:
        if not self.time_range:
            return None
        start_value = self.time_range.split("-", 1)[0].strip()
        if not start_value.isdigit():
            return None
        try:
            return datetime.fromtimestamp(int(start_value), tz=timezone.utc).year
        except (OverflowError, ValueError):
            return None


@dataclass(slots=True)
class ScrapedAdvisory:
    title: str
    url: str

