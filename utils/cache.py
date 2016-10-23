users_cache = {}


def update_cached_user(user, chat, data):
    global users_cache
    if user not in users_cache:
        users_cache[user] = {}
    if chat not in users_cache[user]:
        users_cache[user][chat] = {}
    res = users_cache[user][chat]
    res.update(data)
    users_cache[user][chat] = res


def get_cached_user(user, default=None):
    global users_cache
    return users_cache.get(user, default or {})


def get_cached_user_chat(user, chat, default=None):
    return get_cached_user(user).get(chat, default or {})
