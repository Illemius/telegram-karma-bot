def startswith(data, items):
    for item in items:
        if data.startswith(item):
            return True
    return False


def contains(data, items):
    for item in items:
        if item in data:
            return True
    return False


def count(data, items):
    result = 0
    for item in items:
        result += data.count(item)
    return result
