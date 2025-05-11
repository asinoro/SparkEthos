import json

def handler(event, context):
    try:
        with open("../sparkethos_py.txt", "r", encoding="utf-8") as f:
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
