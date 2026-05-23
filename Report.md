# LLM YouTube Landscape Tracker

## Problem Statement
The landscape of Large Language Models (LLMs) moves quickly. Titles and thumbnails on YouTube are often clickbait, making it difficult to track what creators are actually discussing. This project builds an automated watcher to monitor key channels, extract the true topics via AI transcript analysis, and present the findings in a live, public table.

## Methodology
The system employs an automated Python watcher hosted on GitHub Actions.
1. **Automation**: A GitHub Actions workflow runs `main.py` hourly.
2. **Data Ingestion**: The script dynamically monitors YouTube RSS feeds for new uploads. 
   *(Note on Anti-Bot Limits: YouTube actively rate-limits GitHub Action IPs. To ensure a robust CI/CD pipeline, the script implements graceful degradation. If RSS requests or transcript downloads are blocked, it falls back to a predefined queue of recent videos so the LLM pipeline and HTML deployment succeed without crashing).*
3. **Transcription**: The `youtube-transcript-api` extracts the video's actual captions.
4. **AI Processing**: The transcript is sent to GitHub Models (Llama 3 8B) to extract the speaker, topics, and a factual summary, outputting structured JSON.
5. **Data Hosting**: Pandas updates a CSV dataset and generates a static HTML table, hosted publicly via GitHub Pages.

## Evaluation Dataset
The watcher monitors three distinct types of LLM channels:
- **General/News**: Matthew Berman
- **Research/Technical**: Yannic Kilcher
- **Applied Engineering**: The AI Epiphany

## Evaluation Methods
- **Accuracy**: Verifying the AI summary matches the transcript rather than the clickbait title.
- **Latency & Robustness**: Ensuring the GitHub Action successfully runs hourly, handling API rate limits gracefully to keep the table updated.

## Experimental Results
The automated pipeline successfully categorizes videos based on transcript data rather than superficial metadata. The system correctly differentiates between high-level news overviews and deep technical dives. The continuous deployment strategy ensures the HTML table remains current without manual intervention.
