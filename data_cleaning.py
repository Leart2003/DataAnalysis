from __future__ import annotations

from collections import Counter

from models import AttackRecord


class AttackDataCleaner:
    def __init__(self) -> None:
        self.stats: dict[str, int] = {
            "rows_before": 0,
            "rows_after": 0,
            "duplicates_removed": 0,
            "subcategory_filled": 0,
            "reference_filled": 0,
            "marker_filled": 0,
        }

    def clean(self, records: list[AttackRecord]) -> list[AttackRecord]:
        self.stats["rows_before"] = len(records)
        normalized = [self._normalize_record(record) for record in records]
        filled = [self._fill_missing_values(record) for record in normalized]
        deduped = self._remove_duplicates(filled)
        self.stats["rows_after"] = len(deduped)
        return deduped

    def summarize_missing_values(self, records: list[AttackRecord]) -> dict[str, int]:
        counts: Counter[str] = Counter()
        for record in records:
            for key, value in record.to_csv_row().items():
                if not str(value).strip():
                    counts[key] += 1
        return dict(counts)

    def _normalize_record(self, record: AttackRecord) -> AttackRecord:
        record.attack_category = record.attack_category.strip().title()
        record.attack_subcategory = record.attack_subcategory.strip().title()
        record.protocol = record.protocol.strip().lower()
        record.source_ip = record.source_ip.strip()
        record.source_port = record.source_port.strip()
        record.destination_ip = record.destination_ip.strip()
        record.destination_port = record.destination_port.strip()
        record.attack_name = " ".join(record.attack_name.split())
        record.attack_reference = " ".join(record.attack_reference.split())
        record.marker = record.marker.strip()
        record.time_range = record.time_range.strip()
        return record

    def _fill_missing_values(self, record: AttackRecord) -> AttackRecord:
        if not record.attack_subcategory:
            record.attack_subcategory = "Unknown"
            self.stats["subcategory_filled"] += 1
        if not record.attack_reference:
            record.attack_reference = "No reference available"
            self.stats["reference_filled"] += 1
        if not record.marker:
            record.marker = "N/A"
            self.stats["marker_filled"] += 1
        return record

    def _remove_duplicates(self, records: list[AttackRecord]) -> list[AttackRecord]:
        unique_records: list[AttackRecord] = []
        seen: set[tuple[str, ...]] = set()
        for record in records:
            key = record.dedupe_key()
            if key in seen:
                self.stats["duplicates_removed"] += 1
                continue
            seen.add(key)
            unique_records.append(record)
        return unique_records

