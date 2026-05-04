def format_memory(memory):
    formatted = ""
    for m in memory:
        formatted += f"User: {m['user']}\nBot: {m['bot']}\n"
    return formatted