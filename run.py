import webbrowser
from threading import Timer
from app import create_app  # Ou la fonction/variable que tu utilises pour initialiser ton app Flask

app = create_app()

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    # Ouvre le navigateur au bout de 1.5 seconde (le temps que Flask démarre)
    Timer(1.5, open_browser).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
