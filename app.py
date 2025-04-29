from flask import Flask, render_template, request, jsonify
import sqlite3
from rapidfuzz import fuzz, process

app = Flask(__name__)


def get_all_proverbs():
    conn = sqlite3.connect('proverbs (1).db')
    cursor = conn.cursor()
    cursor.execute("SELECT Punjabi_Idiom, English_Transliteration, English_meaning, Equivalent_English_Idiom FROM proverbs")
    results = cursor.fetchall()
    conn.close()
    return results

def get_dynamic_threshold(query):
    length = len(query)
    if length <= 3:
        return 50
    elif length <= 60:
        return 65
    else:
        return 75

def fuzzy_search_partial(keyword):
    threshold = get_dynamic_threshold(keyword)
    all_rows = get_all_proverbs()
    matches = []
    for row in all_rows:
        punjabi, romanized, meaning, equivalent = row
        punjabi_score = fuzz.partial_ratio(keyword, punjabi)
        romanized_score = fuzz.partial_ratio(keyword, romanized if romanized else "")
        meaning_score = fuzz.partial_ratio(keyword, meaning)
        equivalent_score = fuzz.partial_ratio(keyword, equivalent if equivalent else "")
        
        if max(punjabi_score    , romanized_score, meaning_score, equivalent_score) >= threshold:
            matches.append((punjabi, romanized, meaning, equivalent))
    return matches[:10]


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    keyword = ""
    message = ""

    if request.method == 'POST':
        keyword = request.form['query'].strip()
        selected = request.form.get('selected', 'false') == 'true'

        if keyword:
            all_rows = get_all_proverbs()
            exact_results = [row for row in all_rows if row[0] == keyword or (row[1] and row[1].lower() == keyword.lower())]

            if exact_results:
                results = exact_results
            else:
                results = fuzzy_search_partial(keyword)

            if not results:
                message = "No matching proverb found. Please try again or check the spelling."

    return render_template('damo1 (1).html', results=results, keyword=keyword, message=message)


@app.route('/suggest', methods=['GET'])
def suggest():
    query = request.args.get('q', '').strip()
    suggestions = set()
    
    if query:
        all_rows = get_all_proverbs()
        is_romanized = all(ord(char) < 128 for char in query)

        for row in all_rows:
            punjabi = row[0]
            romanized = row[1] if row[1] else ""

            if is_romanized:
                if fuzz.partial_ratio(query, romanized) >= 80:
                    suggestions.add(romanized)
            else:
                if fuzz.partial_ratio(query, punjabi) >= 60:
                    suggestions.add(punjabi)

        suggestions = sorted(suggestions)[:10]
        
    return jsonify(list(suggestions))

if __name__ == '__main__':
    app.run(debug=True)
