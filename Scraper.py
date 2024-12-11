import streamlit as st
import random
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import re
import json
import pandas as pd


class CategoryProductScraper:
    def __init__(self, url):
        self.base_url = url.rstrip('/')
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0',
        ]
        self.session = requests.Session()

    def get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    def get_page_content(self, url):
        try:
            response = self.session.get(url, headers=self.get_headers())
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            return response.content
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching URL: {e}")
            return None

    def scrape_categories_bs(self):
        html_content = self.get_page_content(self.base_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        categories = []

        potential_navs = soup.find_all(['nav', 'ul'], class_=re.compile(r'(nav|menu|category|desktop)', re.I))
        for nav in potential_navs:
            links = nav.find_all('a', href=True)
            for link in links:
                name = link.text.strip()
                href = urljoin(self.base_url, link['href'])
                if name and href and href not in [c['link'] for c in categories]:
                    categories.append({'name': name, 'link': href})

        return categories


    def scrape_products_bs(self, category_url):
        html_content = self.get_page_content(category_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        products = []

        product_cards = soup.select('[data-testid^="product-card"]') 

        for card in product_cards:
            product = {}

            name_tag = card.select_one('[class*="title"]')
            product['name'] = name_tag.text.strip() if name_tag else "N/A"

            price_tag = card.select_one('[data-testid="product-card__price"], [class*="price"]')
            if price_tag:
                price_text = price_tag.text.strip()
                price_match = re.search(r"[\d,.]+", price_text)
                product['price'] = price_match.group(0) if price_match else "N/A"  
            else:
                product['price'] = "N/A"

            link_tag = card.select_one('a[href]')
            product['link'] = urljoin(self.base_url, link_tag['href']) if link_tag else "N/A"
            products.append(product)


        return products


st.title("Category and Product Scraper")

url = st.text_input("Enter the website URL")
save_format = st.selectbox("Choose save format", ["JSON", "CSV"])


if url:
    scraper = CategoryProductScraper(url)

    st.subheader("Scraping Categories")
    categories = scraper.scrape_categories_bs()

    if categories:
        st.write(f"Found {len(categories)} categories:")
        for category in categories:
            st.write(f"- {category['name']} ({category['link']})")

        category_links = {category['name']: category['link'] for category in categories}
        selected_category = st.selectbox("Select a category to scrape products", list(category_links.keys()))


        if selected_category:
            st.subheader(f"Scraping Products in Category: {selected_category}")
            products = scraper.scrape_products_bs(category_links[selected_category])

            if products:
                st.write(f"Found {len(products)} products:")

                for product in products:
                    st.write(f"- {product['name']} | Price: {product['price']} | Link: {product['link']}")

                if save_format == "JSON":
                    with open('products.json', 'w', encoding='utf-8') as json_file:  # Use utf-8 encoding
                        json.dump(products, json_file, ensure_ascii=False, indent=4) # Pretty print JSON
                    st.success("Data saved as JSON.")
                else:  # CSV
                    df = pd.DataFrame(products)
                    df.to_csv('products.csv', index=False, encoding='utf-8') # Use utf-8 encoding
                    st.success("Data saved as CSV.")



            else:
                st.write("No products found in this category.")
    else:
        st.write("No categories found.")



