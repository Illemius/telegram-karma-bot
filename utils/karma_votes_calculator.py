import re

COEFFICIENT = .445
KARMA_CHANGE_REGEX = '^(?P<vote>[+\-]{2,})(?P<description>.+)?'


def read_text(text):
    """
    Get data from text
    :param text:
    :return:
    """
    try:
        params = re.match(KARMA_CHANGE_REGEX, text, flags=re.MULTILINE | re.DOTALL).groupdict()
        modifier = params.get('vote', '0')
        description = (params.get('description') or '').strip()
    except:
        pass
    else:
        return modifier or '', description or ''


def calculate_modifiers_amount(modifier):
    """
    +/- counter
    :param modifier:
    :return:
    """
    temp = [0, 0]

    for symbol in modifier:
        if symbol == '+':
            temp[0] += 1
        elif symbol == '-':
            temp[1] += 1

    result = temp[0] - temp[1]
    if temp[0] > temp[1]:
        result -= 1
    elif temp[0] < temp[1]:
        result += 1
    return result


def calculate_karma_amount(count):
    """
    K = |N| ^ .445
    (N = 4096, K = 30)
    :param count:
    :return:
    """
    result = round(abs(count) ** COEFFICIENT)
    if count < 0:
        return -result
    return result


def parse_message(data):
    """
    Parse karma amount and message description
    :param data:
    :return:
    """
    modifier, description = read_text(data)
    modifiers_amount = calculate_modifiers_amount(modifier)
    amount = calculate_karma_amount(modifiers_amount)

    return amount, description


def demo(plus_count, minus_count):
    text = '+' * plus_count + '-' * minus_count + ' test'
    print(text, *parse_message(text))


if __name__ == '__main__':
    demo(10, 4)
    demo(0, 2)
    demo(5, 5)
