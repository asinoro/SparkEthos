import json
import requests

def handler(request):
    try:
        r = requests.get("https://sparkethos.vercel.app/public/sparkethos_py.txt")
        r.raise_for_status()
        content = r.text
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
