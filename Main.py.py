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
        selected = request.form.get('selected', 'false') == 'true'
        if keyword:
            if selected:
                all_rows = get_all_proverbs()
                results = [row for row in all_rows if row[0] == keyword]
            else:
                results = fuzzy_search_partial(keyword)
    return render_template('layout_html.html', results=results, keyword=keyword)

@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '')
    suggestions = []
    if query:
        all_rows = get_all_proverbs()
        for row in all_rows:
            punjabi = row[0]
            score = fuzz.partial_ratio(query, punjabi)
            if score >= 60:
                suggestions.append(punjabi)
        suggestions = sorted(set(suggestions))[:10]
    return jsonify(suggestions)

if __name__ == '__main__':
    app.run(debug=True)
