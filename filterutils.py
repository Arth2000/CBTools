# coding=utf-8
"""
MCEdit filter utilities

Current utilities:
    iter_tile_entities: A decorator to use on the perform function to iter some of the tile entities
    use_if: A decorator to use on command declarations that will disable their use if the given value is False
    make_place_around: A function that create a place_around function using the given prefix
    Some parsing commands for literal nbt tags
    Some stringify commands for builtin nbt tags
"""
import re

try:
    from pymclevel.nbt import TAG_Compound, TAG_List
except ImportError:
    TAG_Compound = dict
    TAG_List = list

__author__ = u'Arth2000'

WHOLE_WORLD_OPTION = u'On'
WHOLE_WORLD = u'Whole World'
BOX = u'Box'

# Parsing functions
SEL_PAT = re.compile(r'^@[apre](\[.*\])?$')
IMPLICIT_KEYS = [u'x', u'y', u'z', u'r']


def iter_tile_entities(predicate, whole_world_option=WHOLE_WORLD_OPTION, whole_world_name=WHOLE_WORLD):
    """
    Iterate over the tile entities that satisfies the given predicate and yield them.
    See UpdateTo1_9.py for an example

    Args:
        predicate: A predicate that says when the tile entity should be use or not
        whole_world_option (unicode): The option used to known if the box should be the whole world
        whole_world_name (unicode): The value if it is on the whole world


    """

    def _iter_tile_entities(fun):
        def __iter_tile_entities(level, box, options):
            # Check if the box is actually the whole world
            if options[whole_world_option] == whole_world_name:
                box = level.bounds

            dirty_chunks = []

            all_chunks = (chunk for chunk, slices, point in level.getChunkSlices(box))

            # Generator that yields that tile entities
            def get_tile_entities():
                for chunk in all_chunks:
                    tile_entities = chunk.getTileEntitiesInBox(box)
                    dirty = False

                    for tile_entity in tile_entities:
                        if predicate(tile_entity):
                            yield tile_entity

                            if not dirty:  # Stock the dirty chunks to not mark as dirty not dirty chunks
                                dirty = True
                                dirty_chunks.append(chunk)

            fun(level, box, options, get_tile_entities)

            for chunk in dirty_chunks:
                level.markDirtyChunk(*chunk.chunkPosition)

        return __iter_tile_entities

    return _iter_tile_entities


def use_if(use):
    """
    decorator that returns None is use is False

    >>> should_be_used = False
    >>> @use_if(should_be_used)
    ... def dummy():
    ...     print(u'This is a dummy function')
    ...
    >>> dummy is None
    True

    >>> should_be_used = True
    >>> @use_if(should_be_used)
    ... def dummy():
    ...     print(u'This is a dummy function')
    ...
    >>> dummy()
    This is a dummy function

    Args:
        use (bool): If the function should be used or not

    Returns: None if use is False, the function otherwise

    """

    def _use_if(value):
        if use:
            return value

        else:
            return None

    return _use_if


def make_place_around(around, exceptions=None, for_class=False):
    """
    Build a place_around function using around as what to place around the value

    >>> p = make_place_around(u'~~~', exceptions=(u'42', u'-42'))
    >>> p(u'This is a value')
    u'~~~This is a value~~~'
    >>> p(u'42')
    u'42'
    >>> p(u'-42', force=True)
    u'~~~-42~~~'
    >>> p(u'~~~666~~~')
    u'~~~666~~~'
    >>> p(u'~~~666')
    u'~~~~~~666~~~'

    :param around: What the place around the value
    :param exceptions: The values that should not be used
    :param for_class: If the place_around command is made to be used in a class ( return staticmethod(place_around) )
    :type around: unicode
    :type for_class: bool
    :return: A function that place around around the given value
    """

    def place_around(value, force=False):
        """
        A function that given some value place around around it if it isn't already there

        :param value: The value to format
        :type value: unicode
        :param force: If the value is a key or not
        :type force: bool
        :return: A string built using the given value
        """
        if not force and exceptions is not None:
            if hasattr(exceptions, u'match') and exceptions.match(value):
                return value

            if hasattr(exceptions, u'__contains__') and value in exceptions:
                return value

        if len(value) * 2 < len(around) or value[:len(around)] != around or value[-len(around):] != around:
            return around + value + around

        else:
            return value

    if for_class:
        place_around = staticmethod(place_around)

    return place_around


def make_get_value(is_nbt):
    if is_nbt:
        def get_value(tag, key):
            return tag[key].value

    else:
        def get_value(tag, key):
            return tag[key]

    return get_value


def make_set_value(is_nbt):
    if is_nbt:
        def set_value(tag, key, value):
            tag[key].value = value

    else:
        def set_value(tag, key, value):
            tag[key] = value

    return set_value


def make_get_set_and_pop_value(is_nbt):
    get_value = make_get_value(is_nbt)
    set_value = make_get_value(is_nbt)

    def pop_value(tag, key):
        value = get_value(tag, key)
        del tag[key]
        return value

    return get_value, set_value, pop_value


def parse_selector(sel):
    """
    Parse a selector
    :param sel: The selector
    :type sel: unicode
    :return: None is sel isn't a valid selector. Otherwise return (type, list of entries)
        where type is the type of the selector (a, p, r or e) and entries is a dict
    :rtype: (unicode, dict)
    
    >>> selector = u'@a[score_test_min=1,score_other_test=3,l=5]'
    >>> parsed_selector = parse_selector(selector)
    >>> expected_result = (u'a', {u'score_test_min': u'1', u'score_other_test': u'3', u'l': u'5'})
    >>> parsed_selector == expected_result
    True

    >>> selector = u'@a[score_test_min=1,score_other_test=3,l=5]'
    >>> parsed_selector = parse_selector(selector)
    >>> reformed_selector = selector_string(*parsed_selector)
    >>> reparsed_selector = parse_selector(reformed_selector)
    >>> parsed_selector == reparsed_selector
    True
    """
    if SEL_PAT.match(sel):
        type = sel[1]

        if len(sel) <= 4:
            return type, {}

        entries = {}
        implicit_key_index = 0

        values = sel[3:-1].split(u',')

        for v in values:
            v = v.split(u'=')
            if len(v) == 1:
                entries[IMPLICIT_KEYS[implicit_key_index]] = v[0]
                implicit_key_index += 1

            else:
                key, value = v
                entries[key] = value

        return type, entries

    return None


def parse_json(json, return_size=False):
    """
    Parse a json

    :param json: The json
    :type json: unicode
    :param return_size: If the size should be returned or not
    :type return_size: bool
    :return: The parsed json

    >>> json = u'["",{text:"This is some text",color:red,extra:[{text:" This is some other text",bold:true}]}]'
    >>> parsed_json = parse_json(json)
    >>> expected_result = [u'""',{u'text': u'"This is some text"', u'color': u'red', u'extra': \
           [{u'text': u'" This is some other text"', u'bold': u'true'}]}]
    >>> parsed_json == expected_result
    True
    """
    json = json.strip()
    try:
        return parse_compound(json, return_size)

    except Exception:
        pass

    try:
        value = parse_list(json)
        return value if return_size else value[1]

    except ValueError:
        raise ValueError(u'Invalid Json {}'.format(json))


def parse_compound(nbt, index=0, return_size=False):
    """
    Parse a compound tag

    :param nbt: The compound tag
    :param index: The index at which the compound tag starts
    :param return_size: If the size should be returned or not
    :return: The parsed compound tag

    >>> tag = u'{Equipment:[{id:269},{id:10},{id:100},{id:"minecraft:iron_chestplate"},{id:"minecraft:skull",' + \
               u'Damage:1}],Riding:{id:Pig}}'
    >>> result = parse_compound(tag)
    >>> expected_result = {u'Equipment': [{u'id': u'269'}, {u'id': u'10'}, {u'id': u'100'}, \
        {u'id': u'"minecraft:iron_chestplate"'}, {u'id': u'"minecraft:skull"', u'Damage': u'1'}], \
        u'Riding': {u'id': u'Pig'}}
    >>> result == expected_result
    True

    >>> other_tag = u'{Equipment:[{}]'
    >>> parse_compound(other_tag)
    Traceback (most recent call last):
        ...
    ValueError: Compound Tag is never closed in {Equipment:[{}]

    >>> parse_compound(u'{name:[value,othervalue]othername:othervalue}')
    Traceback (most recent call last):
        ...
    ValueError: Could not find "," in "{name:[value,othervalue]othername:othervalue}" from index 24 up to index 25.
    """
    if nbt[index] != u'{':
        raise ValueError(u'Expected character {{. Found character {} in {}'.format(nbt[index], nbt))

    tag = {}
    index += 1

    len_nbt = len(nbt)

    i = index
    while nbt[i] != u'}':
        if i > index:
            # To fo after the ,
            i = expect(nbt, i, u',')

            if nbt[i] == u'}':
                break

        i, key = parse_key(nbt, index=i)

        # To go after the :
        i += 1

        i, value = parse_value(nbt, index=i, in_compound=True)
        tag[key] = value

        if i >= len_nbt:
            raise ValueError(u'Compound Tag is never closed in {}'.format(nbt))

    return (i + 1, tag) if return_size else tag


def parse_list(nbt, index=0, return_size=True):
    """
    Parse a list tag

    :param nbt: The list tag
    :param index: The index at which it should start to read the tag
    :param return_size: If the size of the tag should be returned or not
    :return: The parsed list tag and the index at which it ends

    >>> tag = u'[1,2,3,4,5]'
    >>> index, result = parse_list(tag)
    >>> expected_result = [u'1', u'2', u'3', u'4', u'5']
    >>> len(result) == len(expected_result)
    True
    >>> result
    [u'1', u'2', u'3', u'4', u'5']
    >>> index
    11
    """
    if nbt[index] != u'[':
        raise ValueError(u'Expected character [. Found character {} in {}'.format(nbt[index], nbt))

    tag = []
    index += 1

    i = index
    while nbt[i] != u']':
        if i > index:
            i = expect(nbt, i, u',')

        i, value = parse_value(nbt, index=i, in_compound=False)
        tag.append(value)

    return (i + 1, tag) if return_size else tag


def expect(string, index, value):
    """
    Check if there is value at index in string

    >>> expect(u'[a,b,c,d]', 2, u',')
    3
    >>> expect(u'[{}}]', 3, u',')
    Traceback (most recent call last):
        ...
    ValueError: Could not find "," in "[{}}]" from index 3 up to index 4.

    :param string: The string
    :type string: unicode
    :param index: The index
    :type index: int
    :param value: The value to search
    :type value: unicode
    :return: The index at which value ends
    :rtype: int
    :raise ValueError: If it doesn't match
    """
    end = index + len(value)
    if end >= len(string) or string[index:end] != value:
        raise ValueError(u'Could not find "{}" in "{}" from index {} up to index {}.'.format(
            value, string, index, end))

    return end


def parse_key(nbt, index=0):
    """
    Parse a key in a compound tag


    Read the first key
    :param nbt: The key.
    :param index: The index at which the key starts
    :return: The parsed key and the index at which it ends

    >>> key = u'ThisIsAKey:ThisIsAValue'
    >>> index, result = parse_key(key)
    >>> result
    u'ThisIsAKey'
    >>> index
    10
    """
    i = 0
    key = []
    for i in range(index, len(nbt)):
        char = nbt[i]
        if char.isspace():
            continue

        if char == u':':
            break

        key.append(char)

    return i, u''.join(key)


def parse_value(nbt, index=0, in_compound=False):
    """
    Parse a value in a compound or list tag

    :param nbt: the value
    :param index: The index at which the value starts
    :param in_compound: If the value is inside a compound or a list tag
    :return: The parsed value and the index at which it ends
    >>> tag = u'{key:value}'
    >>> parse_value(tag) == parse_compound(tag, return_size=True)
    True

    >>> tag = u'[value,othervalue,42]'
    >>> parse_value(tag) == parse_list(tag)
    True

    >>> tag = u'"This is a string"'
    >>> parse_value(tag) == parse_string(tag)
    True

    >>> tag = u'This is a value, it ended at the ,'
    >>> parse_value(tag)
    (15, u'This is a value')
    """
    first_char = nbt[index]
    if first_char == u'{':
        return parse_compound(nbt, index=index, return_size=True)

    elif first_char == u'[':
        return parse_list(nbt, index=index)

    elif first_char == u'"':
        return parse_string(nbt, index=index)

    else:
        refused = (u',', u'}') if in_compound else (u',', u']')
        value = []
        i = 0
        for i in range(index, len(nbt)):
            char = nbt[i]
            if char in refused:
                break

            value.append(char)

        return i, u''.join(value)


def parse_string(nbt, index=0):
    """
    Parse a string

    >>> parse_string(u'"This is a string" It ended at the "')
    (18, u'"This is a string"')

    :param nbt: The string
    :param index: The index at which the string starts
    :return: The parsed string and the index at which it ends
    """
    if nbt[index] != u'"':
        raise ValueError(u'Invalid character. Expected character ". Found {} in {}'.format(nbt[index], nbt))

    value = [u'"']

    escaped = False
    for i in range(index + 1, len(nbt)):
        char = nbt[i]

        if escaped:
            escaped = False
            value.append(char)

        elif char == u'\\':
            escaped = True
            continue

        else:
            value.append(char)

            if char == u'"':
                return i + 1, u''.join(value)

    raise ValueError(u'String tag isn\'t closed in {}'.format(nbt))


# Stringify methods
def selector_string(type, entries):
    """
    Build a selector based on the given type and entries

    >>> type = u'a'
    >>> entries = {u'score_test_min': u'1'}
    >>> selector_string(type=type, entries=entries)
    u'@a[score_test_min=1]'

    :param type: The type of the selector (a, p, r or e)
    :type type: unicode
    :param entries: The key -> value pairs of this selector
    :type entries: dict[unicode, unicode]
    :return: A string made of type and entries
    :rtype: unicode
    """
    return u'@{}{}'.format(
        type, u'[' + u','.join(k + u'=' + v for k, v in entries.items()) + u']' if len(entries) > 0 else u'')


def make_get_value_from_value(is_nbt):
    if is_nbt:
        return lambda value: value if isinstance(value, TAG_List) or isinstance(value,
                                                                                TAG_Compound) else value.value

    else:
        return lambda value: value


def compound_string(tag, fun=lambda v, force=False: v, is_nbt=False, get_value=None):
    """
    Build a new string in the format of a compound tag with the given tag and function to apply to every value

    >>> compound_string({u'Key': u'Value'})
    u'{Key:Value}'

    >>> tag = u'{Equipment:[{id:269},{id:10},{id:100},{id:"minecraft:iron_chestplate"},{id:"minecraft:skull",' + \
               u'Damage:1}],Riding:{id:Pig}}'
    >>> parse_compound(compound_string(parse_compound(tag))) == \
            parse_compound(tag)
    True

    :param tag: The tag
    :param fun: A function to apply on every values
    :param is_nbt: True if the value is made using nbt tags in place of builtin types
    :param get_value: A function used to get a value
    :return: A string built using the given tag
    """
    get_value = get_value or make_get_value_from_value(is_nbt)

    string = [fun(key, force=True) + u':' + value_string(value, fun, get_value=get_value) for key, value in tag.items()]

    return u'{' + u','.join(string) + u'}'


def list_string(tag, fun=lambda v, force=False: v, is_nbt=False, get_value=None):
    """
    Build a new string in the format of a list tag with the given tag and function to apply to every value

    >>> list_string([u'1', u'2', u'3', u'JKLAMDZ', u'IZJLA', u'42'])
    u'[1,2,3,JKLAMDZ,IZJLA,42]'

    >>> tag = u'[1, 12, 42, 42, 1092, 666, -1]'
    >>> list_string(parse_list(tag, return_size=False)) == tag
    True

    :param tag: The tag
    :param fun: A function to apply on every value
    :param is_nbt: True if the value is made using nbt tags in place of builtin types
    :param get_value: A function used to get a value
    :return: A string built using the given tag
    """
    get_value = get_value or make_get_value_from_value(is_nbt)

    string = [value_string(element, fun, get_value=get_value) for element in tag]
    return u'[' + u','.join(string) + u']'


def value_string(value, fun=lambda v, force=False: v, is_nbt=False, get_value=None):
    """
    Build a new string of the given value

    >>> tag = {u'Key': u'Value'}
    >>> value_string(tag) == compound_string(tag)
    True

    >>> tag = [u'1', u'2', u'3', u'JKLAMDZ', u'IZJLA', u'42']
    >>> value_string(tag) == list_string(tag)
    True

    >>> value_string(u'102')
    u'102'

    :param value: The value
    :param fun: A function to apply on every value
    :param is_nbt: True if the value is made using nbt tags in place of builtin types
    :param get_value: A function used to get a value
    :return: A string built using the given value
    """
    get_value = get_value or make_get_value_from_value(is_nbt)

    if is_nbt:
        tag_compound = TAG_Compound
        tag_list = TAG_List

    else:
        tag_compound = dict
        tag_list = list

    if isinstance(value, tag_compound):
        return compound_string(value, fun, get_value=get_value)

    elif isinstance(value, tag_list):
        return list_string(value, fun, get_value=get_value)

    else:
        return fun(get_value(value))


json_values = re.compile(r'true|false|-?\d+(?:\.\d*)?')

place_quotes = make_place_around(u'"', exceptions=json_values)


def json_string(json):
    """
    Build a new string in the format of strict json using the given json

    >>> j = {u'text': u'This is some text', u'color': u'red'}
    >>> result = parse_json(json_string(j))
    >>> expected_result = {u'"text"': u'"This is some text"', u'"color"': u'"red"'}
    >>> result == expected_result
    True

    :param json: The json
    :type json: object
    :return: A string built using the give json
    """
    return value_string(json, fun=place_quotes)
