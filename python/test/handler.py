def evaluate(payload: dict, context: dict) -> dict:
    print(f"Received payload: {payload}")
    print(f"Received context: {context}")
    print("---------------------------------------")

    return {"text": "some test output"}


def on_started(context: dict):
    print("on_started triggered!")
    print(context)
    print("---------------------------------------")


def on_stopped(context: dict):
    print("on_stopped triggered!")
    print(context)
    print("---------------------------------------")
