from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

app = Flask(__name__)

# Load the dataset
data = pd.read_csv('clothes.csv')

# Combine relevant features into one string for each item
data['features'] = data['Category'] + ' ' + data['Color'] + ' ' + data['Size'] + ' ' + data['Material']

# Initialize CountVectorizer to convert text data into a matrix of token counts
vectorizer = CountVectorizer()

# Fit and transform the feature text into a bag-of-words matrix
feature_matrix = vectorizer.fit_transform(data['features'])

# Calculate cosine similarity between items
cosine_sim = cosine_similarity(feature_matrix, feature_matrix)

# Create a Series with the index of the items
indices = pd.Series(data.index, index=data['Product_Name']).drop_duplicates()

# Function to get recommendations
def get_recommendations_with_attributes(product_name, cosine_sim=cosine_sim):
    idx = indices[product_name]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    product_indices = [i[0] for i in sim_scores]
    return data.iloc[product_indices]

# Function to get image URLs
def get_image_urls(query, api_key, cx):
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}&searchType=image"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        image_urls = [item['link'] for item in data.get('items', [])]
        return image_urls
    else:
        print("Error:", response.status_code)
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations', methods=['POST'])
def recommendations():
    if request.method == 'POST':
        product_name = request.form['product_name']
        
        # Check if the product name is in the dataset
        if product_name not in data['Product_Name'].values:
            return "Product not found", 404
        
        # Get recommendations with attributes
        recommendations_with_attributes = get_recommendations_with_attributes(product_name)
        
        # Extract recommendation names and concatenate attributes
        recommendations = recommendations_with_attributes['Product_Name'].tolist()
        
        # API Key and CX for Google Custom Search
        api_key = 'AIzaSyDdoWR1zXhUl1qptHZHG6ivbYgEViQ_x-8'
        cx = 'e1df8c1bddd7a448b'
        
        # Get image URL for the user input
        user_image_urls = get_image_urls(product_name, api_key, cx)[:2]
        
        # Get image URLs for the recommended items
        recommendation_image_urls = []
        for recommendation in recommendations:
            recommendation_image_urls.extend(get_image_urls(recommendation, api_key, cx)[:2])
        
        # Ensure that there are enough image URLs available for both user input and recommendations
        if len(user_image_urls) == 0 or len(recommendation_image_urls) == 0:
            return "Image URLs not found", 500
        
        return render_template('recommendations.html', product_name=product_name, recommendations=recommendations, user_image_urls=user_image_urls, recommendation_image_urls=recommendation_image_urls)
    else:
        return "Method Not Allowed", 405

if __name__ == '__main__':
    app.run(debug=True,port=9090)
