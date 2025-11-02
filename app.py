import streamlit as st
import pandas as pd
import time
from reddit_client import get_reddit_instance

# ----------------------------
# Helper Functions
# ----------------------------
def build_query(filters):
    return " ".join(str(v) for v in filters.values() if v)

def fetch_reddit_posts(filters, limit=100, time_filter="all", subreddit_name="all"):
    reddit = get_reddit_instance()
    query = build_query(filters)
    results = []

    try:
        for submission in reddit.subreddit(subreddit_name).search(
            query, limit=limit, sort="relevance", time_filter=time_filter
        ):
            results.append({
                "Title": submission.title,
                "Text": submission.selftext[:300],
                "Subreddit": submission.subreddit.display_name,
                "Author": str(submission.author),
                "URL": f"https://www.reddit.com{submission.permalink}",
                "Created": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(submission.created_utc))
            })
    except Exception as e:
        st.error(f"⚠️ Error fetching from Reddit: {e}")

    return pd.DataFrame(results)

# ----------------------------
# Streamlit Page Config
# ----------------------------
st.set_page_config(page_title="Reddit Data Extractor", page_icon="🚀", layout="wide")

# ----------------------------
# Theme Toggle (Light / Dark)
# ----------------------------
theme = st.sidebar.radio("🌓 Theme Mode", ["Dark", "Light"], index=0)

if theme == "Dark":
    bg_color = "#0e0e0e"
    text_color = "white"
    card_bg = "rgba(255, 255, 255, 0.07)"
    accent_color = "#e52e71"
else:
    bg_color = "#fafafa"
    text_color = "#222"
    card_bg = "rgba(0, 0, 0, 0.05)"
    accent_color = "#0078ff"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');
    * {{
        font-family: 'Poppins', sans-serif;
        transition: all 0.4s ease;
    }}
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .main-title {{
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #FAF9F6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: pulse 4s infinite alternate;
    }}
    @keyframes pulse {{
        0% {{ opacity: 0.8; }}
        100% {{ opacity: 1; }}
    }}
    .glass-card {{
        background: {card_bg};
        border-radius: 18px;
        padding: 25px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    .search-btn > button {{
        background: linear-gradient(90deg, #ff8a00, {accent_color});
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 50px;
        padding: 0.7em 2em;
        box-shadow: 0 0 15px {accent_color};
    }}
    .search-btn > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 25px {accent_color};
    }}
    .post-card {{
        background: {card_bg};
        border-left: 5px solid {accent_color};
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        transition: 0.3s;
    }}
    .post-card:hover {{
        transform: scale(1.02);
    }}
    a {{
        color: {accent_color};
        text-decoration: none;
        font-weight: 600;
    }}
    a:hover {{
        color: #ff8a00;
    }}
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Header
# ----------------------------
st.markdown("<h1 class='main-title'>Reddit Data Extractor 🚀</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:1.1em; color:gray;'>Explore Reddit trends with style 🔥</p>", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# Left Sidebar Inputs
# ----------------------------
with st.sidebar:
    st.markdown("### 🎯 Search Filters")
    topic = st.text_input("🔍 Topic", placeholder="e.g. AI jobs, apartments, stocks")
    location = st.text_input("📍 Location (optional)", placeholder="e.g. Delhi, New York")
    subreddit_name = st.text_input("🏠 Subreddit", value="all")
    keywords = st.text_input("💡 Keywords", placeholder="e.g. hiring OR EV cars")

    time_filter = st.selectbox("🕒 Time Range", ["day", "week", "month", "year", "all"], index=4)
    limit = st.slider("📦 Number of posts", 5, 150, 10, step=10)

    st.markdown("<div class='search-btn'>", unsafe_allow_html=True)
    search = st.button("🚀 Search Reddit")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Results Area
# ----------------------------
col_main, col_side = st.columns([3, 1])

with col_main:
    if search:
        if not topic.strip():
            st.error("⚠️ Please enter a topic first!")
        else:
            filters = {"topic": topic, "location": location, "keywords": keywords}
            with st.spinner("🧠 Fetching Reddit posts..."):
                df = fetch_reddit_posts(filters, limit, time_filter, subreddit_name)
                time.sleep(1.0)

            if df.empty:
                st.warning("😕 No results found. Try another subreddit or broader query.")
            else:
                st.success(f"🎉 Found {len(df)} posts from r/{subreddit_name}")
                st.markdown("### 🔥 Top Reddit Posts")

                for _, row in df.iterrows():
                    st.markdown(f"""
                        <div class="post-card">
                            <b style="color:{accent_color};">{row['Title']}</b><br>
                            <small style="color:gray;">r/{row['Subreddit']} • {row['Created']} • 👤 {row['Author']}</small><br><br>
                            <p>{row['Text']}</p>
                            <a href="{row['URL']}" target="_blank">🔗 View on Reddit</a>
                        </div>
                    """, unsafe_allow_html=True)

                # Download Excel
                file_name = "reddit_data_results.xlsx"
                df.to_excel(file_name, index=False)
                with open(file_name, "rb") as f:
                    st.download_button(
                        label="📥 Download Results",
                        data=f,
                        file_name=file_name,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

with col_side:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 💡 Tips")
    st.markdown("""
    - Combine **topics + location** for precise results  
    - Example: `real estate delhi`  
    - Use **specific subreddits** like `r/IndiaInvestments`  
    - Filter by **time range** to get fresh discussions  
    """)
    st.markdown("</div>", unsafe_allow_html=True)
