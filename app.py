from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    # Provide a simple welcome message or API info
    return jsonify({
        "message": "Welcome to the Theme Detector API!",
        "usage": "/detect-theme?url=YOUR_WEBSITE_URL",
        "example": "/detect-theme?url=https://example.com"
    })

@app.route('/detect-theme', methods=['GET'])
def detect_theme():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL parameter is required."}), 400

    try:
        # Fetch the page content
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful

        soup = BeautifulSoup(response.text, 'html.parser')

        # Search for theme-specific stylesheets
        for link in soup.find_all('link', {'rel': 'stylesheet'}):
            href = link.get('href', '')
            if 'wp-content/themes/' in href:
                theme_url = href
                theme_name = href.split('/themes/')[1].split('/')[0]
                style_css_url = f"{href.split('/themes/')[0]}/themes/{theme_name}/style.css"

                # Fetch the style.css file for metadata
                style_response = requests.get(style_css_url)
                if style_response.status_code == 200:
                    metadata = {}
                    for line in style_response.text.splitlines():
                        if ': ' in line:
                            key, value = line.split(': ', 1)
                            metadata[key.strip()] = value.strip()
                    
                    # Extract price (hypothetical, depending on marketplace APIs)
                    metadata['price'] = "Fetching price requires external marketplace API integration."
                    
                    # Return the metadata including theme name, version, and author
                    return jsonify({
                        "theme_name": metadata.get("Theme Name", "Unknown"),
                        "version": metadata.get("Version", "Unknown"),
                        "author": metadata.get("Author", "Unknown"),
                        "price": metadata.get("price", "Not Available"),
                        "style_css_url": style_css_url
                    })

        return jsonify({"error": "Theme information not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
