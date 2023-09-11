# If virtual environment doesn't exist
if [ ! -d ".venv" ]; then
	# Create virtual environment
	python3 -m venv .venv

	# Activate virtual environment
	source .venv/bin/activate

	# Install dependencies
	#@REVISIT
	pip install -e .

# If virtual environment already exists
else
	# Activate virtual environment
	source .venv/bin/activate
fi

# cd to project root
cd src

# Run server
python manage.py runserver
