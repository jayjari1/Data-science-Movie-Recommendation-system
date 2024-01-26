import streamlit as st
import pandas as pd
from joblib import load
import requests

# Load saved components
cosine_similarities_df = load('cosine_similarities_df.joblib')
vectorizer = load('vectorizer.joblib')

# Load your dataset
df = pd.read_csv('tmdb_5000_credits.csv')

# TMDB API key
tmdb_api_key = "8265bd1679663a7ea12ac168da84d2e8"

# Function to get movie recommendations
def get_recommendations(movie_name):
    # Find the index of the input movie in the dataset
    movie_index = df[df['title'] == movie_name].index[0]

    # Get the cosine similarity scores for the input movie
    cosine_scores = cosine_similarities_df.iloc[movie_index]

    # Sort the movies based on similarity scores in descending order
    similar_movies = cosine_scores.sort_values(ascending=False)

    # Exclude the input movie from the recommendation list
    similar_movies = similar_movies.drop(movie_index)

    # Select the top 5 similar movies
    top_5_similar_movies = similar_movies.head(5)

    # Get the titles and movie IDs of the top 5 similar movies
    top_5_movies_info = [(df.loc[movie_idx, 'title'], df.loc[movie_idx, 'movie_id']) for movie_idx in top_5_similar_movies.index]

    return top_5_movies_info

# Function to get movie poster URL from TMDB API
def get_movie_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={tmdb_api_key}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return poster_url
    return None

# Streamlit App
st.title("Movie Recommendation System")

# Dropdown with movie suggestions
movies_suggestions = df['title'].tolist()
selected_movie = st.selectbox("Select a movie:", movies_suggestions)

if st.button("Get Recommendations"):
    if selected_movie:
        # Get recommendations for the selected movie
        recommendations = get_recommendations(selected_movie)

        # Display selected movie poster and name
        selected_movie_poster_url = get_movie_poster(df.loc[df['title'] == selected_movie, 'movie_id'].values[0])
        if selected_movie_poster_url:
            st.image(selected_movie_poster_url, caption=f"{selected_movie}", width=150)
            st.subheader(f"Top 5 Recommendations for {selected_movie}:")

            # Display recommendations with posters and names in a horizontal scrolling container
            poster_container = st.empty()

            with poster_container:
                poster_html = "".join(
                    f'<div style="text-align: center; margin-right: 20px;"><img src="{get_movie_poster(movie_id)}" alt="{title}" width="150"><br>{title}</div>' for title, movie_id in recommendations
                )

                st.markdown(f'<div style="display: flex; justify-content: space-between; overflow-x: auto; white-space: nowrap;">{poster_html}</div>', unsafe_allow_html=True)
        else:
            st.warning(f"Poster not available for {selected_movie}.")
    else:
        st.warning("Please select a movie.")
