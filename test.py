from flask import Flask, render_template, request, jsonify
import sqlite3
from rapidfuzz import fuzz, process

app = Flask(__name__)

# Updated to include Romanized column
def get_all_proverbs():
    conn = sqlite3.connect('database (2).db')
    cursor = conn.cursor()
    cursor.execute("SELECT Punjabi_Idiom, roman, English_meaning, Equivalent_English_Idiom FROM proverbs")
    results = cursor.fetchall()
    conn.close()
    return results

# Fuzzy search now includes Romanized Punjabi
def fuzzy_search_partial(keyword, threshold=70):
    all_rows = get_all_proverbs()
    matches = []
    for row in all_rows:
        punjabi, romanized, meaning, equivalent = row
        punjabi_score = fuzz.partial_ratio(keyword, punjabi)
        romanized_score = fuzz.token_set_ratio(keyword, romanized if romanized else "")
        meaning_score = fuzz.partial_ratio(keyword, meaning)
        equivalent_score = fuzz.partial_ratio(keyword, equivalent if equivalent else "")
        
        if max(punjabi_score, romanized_score, meaning_score, equivalent_score) >= threshold:
            matches.append((punjabi, meaning, equivalent))  # Return consistent structure
    return matches

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    keyword = ""
    message = ""

    if request.method == 'POST':
        keyword = request.form['query'].strip()
        selected = request.form.get('selected', 'false') == 'true'

        if keyword:
            if selected:
                all_rows = get_all_proverbs()
                results = [row[:3] for row in all_rows if row[0] == keyword]
            else:
                results = fuzzy_search_partial(keyword)

            if not results:
                message = "No matching proverb found. Please try again or check the spelling."

    return render_template('a.html', results=results, keyword=keyword, message=message)


# Updated suggestions to use Romanized as well
@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '')
    suggestions = set()
    if query:
        all_rows = get_all_proverbs()
        for row in all_rows:
            punjabi = row[0]
            romanized = row[1] if row[1] else ""
            if fuzz.partial_ratio(query, punjabi) >= 60 or fuzz.partial_ratio(query, romanized) >= 80:
                suggestions.add(punjabi)
        suggestions = sorted(suggestions)[:10]
    return jsonify(list(suggestions))

if __name__ == '__main__':
    app.run(debug=True)
