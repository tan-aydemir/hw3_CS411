from contextlib import contextmanager
import re
import sqlite3
import pytest
from unittest.mock import patch

from meal_max.models.kitchen_model import Meal, create_meal, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats
from meal_max.utils.sql_utils import get_db_connection

######################################################
#
#    Fixtures
#
######################################################

def normalize_whitespace(sql_query: str) -> str:
    return re.sub(r'\s+', ' ', sql_query).strip()

@pytest.fixture
def sample_meal():
    """Fixture that provides a sample meal instance."""
    return Meal(id=1, meal="Pizza", cuisine="Italian", price=5.00, difficulty="MED")

# Mocking the database connection for tests
@pytest.fixture
def mock_cursor(mocker):
    mock_conn = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Mock the connection's cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None  # Default return for queries
    mock_cursor.fetchall.return_value = []
    mock_cursor.commit.return_value = None

    # Mock the get_db_connection context manager from sql_utils
    @contextmanager
    def mock_get_db_connection():
        yield mock_conn  # Yield the mocked connection object

    mocker.patch("meal_max.models.kitchen_model.get_db_connection", mock_get_db_connection)

    return mock_cursor  # Return the mock cursor so we can set expectations per test


##################################################
# Create Meal test cases
##################################################

def test_create_meal(mock_cursor):
    """Test creating a new meal in the catalog."""
    
    # Call the function to create a new meal
    create_meal(meal="Pizza", cuisine="Italian", price=5.00, difficulty="MED")
    
    expected_query = normalize_whitespace("""
    INSERT INTO meals (meal, cuisine, price, difficulty)
        VALUES (?, ?, ?, ?)
    """)
    actual_query = normalize_whitespace(mock_cursor.execute.call_args[0][0])

    assert actual_query == expected_query

# Test error when creating a meal with a negative price
def test_create_meal_invalid_price():
    """Test creating a meal with an invalid price."""

    with pytest.raises(ValueError, match="Invalid price: -5.99. Price must be a positive number."):
        create_meal(meal="Pizza", cuisine="Italian", price=-5.99, difficulty="MED")

# Test error when creating a meal with an invalid difficulty level
def test_create_meal_invalid_difficulty():
    """Test creating a meal with an invalid difficulty level."""

    with pytest.raises(ValueError, match="Invalid difficulty level: EASY. Must be 'LOW', 'MED', or 'HIGH'."):
        create_meal(meal="Pizza", cuisine="Italian", price=5.00, difficulty="EASY")

##################################################
# Delete Meal test cases
##################################################


def test_delete_meal(mock_cursor):
    """Test soft deleting a meal from the catalog."""

    # Simulate that the meal exists (id = 1) and is not deleted
    mock_cursor.fetchone.return_value = [False] 

    # Call the delete_meal function
    delete_meal(1)

    expected_select_query = "SELECT deleted FROM meals WHERE id = ?"
    expected_update_query = "UPDATE meals SET deleted = TRUE WHERE id = ?"

    # Ensure correct SQL queries are executed
    actual_select_query = mock_cursor.execute.call_args_list[0][0][0]
    actual_update_query = mock_cursor.execute.call_args_list[1][0][0]

    assert actual_select_query.strip() == expected_select_query.strip()
    assert actual_update_query.strip() == expected_update_query.strip()

##################################################
# Update Meal test cases
##################################################

# def test_update_meal_stats_invalid_result():
#     """Test updating meal stats with an invalid result."""
    
#     # We want to check if the ValueError is raised when an invalid result is passed
#     with pytest.raises(ValueError, match="Invalid result: invalid. Expected 'win' or 'loss'."):
#         update_meal_stats(1, 'invalid')

def test_get_meal_by_id(mock_cursor):
    """Test retrieving a meal by its ID."""

    # Simulate that the meal exists (id = 1)
    mock_cursor.fetchone.return_value = [1, "Pizza", "Italian", 5.00, "MED", False]

    # Call the function to get the meal by ID
    meal = get_meal_by_id(1)

    assert meal.id == 1
    assert meal.meal == "Pizza"
    assert meal.cuisine == "Italian"
    assert meal.price == 5.00
    assert meal.difficulty == "MED"

# Test getting a meal by name
def test_get_meal_by_name(mock_cursor):
    """Test retrieving a meal by its name."""

    # Simulate that the meal exists (name = "Pizza")
    mock_cursor.fetchone.return_value = [1, "Pizza", "Italian", 5.00, "MED", False]

    # Call the function to get the meal by name
    meal = get_meal_by_name("Pizza")

    assert meal.id == 1
    assert meal.meal == "Pizza"
    assert meal.cuisine == "Italian"
    assert meal.price == 5.00
    assert meal.difficulty == "MED"
