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
```
==================== LIVE JOB PIPELINE DASHBOARD ====================

--- SCRAPER STATUS (8 Browser Tabs) ---
  [Tab-1]  Status: Searching...          Query: "Quantitative Analyst" "USA"
  [Tab-2]  Status: Found Job (14)        Query: "Hedge Fund Analyst" "Singapore"
  [Tab-3]  Status: Searching...          Query: "Private Equity Analyst" "Canada"
  ...

--- LLM ANALYZER STATUS (2 Workers) ---
  [LLM-1]      Status: Analyzing Job         Task:  Analyst, Corporate Finance at MegaCorp
  [LLM-2]      Status: Idle                  Task:

--- OVERALL PROGRESS ---
  Searches Remaining: 12    | Jobs Scraped: 142   | Analysis Queue: 13    | Matches Found: 15
```

## Prerequisites

1.  **Python 3.8+**
2.  **Google Chrome** browser.
3.  **Ollama**: You must have [Ollama](https://ollama.com/) installed and running.

Once Ollama is running, pull the model used by this script:
```bash
ollama pull deepseek-r1:8b
```

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/llm-job-pipeline.git
    cd llm-job-pipeline
    ```

2.  **Install Python dependencies:**
    (Recommended) Create and activate a virtual environment first.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Add Your Resume:**
    -   Place your resume PDF in the root directory of the project.
    -   Update the `CANDIDATE_PROFILE_PDF` variable in `live_job_pipeline.py` to match your resume's filename.

## Usage

Ensure Ollama is running in the background. Then, run the script from your terminal:

```bash
python live_job_pipeline.py
```
The script will start running, and the live dashboard will appear in your console. The results will be saved to three CSV files: `company_list_unfiltered.csv`, `company_list_filtered.csv`, and `llm_analysis_log.csv`.

## Disclaimer

This script is provided for educational purposes. Web scraping can be intensive on websites, so please use it responsibly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

---
---

## Package 2: LinkedIn Lead Agent

This is for the `linkedin_lead_agent.py` script.

**GitHub Repo Name Suggestion:** `linkedin-lead-agent` or `ollama-linkedin-leads`

**GitHub Repository Description:**
`An autonomous agent to find and qualify B2B leads on LinkedIn using Selenium and a local LLM for analysis.`

---

### 1. `LICENSE` File

The **MIT License** is also the best choice here.

**File Name:** `LICENSE`
*(Use the same MIT license text as provided in the first package)*

---

### 2. `requirements.txt` File

**File Name:** `requirements.txt`
```text
ollama
selenium
webdriver-manager
python-dotenv
```

---

### 3. `.env.example` File

This shows users how to set up their credentials file.

**File Name:** `.env.example`
```
# Copy this file to .env and fill in your LinkedIn credentials
LINKEDIN_EMAIL=""
LINKEDIN_PASSWORD=""
```

---
