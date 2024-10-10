#!/bin/bash

# Update package list and install system dependencies
sudo apt update
sudo apt install -y iverilog
sudo apt install -y graphviz graphviz-dev

# Install Python packages from requirements.txt
python3 -m pip install -r requirements.txt

# Reinstall Pygraphviz after graphviz-dev has been installed
python3 -m pip install pygraphviz

# Notify user of completion
echo "All dependencies have been installed successfully!"

