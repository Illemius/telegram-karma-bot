snippets = (
    'helper',
)


def setup():
    for item in snippets:
        __import__(__package__ + '.' + item)
