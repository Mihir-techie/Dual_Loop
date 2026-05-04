def detect_sentiment(text):
    text = text.lower()

    if "angry" in text or "frustrated" in text:
        return "high"
    elif "not working" in text:
        return "medium"
    else:
        return "low"