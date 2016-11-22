snippets = (
#     'fix_utils',
    'helper',
    'karma',
)


def setup():
    for item in snippets:
        __import__(__package__ + '.' + item)
