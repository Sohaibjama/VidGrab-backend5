from flask import Flask, request, jsonify
import yt_dlp
from urllib.parse import urlparse

app = Flask(__name__)

# Define a common set of headers to mimic a web browser
COMMON_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
}

def get_headers_for_url(url):
    """Dynamically generates headers with an appropriate Referer"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    headers = COMMON_HEADERS.copy()
    headers['Referer'] = f'https://{domain}/'
    return headers

# FIXED: Removed /api prefix from routes
@app.route("/", methods=["GET"])
def home():
    return "Flask backend is running!"

@app.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        dynamic_headers = get_headers_for_url(url)
        
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "http_headers": dynamic_headers,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"title": info["title"], "url": info["url"]})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This is required for Vercel to recognize the app
def handler(request, context):
    return app(request, context)

if __name__ == "__main__":
    app.run(debug=True)