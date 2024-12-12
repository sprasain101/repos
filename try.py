    

import streamlit as st
import re
import random
import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class MainWindow:
    def __init__(self):
        self.__init__

    @staticmethod
    def get_headers():
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0',
        ]
        return {
            'User-Agent': random.choice(user_agents),
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

    @staticmethod
    def get_page_content(url):
        try:
            response = requests.get(url, headers=MainWindow.get_headers())
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            st.sidebar.error(f"Error fetching URL: {e}")
            return None

    @staticmethod
    def scrape_categories(url):
        html_content = MainWindow.get_page_content(url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        categories = []

        potential_navs = soup.find_all(['nav', 'ul'], class_=re.compile(r'(nav|menu|category|desktop)', re.I))
        for nav in potential_navs:
            links = nav.find_all('a', href=True)
            for link in links:
                name = link.text.strip()
                href = urljoin(url, link['href'])
                if name and href and href not in [c['link'] for c in categories]:
                    categories.append({'name': name, 'link': href})

        return categories

    @staticmethod
    def scrape_products(category_url):
        html_content = MainWindow.get_page_content(category_url)
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        products = []

        # Find all product cards on the page
        product_cards = soup.select('div.product-card__body')
        for card in product_cards:
            product = {}

            # Extract the product name
            name_tag = card.select_one('div.product-card__title')
            product['name'] = name_tag.text.strip() if name_tag else "N/A"

            # Extract the product price (current price and initial price)
            price_tag = card.select_one('div.product-price__wrapper')
            if price_tag:
                current_price_tag = price_tag.select_one('.product-price.is--current-price')
                initial_price_tag = price_tag.select_one('.product-price.is--striked-out')
                if current_price_tag:
                    product['price'] = current_price_tag.text.strip()
                if initial_price_tag:
                    product['original_price'] = initial_price_tag.text.strip()
                else:
                    product['original_price'] = "N/A"
            else:
                product['price'] = "N/A"
                product['original_price'] = "N/A"

            # Extract the product image URL
            image_tag = card.select_one('img.product-card__hero-image')
            product['image'] = image_tag['src'] if image_tag else "N/A"

            # Extract the product link
            link_tag = card.select_one('a.product-card__link-overlay')
            product['link'] = urljoin(category_url, link_tag['href']) if link_tag else "N/A"

            products.append(product)

        return products


    @staticmethod
    def run():
        st.sidebar.image("world.jpg")
        st.sidebar.title("Web Scraper")

        if "categories" not in st.session_state:
            st.session_state.categories = None
        if "category_links" not in st.session_state:
            st.session_state.category_links = None

        url = st.sidebar.text_input("Enter the URL for scraping:")
        scraper_choice = st.sidebar.selectbox("Choose the scraper to scrape the website", ["BeautifulSoup", "Selenium"])
        save_format = st.sidebar.radio("Choose the file format for data storage", ["CSV", "JSON"])
        scrape_button = st.sidebar.button("Scrape")

        if scrape_button:
            if scraper_choice == "BeautifulSoup":
                st.sidebar.write("Using BeautifulSoup")
                st.session_state.categories = MainWindow.scrape_categories(url)

                if st.session_state.categories:
                    st.session_state.category_links = {category['name']: category['link'] for category in st.session_state.categories}
                    st.write(f"Scraped {len(st.session_state.categories)} categories.")
                else:
                    st.write("No categories found.")

        if st.session_state.categories:
            category_names = [category['name'] for category in st.session_state.categories]
            selected_category = st.selectbox("Select a category to scrape products", category_names)

            if selected_category:
                st.write(f"Scraping products in category: {selected_category}")
                products = MainWindow.scrape_products(st.session_state.category_links[selected_category])

                if products:
                    if save_format == "CSV":
                        df = pd.DataFrame(products)
                        csv_file = 'products.csv'
                        df.to_csv(csv_file, index=False, encoding='utf-8')
                        st.download_button(
                            label="Download CSV",
                            data=open(csv_file, 'rb').read(),
                            file_name="products.csv",
                            mime="text/csv"
                        )
                    elif save_format == "JSON":
                        json_file = 'products.json'
                        with open(json_file, 'w', encoding='utf-8') as file:
                            json.dump(products, file, ensure_ascii=False, indent=4)
                        st.download_button(
                            label="Download JSON",
                            data=open(json_file, 'rb').read(),
                            file_name="products.json",
                            mime="application/json"
                        )
                else:
                    st.write("No products found in this category.")

MainWindow.run()
