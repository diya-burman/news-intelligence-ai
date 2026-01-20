# Multi-Source News Intelligence with AI-Driven Insights

## Objective
Analyze news articles from multiple sources on the same topic, detect bias,
identify contradictions, and generate an executive-level intelligence report
using Azure OpenAI.

## Topic
Google layoffs / workforce reductions

## Sources
- The Verge
- AP News
- BBC

## Tech Stack
- Python
- BeautifulSoup / newspaper3k
- Azure OpenAI (via Azure Key Vault)
- Streamlit

## Workflow
1. Scrape articles using `scraper.py`
2. Analyze each article using Azure OpenAI (`ai_analysis.py`)
3. Generate cross-source intelligence report (`report_generator.py`)
4. Visualize insights using Streamlit dashboard (`app.py`)

## How to Run
1. Create virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Configure Azure credentials in `.env`
4. Run:
   - `python scraper.py`
   - `python ai_analysis.py`
   - `python report_generator.py`
   - `streamlit run app.py`
