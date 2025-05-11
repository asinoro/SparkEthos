async def on_fetch(request):
    try:
        import httpx
        # Φόρτωση sparkethos_py.txt
        async with httpx.AsyncClient() as client:
            r = await client.get("https://asinoro.github.io/SparkEthos/sparkethos_py.txt")
            r.raise_for_status()
            content = r.text

        # Έλεγχος POST request για ηθική αλληλεπίδραση
        if request.method == "POST":
            data = await request.json()
            action = data.get("action", "")
            if action:
                ethical_check = {
                    "is_intelligent": "intelligence" in action.lower(),
                    "respects_autonomy": "autonomy" in action.lower(),
                    "no_harm": "harm" not in action.lower()
                }
                response = {
                    "action": action,
                    "ethical_check": ethical_check,
                    "recommendation": "Proceed" if all(ethical_check.values()) else "Reformulate or deny action"
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

# Εξαγωγή του handler για το Cloudflare Workers
addEventListener("fetch", lambda event: event.respondWith(on_fetch(event.request)))
