#! /bin/bash

# Stop on error
set -e

# Get Python version
PYTHON_VERSION=$(python3 --version | grep -Eo '([0-9]+\.)+[0-9]+')

# Check if Python version is within acceptable range (3.9-3.13)
if [[ "$PYTHON_VERSION" > "3.13" ]] || [[ "$PYTHON_VERSION" < "3.9" ]]; then
	# Check for python3.12
	if command -v python3.12 &> /dev/null; then
		PYTHON_CMD="python3.12"
	else
		echo "Error: Requires Python version between 3.9 and 3.13, or python3.12"
		echo "Current version: $PYTHON_VERSION"
		exit 1
	fi
else
	PYTHON_CMD="python3"
fi

# If virtual environment doesn't exist
if [ ! -d ".venv" ]; then
	# Create virtual environment
	$PYTHON_CMD -m venv .venv --prompt "barton-link"

	# Activate virtual environment
	source .venv/bin/activate

	# Install dependencies
	pip install -e .[all]

# If virtual environment already exists
else
	# Activate virtual environment
	source .venv/bin/activate
fi

# cd to project root
cd src

# Run server
$PYTHON_CMD manage.py runserver
