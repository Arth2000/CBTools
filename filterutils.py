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
    from pymclevel.nbt import TAG_BYTE, TAG_SHORT, TAG_INT, TAG_LONG, TAG_FLOAT, TAG_DOUBLE, TAG_STRING, \
        TAG_Compound, TAG_List
except ImportError:
    TAG_BYTE = 1
    TAG_SHORT = 2
    TAG_INT = 3
    TAG_LONG = 4
    TAG_FLOAT = 5
    TAG_DOUBLE = 6
    TAG_STRING = 8
    TAG_Compound = dict
    TAG_List = list


__author__ = u'Arth2000'

WHOLE_WORLD_OPTION = u'On'
WHOLE_WORLD = u'Whole World'
BOX = u'Box'

ITEMS_TABLE = {0: u'air', 1: u'stone', 2: u'grass', 3: u'dirt', 4: u'cobblestone', 5: u'planks', 6: u'sapling',
               7: u'bedrock',
               8: u'flowing_water', 9: u'water', 10: u'flowing_lava', 11: u'lava', 12: u'sand', 13: u'gravel',
               14: u'gold_ore',
               15: u'iron_ore', 16: u'coal_ore', 17: u'log', 18: u'leaves', 19: u'sponge', 20: u'glass',
               21: u'lapis_ore',
               22: u'lapis_block', 23: u'dispenser', 24: u'sandstone', 25: u'noteblock', 26: u'bed',
               27: u'golden_rail',
               28: u'detector_rail', 29: u'sticky_piston', 30: u'web', 31: u'tallgrass', 32: u'deadbush',
               33: u'piston',
               34: u'piston_head', 35: u'wool', 37: u'yellow_flower', 38: u'red_flower', 39: u'brown_mushroom',
               40: u'red_mushroom', 41: u'gold_block', 42: u'iron_block', 43: u'double_stone_slab',
               44: u'stone_slab',
               45: u'brick_block', 46: u'tnt', 47: u'bookshelf', 48: u'mossy_cobblestone', 49: u'obsidian',
               50: u'torch',
               51: u'fire', 52: u'mob_spawner', 53: u'oak_stairs', 54: u'chest', 55: u'redstone_wire',
               56: u'diamond_ore',
               57: u'diamond_block', 58: u'crafting_table', 59: u'wheat', 60: u'farmland', 61: u'furnace',
               62: u'lit_furnace',
               63: u'standing_sign', 64: u'wooden_door', 65: u'ladder', 66: u'rail', 67: u'stone_stairs',
               68: u'wall_sign',
               69: u'lever', 70: u'stone_pressure_plate', 71: u'iron_door', 72: u'wooden_pressure_plate',
               73: u'redstone_ore', 74: u'lit_redstone_ore', 75: u'unlit_redstone_torch', 76: u'redstone_torch',
               77: u'stone_button', 78: u'snow_layer', 79: u'ice', 80: u'snow', 81: u'cactus', 82: u'clay',
               83: u'reeds',
               84: u'jukebox', 85: u'fence', 86: u'pumpkin', 87: u'netherrack', 88: u'soul_sand', 89: u'glowstone',
               90: u'portal', 91: u'lit_pumpkin', 92: u'cake', 93: u'unpowered_repeater', 94: u'powered_repeater',
               95: u'stained_glass', 96: u'trapdoor', 97: u'monster_egg', 98: u'stonebrick',
               99: u'brown_mushroom_block',
               100: u'red_mushroom_block', 101: u'iron_bars', 102: u'glass_pane', 103: u'melon_block',
               104: u'pumpkin_stem',
               105: u'melon_stem', 106: u'vine', 107: u'fence_gate', 108: u'brick_stairs',
               109: u'stone_brick_stairs',
               110: u'mycelium', 111: u'waterlily', 112: u'nether_brick', 113: u'nether_brick_fence',
               114: u'nether_brick_stairs', 115: u'nether_wart', 116: u'enchanting_table', 117: u'brewing_stand',
               118: u'cauldron', 119: u'end_portal', 120: u'end_portal_frame', 121: u'end_stone',
               122: u'dragon_egg',
               123: u'redstone_lamp', 124: u'lit_redstone_lamp', 125: u'double_wooden_slab', 126: u'wooden_slab',
               127: u'cocoa', 128: u'sandstone_stairs', 129: u'emerald_ore', 130: u'ender_chest',
               131: u'tripwire_hook',
               132: u'tripwire_hook', 133: u'emerald_block', 134: u'spruce_stairs', 135: u'birch_stairs',
               136: u'jungle_stairs', 137: u'command_block', 138: u'beacon', 139: u'cobblestone_wall',
               140: u'flower_pot',
               141: u'carrots', 142: u'potatoes', 143: u'wooden_button', 144: u'skull', 145: u'anvil',
               146: u'trapped_chest',
               147: u'light_weighted_pressure_plate', 148: u'heavy_weighted_pressure_plate',
               149: u'unpowered_comparator',
               150: u'powered_comparator', 151: u'daylight_detector', 152: u'redstone_block', 153: u'quartz_ore',
               154: u'hopper', 155: u'quartz_block', 156: u'quartz_stairs', 157: u'activator_rail', 158: u'dropper',
               159: u'stained_hardened_clay', 160: u'stained_glass_pane', 161: u'leaves2', 162: u'log2',
               163: u'acacia_stairs', 164: u'dark_oak_stairs', 165: u'slime', 166: u'barrier',
               167: u'iron_trapdoor',
               168: u'prismarine', 169: u'sea_lantern', 170: u'hay_block', 171: u'carpet', 172: u'hardened_clay',
               173: u'coal_block', 174: u'packed_ice', 175: u'double_plant', 176: u'standing_banner',
               177: u'wall_banner',
               178: u'daylight_detector_inverted', 179: u'red_sandstone', 180: u'red_sandstone_stairs',
               181: u'stone_slab2',
               182: u'double_stone_slab2', 183: u'spruce_fence_gate', 184: u'birch_fence_gate',
               185: u'jungle_fence_gate',
               186: u'dark_oak_fence_gate', 187: u'acacia_fence_gate', 188: u'spruce_fence', 189: u'birch_fence',
               190: u'jungle_fence', 191: u'dark_oak_fence', 192: u'acacia_fence', 193: u'spruce_door',
               194: u'birch_door',
               195: u'jungle_door', 196: u'acacia_door', 197: u'dark_oak_door', 2256: u'record_13',
               2257: u'record_cat',
               2258: u'record_blocks', 2259: u'record_chirp', 2260: u'record_far', 2261: u'record_mall',
               2262: u'record_mellohi', 2263: u'record_stal', 2264: u'record_strad', 2265: u'record_ward',
               2266: u'record_11', 2267: u'record_wait', 256: u'iron_shovel', 257: u'iron_pickaxe',
               258: u'iron_axe',
               259: u'flint_and_steel', 260: u'apple', 261: u'bow', 262: u'arrow', 263: u'coal', 264: u'diamond',
               265: u'iron_ingot', 266: u'gold_ingot', 267: u'iron_sword', 268: u'wooden_sword',
               269: u'wooden_shovel',
               270: u'wooden_pickaxe', 271: u'wooden_axe', 272: u'stone_sword', 273: u'stone_shovel',
               274: u'stone_pickaxe',
               275: u'stone_axe', 276: u'diamond_sword', 277: u'diamond_shovel', 278: u'diamond_pickaxe',
               279: u'diamond_axe', 280: u'stick', 281: u'bowl', 282: u'mushroom_stew', 283: u'golden_sword',
               284: u'golden_shovel', 285: u'golden_pickaxe', 286: u'golden_axe', 287: u'string', 288: u'feather',
               289: u'gunpowder', 290: u'wooden_hoe', 291: u'stone_hoe', 292: u'iron_hoe', 293: u'diamond_hoe',
               294: u'golden_hoe', 295: u'wheat_seeds', 296: u'wheat', 297: u'bread', 298: u'leather_helmet',
               299: u'leather_chestplate', 300: u'leather_leggings', 301: u'leather_boots',
               302: u'chainmail_helmet',
               303: u'chainmail_chestplate', 304: u'chainmail_leggings', 305: u'chainmail_boots',
               306: u'iron_helmet',
               307: u'iron_chestplate', 308: u'iron_leggings', 309: u'iron_boots', 310: u'diamond_helmet',
               311: u'diamond_chestplate', 312: u'diamond_leggings', 313: u'diamond_boots', 314: u'golden_helmet',
               315: u'golden_chestplate', 316: u'golden_leggings', 317: u'golden_boots', 318: u'flint',
               319: u'porkchop',
               320: u'cooked_porkchop', 321: u'painting', 322: u'golden_apple', 323: u'sign', 324: u'wooden_door',
               325: u'bucket', 326: u'water_bucket', 327: u'lava_bucket', 328: u'minecart', 329: u'saddle',
               330: u'iron_door',
               331: u'redstone', 332: u'snowball', 333: u'boat', 334: u'leather', 335: u'milk_bucket',
               336: u'brick',
               337: u'clay_ball', 338: u'reeds', 339: u'paper', 340: u'book', 341: u'slime_ball',
               342: u'chest_minecart',
               343: u'furnace_minecart', 344: u'egg', 345: u'compass', 346: u'fishing_rod', 347: u'clock',
               348: u'glowstone_dust', 349: u'fish', 350: u'cooked_fish', 351: u'dye', 352: u'bone', 353: u'sugar',
               354: u'cake', 355: u'bed', 356: u'repeater', 357: u'cookie', 358: u'filled_map', 359: u'shears',
               360: u'melon',
               361: u'pumpkin_seeds', 362: u'melon_seeds', 363: u'beef', 364: u'cooked_beef', 365: u'chicken',
               366: u'cooked_chicken', 367: u'rotten_flesh', 368: u'ender_pearl', 369: u'blaze_rod',
               370: u'ghast_tear',
               371: u'gold_nugget', 372: u'nether_wart', 373: u'potion', 374: u'glass_bottle', 375: u'spider_eye',
               376: u'fermented_spider_eye', 377: u'blaze_powder', 378: u'magma_cream', 379: u'brewing_stand',
               380: u'cauldron', 381: u'ender_eye', 382: u'speckled_melon', 383: u'spawn_egg',
               384: u'experience_bottle',
               385: u'fire_charge', 386: u'writable_book', 387: u'written_book', 388: u'emerald',
               389: u'item_frame',
               390: u'flower_pot', 391: u'carrot', 392: u'potato', 393: u'baked_potato', 394: u'poisonous_potato',
               395: u'map', 396: u'golden_carrot', 397: u'skull', 398: u'carrot_on_a_stick', 399: u'nether_star',
               400: u'pumpkin_pie', 401: u'fireworks', 402: u'firework_charge', 403: u'enchanted_book',
               404: u'comparator',
               405: u'netherbrick', 406: u'quartz', 407: u'tnt_minecart', 408: u'hopper_minecart',
               409: u'prismarine_shard',
               410: u'prismarine_crystals', 411: u'rabbit', 412: u'cooked_rabbit', 413: u'rabbit_stew',
               414: u'rabbit_foot',
               415: u'rabbit_hide', 416: u'armor_stand', 417: u'iron_horse_armor', 418: u'golden_horse_armor',
               419: u'diamond_horse_armor', 420: u'lead', 421: u'name_tag', 422: u'command_block_minecart',
               423: u'mutton',
               424: u'cooked_mutton', 425: u'banner', 427: u'spruce_door', 428: u'birch_door', 429: u'jungle_door',
               430: u'acacia_door', 431: u'dark_oak_door'}

# Parsing functions
SEL_PAT = re.compile(r'^@[apre](\[.*\])?$')
IMPLICIT_KEYS = [u'x', u'y', u'z', u'r']

TILE_ENTITIES = 0b01
TILE_ENTITY = TILE_ENTITIES
ENTITIES = 0b10
ENTITY = ENTITIES
TILE_AND_ENTITIES = 0b11

objects = {
    TILE_ENTITIES: 'getTileEntitiesInBox',
    ENTITIES: 'getEntitiesInBox'
}


def iter_on(predicate, what=TILE_AND_ENTITIES, whole_world_option=WHOLE_WORLD_OPTION, whole_world_=WHOLE_WORLD):
    """
    Iterate on the entities and/or tile entities in the box or the whole world

    Args:
        predicate: A function that given the options returns True when the entity should be formatted, False otherwise
        what: On what (Entities, TileEntities or both) this should iterate
        whole_world_option: The name of the option used to know if the filter should be applied on the whole world
        whole_world_: The value if it should be used on the whole world

    Returns:

    """

    def _iter_on(fun):
        def __iter_on(level, box, options):
            # Check if the box is actually the whole world
            if options[whole_world_option] == whole_world_:
                box = level.bounds

            dirty_chunks = []

            all_chunks = (chunk for chunk, slices, point in level.getChunkSlices(box))

            # Generator that yields that tile entities
            def get_tile_entities():
                for chunk in all_chunks:
                    dirty = False
                    for key, name in objects.iteritems():
                        if what & key:
                            for entity in chunk.__getattribute__(name)(box):
                                if predicate(entity):
                                    yield entity, key

                                    if not dirty:  # Stock the dirty chunks to not mark as dirty not dirty chunks
                                        dirty = True
                                        dirty_chunks.append(chunk)

            fun(level, box, options, get_tile_entities)

            for chunk in dirty_chunks:
                level.markDirtyChunk(*chunk.chunkPosition)

        return __iter_on

    return _iter_on

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


def suffix(suf):
    return lambda v: v + suf


NBT_SUFFIXES = {
    TAG_BYTE: suffix(u'b'),
    TAG_SHORT: suffix(u's'),
    TAG_LONG: suffix(u'L'),
    TAG_FLOAT: suffix(u'f'),
    TAG_DOUBLE: suffix(u'd'),
    TAG_STRING: lambda v: u'"' + v + u'"'
}


def nbt_string(tag):
    """
    Stringify the tag

    Args:
        tag: The tag to stringify

    Returns: A string representing the tag in a format usable in commands

    """
    if isinstance(tag, TAG_Compound):
        return tag_compound_string(tag)

    elif isinstance(tag, TAG_List):
        return tag_list_string(tag)

    else:
        return value_tag_string(tag)


def tag_compound_string(tag):
    """
    Stringify a compound tag

    Args:
        tag (TAG_Compound): The tag to stringify

    Returns (unicode): A string representing the tag in a format usable in commands

    """
    result = []
    for key, value in tag.iteritems():
        result.append(key + u':' + nbt_string(value))

    return u'{' + u','.join(result) + u'}'


def tag_list_string(tag):
    """
    Stringify a list tag

    Args:
        tag (TAG_List): The tag to stringify

    Return (unicode): A string representing the tag in a format usable in commands

    """
    result = []
    for value in tag:
        result.append(nbt_string(value))

    return u'[' + u','.join(result) + u']'


def value_tag_string(tag):
    """
    Stringify a string tag

    Args:
        tag: The tag to stringify

    Returns (basestring): A string representing the tag in a format usable in commands

    """
    return NBT_SUFFIXES.get(tag.tagID, lambda v: v)(unicode(tag.value))
