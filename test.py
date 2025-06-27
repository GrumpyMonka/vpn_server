import requests
import base64
from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
def index():
    return '🟢 Server is running. Use /mergedsub to get the merged subscription.'

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/mergedsub')
def merged_subscription():
    urls = [
        'http://139.28.97.16:2096/sub/f3uhu9m15p8qnmq7',
        'http://79.110.48.11:2096/sub/f3uhu9m15p8qnmq7'
    ]
    nodes = []

    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            decoded = base64.b64decode(r.text).decode()
            nodes.extend(decoded.strip().splitlines())
            print(f"✅ Loaded from {url}")
        except Exception as e:
            print(f"❌ Failed to load from {url}: {e}")

    if not nodes:
        return Response("No data fetched from any URL", status=500)

    merged = "\n".join(nodes)
    encoded = base64.b64encode(merged.encode()).decode()
    return Response(encoded, mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
