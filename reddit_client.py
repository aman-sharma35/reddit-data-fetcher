import praw
import streamlit as st

def get_reddit_instance():
    reddit = praw.Reddit(
        client_id = st.secrets.get("client_id"),
        client_secret = st.secrets.get("client_secret"),
        user_agent = st.secrets.get("user_agent", "RedditDataUI/1.0")
    )
    return reddit
