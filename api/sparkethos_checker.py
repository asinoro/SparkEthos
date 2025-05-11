
import json
import os

def handler(request):
    try:
        # Υποθέτουμε ότι το sparkethos_py.txt είναι στη ρίζα
        file_path = os.path.join(os.path.dirname(__file__), '..', 'public', 'sparkethos_py.txt')
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "statusCode": 200,
            "body": json.dumps({
                "line_count": content.count("\n") + 1,
                "preview": content[:300]
            }),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
