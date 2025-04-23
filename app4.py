from flask import Flask, render_template, request, jsonify
import sqlite3
from rapidfuzz import fuzz

app = Flask(__name__)

def get_all_proverbs():
    conn = sqlite3.connect('proverbs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT Punjabi_Idiom, English_meaning, Equivalent_English_Idiom FROM proverbs")
    results = cursor.fetchall()
    conn.close()
    return results

def fuzzy_search_partial(keyword, threshold=70):
    all_rows = get_all_proverbs()
    matches = []
    for row in all_rows:
        punjabi, meaning, equivalent = row

        # Check similarity for each field
        punjabi_score = fuzz.partial_ratio(keyword, punjabi)
        meaning_score = fuzz.partial_ratio(keyword, meaning)
        equivalent_score = fuzz.partial_ratio(keyword, equivalent if equivalent else "")

        if max(punjabi_score, meaning_score, equivalent_score) >= threshold:
            matches.append(row)
    return matches

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    keyword = ""
    if request.method == 'POST':
        keyword = request.form['query'].strip()
        if keyword:
            results = fuzzy_search_partial(keyword)
    return render_template('Templates.html', results=results, keyword=keyword)

@app.route('/suggest', methods=['GET'])
def suggest():
    keyword = request.args.get('q', '')
    suggestions = []
    if keyword:
        all_rows = get_all_proverbs()
        suggestions = [
            row[0] for row in all_rows
            if fuzz.partial_ratio(keyword, row[0]) > 70
        ][:10]  # Limit to 10 suggestions
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
