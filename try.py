import requests
from bs4 import BeautifulSoup
import json
import random
import string


# Function to generate random 8-digit alphanumeric string for ID
def generate_random_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


# Function to extract data from a single news article
def extract_news_data(news_url):
    response = requests.get(news_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title (skip if not found)
    title_tag = soup.find('h1', class_='news-big-title')
    title = title_tag.text.strip() if title_tag else None

    # Extract author (skip if not found)
    author_tag = soup.find('span', class_='author vcard')
    author = author_tag.text.strip() if author_tag else None

    # Extract published date (skip if not found)
    published_date_tag = soup.find('time', class_='entry-date')
    published_date = published_date_tag.text.strip() if published_date_tag else None

    # Extract images: filter out unnecessary images, only taking images within the article content
    images = [img['src'] for img in soup.find_all('img', src=True) if 'uploads' in img['src']]

    # Extract news detail (paragraphs): filter out non-text elements
    paragraphs = [p.text.strip() for p in soup.find_all('p') if p.text.strip()]

    # Prepare the data in the desired format
    news_data = {
        'id': generate_random_id(),
        'link': news_url,
        'title': title,
        'author': author,
        'published_date': published_date,
        'images': images,
        'paragraphs': paragraphs
    }
    return news_data


# Function to scrape a single page
def scrape_page(page_num):
    url = f'https://en.setopati.com/view?page={page_num}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all article links on the current page
    article_links = [a['href'] for a in soup.find_all('a', href=True) if '/view/' in a['href']]

    news_list = []
    # Scrape data for each article
    for link in article_links:
        # Ensure the link is absolute (starting with 'https://')
        if not link.startswith('https://'):
            full_url = f'https://en.setopati.com{link}'  # Relative URL
        else:
            full_url = link  # Absolute URL

        news_data = extract_news_data(full_url)
        news_list.append(news_data)

    return news_list


# Function to scrape data from all pages
def scrape_all_pages():
    all_news_data = []

    # Loop through all pages (1-6)
    for page_num in range(1, 7):
        print(f"Scraping page {page_num}")
        news_data = scrape_page(page_num)
        all_news_data.extend(news_data)

    return all_news_data


# Main function to run the scraper and save the data to news.json
def main():
    news_data = scrape_all_pages()

    # Save the extracted data to news.json in the required format
    with open('news.json', 'w') as json_file:
        json.dump(news_data, json_file, indent=2)


if __name__ == "main":
    main()
