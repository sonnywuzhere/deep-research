#!/bin/bash

# Virtual Environment Setup Script for Deep Research Project
# This script creates a virtual environment and installs dependencies

echo "🔧 Setting up virtual environment for Deep Research project..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

echo ""
echo "✨ Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the Streamlit app, use:"
echo "  streamlit run app.py"
echo ""
