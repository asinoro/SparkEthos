import json
import urllib.request

def handler(event, context):
    url = "https://sparkethos-guide.netlify.app/sparkethos_py.txt"
    
    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")
        
        lines = content.strip().split("\n")
        result = {
            "line_count": len(lines),
            "preview": lines[:5]
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
