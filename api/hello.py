import json

def handler(request):
    try:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Hello from Vercel Functions!"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
