import streamlit as st
import re

st.title("Web Scraper")
pattern = "[a-zA-Z0-9]+@[a-zA-Z]+\.(com|edu|net)"
x = st.text_input("Enter the url for scrapping: ")
st.write(f"URL: {x}")
# if re.match(pattern, x):
#    st.write(f"URL: {x}")
# else:
#    st.write(f"invalid url")
