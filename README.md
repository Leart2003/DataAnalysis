# DataAnalysis Project

Ky projekt ploteson kerkesat e dorezimit per:

- Mbledhjen e te dhenave
- Pastrimin e te dhenave
- Klasa, objekte dhe funksione per secilen faze
- Mbushjen e te dhenave qe mungojne
- Largimin e duplikateve
- Leximin e te dhenave
- Shkrimin e queries dhe filters
- Paraqitjen grafike me 3 lloje grafikesh
- Web scraping

## Skedaret kryesore

- `main.py` - ekzekuton te gjithe projektin nga fillimi ne fund
- `data_collection.py` - leximi dhe shkrimi i te dhenave
- `data_cleaning.py` - pastrimi, normalizimi, mbushja e vlerave qe mungojne, largimi i duplikateve
- `query_engine.py` - krijimi i databazes SQLite dhe ekzekutimi i queries
- `visualization.py` - gjenerimi i grafikave SVG dhe dashboard-it HTML
- `web_scraper.py` - web scraping nga faqja e CISA
- `reporting.py` - krijimi i raportit perfundimtar
- `models.py` - klasat e objekteve

## Si ekzekutohet

```bash
python main.py
```

## Rezultatet

Pas ekzekutimit krijohet dosja `outputs/` me:

- `cleaned_cybersecurity_attacks.csv`
- `cybersecurity_attacks.db`
- `query_results.json`
- `scraped_cisa_advisories.json`
- `bar_chart_attack_categories.svg`
- `pie_chart_protocols.svg`
- `line_chart_destination_ports.svg`
- `dashboard.html`
- `raport_dorezimi.txt`
