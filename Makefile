VERSiON = 1.0.0

install_dependencies:
	@echo "Installing dependencies..."
	@pip install --upgrade pip
	@pip install --upgrade pip-tools
	@pip-compile requirements.in --upgrade
	@pip install -r requirements.txt
	@echo "Dependencies installed."

lint:
	@echo "Running lint..."
	@flake8 --ignore=E501,W503,E203 ./Bit
	@echo "Lint done."

black:
	@echo "Running black..."
	@black ./Bit
	@echo "Black done."

mypy:
	@echo "Running mypy..."
	@mypy ./Bit
	@echo "Mypy done."

test: lint black mypy
	# @echo "Running tests..."
	# @python3 -m unittest discover -s ./Bit -p "*_test.py"
	@echo "Tests done."

run_bit:
	@echo "Running bit..."
	@python3 ./Bit/main.py >> trading.log 2>&1 &

docker_build:
	@echo "Building Kraken BTC trading docker agent image..."
	@docker build -t kraken-btc-trading-agent:$(VERSiON) .

deployment: docker_build
	@echo "Deploying agents..."
	@docker-compose up

