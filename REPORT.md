# Recruitment exercise report: LLM YouTube landscape tracker

**Live Site:** [[https://cycjasmine616.github.io/Recruitment-exercise-LLM-YouTube-landscape-tracker/](https://cycjasmine616.github.io/Recruitment-exercise-LLM-YouTube-landscape-tracker/)]

**Repository:** [[GitHub Repository](https://github.com/cycjasmine616/Recruitment-exercise-LLM-YouTube-landscape-tracker)]

---

## Problem Statement
YouTube includes a lot of videos related to LLMs theme.Thus, it is difficult for us to know **who** is speaking about **which** LLM topics, **what** they actually say, and **how channels relate** to each other on LLM themes just by the titles or thumbnail. 
This project set up an automated watcher that follows several YouTube channels, classify videos by the LLM topics it discussed, and host a livesite that allow users to look at the table to find the category  of videos they want of these channels focusing on LLMs.

## Methodology
The pipeline runs in five steps:
1. **Data Collection**: The YouTube Data API searches across queries like *"transformer attention mechanism,"* *"LLM fine-tuning guide,"* and *"RAG retrieval augmented generation,"* pulling 4 results per query from whichever channels appear.
   
2. **Topic Classification**:  A keyword-based analyser scans each video's title and description, slotting it into one or more of 9 LLM categories: Transformer Architecture, Model Training, Prompt Engineering, RAG Systems, Model Evaluation, Safety & Alignment, Open Source LLMs, AI Agents, and LLM Applications.
 
4. **Transcript Acquisition**: The `youtube-transcript-api` library attempts to fetch auto-generated captions for deeper analysis; videos without transcripts fall back to description-based classification.
   
5. **Channel Relationships**: Jaccard similarity compares the sets of topics each channels covers, so that we can have the channels overlap the most on LLM themes.
   
6. **Deployment**: Results export as JSON files and a static HTML table, hosted on GitHuB Page publicly and updated through GitHub Codespaces every 12 hours or through the GitHub Action.

## Evaluation Dataset
The program analyzed **25 videos from 17 channels**, including:
- **Technical Education**: 3Blue1Brown, Google Cloud Tech, Strata, Under The Hood, Gal Lahat
- **Practical Tutorials**: Kevin Stratvert, Dave's Garage, David Ondrej, Warp, Nick Cornelius, antigravkids
- **General AI Enthusiasts**: Curious Steve, corbin, Adam Lucek
- **Enterprise & Industry**: IBM Technology, Ken Jee, Lex Fridman
- 
## Evaluation Methods
The system was evaluated on three aspects, whether every video got tagged with relevant topics, whether channel similarity scores matched a manual spot-check, and whether transcripts were actually recoverable.
- **Topic Coverage**: All videos received at least 1 toopic label from the 9 LLM categories, including: General AI, Model Training, AI Agents, Transformer Architecture, Multimodal, Transformer Architecture, Model Evaluation, RAG Systems and Open Source LLMs.
- **Channel Similarity**: Jaccard similarity scores (0-1 range) were calculated for channel pairs that share at least 2 topics, then spot-check manually against the actual video content.
- However, my program can not build the AI function of transcribing the videos or reliable captions.
- **Transcript Success Rate**: None of the 25 videos returned usable. This forced the system to rely on titles and descriptions.

## Experimental Results
The pipeline successfully classify 25 videos from 17 channels into 9 LLMs topics. Also channel relationship analysis reveals four groupings, they are a technical education group, a practical tutorials group, a general AI Enthusiasts group and an Enterprise & Industry group. 
However, it is failed to have the AI transcript of the videos or reliable caption due to YouTube API restrictions,  therefore the column of "What They Said About LLMs"" is replaced by the titles and the videos' descriptions.
