from contextlib import contextmanager
import re
import sqlite3
import pytest
from unittest.mock import patch

from meal_max.models.kitchen_model import Meal, create_meal, clear_meals, delete_meal, get_leaderboard, get_meal_by_id, get_meal_by_name, update_meal_stats
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

def test_create_meal_duplicate(mock_cursor):
    """Test creating a meal with a duplicate cuisine, price, and difficulty (should raise an error)."""

    # Simulate that the database will raise an IntegrityError due to a duplicate entry
    mock_cursor.execute.side_effect = sqlite3.IntegrityError("UNIQUE constraint failed: meals.cuisine, meals.price, meals.difficulty")

    # Expect the function to raise a ValueError with a specific message when handling the IntegrityError
    with pytest.raises(ValueError, match="Meal with name 'Pizza' already exists"):
        create_meal(meal="Pizza", cuisine="Italian", price=5.00, difficulty="MED")


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
# Clear Meals test case
##################################################

def test_clear_meals(mock_cursor, mocker):
    """Test clearing the entire meal table (removes all meals)."""

    # Mock the file reading
    mocker.patch.dict('os.environ', {'SQL_CREATE_TABLE_PATH': 'sql/create_meal_table.sql'})
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="The body of the create statement"))

    # Call the clear_database function
    clear_meals()

    # Ensure the file was opened using the environment variable's path
    mock_open.assert_called_once_with('sql/create_meal_table.sql', 'r')

    # Verify that the correct SQL script was executed
    mock_cursor.executescript.assert_called_once()

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

def test_delete_meal_bad_id(mock_cursor):
    """Test error when trying to delete a non-existent meal."""

    # Simulate that no meal exists with the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when attempting to delete a non-existent meal
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        delete_meal(999)

def test_delete_meal_already_deleted(mock_cursor):
    """Test error when trying to delete a meal that's already marked as deleted."""

    # Simulate that the meal exists but is already marked as deleted
    mock_cursor.fetchone.return_value = ([True])

    # Expect a ValueError when attempting to delete a meal that's already been deleted
    with pytest.raises(ValueError, match="Meal with ID 999 has been deleted"):
        delete_meal(999)


##################################################
# Get Meal test cases
##################################################


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

def test_get_meal_by_id_bad_id(mock_cursor):
    # Simulate that no meal exists for the given ID
    mock_cursor.fetchone.return_value = None

    # Expect a ValueError when the meal is not found
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

##################################################
# Update Meal Stats test cases
##################################################

def test_update_meal_stats_win(mock_cursor):
    """Test updating the battle stats when result is 'win'"""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and result
    meal_id = 1
    result = "win"
    update_meal_stats(meal_id, result)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?
    """)

     # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID, reasult)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."


def test_update_meal_stats_loss(mock_cursor):
    """Test updating the battle stats when result is 'loss'"""

    # Simulate that the meal exists and is not deleted (id = 1)
    mock_cursor.fetchone.return_value = [False]

    # Call the update_meal_stats function with a sample meal ID and result
    meal_id = 1
    result = "loss"
    update_meal_stats(meal_id, result)

    # Normalize the expected SQL query
    expected_query = normalize_whitespace("""
        UPDATE meals SET battles = battles + 1 WHERE id = ?
    """)

     # Ensure the SQL query was executed correctly
    actual_query = normalize_whitespace(mock_cursor.execute.call_args_list[1][0][0])

    # Assert that the SQL query was correct
    assert actual_query == expected_query, "The SQL query did not match the expected structure."

    # Extract the arguments used in the SQL call
    actual_arguments = mock_cursor.execute.call_args_list[1][0][1]

    # Assert that the SQL query was executed with the correct arguments (meal ID, reasult)
    expected_arguments = (meal_id,)
    assert actual_arguments == expected_arguments, f"The SQL query arguments did not match. Expected {expected_arguments}, got {actual_arguments}."

### Test for Updating a Deleted Meal:
def test_update_meal_stats_deleted_meal(mock_cursor):
    """Test error when trying to update stats for a deleted meal."""

    # Simulate that the meal exists but is marked as deleted (id = 1)
    mock_cursor.fetchone.return_value = [True]

    # Expect a ValueError when attempting to update a deleted meal
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        update_meal_stats(1, "win")

    # Ensure that no SQL query for updating meal count was executed
    mock_cursor.execute.assert_called_once_with("SELECT deleted FROM meals WHERE id = ?", (1,))