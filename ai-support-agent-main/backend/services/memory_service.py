memory_db = {}

def get_memory(user_id):
    return memory_db.get(user_id, [])

def save_memory(user_id, user_msg, bot_response):
    if user_id not in memory_db:
        memory_db[user_id] = []

    memory_db[user_id].append({
        "user": user_msg,
        "bot": bot_response
    })