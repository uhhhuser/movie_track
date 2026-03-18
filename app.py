from flask import Flask, render_template, request
from search import searchMovie

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    
    query = request.args.get('query', '')
    
    if query:
        results = searchMovie(query)
    else:
        results = []
    
    return render_template('search.html', query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)
