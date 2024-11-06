import pytest
from meal_max.models.kitchen_model import Meal, create_meal, delete_meal, get_leaderboard
from meal_max.utils.sql_utils import get_db_connection

@pytest.fixture
def sample_meal():
    """Fixture that provides a sample meal instance."""
    return Meal(id=1, meal="Pizza", cuisine="Italian", price=5.0, difficulty="LOW")

@pytest.fixture
def db_conn():
    """Fixture to set up and tear down a temporary database connection."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal TEXT UNIQUE,
            cuisine TEXT,
            price REAL,
            difficulty TEXT,
            deleted BOOLEAN DEFAULT FALSE
        )
    """)
    conn.commit()
    yield conn
    conn.close()

##################################################
# Create meal test cases
##################################################