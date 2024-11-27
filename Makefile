install_dependencies:
	@echo "Installing dependencies..."
	@pip install --upgrade pip
	@pip install --upgrade pip-tools
	@pip-compile requirements.in --upgrade
	@pip install -r requirements.txt
	@echo "Dependencies installed."

run_bit:
	@echo "Running bit..."
	@python3 ./Bit/main.py >> trading.log 2>&1 &

docker_build:
	@echo "Building docker image..."
	@docker build -t kraken-trading-bot:0.0.1 .

