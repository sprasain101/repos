import streamlit as st
import re

class MainWindow():
    def __init__(self):
        self.__init__

    def run():
        st.image("world.jpg")
        st.title("Web Scraper")
        pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
        x = st.text_input("Enter the url for scrapping: ")
        st.write(f"URL: {x}")
        # if re.search(pattern, x):
        #    st.write(f"URL: {x}")
        # else:
        #    st.write(f"invalid url")

        st.selectbox("Choose the scraper to scrape the website", ["BeautifulSoup", "Selenium"])
        st.radio("Choose the file for the data to be stored", ["CSV", "JSON"])
        btn = st.button("Click")
        if btn:
            st.write("button clicked")

MainWindow.run()
