import re

from utils.text_utils import startswith, count

COEFFICIENT = .445
KARMA_CHANGE_REGEX = '^(?P<vote>[+\-]{1,}|(?:🍪|👍🏻|👍🏼|👍🏽|👍🏾|👍🏿|👍|👎🏻|👎🏼|👎🏽|👎🏾|👎🏿|👎)+)(?P<description>.+)?'


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
        return '', ''
    else:
        return modifier or '', description or ''


def calculate_modifiers_amount(modifier):
    """
    +/- counter
    :param modifier:
    :return:
    """
    temp = [0, 0]

    temp[0] = count(modifier, ('+', '👍', '🍪'))
    temp[1] = count(modifier, ('-', '👎'))

    result = temp[0] - temp[1]
    if startswith(modifier, ('+', '-')):
        if temp[0] > temp[1]:
            result -= 1
        elif temp[0] < temp[1]:
            result += 1
    return result


def change_karma_calculator(skip_amount=5):
    def decorator(func):
        def wrapper(count):
            if count > skip_amount:
                return skip_amount + func(count - skip_amount)
            return count

        return wrapper

    return decorator


@change_karma_calculator(5)
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
