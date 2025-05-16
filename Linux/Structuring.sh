# Create main project directory
mkdir -p jarvis
cd jarvis

# Create the subdirectories
mkdir -p config core/{memory,llm,rag,agent/tools} voice integrations/{smart_home,personal,services} utils data/{vector_db,user_data,logs,credentials} ui tests/{unit,integration,fixtures}

# Create basic files
touch README.md .gitignore requirements.txt setup.py Dockerfile docker-compose.yml .env
touch config/{default_config.yaml,user_config.yaml}
