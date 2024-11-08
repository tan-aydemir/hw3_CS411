import pytest
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal


"""
Functions to consider

init
battle(self)
clear_combatants(self)
get_battle_score(self, combatant: Meal)
get_combatants(self)
prep_combatant(self, combatant_data: Meal)
"""

@pytest.fixture()
def battle_model():
    return BattleModel()

@pytest.fixture
def sample_meal1():
    return Meal(1, "Meal-1", "Turkish", 29, 'HIGH')

@pytest.fixture
def sample_meal2():
    return Meal(2, "Meal-2", "Italian", 27, 'MED')

@pytest.fixture
def sample_combatants(sample_meal1, sample_meal2):
    return [sample_meal1, sample_meal2]


##################################################
# Combatant Unit Test Cases
##################################################
def test_get_combatants(battle_model, sample_combatants):
    """Test getting the list of combatants"""
    battle_model.combatants.extend(sample_combatants)
    
    # Check if lengths match
    assert len(battle_model.combatants) == len(sample_combatants), f"Expected {len(battle_model.combatants)} combatants, but got {len(sample_combatants)}"

    result = battle_model.get_combatants()
    
    assert result == sample_combatants or result[::-1] == sample_combatants, f"Expected {sample_combatants}, but got {battle_model.combatants}"
    assert len(battle_model.combatants) == 2, f"Expected length: 2, but received {len(battle_model.combatants)}"
    
def test_prep_combatants(battle_model, sample_meal1, sample_meal2, sample_combatants):
    """Test adding a meal to the combatant list. Make sure that attributes also match"""
    battle_model.combatants = []
    battle_model.prep_combatant(sample_meal1)
    # Check if lengths match
    assert len(battle_model.combatants) == 1, f"Expected length to be 1, but got {len(battle_model.combatants)}"
    
    # Check if contents match
    current_meal = battle_model.combatants[0]
    # Check if id matches
    assert current_meal.id == sample_meal1.id, f"Expected an ID of {sample_meal1.id}, but got {current_meal.id}"
    # Check if meal matches
    assert current_meal.meal == sample_meal1.meal, f"Expected a meal called {sample_meal1.meal}, but got {current_meal.meal}"
    # Check if cuisine matches
    assert current_meal.cuisine == sample_meal1.cuisine, f"Expected a cuisine called {sample_meal1.cuisine}, but got {current_meal.cuisine}"
    # Check if price matches
    assert current_meal.price == sample_meal1.price, f"Expected a cuisine called {sample_meal1.price}, but got {current_meal.price}"
    # Check if difficulty matches
    assert current_meal.difficulty == sample_meal1.difficulty, f"Expected a difficulty of {sample_meal1.difficulty}, but got {current_meal.difficulty}"
    
    
def test_prep_combatants_list_full(battle_model, sample_combatants, sample_meal1):
    "Test prep_combatants_list raises error for when the list is full"
    battle_model.combatants.extend(sample_combatants)
    with pytest.raises(ValueError, match="Combatant list is full, cannot add more combatants."):
        battle_model.prep_combatant(sample_meal1)

def test_clear_combatants(battle_model, sample_combatants):
    """Test clearing the entire list"""
    battle_model.combatants.extend(sample_combatants)
    battle_model.clear_combatants()
    assert len(battle_model.combatants) == 0, f"Combatant list should be empty after it's cleared. "
   
def test_get_battle_score(battle_model, sample_combatants, sample_meal1):
    battle_model.combatants.extend(sample_combatants)
    
    # Check if difficulties match
    assert battle_model.combatants[0].difficulty == sample_meal1.difficulty, "Difficulties must be equal"
    
    test_result = (sample_meal1.price * len(sample_meal1.cuisine)) - 1
    result = battle_model.get_battle_score(battle_model.combatants[0])
    
    assert result == test_result, f"The battle score must be {test_result}, but {result} was received"
    
def test_battle(battle_model, sample_combatants):
    battle_model.combatants.extend(sample_combatants)
    result = battle_model.battle()
    assert result in {"Turkish", "Italian"}, "Returned meal is not accurate"
    
def test_battle_not_enough_combatants(battle_model):
    "Test battle() raises error when list doesn't have 2 combatants in it"
    battle_model.combatants = []
    battle_model.combatants.append(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped for a battle."):
        battle_model.battle()
    
