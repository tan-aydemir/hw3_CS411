#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}

##########################################################
#
# Meal Management
#
##########################################################

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal - $cuisine, $price, $difficulty) to the meal table..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":$difficulty}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

clear_meals() {
  echo "Clearing meals..."
  response=$(curl -s -X POST "$BASE_URL/clear-meals")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meals cleared successfully."
  else
    echo "Failed to clear meals."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (name $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}

############################################################
#
# Leaderboard
#
############################################################

get_leaderboard() {
  echo "Retrieving leaderboard..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve leaderboard."
    exit 1
  fi
}

############################################################
#
# Arrange Playlist
#
############################################################
# Smoke Test 1: Battle Route
battle() {
  echo "Initiating battle..."
  
  # Make a GET request to the /api/battle endpoint
  response=$(curl -s -w "%{http_code}" -o /tmp/response.json -X GET "$BASE_URL/battle")
  
  # Check the HTTP response code and verify if it's 200 (OK)
  if [ "$response" -ne 200 ]; then
    echo "Error: HTTP response code $response. Battle initiation failed."
    cat /tmp/response.json
    exit 1
  fi
  
  # Check if the response contains the expected status and winner
  if echo "$response" | jq -e '.status == "battle complete"' > /dev/null && echo "$response" | jq -e '.winner != null' > /dev/null; then
    echo "Battle completed successfully."
  else
    echo "Failed to initiate battle."
    cat /tmp/response.json
    exit 1
  fi
}


# Smoke Test 2: Clear Combatants
clear_combatants() {
  echo "Clearing all combatants..."
  
  # Sending the POST request to the full API URL
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  # Check if the response contains the expected status
  if echo "$response" | grep -q '"status": "combatants cleared"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants. Response was: $response"
    exit 1
  fi
}

# Smoke Test 3: Get Combatants
get_combatants() {
  echo "Retrieving combatants..."
  response=$(curl -s -X GET "$BASE_URL/api/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve combatants."
    exit 1
  fi
}

# Smoke Test 4: Prep Combatant
prep_combatant() {
  meal_name=$1
  cuisine=$2
  price=$3
  difficulty=$4

  if [ -z "$meal_name" ] || [ -z "$cuisine" ] || [ -z "$price" ] || [ -z "$difficulty" ]; then
    echo "Please provide all required meal attributes: meal, cuisine, price, and difficulty."
    exit 1
  fi

  echo "Preparing combatant meal: $meal_name"
  
  # Construct the meal JSON object
  meal_json=$(cat <<EOF
{
  "meal": "$meal_name",
  "cuisine": "$cuisine",
  "price": $price,
  "difficulty": "$difficulty"
}
EOF
)

  # Send the POST request with the meal data
  response=$(curl -s -X POST "$BASE_URL/api/prep-combatant" -H "Content-Type: application/json" -d "$meal_json")

  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Combatant $meal_name prepared successfully."
  else
    echo "Failed to prepare combatant."
    exit 1
  fi
}

############################################################
#
# Run Smoke Tests
#
############################################################

# Health checks
check_health
check_db

# Create meals
create_meal "Pizza" "Italian" 5.00 "MED"
create_meal "Pasta" "Italian" 10.00 "LOW"
create_meal "Tacos" "Mexican" 7.00 "MED"
create_meal "Sushi" "Japanese" 20.00 "HIGH"
create_meal "Burger" "American" 9.00 "LOW"

# Delete meals
delete_meal_by_id 1
delete_meal_by_id 2

# Get meals

get_meal_by_id 3
get_meal_by_name "Sushi"

get_leaderboard

# Clear meals
clear_meals

# Playlist tests
battle
clear_combatants
get_combatants
prep_combatant "Pizza" "Italian" 12.99 "Easy"





