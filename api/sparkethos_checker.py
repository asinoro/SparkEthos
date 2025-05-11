from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route("/api/sparkethos_checker")
def sparkethos_checker():
    try:
        r = requests.get("https://sparkethos.vercel.app/sparkethos_py.txt")
        r.raise_for_status()
        return Response(r.text, mimetype='text/plain')
    except Exception as e:
        return Response(f"Σφάλμα: {e}", status=500, mimetype='text/plain')

# Αν θες να το τρέξεις τοπικά:
if __name__ == "__main__":
    app.run(debug=True)
