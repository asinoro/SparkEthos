import os

def handler(event, context):
    try:
        with open("sparkethos_py.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/plain; charset=utf-8",
                "Access-Control-Allow-Origin": "*"
            },
            "body": content
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Error: {str(e)}"
        }