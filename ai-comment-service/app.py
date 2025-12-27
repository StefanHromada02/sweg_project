from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "tinyllama"


def generate_sarcastic_comment(post_title: str, post_text: str) -> str:
    """Generate a sarcastic comment using Ollama."""
    prompt = f"""Generate a short, sarcastic comment (max 2 sentences) about this post:
Title: {post_title}
Text: {post_text}

Be witty and sarcastic, but not mean. Keep it brief and funny."""

    try:
        response = requests.post(
            OLLAMA_API,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.8,
                    "max_tokens": 100
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "Wow, so interesting... I guess.").strip()
        else:
            logger.error(f"Ollama API error: {response.status_code}")
            return "My AI brain is too tired for this. 🙄"
            
    except Exception as e:
        logger.error(f"Error generating comment: {str(e)}")
        return "Error generating sarcasm. How ironic."


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "model": MODEL}), 200


@app.route('/generate-comment', methods=['POST'])
def generate_comment():
    """Generate a sarcastic AI comment for a post."""
    try:
        data = request.get_json()
        
        if not data or 'title' not in data or 'text' not in data:
            return jsonify({"error": "Missing title or text"}), 400
        
        post_title = data['title']
        post_text = data['text']
        
        logger.info(f"Generating comment for post: {post_title}")
        
        comment = generate_sarcastic_comment(post_title, post_text)
        
        return jsonify({
            "comment": comment,
            "generated_by": "AI (TinyLlama)"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in generate_comment: {str(e)}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
