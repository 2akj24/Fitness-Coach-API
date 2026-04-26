from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# 1. MAKE SURE THIS IS CORRECT
OPENROUTER_API_KEY = "Private" 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_plan', methods=['POST'])
def get_plan():
    try:
        data = request.form
        
        with open('diets.json') as f:
            diet_db = json.load(f)
        
        suggested_meals = diet_db[data['goal']][data['diet_type']][data['protein_pref']]

        prompt = f"User: {data['weight']}kg, Goal: {data['goal']}. Use these Indian meals: {suggested_meals}. Give a 1-day plan."

        # OpenRouter Call
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "google/gemini-2.0-flash-001", 
                "messages": [{"role": "user", "content": prompt}]
            }),
            timeout=15 # Added timeout
        )
        
        # Check if API returned an error
        if response.status_code != 200:
            print(f"API Error: {response.text}")
            return jsonify({"plan": "API Error: " + response.text}), 500

        result = response.json()
        return jsonify({"plan": result['choices'][0]['message']['content']})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"plan": f"Internal Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
