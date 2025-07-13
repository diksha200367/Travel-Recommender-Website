from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/recommend": {"origins": "http://127.0.0.1:5500"}})

# Add a Home Route (Fix for 404 Error)
@app.route('/')
def home():
    return "Welcome to the Travel Recommender System API! 🚀 Visit /recommend to get recommendations."

# Load dataset
try:
    df = pd.read_csv('transformed_excel.csv', encoding='ISO-8859-1')
except Exception as e:
    print(f"Error loading CSV file: {e}")
    df = pd.DataFrame(columns=['CITY', 'STATE', 'TOURIST SPOT', 'SEASON', 'ACTIVITIES', 'TYPE OF ATTRACTION'])

df.columns = df.columns.str.strip()

for col in ['SEASON', 'ACTIVITIES', 'TYPE OF ATTRACTION']:
    df[col] = df[col].fillna('')

df['combined_features'] = df['SEASON'] + ' ' + df['ACTIVITIES'] + ' ' + df['TYPE OF ATTRACTION']

if not df.empty:
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['combined_features'])
else:
    vectorizer = None
    tfidf_matrix = None

@app.route('/recommend', methods=['POST'])
def recommend():
    print("✅ Received request on /recommend")
    
    try:
        data = request.json
        user_season = data.get('season', '').strip()
        user_activities = data.get('activities', '').strip().split(',')  # Split activities into a list

        # Ensure activities are not empty
        if not user_season or not user_activities:
            return jsonify({'error': 'Please enter both season and at least one activity.'}), 400

        # Clean activity input
        user_activities = [activity.strip() for activity in user_activities]

        # Combine the user's season and activities into a single search string
        user_input = f"{user_season} " + ' '.join(user_activities)

        if vectorizer is None or tfidf_matrix is None:
            return jsonify({'error': 'Recommendation system not initialized due to missing data.'}), 500

        # Transform the user input and calculate cosine similarities
        user_input_tfidf = vectorizer.transform([user_input])
        cosine_similarities = cosine_similarity(user_input_tfidf, tfidf_matrix).flatten()

        # Get the top 7 most similar tourist spots
        similar_indices = cosine_similarities.argsort()[-7:][::-1]

        recommended_df = df.iloc[similar_indices][['CITY', 'STATE', 'TOURIST SPOT', 'TYPE OF ATTRACTION', 'ACTIVITIES']]

        # Filter recommendations to ensure they match all user activities
        recommended_spots = []
        for _, row in recommended_df.iterrows():
            spot_activities = row['ACTIVITIES'].split(', ')  # Split activities in the dataset
            if all(activity in spot_activities for activity in user_activities):
                recommended_spots.append({
                    'CITY': row['CITY'],
                    'STATE': row['STATE'],
                    'TOURIST SPOT': row['TOURIST SPOT'],
                    'TYPE OF ATTRACTION': row['TYPE OF ATTRACTION']
                })

        if not recommended_spots:
            return jsonify({'error': 'No recommendations found for the selected activities. Try different preferences.'}), 404

        return jsonify({'recommended_spots': recommended_spots})

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
