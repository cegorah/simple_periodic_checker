import pytest


async def test_default_tables(database):
    await database.raw_query(
        """
        SELECT * FROM {}
        """, table_name="ProcessedResult"
    )
    await database.raw_query(
        """
        SELECT * FROM {}
        """, table_name="RawResult"
    )
    await database.raw_query(
        """
        SELECT * FROM {}
        """, table_name="Process"
    )
    await database.raw_query(
        """
        SELECT * FROM {}
        """, table_name="Tasks"
    )


async def test_table_works(database):
    db = database
    await db.raw_query(
        """
        CREATE TABLE IF NOT EXISTS TestTable(
            id SERIAL PRIMARY KEY 
        )
        """
    )
    await db.raw_query(
        """
        SELECT * FROM {}
        """, table_name="TestTable"
    )
    await db.raw_query(
        """
        DROP TABLE TestTable
        """
    )


@pytest.mark.xfail
async def test_table_not_exists(database):
    await database.raw_query(
        """
        DROP TABLE TestTable1
        """
    )
