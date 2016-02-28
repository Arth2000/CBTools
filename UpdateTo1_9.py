# coding=utf-8
"""
MCEdit filter used to update Minecraft commands from 1.7 or 1.8 format to 1.9 format
"""

from filterutils import *

__author__ = u'Arth2000'

# The name of the options
SAY_TO_TELLRAW = u'/say to /tellraw'
KEEP_SAY = 0
SAY_TO_TEXT = 1
SAY_TO_TRANSLATE = 2


class Formatter(object):
    KEEP_ID_TAG = {u'ench', u'CustomPotionEffects', u'SkullOwner', u'Decorations', u'tag'}

    # The table with the indices of the items
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

    ITEM_ID_PAT = re.compile(r'^-?\d+(?P<type>[bBsSlL])?$')

    def format_compound(self, tag, base_entity=None, return_type=True, change_id=True):
        """
        Format a compound tag to fix 1.8 errors in it

        >>> # Create a new formatter
        >>> f = Formatter(SAY_TO_TRANSLATE)

        >>> # It changes the riding tag
        >>> f.format_compound({u'Riding': {u'id': u'Pig'}}, base_entity=u'Zombie')
        ({u'Passengers': [{u'id': u'Zombie'}]}, u'Pig')

        >>> # It changes the Equipment tag and the item ids
        >>> value = f.format_compound({u'Equipment': [{u'id': u'269'}, {u'id': u'"minecraft:diamond_boots"'}, \
                                                      {u'tag': {u'ench': [{u'id': u'16'}]}}]}, \
                                      return_type=False)
        >>> value[u'HandItems']
        [{u'id': u'"minecraft:wooden_shovel"'}, {}]
        >>> value[u'ArmorItems']
        [{u'id': u'"minecraft:diamond_boots"'}, {u'tag': {u'ench': [{u'id': u'16'}]}}]

        >>> # It changes the HealF and Health tags
        >>> f.format_compound({u'HealF': u'100F', u'Health': u'99'}, return_type=False)
        {u'Health': u'100F'}

        >>> # It changes teh DropChances tag
        >>> result = f.format_compound({u'DropChances': [u'1F', u'2F', u'0F', u'0.35F', u'0.8F']}, return_type=False)
        >>> result[u'HandDropChances']
        [u'1F', u'1F']
        >>> result[u'ArmorDropChances']
        [u'2F', u'0F', u'0.35F', u'0.8F']

        >>> # It changes the Command tag by formatting it
        >>> f.format_compound({u'Command': u'/summon Zombie ~ ~ ~ {Riding:{id:Pig}}'}, return_type=False)
        {u'Command': u'"/summon Pig ~ ~ ~ {Passengers:[{id:Zombie}]}"'}

        :param tag: The tag
        :type tag: dict
        :param base_entity: The base entity if there is one (for commands like /summon base_entity)
        :param return_type: If it's the first time this function is called
        :param change_id: If the id tag should be changed or not
        :return: The formatted compound tag
        """
        if tag is None:
            return None

        def format_c(tag):
            for k, v in tag.items():
                if isinstance(v, dict):
                    tag[k] = self.format_compound(v, return_type=False,
                                                  change_id=change_id and k not in self.KEEP_ID_TAG)

                elif isinstance(v, list):
                    format_l(v)

        def format_l(tag):
            for i, t in enumerate(tag):
                if isinstance(t, dict):
                    tag[i] = self.format_compound(t, return_type=False, change_id=change_id)

                elif isinstance(t, list):
                    format_l(t)

        format_c(tag)

        entity = None

        if update_num_ids and change_id and u'id' in tag:
            id = tag[u'id']
            match = self.ITEM_ID_PAT.match(id)
            if match:
                gd = match.groupdict()
                if gd.get(u'type') is not None:
                    id = id[:-1]

                tag[u'id'] = u'"minecraft:' + self.ITEMS_TABLE[int(id)] + u'"'

        if u'Command' in tag:
            cmd = tag[u'Command']
            tag[u'Command'] = u'"' + self.format_command(
                cmd[1:-1] if (cmd[0] == u'"' and cmd[-1] == u'"') else cmd) + u'"'

        if u'Equipment' in tag:
            equipment = tag.pop(u'Equipment')

            tag[u'HandItems'] = [equipment[0], {}]
            tag[u'ArmorItems'] = [equipment[i] for i in range(1, len(equipment))]

        if u'HealF' in tag:
            healF = tag.pop(u'HealF')
            tag[u'Health'] = healF

        if u'DropChances' in tag:
            drop_chances = tag.pop(u'DropChances')

            tag[u'HandDropChances'] = [drop_chances[0], drop_chances[0]]
            tag[u'ArmorDropChances'] = [drop_chances[i] for i in range(1, len(drop_chances))]

        if u'Riding' in tag:
            entity = self.format_compound(tag.pop(u'Riding'), return_type=False)

            if base_entity is not None:
                tag[u'id'] = base_entity

            if u'Passengers' not in entity:
                entity[u'Passengers'] = []

            entity[u'Passengers'].append(tag)
            tag = entity

        if return_type:
            if entity is not None and u'id' in entity:
                return tag, entity.pop(u'id')

            else:
                return tag, None

        return tag

    class CommandFormatter:
        """
        Represent a command formatter

        >>> c = Formatter.CommandFormatter( \
                re.compile(r'^/?summon-pos(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<entity>\S+)$'), \
                lambda **dic: u'/summon {entity}{pos}'.format(**dic))
        >>> c.format(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon Zombie 666 42 ~-3'
        """

        def __init__(self, pattern=None, formatter=None):
            if not hasattr(self, u'pattern'):
                self.pattern = pattern

            if not hasattr(self, u'formatter'):
                self.formatter = formatter

        def format(self, cmd):
            """
            Try to format the given command

            >>> c = Formatter.CommandFormatter( \
                re.compile(r'^/?summon-pos(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<entity>\S+)$'), \
                lambda **dic: u'/summon {entity}{pos}'.format(**dic))
            >>> str(c.format("/summon-pos This command doesn't match the pattern"))
            'None'
            >>> c.format("/summon-pos ~ ~ ~ ThisCommandDoesMatch")
            u'/summon ThisCommandDoesMatch ~ ~ ~'

            :param cmd: The command to format
            :return: The formatted command if it matches. None otherwise
            """
            match = self.pattern.match(cmd)
            if match is None:
                return None

            else:
                return self.formatter(**match.groupdict())

    def command(self, pattern):
        """
        A decorator that defines that the following function is a command

        It adds the given command and the pattern to the list of known commands

        >>> f = Formatter()
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon-pos 666 42 ~-3 Zombie'
        >>> @f.command(re.compile(r'^/?summon-pos(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<entity>\S+)$'))
        ... def summon_pos(**dic):
        ...     return u'/summon {entity}{pos}'.format(**dic)
        ...
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon Zombie 666 42 ~-3'

        :param pattern: The pattern of the command
        """

        def _command(cmd):
            if cmd is None:
                return None

            if hasattr(cmd, u'__call__'):
                entry = self.CommandFormatter(pattern, cmd)

            else:
                entry = cmd(pattern)

            self.commands.append(entry)

            return cmd

        return _command

    def class_cmd(self, cls):
        """
        Adds a new command to the list of known commands

        Should be used on a class

        >>> f = Formatter()
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon-pos 666 42 ~-3 Zombie'
        >>> @f.class_cmd
        ... class SummonPosCommand(Formatter.CommandFormatter):
        ...     pattern = re.compile(r'^/?summon-pos(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<entity>\S+)$')
        ...     formatter = lambda self, **dic: u'/summon {entity}{pos}'.format(**dic)
        ...
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon Zombie 666 42 ~-3'

        :param cls:
        :return:
        """
        if cls is None:
            return None

        self.commands.append(cls())

        return cls

    def selector(self, fun):
        """
        A decorator that given the entries of a command parse the selector and the nbt

        >>> f = Formatter()
        >>> cmd = u'@e[type=Pig] {Riding:{id:Zombie}}'
        >>> f.format_command(cmd)
        u'@e[type=Pig] {Riding:{id:Zombie}}'

        >>> @f.command(re.compile(r'^(?P<sel>\S+) (?P<nbt>\{.*\})$'))
        ... @f.selector
        ... def test_string(**dic):
        ...     return u'/testfor {sel} {nbt}'.format(**dic)
        ...
        >>> f.format_command(cmd)
        u'/testfor @e[type=Zombie] {Passengers:[{id:Pig}]}'

        :param fun: The function
        """

        def _selector(**dic):

            sel = parse_selector(dic[u'sel'])

            if sel is not None:  # If sel is a valid selector
                t = sel[1].get(u'type')  # Find the type of the selector

                # Parse the nbt with the given type
                nbt, type = self.format_compound(parse_compound(dic[u'nbt']), t)

                # Change the type if needed
                # Example: /summon Zombie ~ ~ ~ {Riding:{id:Pig}}
                # becomes  /summon Pig ~ ~ ~ {Passengers:[{id:Zombie}]}
                sel[1][u'type'] = type or t

                if sel[1][u'type'] is None:  # If there is no type defined then delete that entry
                    del sel[1][u'type']

                dic[u'sel'] = selector_string(*sel)

            else:
                nbt = self.format_compound(parse_compound(dic[u'nbt']), return_type=False)

            dic[u'nbt'] = compound_string(nbt)

            return fun(**dic)

        return _selector

    def nbt(self, fun):
        """
        A decorator that given the entries of a command parse and format the nbts

        >>> f = Formatter()
        >>> cmd = u'minecraft:command_block 666 42 ~-3 {Command:"minecraft:stone ~ ~1 ~ {}"}'
        >>> f.format_command(cmd)
        u'minecraft:command_block 666 42 ~-3 {Command:"minecraft:stone ~ ~1 ~ {}"}'
        >>> @f.command(re.compile(r'(?P<block>\S+)(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<nbt>\{.*\})'))
        ... @f.nbt
        ... def setblock(**dic):
        ...     return u'/setblock{pos} {block} 0 replace {nbt}'.format(**dic)
        ...
        >>> f.format_command(cmd)
        u'/setblock 666 42 ~-3 minecraft:command_block 0 replace {Command:"/setblock ~ ~1 ~ minecraft:stone 0 replace {}"}'


        :param fun: The function to decorate
        :return: The decorated function
        """

        def _nbt(**dic):
            nbt = compound_string(self.format_compound(parse_compound(dic[u'nbt']), return_type=False))
            dic[u'nbt'] = nbt
            return fun(**dic)

        return _nbt

    def json(self, fun):
        """
        A decorator that given every entries in a function parse the json and format it

        >>> f = Formatter()
        >>> cmd = u'print {ThisIsAJson:ThisIsAValue}'
        >>> f.format_command(cmd)
        u'print {ThisIsAJson:ThisIsAValue}'
        >>> @f.command(re.compile(r'^/?print (?P<json>.*)$'))
        ... @f.json
        ... def print_string(**dic):
        ...     return u'/tellraw @a {json}'.format(**dic)
        ...
        >>> f.format_command(cmd)
        u'/tellraw @a {"ThisIsAJson":"ThisIsAValue"}'

        :param fun:
        :return:
        """

        def _json(**dic):
            json = json_string(parse_json(dic[u'json']))
            dic[u'json'] = json
            return fun(**dic)

        return _json

    def selector_cmd(self, pattern, string):
        """
        Add a new command that uses a selector with the given pattern and string interpolation

        Same as
        @formatter.command(pattern)
        @formatter.selector
        def fun(**kwargs):
            return string.format(**kwargs)

        >>> f = Formatter()
        >>> cmd = u'@e[type=Pig] {Riding:{id:Zombie}}'
        >>> f.format_command(cmd)
        u'@e[type=Pig] {Riding:{id:Zombie}}'
        >>> f.selector_cmd(re.compile(r'^(?P<sel>\S+) (?P<nbt>\{.*\})$'), u'/testfor {sel} {nbt}')
        >>> f.format_command(cmd)
        u'/testfor @e[type=Zombie] {Passengers:[{id:Pig}]}'


        :param pattern: The pattern used to recognize the command
        :param string: The string used to build the result (Like u'/scoreboard players {op} {sel} {obj} {value} {nbt}')
        """

        @self.command(pattern)
        @self.selector
        def formatter(**kwargs):
            return string.format(**kwargs)

    def json_cmd(self, pattern, string):
        """
        Add a new command that uses some json

        Same as
        @formatter.command(pattern)
        @formatter.json
        def fun(**kwargs):
            return string.format(**kwargs)

        >>> f = Formatter()
        >>> cmd = u'print {ThisIsAJson:ThisIsAValue}'
        >>> f.format_command(cmd)
        u'print {ThisIsAJson:ThisIsAValue}'
        >>> f.json_cmd(re.compile(r'^/?print (?P<json>.*)$'), u'/tellraw @a {json}')
        >>> f.format_command(cmd)
        u'/tellraw @a {"ThisIsAJson":"ThisIsAValue"}'

        :param pattern: The pattern used to recognize the command
        :param string: The string used the build the result (Like u'/tellraw {sel} {json}')
        """

        @self.command(pattern)
        @self.json
        def formatter(**kwargs):
            return string.format(**kwargs)

    def nbt_cmd(self, pattern, string):
        """
        Add a new comand that uses some nbt

        Same as
        @formatter.command(pattern)
        @formatter.nbt
        def fun(**kwargs):
            return string.format(**kwargs)

        If you also need a selector use formatter.selector_cmd

        >>> f = Formatter()
        >>> cmd = u'minecraft:command_block 666 42 ~-3 {Command:"minecraft:stone ~ ~1 ~ {}"}'
        >>> f.format_command(cmd)
        u'minecraft:command_block 666 42 ~-3 {Command:"minecraft:stone ~ ~1 ~ {}"}'
        >>> f.nbt_cmd(re.compile(r'(?P<block>\S+)(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<nbt>\{.*\})'), \
                      u'/setblock{pos} {block} 0 replace {nbt}')
        >>> f.format_command(cmd)
        u'/setblock 666 42 ~-3 minecraft:command_block 0 replace {Command:"/setblock ~ ~1 ~ minecraft:stone 0 replace {}"}'

        :param pattern: The pattern used to recognize the command
        :param string: The string used to build the result (Like u'/give {sel} {item} {amount} {data} {nbt}')
        """

        @self.command(pattern)
        @self.nbt
        def formatter(**kwargs):
            return string.format(**kwargs)

    def __init__(self, say_to_tellraw=KEEP_SAY):
        self.commands = []

        execute_pat = re.compile(r'^(?P<execute>/?execute \S+(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3} )(?P<cmd>.+)$')

        @self.command(execute_pat)
        def execute_string(**dic):
            return dic[u'execute'] + self.format_command(dic[u'cmd'])

        summon_pat = re.compile(
            r'^/?summon (?P<entity>\S+) ?(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<nbt>\{.*\})$')

        @self.command(summon_pat)
        def summon_string(**dic):
            nbt, type = self.format_compound(parse_compound(dic[u'nbt']), dic[u'entity'])

            return u'/summon {}{} {}'.format(type or dic[u'entity'], dic[u'pos'], compound_string(nbt))

        # The selector commands
        scoreboard_pat = re.compile(
            r'^/?scoreboard players (?P<op>set|add|remove) (?P<sel>\S+) (?P<obj>\S+) (?P<val>\S+) (?P<nbt>\{.*\})$')
        self.selector_cmd(scoreboard_pat, u'/scoreboard players {op} {sel} {obj} {val} {nbt}')

        testfor_pat = re.compile(r'^/?testfor (?P<sel>\S+)(?: (?P<nbt>\{.*\}))$')
        self.selector_cmd(testfor_pat, u'/testfor {sel} {nbt}')

        entity_pat = re.compile(r'^/?entitydata (?P<sel>\S+) (?P<nbt>\{.*\})$')
        self.selector_cmd(entity_pat, u'/entitydata {sel} {nbt}')

        # Custom commands
        summon_at_pat = re.compile(
            r'^/?summon-at (?P<entity>\S+) (?P<nbt>\{.*\})(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3})')

        @self.command(summon_at_pat)
        def summon_at_string(**dic):
            return summon_string(**dic)

        summon_if_at_pat = re.compile(
            r'^/?summon-if-at (?P<entity>\S+) (?P<nbt>\{.*\}) (?P<sel>\S+)(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3})$')

        @self.command(summon_if_at_pat)
        def summon_if_at_string(**dic):
            return u'/execute {} ~ ~ ~ {}'.format(dic[u'sel'], summon_string(**dic))

        # The json commands
        tellraw_pat = re.compile(r'^/?tellraw (?P<sel>\S+) (?P<json>.*)$')
        self.json_cmd(tellraw_pat, u'/tellraw {sel} {json}')

        title_pat = re.compile(r'^/?title (?P<sel>\S+) (?P<type>title|subtitle) (?P<json>.*)$')
        self.json_cmd(title_pat, u'/title {sel} {type} {json}')

        # The nbt commands
        give_pat = re.compile(r'^/?give (?P<sel>\S+) (?P<item>\S+) (?P<amount>\S+) (?P<data>\S+) (?P<nbt>\{.*\})$')
        self.nbt_cmd(give_pat, u'/give {sel} {item} {amount} {data} {nbt}')

        setblock_pat = re.compile(
            r'^/?setblock(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<id>\S+) (?P<data>\S+) (?P<oldBlock>\S+)'
            r' (?P<nbt>\{.*\})$')
        self.nbt_cmd(setblock_pat, u'/setblock{pos} {id} {data} {oldBlock} {nbt}')

        fill_pat = re.compile(
            r'^/?fill(?P<pos1>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3})(?P<pos2>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~))'
            r'{3}) (?P<id>\S+) (?P<data>\S+) (?P<oldBlock>\S+) (?P<nbt>\{.*\})$')
        self.nbt_cmd(fill_pat, u'/fill{pos1}{pos2} {id} {data} {oldBlock} {nbt}')

        blockdata_pat = re.compile(r'^/?blockdata(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<nbt>\{.*\})$')
        self.nbt_cmd(blockdata_pat, u'/blockdata{pos} {nbt}')

        replaceitem_pat = re.compile(
            r'^/?replaceitem (?P<where>block((?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3})|entity \S+) (?P<slot>\S+) '
            r'(?P<item>\S+) (?P<amount>\S+) (?P<data>\S+) (?P<nbt>\{.*\})$')
        self.nbt_cmd(replaceitem_pat, u'/replaceitem {where} {slot} {item} {amount} {data} {nbt}')

        clear_pat = re.compile(r'^/?clear (?P<sel>\S+) (?P<item>\S+) (?P<data>\S+) (?P<maxCount>\S+) (?P<nbt>\{.*\})$')
        self.nbt_cmd(clear_pat, u'/clear {sel} {item} {data} {maxCount} {nbt}')

        testforblock_pat = re.compile(
            r'^/?testforblock(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<id>\S+) (?P<data>\S+) '
            r'(?P<nbt>\{.*\})$')
        self.nbt_cmd(testforblock_pat, u'/testforblock{pos} {id} {data} {nbt}')

        @self.class_cmd
        @use_if(say_to_tellraw == SAY_TO_TEXT or say_to_tellraw == SAY_TO_TRANSLATE)
        class SayCommand(object, self.CommandFormatter):
            """
            Command that change a /say command into a /tellraw command
            """

            pattern = re.compile(r'^/?say (?P<value>.*)$')

            # Some useful values

            # Color codes
            COLOR_BLACK = 0
            COLOR_DARK_BLUE = 1
            COLOR_DARK_GREEN = 2
            COLOR_DARK_AQUA = 3
            COLOR_DARK_RED = 4
            COLOR_DARK_PURPLE = 5
            COLOR_GOLD = 6
            COLOR_GRAY = 7
            COLOR_DARK_GRAY = 8
            COLOR_BLUE = 9
            COLOR_GREEN = 10
            COLOR_AQUA = 11
            COLOR_RED = 12
            COLOR_LIGHT_PURPLE = 13
            COLOR_YELLOW = 14
            COLOR_WHITE = 15
            COLOR_RESET = 16

            # Modifier codes
            # Used to make a bitmask
            NULL = 0b00000
            BOLD = 0b00001
            OBFUSCATED = 0b00010
            STRIKETHROUGH = 0b00100
            UNDERLINED = 0b01000
            ITALIC = 0b10000

            # The value to the name
            color_values = {COLOR_BLACK: u'black', COLOR_DARK_BLUE: u'dark_blue', COLOR_DARK_GREEN: u'dark_green',
                            COLOR_DARK_AQUA: u'dark_aqua', COLOR_DARK_RED: u'dark_red',
                            COLOR_DARK_PURPLE: u'dark_purple',
                            COLOR_GOLD: u'gold', COLOR_GRAY: u'gray', COLOR_DARK_GRAY: u'dark_gray',
                            COLOR_BLUE: u'blue',
                            COLOR_GREEN: u'green', COLOR_AQUA: u'aqua', COLOR_RED: u'red',
                            COLOR_LIGHT_PURPLE: u'light_purple', COLOR_YELLOW: u'yellow', COLOR_WHITE: u'white',
                            COLOR_RESET: u'reset'}

            # The code to the value
            color_table = {u'0': COLOR_BLACK, u'1': COLOR_DARK_BLUE, u'2': COLOR_DARK_GREEN, u'3': COLOR_DARK_AQUA,
                           u'4': COLOR_DARK_RED, u'5': COLOR_DARK_PURPLE, u'6': COLOR_GOLD, u'7': COLOR_GRAY,
                           u'8': COLOR_DARK_GRAY, u'9': COLOR_BLUE, u'a': COLOR_GREEN, u'b': COLOR_AQUA,
                           u'c': COLOR_RED,
                           u'd': COLOR_LIGHT_PURPLE, u'e': COLOR_YELLOW, u'f': COLOR_WHITE, u'r': COLOR_RESET}

            # The code to the value
            modifier_table = {u'l': BOLD, u'k': OBFUSCATED, u'm': STRIKETHROUGH, u'n': UNDERLINED, u'o': ITALIC}

            modifier_values = {BOLD: u'"bold":true', OBFUSCATED: u'"obfuscated":true',
                               STRIKETHROUGH: u'"strikethrough":true', UNDERLINED: u'"underlined":true',
                               ITALIC: u'"italic":true'}

            selector_pattern = re.compile(r'(@[apre](?:(?:\[(?:\w+=\w+)*\])|(?=\s)|$))')

            def __init__(self):
                super(self.__class__, self).__init__()

                if say_to_tellraw == SAY_TO_TRANSLATE:
                    self.text_tag = u'translate'

                elif say_to_tellraw == SAY_TO_TEXT:
                    self.text_tag = u'text'

            def formatter(self, **dic):
                value = dic[u'value']

                result = []

                for color, modifier, text in self.split_value(value):
                    c = self.get_color(color)
                    modifiers = self.get_modifiers_json(modifier)

                    for t in self.get_text(text):
                        result.append(modifiers + [c, t])

                return u'/tellraw @a ["",{' + u'},{'.join(map(u','.join, result)) + u'}]'

            @classmethod
            def split_value(cls, text):
                parts = text.split(u'§')

                modifier = cls.NULL
                color = cls.COLOR_RESET

                yield color, modifier, parts.pop(0)

                for mod, part in cls.split_parts(parts):
                    if mod in cls.modifier_table:
                        modifier |= cls.modifier_table[mod]

                    elif mod in cls.color_table:
                        color = cls.color_table[mod]
                        modifier = cls.NULL

                    if part == u'':
                        continue

                    yield color, modifier, part

            @staticmethod
            def split_parts(parts):
                for part in parts:
                    yield part[0], part[1:]

            def get_text(self, text):
                parts = self.selector_pattern.split(text)

                sel = True
                for p in parts:
                    sel = not sel

                    if sel:
                        yield u'"selector":"' + p + u'"'
                        continue

                    elif p == u'':
                        continue

                    elif self.text_tag == u'translate':
                        p = p.replace(u'%', u'%%')
                        p = p.replace(u'"', u'\\"')
                        nb_eq = p.count(u'=')
                        if nb_eq > 0:
                            yield u'"translate":"' + p.replace(u'=', u'%s') + u'","with":[' + u','.join(
                                [u'"="'] * nb_eq) + u']'

                        else:
                            yield u'"translate":"' + p + u'"'

                    else:
                        yield u'"' + self.text_tag + u'":"' + p + u'"'

            @classmethod
            def get_color(cls, color):
                return u'"color":"' + cls.color_values[color] + u'"'

            @classmethod
            def get_modifiers_json(cls, modifiers):
                result = []
                for key, value in cls.modifier_values.items():
                    if modifiers & key:
                        result.append(value)

                return result

    def format_command(self, cmd):
        """
        Format a single command

        Looks into every pattern to see if it matches.
        If it does then it returns its stringify method

        >>> f = Formatter(SAY_TO_TRANSLATE)
        >>> f.format_command(u'/execute @a ~ ~ ~ /say link=99% noob')
        u'/execute @a ~ ~ ~ /tellraw @a ["",{"color":"reset","translate":"link%s99%% noob","with":["="]}]'

        >>> summon = f.format_command(u'/summon Zombie ~ ~ ~ {Equipment:[{id:269}],Riding:{id:Pig}}')
        >>> m = re.match(r'^/summon Pig ~ ~ ~ (?P<nbt>\{.*\})$', summon)
        >>> m is not None
        True
        >>> expected_result = {u'Passengers': [ \
            {u'id': u'Zombie', u'HandItems':[{u'id': u'"minecraft:wooden_shovel"'}, {}], u'ArmorItems': []}]}
        >>> parse_compound(m.groupdict()[u'nbt']) == expected_result
        True

        >>> f.format_command(u'/scoreboard players set @e[type=Zombie] test 1 {DropChances:[0F,0F,1F,2F,0.35F]}')
        u'/scoreboard players set @e[type=Zombie] test 1 {HandDropChances:[0F,0F],ArmorDropChances:[0F,1F,2F,0.35F]}'

        :param cmd: The command
        :type cmd: unicode
        :return: The formated command
        :rtype: str
        """
        cmd = cmd.strip()

        for command in self.commands:

            result = command.format(cmd)
            if result is not None:
                return result

        return cmd

    options = [
        (u'/say to /tellraw', u'say_to_tellraw',
         {u'Use Translate': SAY_TO_TRANSLATE, u'Use text': SAY_TO_TEXT, u'No': KEEP_SAY})
    ]

    @classmethod
    def new(cls, options):
        return cls(**{key: values[options[name]] for name, key, values in cls.options})


# The minecraft version this filter is made for
mc_version = u'1.8'

# The release version
release_version = u'1.1.3'

# The inputs
inputs = (
    (WHOLE_WORLD_OPTION, (WHOLE_WORLD, BOX)),
    (u'/say to /tellraw', (u'Use Translate', u'Use Text', u'No')),
    (u'Update Numerical IDs', True),
)

update_num_ids = True

displayName = u'UpdateTo1.9 MC{} R{}'.format(mc_version, release_version)


@iter_tile_entities(lambda te: te[u'id'].value == u'Control')
def perform(level, box, options, tile_entities):
    formatter = Formatter.new(options)
    for cmd_block in tile_entities():
        cm = cmd_block[u'Command'].value
        print(cm)

        c = formatter.format_command(cm)
        print(c)

        cmd_block[u'Command'].value = c
