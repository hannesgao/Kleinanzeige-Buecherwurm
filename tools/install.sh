#!/bin/bash
# Installation script for Kleinanzeigen Crawler

set -e

echo "🚀 Kleinanzeigen Crawler Installation Script"
echo "============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   echo "Please run as a regular user"
   exit 1
fi

# Check Python version
echo "🐍 Checking Python version..."
python3 --version || {
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
}

# Check if pip3 is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    echo "Please install python3-pip"
    echo "Ubuntu: sudo apt install python3-pip"
    exit 1
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip3 install --upgrade pip

# Install requirements
echo "📥 Installing Python packages..."
pip3 install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data

# Set up environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Setting up environment file..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "⚠️  Please edit .env with your database and email settings"
else
    echo "✅ .env file already exists"
fi

# Check Chrome installation
echo "🌐 Checking Chrome browser..."
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo "✅ Chrome browser found"
else
    echo "⚠️  Chrome browser not found"
    echo "Please install Google Chrome or Chromium browser"
    echo "Ubuntu: sudo apt install google-chrome-stable"
fi

# Run setup check
echo "🔍 Running setup verification..."
python3 tools/check_setup.py

echo ""
echo "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Run: python main.py --init-db"
echo "3. Test: python main.py --test --headless"
echo "4. Run: python main.py --schedule"
echo ""
echo "For help: python main.py --help"