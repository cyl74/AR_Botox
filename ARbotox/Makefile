# Define the virtual environment directory
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python3
PIP = $(VENV_DIR)/bin/pip

$(VENV_DIR)/bin/activate:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

.PHONY: install_package
install_package: $(VENV_DIR)/bin/activate
	$(PIP) install $(get)

# New install rule
install: $(VENV_DIR)/bin/activate
	@echo "Installing virtual environment and all dependencies for ARbotox."
	$(PIP) install -r requirements.txt

run: $(VENV_DIR)/bin/activate
	@echo "Running ARbotox..."
	$(PYTHON) main.py

# Run using MediaPipe version
run_mediapipe: $(VENV_DIR)/bin/activate
	@echo "Running ARbotox with MediaPipe..."
	$(PYTHON) main_mediapipe.py

clean:
	rm -rf $(VENV_DIR)
	rm -rf __pycache__

.PHONY: install run run_mediapipe clean

