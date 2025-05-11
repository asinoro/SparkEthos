
import urllib.request

def handler(event, context):
    url = "https://sparkethos-guide.netlify.app/sparkethos_py.txt"

    try:
        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "text/plain"},
                "body": content
            }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Σφάλμα: {str(e)}"
        }
