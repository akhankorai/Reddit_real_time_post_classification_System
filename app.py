import streamlit as st
import pandas as pd
import praw
import re
import nltk
import datetime
import os

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# ------------------------------
# NLTK setup
# ------------------------------
nltk.download("punkt", quiet=True)
nltk.download("stopwords", quiet=True)


def clean_text(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return ""
    text = text.lower()
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z\s]", "", text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    tokens = [w for w in tokens if w not in stop_words]
    return " ".join(tokens)


# ------------------------------
# Reddit fetch function using PRAW
# ------------------------------
def fetch_reddit_posts(client_id, client_secret, user_agent, subreddits, posts_per_sub=20):
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    rows = []
    for sub_name in subreddits:
        subreddit = reddit.subreddit(sub_name)
        for submission in subreddit.hot(limit=posts_per_sub):
            author_name = str(submission.author) if submission.author else "Unknown"
            rows.append({
                "subreddit": sub_name,
                "post_id": submission.id,
                "title": submission.title,
                "body": submission.selftext,
                "author": author_name,
                "num_comments": submission.num_comments,
                "upvotes": submission.score,
                "created_utc": submission.created_utc,
                "url": submission.url,
            })
    return pd.DataFrame(rows)


# ------------------------------
# Topic mapping for subreddits
# ------------------------------
TOPIC_MAP = {
    "technology": "Technology",
    "AskReddit": "General",
    "mentalhealth": "Mental Health",
    "worldnews": "News",
    "science": "Science",
}


# ------------------------------
# Train Naive Bayes topic classifier
# ------------------------------
def train_topic_model(df: pd.DataFrame):
    df = df.copy()
    df["topic"] = df["subreddit"].map(TOPIC_MAP)
    df = df.dropna(subset=["topic"])

    # Build cleaned_text
    df["title"] = df["title"].fillna("")
    df["body"] = df["body"].fillna("")
    df["text_for_cleaning"] = df["title"] + " " + df["body"]
    df["cleaned_text"] = df["text_for_cleaning"].apply(clean_text)

    mask = df["cleaned_text"].str.strip() != ""
    df = df[mask]

    if df.empty:
        return df, None, None

    X = df["cleaned_text"]
    y = df["topic"]

    vectorizer = TfidfVectorizer(max_features=5000)
    X_vec = vectorizer.fit_transform(X)

    model = MultinomialNB()
    model.fit(X_vec, y)

    # Predict for all rows
    df["predicted_topic"] = model.predict(X_vec)

    return df, vectorizer, model


# ------------------------------
# Streamlit App
# ------------------------------
def main():
    st.set_page_config(page_title="Reddit NLP Pipeline", layout="wide")
    st.title("Reddit → NLP → Classification → Power BI (Streamlit Demo)")

    st.markdown(
        "This app shows the same pipeline as your assignment: "
        "**Reddit API → Cleaning → Topic Classification → Visualization → CSV for Power BI**."
    )

    # --------------------------------
    # SIDEBAR: Mode + Reddit API keys
    # --------------------------------
    st.sidebar.header("Settings")

    mode = st.sidebar.radio(
        "Choose data source:",
        ["Use existing CSV", "Fetch fresh from Reddit"],
    )

    df_raw = None

    if mode == "Fetch fresh from Reddit":
        st.sidebar.subheader("Reddit API Credentials")
        client_id = st.sidebar.text_input("Client ID")
        client_secret = st.sidebar.text_input("Client Secret", type="password")
        user_agent = st.sidebar.text_input("User Agent", value="my_reddit_app by u/your_username")

        st.sidebar.subheader("Subreddits & Limits")
        default_subs = ["technology", "AskReddit", "mentalhealth", "worldnews", "science"]
        subreddits = st.sidebar.multiselect(
            "Subreddits",
            default_subs,
            default=default_subs
        )
        posts_per_sub = st.sidebar.slider("Posts per subreddit", 10, 100, 20)

        fetch_button = st.sidebar.button("Fetch from Reddit")

        if fetch_button:
            if not client_id or not client_secret or not user_agent:
                st.error("Please enter your Reddit API credentials.")
                return
            if not subreddits:
                st.error("Please select at least one subreddit.")
                return

            with st.spinner("Fetching posts from Reddit..."):
                df_raw = fetch_reddit_posts(
                    client_id,
                    client_secret,
                    user_agent,
                    subreddits,
                    posts_per_sub=posts_per_sub,
                )
            st.success(f"Fetched {len(df_raw)} posts.")
    else:
        st.sidebar.subheader("Upload processed_reddit_data.csv or raw CSV")
        uploaded = st.sidebar.file_uploader("Upload CSV", type=["csv"])
        if uploaded is not None:
            df_raw = pd.read_csv(uploaded)

    # --------------------------------
    # If no data yet, show info and stop
    # --------------------------------
    if df_raw is None or df_raw.empty:
        st.info("Upload a CSV in the sidebar or fetch fresh data from Reddit to continue.")
        return

    st.subheader("Raw / Input Data Preview")
    st.dataframe(df_raw.head())

    # --------------------------------
    # Train model + classify
    # --------------------------------
    st.subheader("Training Topic Classifier and Cleaning Text...")
    with st.spinner("Cleaning text and training Naive Bayes model..."):
        df_classified, vectorizer, model = train_topic_model(df_raw)

    if df_classified is None or df_classified.empty:
        st.error("No valid text after cleaning. Please check your data.")
        return

    st.success("Classification complete!")
    st.write("Preview of classified data:")
    st.dataframe(df_classified[["subreddit", "title", "cleaned_text", "predicted_topic"]].head())

    # --------------------------------
    # Simple visualizations inside Streamlit
    # --------------------------------
    st.markdown("## Basic Visualizations (Streamlit)")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Posts per Topic")
        topic_counts = df_classified["predicted_topic"].value_counts()
        st.bar_chart(topic_counts)

    with col2:
        st.markdown("### Posts per Subreddit")
        sub_counts = df_classified["subreddit"].value_counts()
        st.bar_chart(sub_counts)

    st.markdown("### Average Upvotes per Topic")
    avg_upvotes = df_classified.groupby("predicted_topic")["upvotes"].mean()
    st.bar_chart(avg_upvotes)

    # --------------------------------
    # SAVE FOR POWER BI (LOCAL + GOOGLE DRIVE)
    # --------------------------------
    st.markdown("## Save Classified Data for Power BI")

    # Add generation timestamp
    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_classified["generated_at"] = generated_at

    # 1) Save in app folder
    local_file = "classified_reddit_data.csv"
    df_classified.to_csv(local_file, index=False, encoding="utf-8")

    # 2) Save in Google Drive folder (CHANGE PATH IF NEEDED)
    gdrive_path = r"G:\My Drive\Reddit_Project\classified_reddit_data.csv"

    gdrive_saved = False
    try:
        os.makedirs(os.path.dirname(gdrive_path), exist_ok=True)
        df_classified.to_csv(gdrive_path, index=False, encoding="utf-8")
        gdrive_saved = True
    except Exception as e:
        st.warning(f"Could not save to Google Drive path: {gdrive_path}\nError: {e}")

    st.success(f"Local file saved: {os.path.abspath(local_file)}")
    st.write(f"Generated at: **{generated_at}**")

    if gdrive_saved:
        st.success(f"Also saved to Google Drive path:\n`{gdrive_path}`")
    else:
        st.info(
            "Once you fix the Google Drive path above, the app will automatically "
            "save the CSV there for Power BI scheduled refresh."
        )

   
    st.markdown("## Download Classified Data")

    csv_bytes = df_classified.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download classified_reddit_data.csv",
        data=csv_bytes,
        file_name="classified_reddit_data.csv",
        mime="text/csv",
    )

    st.markdown(
        "> This file (`classified_reddit_data.csv`) can be loaded into **Power BI** "
        "for your final dashboard, and the Google Drive version can be used for "
        "**scheduled refresh** in Power BI Service."
    )
    st.markdown("## View Power BI Dashboard")

    powerbi_url = "https://app.powerbi.com/view?r=eyJrIjoiYzhkYTZmNTEtM2NmYy00MDY0LThiMDUtODg3NzYwMjYwYjcxIiwidCI6IjFmYzhkNGZiLWQyMmEtNDY3Zi1iYzA0LWFiOGFjYmFjZWFkYiIsImMiOjl9"  
    # Replace <YOUR_REPORT_ID> with your actual Power BI report link

    st.markdown(
        f"[Click here to open Power BI Dashboard]({powerbi_url})",
        unsafe_allow_html=True
    )

    # Or use a button that opens the link
    if st.button("Open Power BI Dashboard"):
        st.markdown(f"Dashboard link: [Power BI Dashboard]({powerbi_url})")


if __name__ == "__main__":
    main()
