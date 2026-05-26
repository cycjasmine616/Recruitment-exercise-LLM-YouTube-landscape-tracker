# Recruitment exercise report: LLM YouTube landscape tracker

**Live Site:** [[https://cycjasmine616.github.io/Recruitment-exercise-LLM-YouTube-landscape-tracker/](https://cycjasmine616.github.io/Recruitment-exercise-LLM-YouTube-landscape-tracker/)]

**Repository:** [[GitHub Repository](https://github.com/cycjasmine616/Recruitment-exercise-LLM-YouTube-landscape-tracker)]

---

## Problem Statement
YouTube is flooded with LLM content. It is difficult for us to know **who** is speaking about **which** LLM topics, **what** they actually say, and **how channels relate** to each other on LLM themes just by the titles or thumbnail. 
This project set up an automated watcher that follows several YouTube channels, classify videos by the LLM topics discussed, and host a livesite tthat allow users to look at the table about the videos of these channels focusing on LLMs.

## Methodology
The pipeline runs in five steps:
1. **Data Collection**: YouTube Data API v3 searches for LLM-related videos across queries like "transformer attention mechanism," "LLM fine-tuning guide," and "RAG retrieval augmented generation," fetching 4 results per query from diverse channels.
2. **Topic Classification**: A keyword-based NLP analyzer classifies each video into 9 LLM categories (Transformer Architecture, Model Training, Prompt Engineering, RAG Systems, Model Evaluation, Safety & Alignment, Open Source LLMs, AI Agents, LLM Applications) by matching terms in titles and descriptions.
3. **Transcript Acquisition**: The `youtube-transcript-api` library attempts to fetch auto-generated captions for deeper analysis; videos without transcripts fall back to description-based classification.
4. **Channel Relationships**: Jaccard similarity is calculated between channel topic sets to identify which channels cover overlapping LLM themes.
5. **Deployment**: Results export as JSON files and a static HTML table, hosted publicly via GitHub Pages and updated through GitHub Codespaces for every 12 hours.

## Evaluation Dataset
The program analyzed **25 videos from 17 channels**, including:
- **Technical Education**: 3Blue1Brown, Google Cloud Tech, Strata, Under The Hood, Gal Lahat
- **Practical Tutorials**: Kevin Stratvert, Dave's Garage, David Ondrej, Warp, Nick Cornelius, antigravkids
- **General AI Enthusiasts**: Curious Steve, corbin, Adam Lucek
- **Enterprise & Industry**: IBM Technology, Ken Jee, Lex Fridman
- 
## Evaluation Methods
- **Topic Coverage**: 100% of videos received topic classifications across the 9 LLM categories
- **Channel Similarity**: Jaccard similarity scores (0-1 range) calculated for channel pairs sharing ≥2 topics, manually validated against content review
- **Transcript Success Rate**: 0 of 25 videos returned accessible transcripts, limiting deep content analysis to video descriptions and highlighting a key system constraint

## Experimental Results
The pipeline successfully classify 25 videos from 17 channels into structured LLM topics. **Model Training & Fine-tuning** and **Transformer Architecture** dominate coverage, while **Safety & Alignment** remains under-represented. 
Channel relationship analysis reveals four groups: a technical education group, a practical tutorials group, a general AI Enthusiasts group and an Enterprise & Industry group. 
However, it is failed to have the AI transcript of the videos or reliable caption due to YouTube API restrictions,  therefore the column of "What They Said About LLMs"" is replaced by the titles and the videos' descriptions.
