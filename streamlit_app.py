import streamlit as st
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

class MainWindow():
    def __init__(self):
        self.__init__

    def run():
        st.sidebar.image("world.jpg")
        st.sidebar.title("Web Scraper")
        pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        # if re.search(pattern, x):
        #    st.write(f"URL: {x}")
        # else:
        #    st.write(f"invalid url")
        x = st.sidebar.text_input("Enter the url for scrapping: ")
        st.sidebar.write(f"URL: {x}")  
        select = st.sidebar.selectbox("Choose the scraper to scrape the website", ["BeautifulSoup", "Selenium"])
        generate = st.sidebar.radio("Choose the file for the data to be stored", ["CSV", "JSON"])
        btn = st.sidebar.button("Scrape")
        if btn:
            st.sidebar.write("button clicked")
        if select == 'BeautifulSoup':
            res = requests.get(x)
            st.write(res)
            content = BeautifulSoup(res.content, 'html.parser')
            links = content.find_all(div, class_='news')
            for link in links:
                text = link.find('span', class_="text")
                author = link.find('span', class_="author")
                link = link.find('a')
              #st.code(content)
                content.append([text, author, link])
        else:
            driver = webdriver.Chrome()
            driver.get(x)
        
        if generate == 'CSV':
            try:
                df = pd.DataFrame(content)
                df.to_csv('content.csv', index=False, header=['Text', 'Author', 'Link'])
            except:
                st.write("loading...")

MainWindow.run()
