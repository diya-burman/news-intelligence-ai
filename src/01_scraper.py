import json
from datetime import datetime
from newspaper import Article

def extract_article(url, source):
    try:
        a = Article(url)
        a.download()
        a.parse()

        return {
            "source": source,
            "url": url,
            "headline": a.title,
            "content": a.text,
            "publication_date": a.publish_date.isoformat() if a.publish_date else None,
            "scraped_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        print(f"❌ Failed: {url} | Error: {e}")
        return None

def main():
    with open("data/source_urls.json", "r", encoding="utf-8") as f:
        source_urls = json.load(f)

    all_articles = []
    for source, urls in source_urls.items():
        for url in urls:
            print(f"Scraping {source} -> {url}")
            article_data = extract_article(url, source)
            if article_data and article_data["content"]:
                all_articles.append(article_data)

    # Save output
    with open("data/raw_articles.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Done. Scraped {len(all_articles)} articles.")
    print("Saved to data/raw_articles.json")

if __name__ == "__main__":
    main()
