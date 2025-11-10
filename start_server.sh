#!/bin/bash

echo "========================================"
echo "Distributed Jupyter Server"
echo "========================================"
echo ""

# Check Python
echo "[1/4] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python is not installed"
    exit 1
fi
echo "Python OK"
echo ""

# Install server dependencies
echo "[2/4] Installing server dependencies..."
cd server
pip3 install -r requirements.txt > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Error: Failed to install server dependencies"
    cd ..
    exit 1
fi
echo "Server dependencies OK"
cd ..
echo ""

# Check if client is built
echo "[3/4] Checking client build..."
if [ -f "client/dist/index.html" ]; then
    echo "Client build found"
else
    echo "Client not built. Building now..."
    cd client
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo "Error: Node.js is not installed"
        echo "Please install Node.js from https://nodejs.org/"
        cd ..
        exit 1
    fi
    
    # Install and build
    echo "Installing client dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install client dependencies"
        cd ..
        exit 1
    fi
    
    echo "Building client..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build client"
        cd ..
        exit 1
    fi
    
    cd ..
    echo "Client build complete"
fi
echo ""

# Check configuration
echo "[4/4] Checking configuration..."
if [ ! -f "config/config.yaml" ]; then
    echo "Config file not found. Creating from example..."
    cp config/config.example.yaml config/config.yaml
    echo ""
    echo "========================================"
    echo "IMPORTANT: Please edit config/config.yaml"
    echo "- Change secret_key"
    echo "- Set admin_emails"
    echo "- Set whitelist_emails"
    echo "========================================"
    echo ""
    read -p "Press Enter to continue..."
fi

# Initialize database
echo "Initializing database..."
cd server
python3 setup_db.py
if [ $? -ne 0 ]; then
    echo "Warning: Database initialization had issues"
fi
cd ..
echo ""

# Start server
echo "========================================"
echo "Starting Distributed Jupyter Server"
echo "========================================"
echo ""
echo "Access the application at:"
echo "  http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

python3 main.py
