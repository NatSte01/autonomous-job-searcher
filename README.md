# LLM Job Pipeline

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Built with](https://img.shields.io/badge/Built%20with-Selenium%20%26%20Ollama-green)

An autonomous job search agent that uses multi-threaded web scraping and a local Large Language Model (LLM) to find, filter, and score job opportunities based on your resume.

This script automates the tedious process of sifting through job boards by launching multiple browser tabs to search in parallel, then using AI to intelligently determine which jobs are a true match for your profile.

## Key Features

- **High-Speed Scraping:** Utilizes multi-threading to run up to 8 browser tabs concurrently, dramatically speeding up the search process.
- **Privacy-Focused:** Searches through public SearxNG instances to avoid direct tracking from major search engines.
- **Local LLM Analysis:** Integrates with Ollama to run a powerful language model locally. Your resume and job data never leave your machine.
- **Resume-Based Filtering:** Automatically parses your resume from a PDF and uses it as the context for the LLM to score job relevance.
- **Live Console UI:** A dynamic dashboard in your terminal provides a real-time overview of scraper tabs, LLM workers, and overall progress.

### Live Dashboard Preview
==================== LIVE JOB PIPELINE DASHBOARD ====================
--- SCRAPER STATUS (8 Browser Tabs) ---
[Tab-1] Status: Searching... Query: "Quantitative Analyst" "USA"
[Tab-2] Status: Found Job (14) Query: "Hedge Fund Analyst" "Singapore"
[Tab-3] Status: Searching... Query: "Private Equity Analyst" "Canada"
...
--- LLM ANALYZER STATUS (2 Workers) ---
[LLM-1] Status: Analyzing Job Task: Analyst, Corporate Finance at MegaCorp
[LLM-2] Status: Idle Task:
--- OVERALL PROGRESS ---
Searches Remaining: 12 | Jobs Scraped: 142 | Analysis Queue: 13 | Matches Found: 15
Generated code
## Prerequisites

1.  **Python 3.8+**
2.  **Google Chrome** browser.
3.  **Ollama**: You must have [Ollama](https://ollama.com/) installed and running.

Once Ollama is running, pull the model used by this script:
```bash
ollama pull deepseek-r1:8b
