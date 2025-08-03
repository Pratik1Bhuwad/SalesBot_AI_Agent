import pandas as pd
import numpy as np
from datetime import datetime
import PyPDF2
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
import openai
from openai import OpenAI

my_key="YOUR_OPENAI_API_KEY"  # Replace with your actual OpenAI API key
client=OpenAI(api_key=my_key)
def load_data():
    df= pd.read_excel('sales_transactions_2022_2024.xlsx')
    feedback= pd.read_csv('customer_feedback_large.csv')

    with open('market_trends_extended.txt', 'r') as f:
        market=f.read()

    reader = PyPDF2.PdfReader('board_meeting_summary_long.pdf')
    pdf= ""
    for page in reader.pages:
        pdf += page.extract_text()

    return df, feedback, market, pdf

#storing the data in variables
df,feedback, market_text, pdf_text = load_data()

#Processing of data
df['Date']=pd.to_datetime(df['Date'])
df['Month']=df['Date'].dt.to_period('M')
df['Quarter']=df['Date'].dt.to_period('Q')
df['Year']=df['Date'].dt.year
top_product=df.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(5)
region_pref=df.groupby('Region')['Revenue'].sum()
product_units=df.groupby('Product')['Units Sold'].sum().sort_values(ascending=False)
feedback_summary=feedback['Feedback'].value_counts().head()

#Strimlit UI setup
import streamlit as st
st.set_page_config(page_title="Sales AI Agent", layout="wide")
st.title('Sales Business AI Agent')
st.markdown('Ask anything about the company performance, product sales, customer feedback, and market trends.')

query = st.text_input("Enter your query here:")

if st.button('Get Insights from AI Agent'):
    openai.api_key=my_key
    prompt = f""""
            You are a highly skilled business analyst AI Assistant
            Here is the business context to use in your answer.

            Top Product by Revenue:
            {top_product.to_string()}

            Product Units Sold Per Product:
            {product_units.to_string()}

            Revenue By Region:
            {region_pref.to_string()}

            Market Trend Highlights:
            {market_text[:100]}

            Board Meeting Summary:
            {pdf_text[:100]}

            Feedback Summary of the Customers:
            {feedback_summary.to_string()}

            Now analyze and answer te query:{query}   
"""

    with st.spinner('Analyzing...'):
        try:
            response=client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': prompt}]
            )
            st.success('Analysis complete!')
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"An error occurred: {e}")