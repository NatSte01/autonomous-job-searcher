# LLM Job Pipeline

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![Built with](https://img.shields.io/badge/Built%20with-Selenium%20%26%20Ollama-green)

A collection of Python-based autonomous agents that leverage Selenium for web automation and local Large Language Models (via Ollama) for intelligent decision-making. This repository contains two primary agents: a **Live Job Pipeline** for finding and filtering job opportunities and a **LinkedIn Lead Agent** for identifying potential clients.

## Features

- **Local LLM Integration:** Uses Ollama to run powerful language models locally for data analysis, filtering, and qualification, ensuring privacy and no API costs.
- **Browser Automation:** Employs Selenium and `webdriver-manager` to automate complex browser interactions, from searching to data extraction.
- **Multi-threaded Scraping (Job Pipeline):** The Job Pipeline uses multiple browser tabs concurrently to scrape job listings at high speed.
- **State Persistence (Lead Agent):** The LinkedIn agent saves its progress and avoids reprocessing the same leads across multiple runs.
- **Dynamic Console UI:** The Job Pipeline features a live, refreshing dashboard in the console to monitor the status of all concurrent processes.

---

## The Agents

### 1. Live Job Pipeline

This agent automates the process of finding relevant job postings. It searches public SearxNG instances for roles based on predefined titles and locations, then uses an LLM to score and filter these jobs against a candidate's resume.

**How it works:**
1.  Scrapes job sites using a list of search queries.
2.  Parses the candidate's resume from a PDF file.
3.  For each job found, it sends the job title to a local LLM.
4.  The LLM evaluates if the job is a good match for the candidate's profile.
5.  Saves unfiltered, filtered, and log data into separate CSV files.

**Example Console Output:**
```
==================== LIVE JOB PIPELINE DASHBOARD ====================

--- SCRAPER STATUS (8 Browser Tabs) ---
  [Tab-1]  Status: Searching...          Query: "Quantitative Analyst" "USA"
  [Tab-2]  Status: Found Job (14)        Query: "Hedge Fund Analyst" "Singapore"
  [Tab-3]  Status: Searching...          Query: "Private Equity Analyst" "Canada"
  [Tab-4]  Status: Finished              Query: "M&A Analyst" "United Kingdom"
  ...

--- LLM ANALYZER STATUS (2 Workers) ---
  [LLM-1]      Status: Analyzing Job         Task:  Analyst, Corporate Finance at MegaCorp
  [LLM-2]      Status: Idle                  Task:

--- OVERALL PROGRESS ---
  Searches Remaining: 12    | Jobs Scraped: 142   | Analysis Queue: 13    | Matches Found: 15

--- RECENT EVENTS (LLM Judgements) ---
  [14:32:10] [✓] Match (Score: 9/10): Hedge Fund Analyst at Quant Capital
  [14:32:08] [-] No Match (Score: 3/10): Data Analyst at Retail Chain Inc.
  ...
```

### 2. LinkedIn Lead Agent

This agent logs into LinkedIn, searches for posts indicating a need for a Virtual Assistant (VA), and uses an LLM to qualify them as leads. This helps automate B2B lead generation for freelancers and agencies.

**How it works:**
1. Logs into LinkedIn using credentials from a `.env` file.
2. Iterates through a list of search queries (e.g., "looking for a virtual assistant").
3. Scrolls through the search results, expanding posts to read their full text.
4. Sends the post content to a local LLM to determine if it's a genuine lead.
5. Saves qualified leads, including the post link and author, to a CSV file.

---

## Prerequisites

Before you begin, ensure you have the following installed:
1.  **Python 3.8+**
2.  **Google Chrome** browser.
3.  **Ollama**: You must have [Ollama](https://ollama.com/) installed and running on your machine.

Once Ollama is running, pull the model used by these scripts:
```bash
ollama pull deepseek-r1:8b
```

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/python-llm-automation-agents.git
    cd python-llm-automation-agents
    ```

2.  **Install Python dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Configure the Agents:**
    -   **For the Live Job Pipeline:**
        -   Rename your resume to `Nathaniel Ibabao_Resume.pdf` and place it in the root directory, or update the `CANDIDATE_PROFILE_PDF` variable in `live_job_pipeline.py` with your file's name.

    -   **For the LinkedIn Lead Agent:**
        -   Create a `.env` file in the root directory by copying the example:
          ```bash
          cp .env.example .env
          ```
        -   Edit the `.env` file and add your LinkedIn credentials:
          ```
          LINKEDIN_EMAIL="your_email@example.com"
          LINKEDIN_PASSWORD="your_linkedin_password"
          ```

## Usage

To run an agent, simply execute its Python script from your terminal:

**To run the Job Pipeline:**
```bash
python live_job_pipeline.py
```

**To run the LinkedIn Lead Agent:**
```bash
python linkedin_lead_agent.py
```

---

## ⚠️ Disclaimer

-   These scripts are provided for educational purposes only. Use them at your own risk.
-   **Important:** Automating social media platforms like LinkedIn is against their Terms of Service and can result in your account being restricted or banned. The LinkedIn Lead Agent should be used with caution and is intended as a proof-of-concept.
-   The authors are not responsible for any misuse or damage caused by these scripts.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```
