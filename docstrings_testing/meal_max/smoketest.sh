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


# Smoke Test 2: Clear Combatants Route
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

# Smoke Test 3: Get Combatants Route
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

# Smoke Test 4: Prep Combatant Route
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

# Run the smoke tests


# clear_combatants
# get_combatants
prep_combatant "Pizza" "Italian" 12.99 "Easy"





