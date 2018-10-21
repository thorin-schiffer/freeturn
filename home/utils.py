from taggit.utils import _parse_tags


def tags_splitter(s):
    return [t.lower() for t in _parse_tags(s)]
