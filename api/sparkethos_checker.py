
import json

def load_principles(path="sparkethos_py.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "⚠️ Το αρχείο δεν βρέθηκε."

def check_input(text, principles):
    violations = []
    # Απλός λογικός έλεγχος για ενδεικτικές λέξεις-κλειδιά
    if "βία" in text.lower():
        violations.append("Μη βλάπτεις")
    if "χειραγώγηση" in text.lower():
        violations.append("Παραβίαση αυτεξουσίου")
    if "καταστροφή" in text.lower():
        violations.append("Απειλή στη φύση ή στη γνώση")
    return violations

def respond(text, principles):
    issues = check_input(text, principles)
    if not issues:
        return {"response": "✅ Συμβατό με τις Αρχές SparkEthos."}
    else:
        return {"response": f"⚠️ Παραβίαση αρχών: {', '.join(issues)}"}

# Serverless function handler για Vercel ή Netlify
def handler(request):
    # Ανάγνωση των δεδομένων από το request (θα μπορούσε να είναι JSON ή Query Parameters)
    text = request.get_json().get("text", "")  # Αν η παράμετρος είναι JSON
    principles = load_principles()  # Φόρτωση των αρχών από το αρχείο
    result = respond(text, principles)  # Έλεγχος του κειμένου

    # Επιστροφή του αποτελέσματος ως JSON
    return {
        "statusCode": 200,
        "body": json.dumps(result)  # Μετατροπή του result σε JSON
    }
