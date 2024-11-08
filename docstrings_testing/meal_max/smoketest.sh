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

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Combatants list cleared successfully."
  else
    echo "Failed to clear playlist."
    exit 1
  fi
}

test_prep_combatant_valid() {
  meal_name=$1
  echo "Testing prep combatant with valid meal: $meal_name..."
  
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_name\"}")

  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Valid meal test passed."
    if [ "$ECHO_JSON" = true ]; then
      echo "Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Valid meal test failed."
    exit 1
  fi
}

prep_combatant() {
  echo "Running smoke test for prep_combatant..."

  # Case 1: Valid meal test
  valid_response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d '{"meal": "Pasta"}')

  if echo "$valid_response" | grep -q '"status": "combatant prepared"'; then
    echo "Valid meal test passed."
    [ "$ECHO_JSON" = true ] && echo "Response JSON:" && echo "$valid_response" | jq .
  else
    echo "Valid meal test failed."
    exit 1
  fi

  # Case 2: Missing meal test
  missing_response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d '{}')

  if echo "$missing_response" | grep -q '"error": "You must name a combatant"'; then
    echo "Missing meal test passed."
    [ "$ECHO_JSON" = true ] && echo "Response JSON:" && echo "$missing_response" | jq .
  else
    echo "Missing meal test failed."
    exit 1
  fi

  # Case 3: Invalid meal name test (simulating error handling)
  invalid_response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d '{"meal": "InvalidMeal"}')

  if echo "$invalid_response" | grep -q '"error"'; then
    echo "Error handling test passed."
    [ "$ECHO_JSON" = true ] && echo "Response JSON:" && echo "$invalid_response" | jq .
  else
    echo "Error handling test failed."
    exit 1
  fi
}

# Health checks
check_health
check_db

# Battle model checks
clear_combatants
prep_combatant




