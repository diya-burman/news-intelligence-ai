import json
from datetime import datetime
from openai import AzureOpenAI
from keyvault import get_secrets


def get_client():
    s = get_secrets()
    client = AzureOpenAI(
        api_key=s["api_key"],
        azure_endpoint=s["endpoint"],
        api_version="2024-02-01"
    )
    return client, s["deployment"]


def safe_date(d):
    if not d:
        return None
    try:
        # handles ISO strings
        return datetime.fromisoformat(str(d).replace("Z", ""))
    except:
        return None


def main():
    # Load analyzed articles
    with open("data/analyzed_articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    if not articles:
        print("❌ analyzed_articles.json is empty. Run 03_ai_analysis.py first.")
        return

    # Compact dataset (so token usage is low)
    compact = []
    for a in articles:
        analysis = a.get("analysis", {})
        compact.append({
            "source": a.get("source"),
            "headline": a.get("headline"),
            "url": a.get("url"),
            "publication_date": a.get("publication_date"),
            "summary": analysis.get("summary"),
            "sentiment": analysis.get("sentiment"),
            "topic_tags": analysis.get("topic_tags"),
            "bias_score": analysis.get("bias_score"),
            "bias_notes": analysis.get("bias_notes")
        })

    client, deployment = get_client()

    prompt = f"""
You are a Senior News Intelligence Analyst.

You are given news articles from 3 sources on the SAME topic.
Generate an intelligence report by comparing sources.

Return STRICT JSON with the following keys:

1) executive_summary:
   - 100 to 150 words

2) bias_comparison_matrix:
   - list of objects like:
     {{
       "source": "...",
       "overall_tone": "neutral/critical/supportive/mixed",
       "bias_score_avg": number,
       "framing": "how they frame story in 1-2 lines",
       "what_they_emphasize": ["...","..."],
       "what_they_downplay": ["...","..."]
     }}

3) key_facts_chronology:
   - list of objects sorted by date
     {{
       "date": "YYYY-MM-DD or null",
       "fact": "...",
       "sources_supporting": ["source1","source2"]
     }}

4) contradictions_or_conflicts:
   - list of objects
     {{
       "issue": "...",
       "source_claims": {{
         "SourceA": "...",
         "SourceB": "..."
       }},
       "likely_reason": "missing data / different framing / different numbers / uncertainty"
     }}

5) consensus_summary:
   - 5-8 bullet points

6) unique_angles_by_source:
   - object/dict mapping source -> list of unique points

7) actionable_insights:
   - list of 5-8 items (what readers should know/do)

Use ONLY the given dataset. If something is unknown, say "unclear".

DATASET:
{json.dumps(compact, ensure_ascii=False)}
"""

    print("🧠 Generating final intelligence report...")

    resp = client.chat.completions.create(
        model=deployment,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON. No markdown, no extra text."},
            {"role": "user", "content": prompt}
        ]
    )

    report_text = resp.choices[0].message.content

    # Convert to dict
    try:
        report = json.loads(report_text)
    except Exception as e:
        print("❌ AI returned non-JSON response. Saving raw output for debugging.")
        with open("data/final_report_raw.txt", "w", encoding="utf-8") as f:
            f.write(report_text)
        print("Saved: data/final_report_raw.txt")
        raise e

    # Save final report
    with open("data/final_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("✅ Final report generated: data/final_report.json")


if __name__ == "__main__":
    main()
