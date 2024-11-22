#!/bin/bash

# Path to backend and frontend directories
BACKEND_DIR="/Users/alexclassen/git/pngEx/backend"
FRONTEND_DIR="/Users/alexclassen/git/pngEx/frontend"

# Check for arguments
if [ "$1" == "start" ]; then
    echo "Starting Flask backend and React frontend..."

    # Navigate to backend directory and start Flask
    cd $BACKEND_DIR
    nohup python3 main.py > backend.log 2>&1 &  # Run Flask in the background
    echo $! > flask.pid  # Save Flask process ID

    # Navigate to frontend directory and start React
    cd $FRONTEND_DIR
    nohup npm start > frontend.log 2>&1 &  # Run React in the background
    echo $! > react.pid  # Save React process ID

    echo "Flask backend and React frontend started successfully!"

elif [ "$1" == "stop" ]; then
    echo "Stopping Flask backend and React frontend..."

    # Stop Flask backend
    if [ -f flask.pid ]; then
        kill $(cat flask.pid)
        rm flask.pid
        echo "Flask backend stopped."
    else
        echo "Flask backend is not running."
    fi

    # Stop React frontend
    if [ -f react.pid ]; then
        kill $(cat react.pid)
        rm react.pid
        echo "React frontend stopped."
    else
        echo "React frontend is not running."
    fi

else
    echo "Usage: $0 {start|stop}"
fi
