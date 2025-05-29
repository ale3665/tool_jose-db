from pathlib import Path
from pandas import DataFrame
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    Engine,
)


class DB:
    def __init__(self, fp: Path) -> None:
        self.engine: Engine = create_engine(f"sqlite:///{fp}")
        self.metadata: MetaData = MetaData()

    def create_tables(self) -> None:
        Table(
            "front_matter",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("url", String, nullable=False),
            Column("html", String, nullable=False),
            Column("page", Integer, nullable=False),
        )

        Table(
            "metadata",
            self.metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("url", String, nullable=False),
            Column("title", String, nullable=False),
            Column("publication_date", String, nullable=True),
            Column("authors", String, nullable=True),
            Column("status", String, nullable=True),
        )

        self.metadata.create_all(bind=self.engine, checkfirst=True)

    def df2table(self, df: DataFrame, table: str) -> None:
        df.to_sql(
            name=table,
            con=self.engine,
            if_exists="append",
            index=False,
        )

