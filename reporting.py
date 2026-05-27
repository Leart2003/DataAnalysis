from __future__ import annotations

from pathlib import Path


class SubmissionReportWriter:
    def write_report(
        self,
        output_path: str | Path,
        cleaner_stats: dict[str, int],
        query_summary: dict[str, object],
        scraped_count: int,
        scrape_error: str | None,
    ) -> Path:
        lines = [
            "PROJEKTI I ANALIZES SE TE DHENAVE",
            "",
            "1. Mbledhja e te dhenave",
            "Te dhenat u lexuan nga skedari Cybersecurity_attacks.csv.",
            "",
            "2. Pastrimi i te dhenave",
            f"Rreshta para pastrimit: {cleaner_stats['rows_before']}",
            f"Rreshta pas pastrimit: {cleaner_stats['rows_after']}",
            f"Duplikate te larguara: {cleaner_stats['duplicates_removed']}",
            f"Attack subcategory te mbushura: {cleaner_stats['subcategory_filled']}",
            f"Attack reference te mbushura: {cleaner_stats['reference_filled']}",
            f"Kolona marker te mbushura: {cleaner_stats['marker_filled']}",
            "",
            "3. Queries dhe filters",
            f"Kategorite me te shpeshta: {query_summary['top_categories']}",
            f"Protokollet me te shpeshta: {query_summary['top_protocols']}",
            f"Filtrim shembull per Exploits + tcp: {query_summary['sample_filter_count']} rezultate",
            "",
            "4. Web scraping",
            f"Artikuj/advisories te marra nga web: {scraped_count}",
        ]
        if scrape_error:
            lines.append(f"Shenim: web scraping nuk u ekzekutua plotesisht ne kete ambient: {scrape_error}")
        else:
            lines.append("Web scraping u realizua me sukses.")
        lines.extend(
            [
                "",
                "5. Paraqitja grafike",
                "Jane gjeneruar 3 lloje grafike: bar chart, pie chart dhe line chart.",
            ]
        )

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

