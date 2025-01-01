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
	@echo "Building btc docker image..."
	@docker build -t btc-trading-bot:0.1.5 .
	# @echo "Building eth docker image..."
	# @docker build -t eth-trading-bot:0.1.5 ./ETH/.
	# @echo "Building xrp docker image..."
	# @docker build -t xrp-trading-bot:0.1.5 ./XRP/.

deployment: docker_build
	@echo "Deploying agents..."
	@docker-compose up

run_btc_unittests:
	pytest BTC/

check_test_coverage:
	pytest --cov=BTC/ --cov-report=term-missing

