import os
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re

class OptiSignsScraper:
    def __init__(self, output_dir="articles"):
        self.base_url = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def fetch_articles(self, max_articles=45):
        articles = []
        url = self.base_url
        
        while url and len(articles) < max_articles:
            response = requests.get(url).json()
            articles.extend(response.get('articles', []))
            url = response.get('next_page')
            
        return articles[:max_articles]

    def clean_and_convert(self, article):
        title = article['title']
        body_html = article['body']
        html_url = article['html_url']
        slug = article.get('slug')
        if not slug:
            slug = title.lower()
            slug = re.sub(r'[^a-z0-9\s-]', '', slug)
            slug = re.sub(r'[\s-]+', '-', slug).strip('-')
        
        if not slug:
            slug = str(article['id'])
        
        if not body_html:
            return None, None

        soup = BeautifulSoup(body_html, 'html.parser')
        
        markdown_content = md(str(soup), heading_style="ATX")
        
        full_content = f"--- \nTitle: {title}\nArticle URL: {html_url}\n---\n\n{markdown_content}"
        
        file_path = os.path.join(self.output_dir, f"{slug}.md")
        return file_path, full_content

    def save_all(self):
        print("Đang cào bài viết từ OptiSigns Support...")
        articles = self.fetch_articles()
        saved_count = 0
        
        for art in articles:
            file_path, content = self.clean_and_convert(art)
            if file_path and content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                saved_count += 1
                
        print(f"Đã lưu {saved_count} bài viết dạng Markdown vào thư mục '{self.output_dir}'")

if __name__ == "__main__":
    scraper = OptiSignsScraper()
    scraper.save_all()