import json
from openai import AzureOpenAI
from keyvault import get_secrets

def get_azure_client():
    s = get_secrets()

    client = AzureOpenAI(
        api_key=s["api_key"],
        azure_endpoint=s["endpoint"],
        api_version="2024-02-01"
    )

    return client, s["deployment"]


def analyze_article(client, deployment, article):
    prompt = f"""
You are a news intelligence analyst.

Analyze this news article and return STRICT JSON with:
- summary (3-5 bullet points)
- sentiment: positive/neutral/negative
- entities: list of objects with keys (type, name)
- topic_tags: list of 3-7 short tags
- bias_score: number 0-10
- bias_notes: 2-4 lines explaining any framing/bias

ARTICLE:
Source: {article.get("source")}
Headline: {article.get("headline")}
Published: {article.get("publication_date")}
Content:
{article.get("content")[:6000]}
"""

    response = client.chat.completions.create(
        model=deployment,
        temperature=0.3,
        messages=[
            {"role": "system", "content": "Respond ONLY in valid JSON. No markdown."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)


def main():
    # Load scraped articles
    with open("data/raw_articles.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    if len(articles) == 0:
        print("❌ No articles found in data/raw_articles.json")
        return

    client, deployment = get_azure_client()

    analyzed = []
    for i, art in enumerate(articles, start=1):
        print(f"🔎 Analyzing {i}/{len(articles)}: {art.get('headline')}")

        try:
            analysis = analyze_article(client, deployment, art)
            art["analysis"] = analysis
            analyzed.append(art)
        except Exception as e:
            print(f"❌ Failed to analyze article: {e}")

    # Save output
    with open("data/analyzed_articles.json", "w", encoding="utf-8") as f:
        json.dump(analyzed, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Saved {len(analyzed)} analyzed articles to data/analyzed_articles.json")


if __name__ == "__main__":
    main()
