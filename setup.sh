#!/bin/bash

echo "Setting up LLM YouTube Tracker with Hugging Face models..."

python3 -m venv venv
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip

read -p "Do you have limited RAM/CPU? (y/n): " limited_ram
if [ "$limited_ram" = "y" ]; then
    echo "Installing lightweight dependencies..."
    pip install -r requirements-minimal.txt
    echo "Using lightweight analyzer (no ML models needed)"
else
    echo "Installing full dependencies..."
    pip install -r requirements.txt
    
    echo "Downloading ML models (this may take 10-30 minutes on first run)..."
    python model_download.py
fi

if [ ! -f .env ]; then
    cat > .env << EOF
YOUTUBE_API_KEY=your-youtube-api-key-here
DATABASE_URL=sqlite:///youtube_tracker.db
EOF
    echo "Created .env file. Please add your YouTube API key."
fi

mkdir -p templates

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your YouTube API key"
echo "2. Run the app: uvicorn main:app --reload"
echo "3. Open http://localhost:8000 in your browser"
echo ""
echo "For first run with full models, expect 5-10 minutes for model loading."
echo "Subsequent runs will be much faster (models are cached)."
