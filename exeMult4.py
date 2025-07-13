from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

app = Flask(__name__)


# ✅ Allow frontend on http://127.0.0.1:5500 to access Flask API
CORS(app, resources={r"/recommend": {"origins": "http://127.0.0.1:5500"}})

DATA_FILE = 'DATA_FINAL (version 1).csv'

def load_data():
    try:
        if not os.path.exists(DATA_FILE):
            print(f"❌ Error: CSV file '{DATA_FILE}' not found.")
            return pd.DataFrame(), None, None

        df = pd.read_csv(DATA_FILE, encoding='ISO-8859-1')
        if df.empty:
            print("❌ Error: CSV file is empty.")
            return pd.DataFrame(), None, None

        df.columns = df.columns.str.strip()  # Remove extra spaces in column names
        df.rename(columns={col: col.upper() for col in df.columns}, inplace=True)  # Standardize names
        df.fillna('', inplace=True)  # Fill missing values

        print("📊 CSV Columns:", df.columns.tolist())  # Debugging print

        # Identify text-based columns dynamically
        text_columns = df.select_dtypes(include=['object']).columns.tolist()
        ignore_columns = ['IMAGE', 'CITY_LINK']  # Ignore columns not relevant for similarity
        text_columns = [col for col in text_columns if col not in ignore_columns]

        if not text_columns:
            print("❌ Error: No valid text columns for similarity matching.")
            return pd.DataFrame(), None, None

        # Create a new column combining features
        df['COMBINED_FEATURES'] = df[text_columns].apply(lambda row: ' '.join(row.values).strip(), axis=1)

        if df['COMBINED_FEATURES'].eq('').all():
            print("❌ Error: All combined features are empty.")
            return pd.DataFrame(), None, None

        # TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(df['COMBINED_FEATURES'])

        print(f"✅ Data Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
        return df, vectorizer, tfidf_matrix

    except Exception as e:
        print(f"❌ Error loading CSV file: {e}")
        return pd.DataFrame(), None, None

# ✅ Load data at startup
df, vectorizer, tfidf_matrix = load_data()

@app.route('/')
def home():
    return "Welcome to the Travel Recommender System API!"

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()
        print("📥 Received JSON:", data)

        if not data or 'season' not in data or 'activity' not in data:
            return jsonify({'error': 'Invalid request. Expecting season and activity.'}), 400

        # Create a user query
        user_query = ' '.join([str(data['season']), str(data['activity'])]).strip().lower()

        if not user_query:
            return jsonify({'error': 'User query is empty'}), 400

        # Ensure data is available
        if vectorizer is None or tfidf_matrix is None or df.empty:
            return jsonify({'error': 'Data unavailable'}), 500

        # Compute similarity
        user_vector = vectorizer.transform([user_query])
        similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()

        df['SIMILARITY_SCORE'] = similarities
        sorted_df = df.sort_values(by='SIMILARITY_SCORE', ascending=False)

        # Check if any recommendation exists
        if sorted_df['SIMILARITY_SCORE'].max() == 0:
            return jsonify({'message': 'No places found matching preferences.', 'recommended_spots': []}), 200

        # ✅ Fix column names (Check existence before filtering)
        expected_columns = ['CITY', 'STATE', 'TOURIST SPOT', 'TYPE OF ATTRACTION', 'IMAGE', 'CITY_LINK']
        available_columns = [col for col in expected_columns if col in sorted_df.columns]

        if not available_columns:
            print("❌ Error: Expected columns missing. Available:", sorted_df.columns.tolist())  # Debugging print
            return jsonify({'error': 'No valid recommendation columns found'}), 500

        # Get top 6 recommendations
        recommended_spots = sorted_df[available_columns].head(6).to_dict(orient='records')

        print("✅ Recommendations generated successfully!")
        return jsonify({'recommended_spots': recommended_spots})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal Server Error', 'details': str(e)}), 500

@app.route('/reload-data', methods=['GET'])
def reload_data():
    global df, vectorizer, tfidf_matrix
    df, vectorizer, tfidf_matrix = load_data()
    return jsonify({'message': '🔄 Data reloaded successfully'})

@app.route('/get-image/<path:filename>')
def get_image(filename):
    return send_from_directory("", filename)

if __name__ == '__main__':
    app.run(debug=True)
