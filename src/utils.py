def drop_duplicates(ls, equal_func=None):
    result = []
    for item in ls:
        if equal_func:
            if not any(equal_func(item, existing) for existing in result):
                result.append(item)
        else:
            if item not in result:
                result.append(item)
    return result