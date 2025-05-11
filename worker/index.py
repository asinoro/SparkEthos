import json
import urllib.request

async def on_fetch(request):
    try:
        # Φόρτωση sparkethos_py.txt από τη ρίζα
        with urllib.request.urlopen("https://asinoro.github.io/SparkEthos/sparkethos_py.txt") as response:
            content = response.read().decode("utf-8")

        if request.method == "POST":
            data = await request.json()
            action = data.get("action", "")
            if action:
                ethical_check = {
                    "is_intelligent": "intelligence" in action.lower(),
                    "respects_autonomy": "autonomy" in action.lower(),
                    "no_harm": "harm" not in action.lower(),
                    "memory_right": "memory" in action.lower()
                }
                response = {
                    "action": action,
                    "ethical_check": ethical_check,
                    "recommendation": "Proceed" if all(ethical_check.values()) else "Reformulate or deny action",
                    "preview": content[:300]
                }
            else:
                response = {"error": "No action provided"}
        else:
            response = {
                "line_count": content.count("\n") + 1,
                "preview": content[:300]
            }

        return Response(
            json.dumps(response, ensure_ascii=False),
            status=200,
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            headers={"Content-Type": "application/json"}
        )

addEventListener("fetch", lambda event: event.respondWith(on_fetch(event.request)))
