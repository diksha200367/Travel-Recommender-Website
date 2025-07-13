from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load the dataset
df = pd.read_csv('transformed_excel.csv', encoding='ISO-8859-1')

# Strip whitespace from column names
df.columns = df.columns.str.strip()

# Handle NaN values by filling them with an empty string
df['SEASON'] = df['SEASON'].fillna('')
df['ACTIVITIES'] = df['ACTIVITIES'].fillna('')
df['TYPE OF ATTRACTION'] = df['TYPE OF ATTRACTION'].fillna('')

# Combine relevant features into a single string for each tourist spot
df['combined_features'] = df['SEASON'] + ' ' + df['ACTIVITIES'] + ' ' + df['TYPE OF ATTRACTION']

# Create a TF-IDF Vectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['combined_features'])


@app.route('/', methods=['GET', 'POST'])
def index():
    recommended_spots = None
    error_message = None
    if request.method == 'POST':
        user_season = request.form['season'].strip()
        user_activity = request.form['activity'].strip()
        
        # Check if user input is empty
        if not user_season or not user_activity:
            error_message = "Please enter both season and activity."
        else:
            # Create a user input string
            user_input = f"{user_season} {user_activity}"
            
            # Transform the user input into the same TF-IDF space
            user_input_tfidf = vectorizer.transform([user_input])
            
            # Calculate cosine similarity between user input and the dataset
            cosine_similarities = cosine_similarity(user_input_tfidf, tfidf_matrix).flatten()
            
            # Get the indices of the top 7 most similar tourist spots
            similar_indices = cosine_similarities.argsort()[-7:][::-1]
            
            # Get the recommended spots based on the indices
            recommended_df = df.iloc[similar_indices][['CITY', 'STATE', 'TOURIST SPOT', 'TYPE OF ATTRACTION']]
            
            # Group by CITY and STATE, and consolidate TOURIST SPOT and TYPE OF ATTRACTION values
            recommended_spots = (
                recommended_df.groupby(['CITY', 'STATE'], as_index=False)
                .agg({
                    'TOURIST SPOT': lambda x: ', '.join(x),
                    'TYPE OF ATTRACTION': lambda x: ', '.join(x.unique())  # Combine unique values
                })
            )
    
    return render_template('front.html', recommended_spots=recommended_spots, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
