
```markdown
# LLM-Powered Job Search Pipeline

This is an automated, multi-threaded job scraping and analysis tool. It uses a list of public SearXNG instances to search for specified job titles across major Application Tracking Systems (ATS), then leverages a local Large Language Model (LLM) via Ollama to evaluate each job title against a candidate's resume for relevance.

The entire process is visualized in a live terminal dashboard.

## Features

- **Multi-threaded Scraping**: Uses multiple concurrent browser tabs to search for jobs quickly.
- **Privacy-Focused**: Leverages a list of public [SearXNG](https://searx.space/) instances, avoiding direct requests to traditional search engines.
- **Local LLM Analysis**: Utilizes a locally running LLM via [Ollama](https://ollama.com/) for job title analysis. No API keys or data sharing required.
- **Resume-Based Filtering**: Reads a candidate's resume from a PDF to provide context for the LLM's evaluation.
- **Live Terminal Dashboard**: Provides a real-time, color-coded view of scraper and analyzer status, overall progress, and recent LLM judgments.
- **Highly Configurable**: Easily change job titles, target countries, performance settings, and more in the `Config` class.
- **Detailed Output**: Generates three separate CSV files for unfiltered results, LLM-filtered matches, and a complete analysis log.

## Demo

Here is a preview of the live terminal dashboard in action:

```
==================== LIVE JOB PIPELINE DASHBOARD ====================

--- SCRAPER STATUS (8 Browser Tabs) ---
  [Tab-1]  Status: Searching...          Query: "Quantitative Analyst" "USA"
  [Tab-2]  Status: Searching...          Query: "Hedge Fund Analyst" "Singapore"
  [Tab-3]  Status: Found Job (1)         Query: "M&A Analyst" "Canada"
  [Tab-4]  Status: Searching...          Query: "Python Financial Analyst" "USA"
  [Tab-5]  Status: Starting...
  [Tab-6]  Status: Starting...
  [Tab-7]  Status: Starting...
  [Tab-8]  Status: Starting...

--- LLM ANALYZER STATUS (2 Workers) ---
  [LLM-1]      Status: Analyzing Job         Task:  M&A Analyst | Goldman Sachs
  [LLM-2]      Status: Idle

--- OVERALL PROGRESS ---
  Searches Remaining: 142   | Jobs Scraped: 1     | Analysis Queue: 0     | Matches Found: 0

--- RECENT EVENTS (LLM Judgements) ---
  [14:32:15] [+] Found: M&A Analyst | Goldman Sachs
```

## Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.8+](https://www.python.org/downloads/)
- [Google Chrome](https://www.google.com/chrome/)
- [Ollama](https://ollama.com/)

## Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/job-search-pipeline.git
    cd job-search-pipeline
    ```

2.  **Create a virtual environment (recommended):**
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Download an Ollama model:**
    This script is configured to use `deepseek-r1:8b` by default. You can change this in the script, but make sure you have the model pulled.
    ```sh
    ollama pull deepseek-r1:8b
    ```
    Ensure the Ollama application is running in the background.

5.  **Add your resume:**
    Place your resume in the project's root directory and **rename it to `candidate_resume.pdf`**. The script will read this file to understand your profile.

## Usage

Once setup is complete, simply run the script from your terminal:

```sh
python job_pipeline.py
```

The live dashboard will appear. The script will run until all search queries are completed. To stop it early, press `Ctrl+C`.

## Configuration

All major settings can be adjusted in the `Config` class at the top of `job_pipeline.py`:

-   `CANDIDATE_PROFILE_PDF`: The name of your resume file.
-   `OLLAMA_MODEL`: The Ollama model to use for analysis.
-   `JOB_TITLES`: A dictionary of job titles to search for, categorized by your preference.
-   `COUNTRY_PRIORITY`: A list of countries to include in the search queries.
-   `MAX_SCRAPER_TABS` & `MAX_LLM_WORKERS`: Adjust the number of concurrent workers. More tabs may find jobs faster but will use more system resources.
-   `TARGET_JOB_SITES`: A list of ATS domains to target. Only links from these sites will be processed.

## Output Files

The script generates three files in the root directory:

1.  **`company_list_unfiltered.csv`**: Contains every job listing found by the scrapers, regardless of relevance.
2.  **`llm_analysis_log.csv`**: A detailed log of every judgment made by the LLM, including both matches and non-matches.
3.  **`company_list_filtered.csv`**: The final, curated list of jobs that the LLM determined to be a good match, sorted by score. This is your primary output file.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for personal and educational use. Please be respectful of the public SearXNG instances and avoid running the script with excessively high concurrency settings.
```

---
