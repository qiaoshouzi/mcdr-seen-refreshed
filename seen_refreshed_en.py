# Editable contents /
config_path = 'config/seenr_config.yml' # config file
log_file = 'logs/seen_refreshed.log' # log file
# end editable contents / DO NOT have the items below changed unless you know how this plugin works.
import json
import os
import shutil
import time
import re
from mcdreforged.api.all import *
import datetime
import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

PLUGIN_METADATA = {
    'id': 'mcdr_seen_refreshed',
    'version': '1.0.1',
    'name': 'Seen and Liver Refreshed',
    'author': [
        'Pandaria',
        'Fallen_Breath',
        'Ra1ny_Yuki'
    ],
    'link': 'https://github.com/ra1ny-yuki/mcdr-seen-refreshed',
    'dependencies': {
        'mcdreforged': '>=1.0.0'
    }
}
top_args = {
            '-player': '§dplayer only§r',
            '-all': '§7all players§r',
            '-merge': '§7all players§r/§emerged§r',
            '-bot': '§5bot only§r',
            '': ''
        }
pattern_isbot = {'bot': '§5Bot§r ', 'player': '§dPlayer§r '}
bot_list = []
config_file = os.path.join(config_path)
default_config = {
    'seen_prefix': '!!seen',
    'seen_top_prefix': '!!seen-top',
    'liver_prefix': '!!liver',
    'msg_prefix': '[SeenR] ',
    'seen_file': 'config/seenr_data.json'
        }
config_comment = {
    'seen_prefix': 'Command prefix of querying player time since offline, reloading plugin and showing help message.',
    'seen_top_prefix': 'Command prefix of showing the rank of time since offline.',
    'liver_prefix': 'Command prefix of querying player online time.',
    'msg_prefix': 'The content prefix of the message showed by this plugin.',
    'seen_file': 'Player online time data file is stored here.'
}

def output_log(msg : str):
    msg = msg.replace('§r', '').replace('§d', '').replace('§c', '').replace('§6', '').replace('§e', '').replace('§a', '')
    with open(os.path.join(log_file), 'a+') as log:
        log.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + msg + '\n')
    print("[MCDR] " + datetime.datetime.now().strftime("[%H:%M:%S]") + ' [{}/\033[1;32mINFO\033[0m] '.format(PLUGIN_METADATA['id']) + msg)

def refresh_config():
    config_path = os.path.join(config_file)
    global seen_prefix, seen_top_prefix, liver_prefix, seen_file, default_msg_prefix
    if not os.path.exists(config_path):
        open(config_path, 'w+', encoding='UTF-8').close()
    with open(config_path, 'r', encoding='UTF-8') as f:
        cfg = ruamel.yaml.round_trip_load(f)
    for key in default_config.keys():
        try:
            cfg[key]
        except KeyError:
            cfg[key] = default_config[key]
            output_log('Invalid key {} in config file, regenerated this key with its default value.'.format(key))
        except TypeError:
            cfg = default_config
            output_log('Invalid config file, regenerated config with default content.')
            break
        except Exception as e:
            output_log(f'Error Occured. Interrupted loading config. Error info: {e}')
            return
    config = CommentedMap(cfg)
    for key, value in config_comment.items():
        config.yaml_add_eol_comment(value, key)
    with open(config_path, 'w+', encoding = 'UTF-8') as f:
        ruamel.yaml.round_trip_dump(config, f, allow_unicode = True)
    seen_prefix = config['seen_prefix']
    seen_top_prefix = config['seen_top_prefix']
    liver_prefix = config['liver_prefix']
    seen_file = config['seen_file']
    default_msg_prefix = config['msg_prefix']
refresh_config()


def rclick(message: str, hover_text: str, rcontent: str, cevent = 0):
    event_list = [RAction.run_command, RAction.suggest_command, RAction.copy_to_clipboard, RAction.open_url, RAction.open_file]
    return RText(message).set_hover_text(hover_text).set_click_event(event_list[cevent], rcontent)

def display_message(src: CommandSource or Info, msg: str, msg_prefix = default_msg_prefix, broadcast = False):
    try:
        source = src.get_command_source()
    except:
        source = src
    msg = msg_prefix + msg
    if source.is_player and broadcast:
        source.get_server().say(msg)
    else:
        source.reply(msg)


def parse_join_info(info: Info):
    content_splitted = info.content.split(' logged in with entity id ')
    if len(content_splitted) > 1:
        player_info = content_splitted[0].strip(']')
        player_info_list = player_info.split('[')
        player = player_info_list[0]
        player_ip = player_info_list[1]
        ret = [True, player]
        if player_ip == 'local':
            ret[1] = ret[1] + '@bot'
        return ret
    else:
        return [False]
        

def parse_left_info(info: Info):
    content_splitted = info.content.split(' lost connection: ')
    if len(content_splitted) > 1:
        player = content_splitted[0].strip()
        ret = [True, player]
        if content_splitted[1].strip() == 'Killed':
            ret[1] = ret[1] + '@bot'
        return ret
    else:
        return [False]

helpmsg = f'''------ {PLUGIN_METADATA['name']} v{PLUGIN_METADATA['version']} ------
A plugin to query players online and offline time.
§d【Command Help】§r
§7{seen_prefix}§r Show this message.
§7{seen_prefix} reload§r Reload this plugin.
§7{seen_prefix}§r §e<player>§r Query player's offline time.
§7{seen_top_prefix}§r Show the rank of offline time
§7{liver_prefix}§r §e<player>§r Query player's online time.
§7{liver_prefix}§r Show the rank of online time.
§d【Additional Arguments】§r
You can add more arguments when showing the ranks.
The data will not include bot if no more arguments given.
§e(Shadowing player will be proccessed as bot too.)§r
§6There is following arguments available:§6
The argument in same color mustn't be given in 1 command.
§6-all§r Show all the data.
§6-merge§r Show all the data (merging bot and player data)
§6-bot§r Show bot data only.
§e-full§r Can only be used on offline rank, Show all the data instead of top 10, §ebut may show too much message sometimes.
'''.strip()

def display_help(info: Info):
    msg_converted = ''
    prefix = None
    for line in helpmsg.splitlines():
        if not msg_converted == '':
            msg_converted = msg_converted + '\n'
        prefix_seen = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(seen_prefix), line)
        prefix_seen_top = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(seen_top_prefix), line)
        prefix_liver = re.search(r'(?<=§7){}[\w ]*(?=§)'.format(liver_prefix), line)
        if not prefix_seen == prefix_liver == prefix_seen_top:
            if prefix_seen is not None:
                prefix = prefix_seen
            elif prefix_seen_top is not None:
                prefix = prefix_seen_top
            else:
                prefix = prefix_liver
            msg_converted = msg_converted + rclick(line, 'Click here to suggest command.', prefix.group(), 1)
        else:
            msg_converted = msg_converted + line
    display_message(info, msg_converted, '')

def seens_from_file():
    convert_from_mcd = False
    if os.path.isfile("seen.json") and not os.path.exists(seen_file):
        convert_from_mcd = True
        shutil.move("seen.json", seen_file)
    if os.path.isfile("config/seen.json") and not os.path.exists(seen_file):
        convert_from_mcd = True
        shutil.move("config/seen.json", seen_file)        
    if not os.path.exists(seen_file):
        with open(seen_file, "w") as f:
            d = {}
            json.dump(d, f)
        output_log('Seen file invalid, regenerated.')
    with open(seen_file, "r") as f:
        seens_raw = json.load(f)
    if convert_from_mcd:
        seens = {}
        for key, value in seens_raw.items():
            if is_bot(key):
                key = key + '@bot'
            seens[key] = value
        with open(seen_file, "w") as f:
            json.dump(seens, f)
        output_log('Seen file from MCD Seen discovered, converted to newer format.')
    else:
        seens = seens_raw
    return seens
    

@new_thread(PLUGIN_METADATA['id'])
def seen(info: Info, player: str):
    joined, left = player_seen(player)
    bot_joined, bot_left = player_seen(player + '@bot')
    msg = "There isn't data for §dplayer§e {}§r".format(player)
    player_livering = False
    if left == 0 and joined == 0:
        pass
    elif left < joined:
        dt = delta_time(joined)
        ft = formatted_time(dt)
        player_livering = True
        msg = "§dPlayer§e {}§r isnt't offline, and have been online for §a{}§r".format(player, ft)
    elif left > joined:
        dt = delta_time(left)
        ft = formatted_time(dt)
        msg = "§dPlayer§e {}§r have been offline for §6{t}§r".format(player, t = ft)
    else:
        raise ValueError('Error parsing player data. ')
    if bot_left == 0 and bot_joined == 0:
        pass
    elif bot_left < bot_joined:
        if player_livering:
            raise ValueError('Error confirming if bot online. ')
        else:
            bdt = delta_time(bot_joined)
            bft = formatted_time(bdt)
            msg = msg + "\nBut§5 Bot§e {}§r have been spawned for §a{}§r".format(player, bft)
    elif bot_left > bot_joined:
        bdt = delta_time(bot_left)
        bft = formatted_time(bdt)
        if player_livering:
            msg = msg + '\nBut §5bot §e{}§r have been killed for §6{t}§r'.format(player, t = bft)
        else:
            msg = msg + '\n§5Bot §e{}§r have been killed for §6{t}§r'.format(player, t = bft)
    else:
        raise ValueError('Error parsing bot data. ')

    display_message(info, msg)

@new_thread(PLUGIN_METADATA['id'])
def liver(info: Info, player: str):
    joined, left = player_seen(player)
    bot_joined, bot_left = player_seen(player + '@bot')
    player_livering = bot_livering = False
    if left < joined:
        dt = delta_time(joined)
        ft = formatted_time(dt)
        player_livering = True
        msg = "§dPlayer§e {}§r have been online for §a{}".format(player, ft)
    
    if bot_left < bot_joined and not player_livering:
        bdt = delta_time(bot_joined)
        bft = formatted_time(bdt)
        bot_livering = True
        msg = "§5Player§e {}§r have been spawned for §a{}§r".format(player, bft)
    if bot_livering and player_livering:
        raise ValueError('Error confirming if bot is online. ')
    if not bot_livering and not player_livering:
        msg = 'The player is online, ' + rclick('Click here', 'Querying offline time', '!!seen ' + player).set_color(RColor.gray) + 'to query the player\'s offline time.'
    display_message(info, msg)

@new_thread(PLUGIN_METADATA['id'])
def liver_top(info: Info, bot_arg: str):
    fixed = clear_online_player(info.get_server())
    seens = seens_from_file()
    result_raw = {}
    for pr in plist(seens, bot_arg):
        p = pr.split('@')[0]
        if len(pr.split('@')) >= 2:
            bot = 'bot'
            joined, left = player_seen(pr)
        else:
            bot = 'player'
            joined, left = player_seen(pr)
        if left < joined:
            liver = [joined, p, bot]
            if bot_arg == '-merge':
                old_joined = result_raw.get(p)
                if old_joined and old_joined[0] > joined:
                    liver = result_raw[p]
            result_raw[p] = liver

    result = []
    for item in result_raw.values():
        result.append(item)
    result.sort()
    mode = top_args[bot_arg]
    msg = 'Here are the players §acurrently online§r({}): '.format(mode)
    if fixed != 0:
        msg = msg + '\nCorrected §e' + str(fixed) + '§r player\'s data.'
    for r in result:
        joined, player, isbot = r
        dt = delta_time(joined)
        ft = formatted_time(dt)
        pattern2 = {'bot': 'spawned', 'player': 'online'}
        msg = msg + f'\n{pattern_isbot[isbot]} §e{player}§r have been {pattern2[isbot]} for §a{ft}§r'
    display_message(info, msg)

@new_thread(PLUGIN_METADATA['id'])
def seen_top(info: Info, bot_arg: str, full_arg: str):
    fixed = clear_online_player(info.get_server())
    seens = seens_from_file()
    result_raw = {}
    for pr in plist(seens, bot_arg):
        p = pr.split('@')[0]
        if len(pr.split('@')) >= 2:
            bot = 'bot'
            joined, left = player_seen(pr)
        else:
            bot = 'player'
            joined, left = player_seen(pr)
        if left > joined:
            seen = [left, p, bot]
            if bot_arg == '-merge':
                old_left = result_raw.get(p)
                if old_left and old_left[0] < left:
                    seen = result_raw[p]
            result_raw[p] = seen

    result = []
    for item in result_raw.values():
        result.append(item)
    result.sort()
    mode = top_args[bot_arg]
    if full_arg != '-full':
        top_num = min(len(result), 10)
        msg = 'Here are the 10 players §cofflined§r for the longest time({}):'.format(mode)
    else:
        top_num = len(result)
        msg = 'Here are all the players\' offline time data({}):'.format(mode)
    if fixed != 0:
        msg = msg + '\nCorrected §e' + str(fixed) + '§r player\'s data.'
    for i in range(top_num):
        r = result[i]
        left, player, isbot = r
        dt = delta_time(left)
        ft = formatted_time(dt)
        pattern2 = {'bot': 'killed', 'player': 'offline'}
        msg = msg + "\n{i}. {b}§e{p}§r have been {pt} for §6{t}§r.".format(i = i + 1, b = pattern_isbot[isbot], pt = pattern2[isbot], p = player, t = ft)
    display_message(info, msg)

def plist(seens: dict, bot_arg: str):
    players_raw = seens.keys()
    players = []
    for p in players_raw:
        player = p.split('@')[0]
        players.append(player)
    bots = []
    for p in players:
        if players.count(p) == 2:
            if not p in bots:
                bots.append(p + '@bot')
    bot_args = {'-player': players, '-bot': bots, '-all': players_raw, '-merge': players_raw}
    return bot_args[bot_arg]



def now_time():
    t = time.time()
    return int(t)


def delta_time(last_seen: int):
    now = now_time()
    return now - abs(last_seen)


def formatted_time(t: int or str):
    t = int(t)
    values = []
    units = ["sec(s)", "min(s)", "hr(s)", "day(s)"]
    scales = [60, 60, 24]
    for scale in scales:
        value = t % scale
        values.append(value)

        t //= scale
        if t == 0:
            break
    if t != 0:
        # Time large enough
        values.append(t)

    s = ""
    for i in range(len(values)):
        value = values[i]
        unit = units[i]
        s = "{v} {u} ".format(v = value, u = unit) + s
    return s


def player_seen(player: str):
    seens = seens_from_file()
    seen = seens.get(player, 0)
    if seen:
        joined = seen.get('joined', 0)
        left = seen.get('left', 0)
        return joined, left
    else:
        return 0, 0

def is_bot(name: str):
	name = name.upper()
	blacklist = 'A_Pi#nw#sw#SE#ne#nf#SandWall#storage#Steve#Alex#DuperMaster#Nya_Vanilla#Witch#Klio_5#######'.upper()
	black_keys = [r'farm', r'bot_', r'cam', r'_b_', r'bot-', r'bot\d', r'^bot']
	if blacklist.find(name) >= 0 or len(name) < 4 or len(name) > 16:
		return True
	for black_key in black_keys:
		if re.search(black_key.upper(), name):
			return True
	return False



def set_seen(playername: str, time: int, type: str):
    seens = seens_from_file()
    player = seens.get(playername)
    if player is None:
        seens[playername] = {
            'joined': 0,
            'left': 0
        }
    seens[playername][type] = time

    with open(seen_file, "w") as f:
        json.dump(seens, f)

def get_online_player_list(server: ServerInterface):
    return_msg = server.rcon_query('list')
    players_raw = return_msg.split(' players online:')[1].strip()
    players = players_raw.split(', ')
    return players
    
def get_bot_info(online_list: list):
    online_list_real = []
    for item in online_list:
        player = item
        if item in bot_list:
            player = player + '@bot'
        online_list_real.append(player)
    return online_list_real

def clear_online_player(server: ServerInterface, clear_only = False):
    seens = seens_from_file()
    if not clear_only:
        online_list = get_online_player_list(server)
        online_list_real = get_bot_info(online_list)
    else:
        online_list_real = []
    num = 0
    for key, value in seens.items():
        if not key in online_list_real or clear_only:
            if value['joined'] > value['left']:
                t = now_time()
                set_seen(key, t, 'left')
                num = num + 1
                output_log(key + ' left the game. [Corrected]')
        if key in online_list_real and value['joined'] < value['left'] and not clear_only:
            t = now_time()
            set_seen(key, t, 'joined')
            num = num + 1
            output_log(key + ' joined the game. [Corrected]')
    return num


def on_server_stop(server: ServerInterface, server_return_code: int):
    clear_online_player(server, True)

def on_server_start(server: ServerInterface):    
    clear_online_player(server, True)

def on_info(server: ServerInterface, info: Info):
    def cmd_error(source: CommandSource or Info):
	    display_message(source, rclick(
		    '§cCommand Error! §rPlease enter §7' + seen_prefix + '§r to get plugin help message.'.format(seen_prefix),
		    'Click to show help message.',
		    seen_prefix
	    ))

    if info.is_user:
        arg_list = info.content.split(' ')
        if arg_list[0] in [seen_prefix, seen_top_prefix, liver_prefix]:
            info.cancel_send_to_server()
            bot_arg = None
            full_arg = None
            for item in arg_list:
                if item in ['-all', '-bot', '-merge', '-player']:
                    if bot_arg is not None:
                        cmd_error(info)
                        return
                    else:
                        bot_arg = item
                        arg_list.remove(item)
            for item in arg_list:
                if item in ['-full']:
                    if full_arg is not None:
                        cmd_error(info)
                        return
                    else:
                        full_arg = item
                        arg_list.remove(item)

            f = full_arg is None
            b = bot_arg is None
            if b:
                bot_arg = '-player'
            if f:
                full_arg = ''

            @new_thread(PLUGIN_METADATA['id'])
            def parse_cmd():
                cmdlen = len(arg_list)
                if cmdlen == 1 and arg_list[0] == seen_prefix and f and b:
                    display_help(info)
                elif cmdlen == 1 and arg_list[0] == seen_top_prefix:
                    seen_top(info, bot_arg, full_arg)
                elif cmdlen == 1 and arg_list[0] == liver_prefix and f:
                    liver_top(info, bot_arg)    
                elif cmdlen == 2 and arg_list[0] == seen_prefix and arg_list[1] == 'reload':
                    display_message(info, 'Plugin Reloaded! ')
                    server.reload_plugin(PLUGIN_METADATA['id'])
                elif cmdlen == 2 and arg_list[0] == seen_prefix and f and b:
                    try:
                        seen(info, arg_list[1])
                    except ValueError as e:
                        display_message(info, f'§cError excuting command: §4{e}§r Please inform admin to handle it.')
                        output_log('Error Occured: {}'.format(e))
                        raise ValueError(e)
                elif cmdlen == 2 and arg_list[0] == liver_prefix and f and b:
                    try:
                        liver(info, arg_list[1])
                    except ValueError as e:
                        display_message(info, f'§cError excuting command: §4{e}§r Please inform admin to handle it.')
                        output_log('Error Occured: {}'.format(e))
                        raise ValueError(e)

                else:
                    for arg in arg_list:
                        display_message(info, arg, '')
                    cmd_error(info)
        
            parse_cmd()

    if info.is_from_server:
        join_info = parse_join_info(info)
        left_info = parse_left_info(info)
        if join_info[0] or left_info[0]:
            global bot_list
            t = now_time()
            if join_info[0]:
                set_seen(join_info[1], t, 'joined')
                if join_info[1].endswith('@bot'):
                    playername = join_info[1].split('@')[0]
                    bot_list.append(playername)
                output_log(join_info[1] + ' joined the game.')
            elif left_info[0]:
                set_seen(left_info[1], t, 'left')
                if left_info[1].endswith('@bot'):
                    playername = left_info[1].split('@')[0]
                    bot_list.remove(playername)
                output_log(left_info[1] + ' left the game.')
            else:
                output_log('Error parsing player join info.')
                raise ValueError('Error parsing player join info.')
            
                
def on_load(server: ServerInterface, prev_module):
    server.register_help_message(seen_prefix, 'See who the lazist is and who the most hard-working in this server.')
    if prev_module is not None:
        global bot_list
        bot_list = []
        bot_list = prev_module.bot_list
        if prev_module.seen_file != seen_file and os.path.exists(prev_module.seen_file):
            shutil.move(prev_module.seen_file, seen_file)


