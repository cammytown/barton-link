Under heavy development.

# Barton Link
## Search and filter your revelations.

Barton Link is a tool for writers to organize excerpts of writing before (and after) they have been used in a writer's larger work.

Setup
```shell
cd barton-link/

# Optionally create and activate venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .[all] # See pyproject.toml for optional-dependencies

# Setup database with Django
cd src/
python manage.py makemigrations
python manage.py migrate
```

Running Server
```shell
cd src/
python manage.py runserver
```

Development (requires SASS)
```shell
./dev-setup.sh
```

# Features
- Tag excerpts.
- NLP (Natural Language Processing)
    - Determine semantic similarity between excerpts.
    - Automatically tag excerpts.
