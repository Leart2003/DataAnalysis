from __future__ import annotations

from pathlib import Path

from data_cleaning import AttackDataCleaner
from data_collection import CSVDataCollector
from query_engine import SQLiteQueryEngine
from reporting import SubmissionReportWriter
from visualization import SVGChartBuilder
from web_scraper import UNSWGroundTruthWebScraper


# Kjo metode ekzekuton te gjithe projektin nga fillimi deri ne fund.
def main() -> None:
    base_dir = Path(__file__).resolve().parent
    outputs_dir = base_dir / "outputs"

    collector = CSVDataCollector()
    cleaner = AttackDataCleaner()
    query_engine = SQLiteQueryEngine(outputs_dir / "cybersecurity_attacks.db")
    chart_builder = SVGChartBuilder(outputs_dir)
    scraper = UNSWGroundTruthWebScraper()
    reporter = SubmissionReportWriter()

    raw_records = collector.read_csv(base_dir / "Cybersecurity_attacks.csv")
    missing_before = cleaner.summarize_missing_values(raw_records)
    clean_records = cleaner.clean(raw_records)
    missing_after = cleaner.summarize_missing_values(clean_records)

    collector.write_csv(outputs_dir / "cleaned_cybersecurity_attacks.csv", clean_records)

    query_engine.build_database(clean_records)

    top_categories_rows = query_engine.run_query(
        """
        SELECT attack_category, COUNT(*) AS total
        FROM attacks
        GROUP BY attack_category
        ORDER BY total DESC
        LIMIT 8
        """
    )
    top_protocol_rows = query_engine.run_query(
        """
        SELECT protocol, COUNT(*) AS total
        FROM attacks
        GROUP BY protocol
        ORDER BY total DESC
        LIMIT 6
        """
    )
    top_ports_rows = query_engine.run_query(
        """
        SELECT destination_port, COUNT(*) AS total
        FROM attacks
        WHERE destination_port GLOB '[0-9]*'
        GROUP BY destination_port
        ORDER BY total DESC
        LIMIT 10
        """
    )
    filtered_rows = query_engine.filter_attacks(category="Exploits", protocol="tcp", limit=15)

    query_engine.export_json(
        outputs_dir / "query_results.json",
        {
            "top_categories": top_categories_rows,
            "top_protocols": top_protocol_rows,
            "top_destination_ports": top_ports_rows,
            "sample_filter_exploits_tcp": filtered_rows,
        },
    )

    bar_chart = chart_builder.build_bar_chart(
        "Kategorite me te shpeshta te sulmeve",
        [(row["attack_category"], int(row["total"])) for row in top_categories_rows],
        "bar_chart_attack_categories.svg",
    )
    pie_chart = chart_builder.build_pie_chart(
        "Shperndarja e protokolleve",
        [(str(row["protocol"]), int(row["total"])) for row in top_protocol_rows],
        "pie_chart_protocols.svg",
    )
    line_chart = chart_builder.build_line_chart(
        "Top Destination Ports",
        sorted(
            [(str(row["destination_port"]), int(row["total"])) for row in top_ports_rows],
            key=lambda item: int(item[0]),
        ),
        "line_chart_destination_ports.svg",
    )
    dashboard_path = chart_builder.build_dashboard([bar_chart, pie_chart, line_chart])

    scraped_records = scraper.scrape_attack_records(limit=10)
    collector.write_json(
        outputs_dir / "scraped_unsw_ground_truth.json",
        {
            "source": "https://fkie-cad.github.io/COMIDDS/content/datasets/unsw_nb15/",
            "items": [record.to_csv_row() for record in scraped_records],
            "error": scraper.last_error,
        },
    )
    collector.write_csv(outputs_dir / "scraped_unsw_ground_truth.csv", scraped_records)

    combined_records = clean_records + scraped_records
    collector.write_csv(outputs_dir / "combined_cybersecurity_attacks.csv", combined_records)

    query_summary = {
        "top_categories": [row["attack_category"] for row in top_categories_rows[:3]],
        "top_protocols": [row["protocol"] for row in top_protocol_rows[:3]],
        "sample_filter_count": len(filtered_rows),
    }
    report_path = reporter.write_report(
        outputs_dir / "raport_dorezimi.txt",
        cleaner.stats,
        query_summary,
        len(scraped_records),
        scraper.last_error,
    )

    print("Projekti perfundoi me sukses.")
    print(f"Missing values para pastrimit: {missing_before}")
    print(f"Missing values pas pastrimit: {missing_after}")
    print(f"Rreshta para pastrimit: {cleaner.stats['rows_before']}")
    print(f"Rreshta pas pastrimit: {cleaner.stats['rows_after']}")
    print(f"Duplikate te larguara: {cleaner.stats['duplicates_removed']}")
    print(f"Grafiket u ruajten te: {outputs_dir}")
    print(f"Dashboard: {dashboard_path}")
    print(f"Raporti: {report_path}")
    print(f"CSV e scrape-uara: {outputs_dir / 'scraped_unsw_ground_truth.csv'}")
    print(f"CSV e kombinuar: {outputs_dir / 'combined_cybersecurity_attacks.csv'}")
    if scraper.last_error:
        print(f"Web scraping nuk u ekzekutua plotesisht: {scraper.last_error}")
    else:
        print(f"Web scraping perfundoi me {len(scraped_records)} rreshta sulmesh.")


if __name__ == "__main__":
    main()
