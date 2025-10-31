#!/bin/bash

echo "Starting Bangla Plagiarism Checker..."
echo

echo "[1/3] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 not found! Please install Python 3.8+ first."
    exit 1
fi

echo "[2/3] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found! Please install Node.js 18+ first."
    exit 1
fi

echo "[3/3] Starting servers..."
echo

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Starting Backend Server..."
gnome-terminal --title="Bangla Plagiarism - Backend" -- bash -c "cd '$DIR/backend' && python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000; exec bash" 2>/dev/null || \
xterm -T "Bangla Plagiarism - Backend" -e "cd '$DIR/backend' && python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000; bash" 2>/dev/null || \
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR/backend' && python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000\"" 2>/dev/null &

sleep 3

echo "Starting Frontend Server..."
gnome-terminal --title="Bangla Plagiarism - Frontend" -- bash -c "cd '$DIR/frontend' && npm run dev; exec bash" 2>/dev/null || \
xterm -T "Bangla Plagiarism - Frontend" -e "cd '$DIR/frontend' && npm run dev; bash" 2>/dev/null || \
osascript -e "tell application \"Terminal\" to do script \"cd '$DIR/frontend' && npm run dev\"" 2>/dev/null &

echo
echo "==================================="
echo "  Bangla Plagiarism Checker Started"
echo "==================================="
echo
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to exit..."

# Keep script running
while true; do
    sleep 1
done