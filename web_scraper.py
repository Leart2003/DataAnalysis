from __future__ import annotations

import csv
import io
from html.parser import HTMLParser
from urllib.request import Request, urlopen

from models import AttackRecord


class GroundTruthParser(HTMLParser):
    # Mban vetem bllokun <code> qe permban sample rows te dataset-it.
    def __init__(self) -> None:
        super().__init__()
        self.capture_code = False
        self.code_blocks: list[str] = []
        self.current_code: list[str] = []

    # Kur fillon tag-u <code>, fillon ruajtja e tekstit.
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "code":
            self.capture_code = True
            self.current_code = []

    # Mbledh tekstin brenda bllokut <code>.
    def handle_data(self, data: str) -> None:
        if self.capture_code:
            self.current_code.append(data)

    # Kur mbaron blloku <code>, kontrollon nese ai permban kolonat qe na duhen.
    def handle_endtag(self, tag: str) -> None:
        if tag == "code" and self.capture_code:
            code_text = "".join(self.current_code)
            if "Start time,Last time,Attack category,Attack subcategory,Protocol" in code_text:
                self.code_blocks.append(code_text)
            self.capture_code = False
            self.current_code = []


class UNSWGroundTruthWebScraper:
    # Ruajme gabimin e fundit ne rast se scraping deshton.
    def __init__(self) -> None:
        self.last_error: str | None = None

    # Hyn ne faqe, merr HTML-ne dhe kthen sample rows si AttackRecord.
    def scrape_attack_records(self, limit: int = 10) -> list[AttackRecord]:
        url = "https://fkie-cad.github.io/COMIDDS/content/datasets/unsw_nb15/"
        request = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; DataAnalysisProject/1.0)"
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                html = response.read().decode("utf-8", errors="ignore")
        except Exception as error:  # pragma: no cover - depends on network
            self.last_error = str(error)
            return []

        parser = GroundTruthParser()
        parser.feed(html)
        if not parser.code_blocks:
            self.last_error = "Ground truth sample rows were not found on the UNSW page."
            return []

        records = self._parse_ground_truth_block(parser.code_blocks[0])
        return records[:limit]

    # Kthen tekstin e marre nga web-i ne rekordet e njejta si CSV-ja jone.
    def _parse_ground_truth_block(self, code_block: str) -> list[AttackRecord]:
        cleaned_lines = [line.strip().strip("`") for line in code_block.splitlines() if line.strip()]
        csv_text = "\n".join(cleaned_lines)
        reader = csv.DictReader(io.StringIO(csv_text))

        records: list[AttackRecord] = []
        for row in reader:
            start_time = (row.get("Start time") or "").strip()
            end_time = (row.get("Last time") or "").strip()
            time_range = f"{start_time}-{end_time}" if start_time or end_time else ""
            records.append(
                AttackRecord(
                    attack_category=(row.get("Attack category") or "").strip(),
                    attack_subcategory=(row.get("Attack subcategory") or "").strip(),
                    protocol=(row.get("Protocol") or "").strip(),
                    source_ip=(row.get("Source IP") or "").strip(),
                    source_port=(row.get("Source Port") or "").strip(),
                    destination_ip=(row.get("Destination IP") or "").strip(),
                    destination_port=(row.get("Destination Port") or "").strip(),
                    attack_name=(row.get("Attack Name") or "").strip(),
                    attack_reference=(row.get("Attack Reference") or "").strip(),
                    marker=(row.get(".") or "").strip(),
                    time_range=time_range,
                )
            )
        return records
