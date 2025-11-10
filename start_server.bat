@echo off
echo ========================================
echo Distributed Jupyter Server
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo Python OK
echo.

REM Install server dependencies
echo [2/4] Installing server dependencies...
cd server
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Error: Failed to install server dependencies
    cd ..
    pause
    exit /b 1
)
echo Server dependencies OK
cd ..
echo.

REM Check if client is built
echo [3/4] Checking client build...
if exist "client\dist\index.html" (
    echo Client build found
) else (
    echo Client not built. Building now...
    cd client
    
    REM Check Node.js
    node --version >nul 2>&1
    if errorlevel 1 (
        echo Error: Node.js is not installed
        echo Please install Node.js from https://nodejs.org/
        cd ..
        pause
        exit /b 1
    )
    
    REM Install and build
    echo Installing client dependencies...
    call npm install
    if errorlevel 1 (
        echo Error: Failed to install client dependencies
        cd ..
        pause
        exit /b 1
    )
    
    echo Building client...
    call npm run build
    if errorlevel 1 (
        echo Error: Failed to build client
        cd ..
        pause
        exit /b 1
    )
    
    cd ..
    echo Client build complete
)
echo.

REM Initialize database
echo [4/4] Checking configuration...
if not exist "config\config.yaml" (
    echo Config file not found. Creating from example...
    copy config\config.example.yaml config\config.yaml
    echo.
    echo ========================================
    echo IMPORTANT: Please edit config\config.yaml
    echo - Change secret_key
    echo - Set admin_emails
    echo - Set whitelist_emails
    echo ========================================
    echo.
    pause
)

echo Initializing database...
cd server
python setup_db.py
if errorlevel 1 (
    echo Warning: Database initialization had issues
)
cd ..
echo.

REM Start server
echo ========================================
echo Starting Distributed Jupyter Server
echo ========================================
echo.
echo Access the application at:
echo   http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python main.py

pause
