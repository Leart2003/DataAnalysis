from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from models import AttackRecord


class SQLiteQueryEngine:
    # Ruajme rrugen e databazes SQLite.
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)

    # Krijon databazen dhe fut te gjitha rekordet e pastruara ne tabelen attacks.
    def build_database(self, records: list[AttackRecord]) -> None:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS attacks")
            cursor.execute(
                """
                CREATE TABLE attacks (
                    attack_category TEXT,
                    attack_subcategory TEXT,
                    protocol TEXT,
                    source_ip TEXT,
                    source_port TEXT,
                    destination_ip TEXT,
                    destination_port TEXT,
                    attack_name TEXT,
                    attack_reference TEXT,
                    marker TEXT,
                    time_range TEXT,
                    attack_year INTEGER
                )
                """
            )
            cursor.executemany(
                """
                INSERT INTO attacks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        record.attack_category,
                        record.attack_subcategory,
                        record.protocol,
                        record.source_ip,
                        record.source_port,
                        record.destination_ip,
                        record.destination_port,
                        record.attack_name,
                        record.attack_reference,
                        record.marker,
                        record.time_range,
                        record.start_year(),
                    )
                    for record in records
                ],
            )
            connection.commit()

    # Ekzekuton nje query SQL dhe kthen rezultatin si liste dictionaries.
    def run_query(self, sql: str, params: tuple = ()) -> list[dict[str, object]]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(sql, params)
            return [dict(row) for row in cursor.fetchall()]

    # Nderton nje filter sipas kushteve qe i japim dhe kthen rezultatet.
    def filter_attacks(
        self,
        category: str | None = None,
        protocol: str | None = None,
        destination_port: str | None = None,
        keyword: str | None = None,
        limit: int = 20,
    ) -> list[dict[str, object]]:
        clauses: list[str] = []
        params: list[object] = []
        if category:
            clauses.append("attack_category = ?")
            params.append(category)
        if protocol:
            clauses.append("protocol = ?")
            params.append(protocol.lower())
        if destination_port:
            clauses.append("destination_port = ?")
            params.append(destination_port)
        if keyword:
            clauses.append("attack_name LIKE ?")
            params.append(f"%{keyword}%")
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT attack_category, attack_subcategory, protocol, destination_port, attack_name
            FROM attacks
            {where_sql}
            LIMIT ?
        """
        params.append(limit)
        return self.run_query(sql, tuple(params))

    # Ruan rezultatet e query-ve ne file JSON.
    def export_json(self, output_path: str | Path, payload: object) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
