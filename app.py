import streamlit as st
import pandas as pd
import time
from reddit_client import get_reddit_instance

# ----------------------------
# Helper functions
# ----------------------------
def build_query(filters):
    """Converts filters into a Reddit-compatible search string."""
    return " ".join(str(v) for v in filters.values() if v)

def fetch_reddit_posts(filters, limit=100):
    reddit = get_reddit_instance()
    query = build_query(filters)
    st.info(f"Searching Reddit for: **{query}** ...")

    results = []
    for submission in reddit.subreddit("all").search(query, limit=limit):
        results.append({
            "Title": submission.title,
            "Text": submission.selftext[:300],
            "Subreddit": submission.subreddit.display_name,
            "URL": f"https://www.reddit.com{submission.permalink}",
            "Author": str(submission.author),
            "Score": submission.score,
            "Comments": submission.num_comments,
            "Created": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(submission.created_utc))
        })

    df = pd.DataFrame(results)
    return df

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Reddit Data Extractor", page_icon="🔎", layout="centered")

st.title("🔎 Reddit Data Extractor")
st.write("Fetch Reddit posts based on topic, location, and keywords.")

with st.form("filter_form"):
    topic = st.text_input("Topic", placeholder="e.g. apartment, career change, EV cars")
    location = st.text_input("Location (optional)", placeholder="e.g. Delhi, India")
    keywords = st.text_input("Extra keywords (optional)", placeholder="e.g. rent OR buy")
    limit = st.number_input("Number of posts to fetch", min_value=10, max_value=500, value=50, step=10)

    submitted = st.form_submit_button("Fetch Posts")

if submitted:
    filters = {
        "topic": topic,
        "location": location,
        "keywords": keywords
    }

    if not topic.strip():
        st.error("Please enter at least a topic!")
    else:
        df = fetch_reddit_posts(filters, limit)
        if df.empty:
            st.warning("No results found. Try different filters.")
        else:
            st.success(f"✅ Found {len(df)} posts!")
            st.dataframe(df)

            # Save to Excel
            output_file = "reddit_data.xlsx"
            df.to_excel(output_file, index=False)
            with open(output_file, "rb") as f:
                st.download_button(
                    label="📥 Download Excel File",
                    data=f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
