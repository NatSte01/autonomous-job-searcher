import os
import csv
import random
import re
import time
from urllib.parse import urlparse, quote_plus
import threading
from queue import Queue, Empty
from collections import deque
import sys
import json
import fitz

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import ollama

from colorama import init, Fore, Style

class Config:
    # --- CORE CONFIGURATION ---
    # The user's resume file. MUST be in the same directory as this script.
    CANDIDATE_PROFILE_PDF = "candidate_resume.pdf"
    
    # The Ollama model to use for analysis. Make sure you have this model pulled.
    OLLAMA_MODEL = "deepseek-r1:8b"

    # Define your target job titles, categorized by preference.
    JOB_TITLES = {
        "Tier 1": ["Investment Banking Analyst", "Quantitative Analyst", "Hedge Fund Analyst", "Financial Modeling Analyst", "M&A Analyst", "Data Science Finance", "Python Financial Analyst"],
        "Tier 2": ["Private Equity Analyst", "Venture Capital Analyst", "Equity Research Analyst", "Corporate Development Analyst"],
        "Tier 3": ["Operations Management Finance", "Financial Analyst", "FP&A Analyst"]
    }
    
    # Define your target countries in order of priority.
    COUNTRY_PRIORITY = ["USA", "Singapore", "Canada", "Australia", "United Kingdom", "Germany", "Hong Kong"]

    # --- PERFORMANCE & BEHAVIOR ---
    # Number of concurrent browser tabs for scraping.
    MAX_SCRAPER_TABS = 8
    # Number of concurrent LLM workers for analysis.
    MAX_LLM_WORKERS = 2
    # How many pages of search results to go through for each query.
    MAX_PAGES_PER_QUERY = 10
    # How often the terminal UI refreshes (in seconds).
    UI_REFRESH_RATE = 1

    # --- TARGETING ---
    # Public SearXNG instances for privacy-respecting searches. List is randomized.
    SEARXNG_INSTANCES = sorted(list(set([
        "https://search.inetol.net/", "https://searx.stream/", "https://searx.tiekoetter.com/", "https://search.rhscz.eu/", "https://search.indst.eu/",
        "https://search.hbubli.cc/", "https://searx.oloke.xyz/", "https://searx.dresden.network/", "https://search.sapti.me/", "https://searxng.f24o.zip/",
        "https://search.rowie.at/", "https://search.mdosch.de/", "https://searxng.hweeren.com/", "https://search.federicociro.com/", "https://seek.fyi/",
        "https://searx.tuxcloud.net/", "https://searx.foobar.vip/", "https://opnxng.com/", "https://searx.foss.family/", "https://search.einfachzocken.eu/",
        "https://search.catboy.house/", "https://kantan.cat/", "https://search.citw.lgbt/", "https://baresearch.org/", "https://priv.au/",
        "https://searx.perennialte.ch/", "https://suche.dasnetzundich.de/", "https://search.ononoki.org/", "https://search.projectsegfau.lt/",
        "https://search.080609.xyz/", "https://searxng.deliberate.world/", "https://searx.namejeff.xyz/", "https://search.nerdvpn.de/",
        "https://searxng.shreven.org/", "https://searx.sev.monster/", "https://searx.ro/", "https://searxng.website/", "https://darmarit.org/searx/",
        "https://searx.lunar.icu/", "https://search.oh64.moe/", "https://search.privacyredirect.com/", "https://s.datuan.dev/", "https://searxng.biz/",
        "https://nyc1.sx.ggtyler.dev/", "https://paulgo.io/", "https://northboot.xyz/", "https://search.url4irl.com/", "https://search.im-in.space/",
        "https://copp.gg/", "https://fairsuch.net/", "https://searx.mxchange.org/", "https://searx.party/", "https://searx.juancord.xyz/",
        "https://s.mble.dk/", "https://ooglester.com/", "https://metacat.online/", "https://searx.thefloatinglab.world/", "https://find.xenorio.xyz/",
        "https://etsi.me/", "https://sx.catgirl.cloud/", "https://search.canine.tools/", "https://searx.ox2.fr/", "https://www.gruble.de/",
        "https://searx.mbuf.net/", "https://search.ohaa.xyz/", "https://searx.ankha.ac/", "https://searx.zhenyapav.com/", "https://searxng.site/",
        "https://search.librenode.com/"
    ])))
    
    # Target job sites (ATS domains). Only links containing these strings will be processed.
    TARGET_JOB_SITES = [
        "boards.greenhouse.io", "jobs.lever.co", "myworkdayjobs.com", "icims.com", "workable.com",
        "smartrecruiters.com", "taleo.net", "ultipro.com", "bamboohr.com/jobs", "linkedin.com/jobs/view"
    ]

    # --- OUTPUT FILES ---
    UNFILTERED_OUTPUT_FILE = "company_list_unfiltered.csv"
    FILTERED_OUTPUT_FILE = "company_list_filtered.csv"
    LLM_ANALYSIS_LOG_FILE = "llm_analysis_log.csv"

class LiveJobPipeline:
    def __init__(self):
        self.file_lock = threading.Lock()
        self.processed_links = set()
        self.search_task_queue = Queue()
        self.job_analysis_queue = Queue()

        self.ui_state = {
            'scrapers': {str(i+1): {'status': 'Initializing', 'query': ''} for i in range(Config.MAX_SCRAPER_TABS)},
            'analyzers': {str(i+1): {'status': 'Initializing', 'task': ''} for i in range(Config.MAX_LLM_WORKERS)},
            'progress': {'searches_left': 0, 'analysis_queue_size': 0, 'matches_found': 0, 'jobs_scraped': 0},
            'recent_events': deque(maxlen=8)
        }
        self.ui_lock = threading.Lock()
        self.stop_event = threading.Event()

        self.candidate_summary = self._load_candidate_profile_from_pdf()
        if not self.candidate_summary:
            self.driver = None
            self.ollama_client = None
            return

        self.driver = self._setup_driver()
        self.ollama_client = self._setup_ollama_client()
        self._prepare_output_files()

    def _load_candidate_profile_from_pdf(self):
        try:
            print(f"{Fore.YELLOW}Loading candidate profile from {Config.CANDIDATE_PROFILE_PDF}...{Style.RESET_ALL}")
            with fitz.open(Config.CANDIDATE_PROFILE_PDF) as doc:
                text = "".join(page.get_text() for page in doc)
            print(f"{Fore.GREEN}Successfully loaded and parsed candidate profile.{Style.RESET_ALL}")
            return text
        except Exception as e:
            print(f"{Fore.RED}FATAL ERROR: Could not read or find '{Config.CANDIDATE_PROFILE_PDF}'.{Style.RESET_ALL}")
            print(f"Please make sure the PDF file exists in the same directory as the script.")
            print(f"Error details: {e}")
            return None

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--log-level=3")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            return driver
        except Exception as e:
            print(f"{Fore.RED}Failed to set up Selenium driver: {e}{Style.RESET_ALL}")
            return None

    def _setup_ollama_client(self):
        try:
            client = ollama.Client(); client.list(); return client
        except Exception as e:
            print(f"{Fore.RED}Error: Could not connect to Ollama. Is it running?{Style.RESET_ALL}\n{e}")
            return None

    def _prepare_output_files(self):
        files_to_prepare = [
            (Config.FILTERED_OUTPUT_FILE, ["score", "reason", "Job Title", "Company Name", "Source Link", "Country", "Tier", "matched_keywords"]),
            (Config.UNFILTERED_OUTPUT_FILE, ["Job Title", "Company Name", "Source Link", "Country", "Tier"]),
            (Config.LLM_ANALYSIS_LOG_FILE, ["is_match", "score", "reason", "matched_keywords", "Job Title", "Company Name", "Source Link", "Country", "Tier"])
        ]
        for filename, headers in files_to_prepare:
            if os.path.exists(filename): os.remove(filename)
            with self.file_lock:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    csv.writer(f).writerow(headers)

    def _ui_renderer(self):
        while not self.stop_event.is_set():
            output_buffer = []
            with self.ui_lock:
                output_buffer.append(f"{Style.BRIGHT}{Fore.CYAN}{'='*20} LIVE JOB PIPELINE DASHBOARD {'='*20}{Style.RESET_ALL}")
                output_buffer.append(f"\n{Style.BRIGHT}--- SCRAPER STATUS ({Config.MAX_SCRAPER_TABS} Browser Tabs) ---{Style.RESET_ALL}")
                for i in range(Config.MAX_SCRAPER_TABS):
                    scraper_id = str(i + 1); status = self.ui_state['scrapers'][scraper_id]['status']; query = self.ui_state['scrapers'][scraper_id]['query']
                    color = Fore.GREEN if "Found" in status else Fore.YELLOW if "Searching" in status else Fore.WHITE
                    output_buffer.append(f"  [{Fore.BLUE}Tab-{scraper_id}{Style.RESET_ALL}]  Status: {color}{status:<20}{Style.RESET_ALL} Query: {query[:70]}")

                output_buffer.append(f"\n{Style.BRIGHT}--- LLM ANALYZER STATUS ({Config.MAX_LLM_WORKERS} Workers) ---{Style.RESET_ALL}")
                for i in range(Config.MAX_LLM_WORKERS):
                    worker_id = str(i + 1); status = self.ui_state['analyzers'][worker_id]['status']; task = self.ui_state['analyzers'][worker_id]['task']
                    color = Fore.CYAN if "Analyzing" in status else Fore.WHITE
                    output_buffer.append(f"  [{Fore.MAGENTA}LLM-{worker_id}{Style.RESET_ALL}]      Status: {color}{status:<20}{Style.RESET_ALL} Task:  {task[:70]}")

                progress = self.ui_state['progress']
                output_buffer.append(f"\n{Style.BRIGHT}--- OVERALL PROGRESS ---{Style.RESET_ALL}")
                output_buffer.append(f"  Searches Remaining: {Fore.YELLOW}{progress['searches_left']:<6}{Style.RESET_ALL}| Jobs Scraped: {Fore.WHITE}{progress['jobs_scraped']:<6}{Style.RESET_ALL}| Analysis Queue: {Fore.CYAN}{progress['analysis_queue_size']:<6}{Style.RESET_ALL}| Matches Found: {Fore.GREEN}{progress['matches_found']:<6}{Style.RESET_ALL}")

                output_buffer.append(f"\n{Style.BRIGHT}--- RECENT EVENTS (LLM Judgements) ---{Style.RESET_ALL}")
                for event in self.ui_state['recent_events']: output_buffer.append(f"  {event}")

            sys.stdout.write("\033[H\033[J" + "\n".join(output_buffer)); sys.stdout.flush()
            time.sleep(Config.UI_REFRESH_RATE)

    def _update_ui(self, component, id, status, text=""):
        with self.ui_lock:
            if component == 'scraper': self.ui_state['scrapers'][id]['status'] = status; self.ui_state['scrapers'][id]['query'] = text
            elif component == 'analyzer': self.ui_state['analyzers'][id]['status'] = status; self.ui_state['analyzers'][id]['task'] = text
            elif component == 'event': self.ui_state['recent_events'].appendleft(f"[{time.strftime('%H:%M:%S')}] {text}")
            self.ui_state['progress']['searches_left'] = self.search_task_queue.qsize()
            self.ui_state['progress']['analysis_queue_size'] = self.job_analysis_queue.qsize()

    def scraper_worker(self, tab_handle):
        tab_name = threading.current_thread().name
        self._update_ui('scraper', tab_name, 'Starting...')
        self.driver.switch_to.window(tab_handle)
        while not self.search_task_queue.empty() and not self.stop_event.is_set():
            try: task = self.search_task_queue.get_nowait()
            except Empty: break
            self.process_search_query(task, tab_name)
            self.search_task_queue.task_done()
        self._update_ui('scraper', tab_name, 'Finished')

    def process_search_query(self, task_data, tab_name):
        query, country, tier = task_data
        self._update_ui('scraper', tab_name, 'Searching...', query)
        instance_url = random.choice(Config.SEARXNG_INSTANCES)
        hostname = urlparse(instance_url).hostname
        for page_num in range(Config.MAX_PAGES_PER_QUERY):
            if self.stop_event.is_set(): break
            try:
                if page_num == 0:
                    search_url = f"{instance_url.strip('/')}/search?q={quote_plus(query)}"
                    self.driver.get(search_url)

                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.result")))
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                for result in soup.select("article.result"):
                    h3_tag = result.find('h3')
                    if not h3_tag or not (link_tag := h3_tag.find('a')): continue
                    url, title = link_tag.get('href', ''), h3_tag.get_text(strip=True)

                    with self.file_lock:
                        if not url or not title or url in self.processed_links or not any(site in url for site in Config.TARGET_JOB_SITES): continue
                        self.processed_links.add(url)

                    company_name = self._extract_company_name(title, url)
                    if company_name:
                        job_payload = {"company": company_name, "title": title, "url": url, "country": country, "tier": tier}
                        self._save_unfiltered_result(job_payload)
                        with self.ui_lock: self.ui_state['progress']['jobs_scraped'] += 1
                        self.job_analysis_queue.put(job_payload)
                        self._update_ui('scraper', tab_name, f'Found Job ({self.job_analysis_queue.qsize()+1})', title)
                        self._update_ui('event', None, None, f"{Fore.GREEN}[+] Found:{Style.RESET_ALL} {title}")

                if not self._click_next_page(): break
                time.sleep(random.uniform(2, 4))
            except (TimeoutException, WebDriverException):
                self._update_ui('event', None, None, f"{Fore.YELLOW}[!] Tab-{tab_name} failed on {hostname}.{Style.RESET_ALL}"); break

    def _click_next_page(self):
        try:
            next_page_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Next page')]")
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page_button)
            time.sleep(0.5); next_page_button.click(); return True
        except NoSuchElementException: return False

    def _extract_company_name(self, title, url):
        try:
            parsed_url = urlparse(url); hostname = parsed_url.hostname
            if not hostname: return None
            path_parts = parsed_url.path.strip('/').split('/')
            if 'greenhouse.io' in hostname and len(path_parts) > 0 and path_parts[0] not in ['boards', 'jobs']: return path_parts[0].replace('-', ' ').title()
            if 'lever.co' in hostname and len(path_parts) > 0 and path_parts[0] not in ['jobs']: return path_parts[0].replace('-', ' ').title()
        except Exception: pass
        noise = ["Analyst", "Associate", "Hiring", "Careers", "Jobs", "at", "Inc", "LLC", "Ltd", "Partners", "Group", "Holdings", "Job Application for", "Career Opportunities", "Job Search"]
        clean_title = title
        for word in noise: clean_title = re.sub(r'\b' + re.escape(word) + r'\b', '', clean_title, flags=re.IGNORECASE)
        parts = re.split(r' - | \| | – ', clean_title, 1); company = parts[0].strip(); return company if company else None

    def llm_analyzer_worker(self):
        worker_id = threading.current_thread().name
        self._update_ui('analyzer', worker_id, 'Idle')
        while not self.stop_event.is_set():
            try:
                job_data = self.job_analysis_queue.get(timeout=1.0)
            except Empty:
                if self.search_task_queue.empty():
                    break
                continue

            self._update_ui('analyzer', worker_id, 'Analyzing Job', job_data['title'][:70])
            llm_result = self.evaluate_job_with_llm(job_data)

            self._save_llm_analysis_log(job_data, llm_result)

            if llm_result and llm_result.get("is_match"):
                score = llm_result.get('score', 0)
                self._update_ui('event', None, None, f"{Fore.CYAN}[✓] Match (Score: {score}/10):{Style.RESET_ALL} {job_data['title']}")
                with self.ui_lock: self.ui_state['progress']['matches_found'] += 1
                self._save_filtered_result(job_data, llm_result)
            elif llm_result:
                score = llm_result.get('score', 0)
                self._update_ui('event', None, None, f"{Fore.YELLOW}[-] No Match (Score: {score}/10):{Style.RESET_ALL} {job_data['title'][:90]}")
            else:
                self._update_ui('event', None, None, f"{Fore.RED}[!] LLM Analysis Failed:{Style.RESET_ALL} {job_data['title'][:90]}")

            self.job_analysis_queue.task_done()

        self._update_ui('analyzer', worker_id, 'Finished')

    def evaluate_job_with_llm(self, job_data: dict) -> dict | None:
        prompt = f"""You are a world-class career coach. Evaluate a single job title for a candidate based on their summary.
CANDIDATE'S SUMMARY:
{self.candidate_summary}

JOB TITLE TO EVALUATE:
"{job_data['title']}"

Respond ONLY in a valid JSON object with these keys: "is_match" (boolean), "score" (integer 1-10), "reason" (string), "matched_keywords" (list[string])."""
        try:
            response = self.ollama_client.chat(model=Config.OLLAMA_MODEL, messages=[{'role': 'user', 'content': prompt}], format='json', options={'temperature': 0.1})
            results = json.loads(response['message']['content'])
            return results if isinstance(results, dict) else None
        except Exception as e:
            self._update_ui('event', None, None, f"{Fore.RED}[!] LLM processing error: {e}{Style.RESET_ALL}"); return None

    def _save_unfiltered_result(self, job_data):
        with self.file_lock:
            with open(Config.UNFILTERED_OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow([job_data.get('title'), job_data.get('company'), job_data.get('url'), job_data.get('country'), job_data.get('tier')])

    def _save_filtered_result(self, job_data, llm_result):
        with self.file_lock:
            with open(Config.FILTERED_OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow([llm_result.get('score'), llm_result.get('reason'), job_data.get('title'), job_data.get('company'), job_data.get('url'), job_data.get('country'), job_data.get('tier'), ', '.join(llm_result.get('matched_keywords', []))])

    def _save_llm_analysis_log(self, job_data, llm_result):
        with self.file_lock:
            with open(Config.LLM_ANALYSIS_LOG_FILE, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if llm_result:
                    writer.writerow([
                        llm_result.get('is_match', 'ERROR'), llm_result.get('score', 'ERROR'), llm_result.get('reason', 'ERROR'), ', '.join(llm_result.get('matched_keywords', [])),
                        job_data.get('title'), job_data.get('company'), job_data.get('url'), job_data.get('country'), job_data.get('tier')
                    ])
                else:
                    writer.writerow(['LLM_PROCESS_FAILURE', 'N/A', 'N/A', 'N/A', job_data.get('title'), job_data.get('company'), job_data.get('url'), job_data.get('country'), job_data.get('tier')])

    def run(self):
        if not self.driver or not self.ollama_client:
            print(f"{Fore.RED}Pipeline cannot start due to initialization errors.{Style.RESET_ALL}")
            return

        sys.stdout.write("\033[?25l"); sys.stdout.flush()
        try:
            tasks = [(f'"{title}" "{country}"', country, tier) for tier, titles in Config.JOB_TITLES.items() for title in titles for country in Config.COUNTRY_PRIORITY]
            random.shuffle(tasks); [self.search_task_queue.put(task) for task in tasks]

            main_window = self.driver.current_window_handle
            tab_handles = [main_window]
            for _ in range(Config.MAX_SCRAPER_TABS - 1):
                self.driver.switch_to.new_window('tab'); tab_handles.append(self.driver.current_window_handle)

            ui_thread = threading.Thread(target=self._ui_renderer, daemon=True); ui_thread.start()

            all_threads = []
            for i in range(Config.MAX_SCRAPER_TABS):
                thread = threading.Thread(target=self.scraper_worker, name=str(i + 1), args=(tab_handles[i],), daemon=True); all_threads.append(thread); thread.start()
            for i in range(Config.MAX_LLM_WORKERS):
                thread = threading.Thread(target=self.llm_analyzer_worker, name=str(i + 1), daemon=True); all_threads.append(thread); thread.start()

            self.search_task_queue.join(); self.job_analysis_queue.join()
            self.stop_event.set()
            for t in all_threads: t.join()
            ui_thread.join(timeout=0.5)
        finally:
            if self.driver: self.driver.quit()
            sys.stdout.write("\033[?25h"); sys.stdout.flush()

if __name__ == "__main__":
    init(autoreset=True)
    pipeline = LiveJobPipeline()
    try:
        pipeline.run()
    except KeyboardInterrupt:
        print("\nPipeline interrupted by user. Shutting down...")
        if pipeline: pipeline.stop_event.set()
    except Exception as e:
        sys.stdout.write("\033[?25h"); sys.stdout.flush()
        print(f"\nAn unexpected error occurred: {e}")
        if pipeline: pipeline.stop_event.set()
    finally:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"\n{Style.BRIGHT}{Fore.CYAN}{'='*26} PIPELINE COMPLETE {'='*26}{Style.RESET_ALL}")
        print(f"All scraped jobs saved to: {Config.UNFILTERED_OUTPUT_FILE}")
        print(f"Full LLM analysis log saved to: {Config.LLM_ANALYSIS_LOG_FILE}")
        print(f"LLM-filtered results saved to: {Config.FILTERED_OUTPUT_FILE}")
