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

def test_create_meal(db_conn):
    """Test for creating a new meal."""
    create_meal("Tacos", "Mexican", 10.0, "MED")
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM meals WHERE meal = ?", ("Tacos",))
    meal = cursor.fetchone()
    assert meal is not None
    assert meal[1] == "Tacos"
    assert meal[2] == "Mexican"
    assert meal[3] == 10.0
    assert meal[4] == "MED"

def test_create_meal_duplicate(db_conn):
    """Test where creating a duplicate meal raises an error."""
    create_meal("Tacos", "Mexican", 10.0, "MED")
    with pytest.raises(ValueError, match="Meal with name 'Tacos' already exists"):
        create_meal("Tacos", "Mexican", 10.0, "MED")


def test_create_meal_invalid_price(db_conn):
    """Test where creating a meal with an invalid price raises an error."""
    with pytest.raises(ValueError, match="Invalid price"):
        create_meal("Tacos", "Mexican", -10.0, "MED")

def test_create_meal_invalid_difficulty(db_conn):
    """Test where creating a meal with an invalid difficulty level raises an error."""
    with pytest.raises(ValueError, match="Invalid difficulty level"):
        create_meal("Tacos", "Mexican", 10.0, "EXPERT")


