# Automated Job Search & LLM Filtering Pipeline

This project is a powerful, automated job search tool that scrapes the web for relevant job postings and uses a local Large Language Model (LLM) to filter and score them based on your resume. It's designed to save you hours of manual searching by programmatically identifying the most promising opportunities.

The pipeline uses a distributed network of public [SearXNG](https://github.com/searxng/searxng) instances for robust, decentralized web scraping, and leverages [Ollama](https://ollama.com/) to run a local LLM for intelligent, private, and free job analysis.

<img width="1247" height="867" alt="image" src="https://github.com/user-attachments/assets/95350fb3-e1d1-4774-8cad-5a9536be26f0" />

## Features

-   **Multi-Threaded Scraping**: Utilizes multiple parallel browser tabs (via Selenium) to search for jobs simultaneously, dramatically speeding up the process.
-   **Intelligent LLM Filtering**: Connects to a local Ollama instance to analyze each found job title against the content of your resume.
-   **Live TUI Dashboard**: A clean, real-time terminal dashboard shows the status of all scraper and analyzer threads, progress, and recent LLM judgments.
-   **Decentralized & Robust**: Queries a list of public SearXNG instances, making it resilient to any single search provider going down.
-   **Highly Configurable**: Easily change target job titles, countries, LLM model, and performance settings in a central `Config` class.
-   **Detailed Output**: Generates three separate CSV files: one for all scraped jobs, one for the detailed LLM analysis log, and a final, clean list of matched jobs with their scores.
-   **Resume-Based Analysis**: Reads your qualifications directly from a PDF resume to provide tailored job matching.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**
2.  **Google Chrome** browser
3.  **[Ollama](https://ollama.com/)**: You must have Ollama installed and running.
4.  **An Ollama Model**: You need to have pulled a model for the analysis. The script is configured for `deepseek-r1:8b`, but you can use others. Pull the model with:
    ```bash
    ollama pull deepseek-r1:8b
    ```

## Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

Before running the script, you need to configure it for your job search. Open `job_pipeline.py` and edit the `Config` class at the top of the file.

1.  **Add Your Resume**:
    -   Place your resume in PDF format in the root directory of the project.
    -   Update the `CANDIDATE_PROFILE_PDF` variable to match your resume's filename.
    ```python
    # In job_pipeline.py
    class Config:
        # ...
        CANDIDATE_PROFILE_PDF = "Your_Resume_Name.pdf"
    ```

2.  **Define Your Job Search**:
    -   Modify the `JOB_TITLES` dictionary to include the roles you are interested in. You can change the tiers or the titles within them.
    -   Adjust the `COUNTRY_PRIORITY` list to target specific countries.
    ```python
    # In job_pipeline.py
    class Config:
        # ...
        JOB_TITLES = {
            "Tier 1": ["Senior Python Developer", "Machine Learning Engineer"],
            "Tier 2": ["Backend Developer", "Data Engineer"],
            "Tier 3": ["Software Engineer"]
        }
        COUNTRY_PRIORITY = ["USA", "Canada", "United Kingdom"]
        # ...
    ```

3.  **(Optional) Change LLM Model**:
    -   If you are using a different Ollama model, update the `OLLAMA_MODEL` variable.
    ```python
    # In job_pipeline.py
    class Config:
        # ...
        OLLAMA_MODEL = "llama3:8b" # or any other model you have
    ```

4.  **(Optional) Performance Tuning**:
    -   You can adjust `MAX_SCRAPER_TABS` and `MAX_LLM_WORKERS` depending on your machine's CPU and RAM.

## How to Run

1.  Make sure your Ollama application is running in the background.
2.  Execute the script from your terminal:
    ```bash
    python job_pipeline.py
    ```
3.  The live dashboard will appear. The script will run until all search queries are completed. You can stop it at any time with `Ctrl+C`.

## Output Files

The script will generate three CSV files in the project directory:

-   **`company_list_unfiltered.csv`**: A raw list of every job posting found that matched the target job sites.
-   **`llm_analysis_log.csv`**: A detailed log of every job evaluated by the LLM, including its match status, score, and reasoning. This is useful for debugging the LLM's performance.
-   **`company_list_filtered.csv`**: The final, curated list of jobs that the LLM identified as a good match, sorted by score. **This is your primary results file.**

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
