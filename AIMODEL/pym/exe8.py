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
    df = pd.read_csv('DATA_FINAL.csv', encoding='ISO-8859-1')
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
@app.route('/recommend', methods=['POST'])

def recommend():
    try:
        data = request.json
        user_activities = data.get('activities', None)  # Expecting a list of activities

        if not user_activities or not isinstance(user_activities, list) or len(user_activities) == 0:
            return jsonify({'error': 'Please enter at least one activity.'}), 400

        # Clean and lower case the activities list
        user_activities = [activity.strip().lower() for activity in user_activities]

        # Filter places that include any of the activities
        filtered_df = df[df['ACTIVITIES'].apply(lambda x: any(activity in x.lower() for activity in user_activities))]

        if filtered_df.empty:
            return jsonify({'message': 'No places found for the given activities.'}), 200

        # Group by CITY and STATE, merging tourist spots and types of attraction
        grouped_df = filtered_df.groupby(['CITY', 'STATE'], as_index=False).agg({
            'TOURIST SPOT': lambda x: ', '.join(x),
            'TYPE OF ATTRACTION': lambda x: ', '.join(x)
        })

        # Prepare the recommended spots with merged tourist spots and attractions
        recommended_spots = grouped_df[['CITY', 'STATE', 'TOURIST SPOT', 'TYPE OF ATTRACTION']].to_dict(orient='records')

        return jsonify({'recommended_spots': recommended_spots})

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(debug=True)
