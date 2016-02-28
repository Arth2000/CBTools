# coding=utf-8
"""
MCEdit filter used to update Minecraft commands from 1.7 or 1.8 format to 1.9 format
"""

import string

from filterutils import *

__author__ = u'Arth2000'

# The name of the options
SAY_TO_TELLRAW = u'/say to /tellraw'
KEEP_SAY = 0
SAY_TO_TEXT = 1
SAY_TO_TRANSLATE = 2


class CommandPatternFormatter(string.Formatter):
    """
    >>> c = CommandPatternFormatter()
    >>> c.format('summon-by {entity} {nbt} {sel}')
    '^/?summon-by (?P<entity>\\\\S+) (?P<nbt>\\\\{.*\\\\}) (?P<sel>\\\\S+)$'

    >>> c.format('try {nbt-1} {nbt-2} {block}')
    '^/?try (?P<nbt-1>\\\\{.*\\\\}) (?P<nbt-2>\\\\{.*\\\\}) (?P<block>\\\\S+)$'

    """

    def vformat(self, format_string, args, kwargs):
        return r'^/?' + super(CommandPatternFormatter, self).vformat(format_string, args, kwargs) + r'$'

    DEFAULT_DICT = {
        'pos': r'(?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){2}',
        'x': r'(?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)',
        'y': r'(?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)',
        'z': r'(?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)',
        'nbt': r'\{.*\}',
        'json': r'.*',
        'cmd': r'.*',
        'line': r'.*',
    }

    def get_value(self, key, args, kwargs):
        try:
            super(CommandPatternFormatter, self).get_value(key=key, args=args, kwargs=kwargs)
        except (IndexError, KeyError):
            prefix = '(?P<' + key + '>'
            for start, value in self.DEFAULT_DICT.iteritems():
                if key.lower().startswith(start):
                    return prefix + value + ')'

            return prefix + r'\S+)'


class Formatter(object):
    KEEP_ID_TAG = {u'ench', u'CustomPotionEffects', u'SkullOwner', u'Decorations', u'tag'}

    class_commands = []

    class_init = False

    pattern_formatter = CommandPatternFormatter()

    # The table with the indices of the items

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

                tag[u'id'] = u'"minecraft:' + ITEMS_TABLE[int(id)] + u'"'

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

            if isinstance(self.pattern, basestring):
                self.pattern = re.compile(Formatter.pattern_formatter.format(self.pattern))

        def format(self, cmd, **kwargs):
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
                dic = match.groupdict()
                for key, value in kwargs.items():
                    dic[u'_' + key] = value

                return self.formatter(**dic)

    @classmethod
    def command(cls, pattern, commands=class_commands):
        """
        A decorator that defines that the following function is a command

        It adds the given command and the pattern to the list of known commands
        It adds the given command and the pattern to the list of known commands

        >>> f = Formatter()
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon-pos 666 42 ~-3 Zombie'
        >>> @f.inst_command(re.compile(r'^/?summon-pos(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) ' + \
                    r'(?P<entity>\S+)$'))
        ... def summon_pos(**dic):
        ...     return u'/summon {entity}{pos}'.format(**dic)
        ...
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon Zombie 666 42 ~-3'

        >>> @f.inst_command(u'foo-by {entity} {nbt} {sel}')
        ... def summon_by(**dic):
        ...     return u'/execute {sel} ~ ~ ~ /foo {entity} {nbt}'.format(**dic)
        ...
        >>> f.format_command(u'foo-by Zombie {Passengers:[{id:Pig}]} @a')
        u'/execute @a ~ ~ ~ /foo Zombie {Passengers:[{id:Pig}]}'

        :param pattern: The pattern of the command
        :param commands: The list of commands this command should be added to
        """

        if isinstance(pattern, basestring):
            pattern = re.compile(cls.pattern_formatter.format(pattern))

        def _command(cmd):
            if cmd is None:
                return None

            if hasattr(cmd, u'__call__'):
                entry = cls.CommandFormatter(pattern, cmd)

            else:
                entry = cmd(pattern)

            commands.append(entry)

            return cmd

        return _command

    def inst_command(self, pattern):
        return self.command(pattern, commands=self.commands)

    @classmethod
    def class_cmd(cls, clazz, commands=class_commands):
        """
        Adds a new command to the list of known commands

        Should be used on a class

        >>> f = Formatter()
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon-pos 666 42 ~-3 Zombie'
        >>> @f.inst_class_cmd
        ... class SummonPosCommand(Formatter.CommandFormatter):
        ...     pattern = re.compile(r'^/?summon-pos(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<entity>\S+)$')
        ...     formatter = lambda self, **dic: u'/summon {entity}{pos}'.format(**dic)
        ...
        >>> f.format_command(u'/summon-pos 666 42 ~-3 Zombie')
        u'/summon Zombie 666 42 ~-3'

        :param clazz: The class that should be added to the commands
        :param commands: The list of commands the new command should be added to
        """
        if clazz is None:
            return None

        commands.append(clazz())

        return clazz

    def inst_class_cmd(self, pattern):
        return self.class_cmd(pattern, commands=self.commands)

    @staticmethod
    def selector(fun):
        """
        A decorator that given the entries of a command parse the selector and the nbt

        >>> f = Formatter()
        >>> cmd = u'@e[type=Pig] {Riding:{id:Zombie}}'
        >>> f.format_command(cmd)
        u'@e[type=Pig] {Riding:{id:Zombie}}'

        >>> @f.inst_command(re.compile(r'^(?P<sel>\S+) (?P<nbt>\{.*\})$'))
        ... @f.selector
        ... def test_string(**dic):
        ...     return u'/testfor {sel} {nbt}'.format(**dic)
        ...
        >>> f.format_command(cmd)
        u'/testfor @e[type=Zombie] {Passengers:[{id:Pig}]}'

        :param fun: The function
        """

        def _selector(**dic):

            formatter = dic[u'_formatter']

            sel = parse_selector(dic[u'sel'])
            parsed_nbt = parse_compound(dic[u'nbt'])

            if sel is not None:  # If sel is a valid selector
                t = sel[1].get(u'type')  # Find the type of the selector

                # Parse the nbt with the given type
                nbt, type = formatter.format_compound(parsed_nbt, t)

                # Change the type if needed
                # Example: /summon Zombie ~ ~ ~ {Riding:{id:Pig}}
                # becomes  /summon Pig ~ ~ ~ {Passengers:[{id:Zombie}]}
                sel[1][u'type'] = type or t

                if sel[1][u'type'] is None:  # If there is no type defined then delete that entry
                    del sel[1][u'type']

                dic[u'sel'] = selector_string(*sel)

            else:
                nbt = formatter.format_compound(parsed_nbt, return_type=False)

            dic[u'nbt'] = compound_string(nbt)

            return fun(**dic)

        return _selector

    @staticmethod
    def nbt(fun):
        """
        A decorator that given the entries of a command parse and format the nbts

        >>> f = Formatter()
        >>> cmd = u'minecraft:command_block 666 42 ~-3 {Command:"minecraft:stone ~ ~1 ~ {}"}'
        >>> f.format_command(cmd)
        u'minecraft:command_block 666 42 ~-3 {Command:"minecraft:stone ~ ~1 ~ {}"}'
        >>> @f.inst_command(re.compile(r'(?P<block>\S+)(?P<pos>(?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3}) (?P<nbt>\{.*\})'))
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
            nbt = compound_string(dic[u'_formatter'].format_compound(parse_compound(dic[u'nbt']), return_type=False))
            dic[u'nbt'] = nbt
            return fun(**dic)

        return _nbt

    @staticmethod
    def json(fun):
        """
        A decorator that given every entries in a function parse the json and format it

        >>> f = Formatter()
        >>> cmd = u'print {ThisIsAJson:ThisIsAValue}'
        >>> f.format_command(cmd)
        u'print {ThisIsAJson:ThisIsAValue}'
        >>> @f.inst_command(re.compile(r'^/?print (?P<json>.*)$'))
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

    @staticmethod
    def __alias(pattern, string, dec):
        @dec(pattern)
        def formatter(**dic):
            return dic[u'_formatter'].format_command(string.format(**dic))

    @classmethod
    def alias(cls, pattern, string):
        cls.__alias(pattern, string, cls.command)

    def inst_alias(self, pattern, string):
        self.__alias(pattern, string, self.inst_command)

    @staticmethod
    def __cmd_shortcut(modifier, dec, for_class=True):
        """
        Make a new command shortcut

        Returns a function that does the same as
        create a shortcut for basic command definition:

        >>> def t(fun):
        ...     def _t(**dic):
        ...         dic[u't'] = u'Hello, World!'
        ...         return fun(**dic)
        ...     return _t
        ...
        >>> shortcut = Formatter.class_cmd_shortcut(t, for_class=False)
        >>> shortcut(re.compile(r'^/?superT (?P<value>.+)'), u'/megaT {value} {t}')
        >>> f = Formatter()
        >>> f.format_command(u'superT This is such a super T: ')
        u'/megaT This is such a super T: Hello, World!'


        Args:
            modifier: The modifier to apply on the function
            dec: The decorator to give the pattern to

        """

        def make_cmd(pattern, string=None):
            if string is None:
                if not isinstance(pattern, basestring):
                    raise ValueError('String cannot be None when pattern is not a string.')

                string = '/' + pattern

            @dec(pattern)
            @modifier
            def formatter(**kwargs):
                return string.format(**kwargs)

        if for_class:
            make_cmd = staticmethod(make_cmd)

        return make_cmd

    def inst_cmd_shortcut(self, type, for_class=True):
        return self.__cmd_shortcut(type, self.inst_command, for_class=for_class)

    @classmethod
    def class_cmd_shortcut(cls, type, for_class=True):
        return cls.__cmd_shortcut(type, cls.command, for_class=for_class)

    selector_cmd = None
    json_cmd = None
    nbt_cmd = None

    @classmethod
    def __class_init(cls):
        cls.selector_cmd = cls.class_cmd_shortcut(cls.selector)
        cls.json_cmd = cls.class_cmd_shortcut(cls.json)
        cls.nbt_cmd = cls.class_cmd_shortcut(cls.nbt)

        cls.__class_commands_init()

    @classmethod
    def __class_commands_init(cls):
        @cls.command(ur'execute {sel} {pos} {cmd}')
        def execute_string(**dic):
            return u'/execute {} {} {}'.format(dic[u'sel'], dic[u'pos'], dic[u'_formatter'].format_command(dic[u'cmd']))

        @cls.command(u'summon {entity} {pos} {nbt}')
        def summon_string(**dic):
            nbt, type = dic[u'_formatter'].format_compound(parse_compound(dic[u'nbt']), dic[u'entity'])

            return u'/summon {} {} {}'.format(type or dic[u'entity'], dic[u'pos'], compound_string(nbt))

        # The selector commands
        cls.selector_cmd(u'scoreboard players {op} {sel} {obj} {val} {nbt}')

        cls.selector_cmd(u'/testfor {sel} {nbt}')

        cls.selector_cmd(u'/entitydata {sel} {nbt}')

        # Custom commands
        cls.alias(u'summon-at {entity} {nbt} {pos}', u'/summon {entity} {pos} {nbt}')

        cls.alias(u'summon-if-at {entity} {nbt} {sel} {pos}', u'/execute {sel} ~ ~ ~ /summon {entity} {pos} {nbt}')

        # The json commands
        cls.json_cmd(u'/tellraw {sel} {json}')

        cls.json_cmd(u'/title {sel} {type} {json}')

        # The nbt commands
        cls.nbt_cmd(u'/give {sel} {item} {amount} {data} {nbt}')

        cls.nbt_cmd(u'/setblock {pos} {id} {data} {oldBlock} {nbt}')

        cls.nbt_cmd(u'/fill {pos1} {pos2} {id} {data} {oldBlock} {nbt}')

        cls.nbt_cmd(u'/blockdata {pos} {nbt}')

        replaceitem_pat = re.compile(
            r'^/?replaceitem (?P<where>block((?: (?:~?-?(?:\d+(?:\.\d*)?|\.\d+)|~)){3})|entity \S+) (?P<slot>\S+) '
            r'(?P<item>\S+) (?P<amount>\S+) (?P<data>\S+) (?P<nbt>\{.*\})$')
        cls.nbt_cmd(replaceitem_pat, u'/replaceitem {where} {slot} {item} {amount} {data} {nbt}')

        cls.nbt_cmd(u'/clear {sel} {item} {data} {maxCount} {nbt}')

        cls.nbt_cmd(u'/testforblock {pos} {id} {data} {nbt}')

    def __init__(self, say_to_tellraw=KEEP_SAY):
        if not self.class_init:
            self.__class_init()

        self.selector_inst_cmd = self.inst_cmd_shortcut(self.selector)
        self.json_inst_cmd = self.inst_cmd_shortcut(self.json)
        self.nbt_inst_cmd = self.inst_cmd_shortcut(self.nbt)

        self.commands = []

        @self.inst_class_cmd
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

    def format_command(self, cmd, nbt=None):
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

        >>> f.format_command(u'/summon-at Zombie {Riding:{id:Pig}} 666 42 ~-3')
        u'/summon Pig 666 42 ~-3 {Passengers:[{id:Zombie}]}'

        :param cmd: The command
        :type cmd: unicode
        :param nbt: The nbt values of the command block
        :return: The formatted command
        :rtype: str
        """
        cmd = cmd.strip()

        for command in self.commands + self.class_commands:

            result = command.format(cmd, nbt=nbt, formatter=self)
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
    (u'Custom Command Path', (u'string', u'value=')),
)

update_num_ids = True

displayName = u'UpdateTo1.9 MC{} R{}'.format(mc_version, release_version)


@iter_on(lambda te: te[u'id'].value == u'Control', TILE_ENTITIES)
def perform(level, box, options, tile_entities):
    formatter = Formatter.new(options)
    for cmd_block, _ in tile_entities():
        cm = cmd_block[u'Command'].value

        c = formatter.format_command(cm, cmd_block)

        cmd_block[u'Command'].value = c
