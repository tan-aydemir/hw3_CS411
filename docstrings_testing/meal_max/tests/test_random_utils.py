import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal
from unittest.mock import patch, MagicMock
from meal_max.utils.random_utils import get_random
import requests

def test_get_random_success(mocker):
    """Test get_random() returns successfully"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "0.56"
    
    mocker.patch("requests.get", return_value=mock_response)
    
    result = get_random()
    assert result == 0.56, f"Expected 0.56 but got {result}"
    
def test_get_random_invalid_response(mocker):
    """Test get_random() random org receives invalid response"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Invalid number"
    
    mocker.patch("requests.get", return_value=mock_response)
    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()
        
def test_get_random_timeout(mocker):
    """Test get_random() timed out"""
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)
    with pytest.raises(RuntimeError, match="Request to random.org timed out."):
        get_random()
        
def test_get_random_request_exception(mocker):
    """Test get_random() encountered network error"""
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Network error"))
    
    with pytest.raises(RuntimeError, match="Request to random.org failed: Network error"):
        get_random()