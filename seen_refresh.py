import json
import os
import shutil
import time
import re
from mcdreforged.api.all import *

PLUGIN_NAME_SHORT = 'Seen Refreshed (ES)'
PLUGIN_METADATA = {
    'id': 'mcdr_seen_refreshed',
    'version': '0.9.9',
    'name': 'Seen and Liver Refreshed (Experimental Sample)',
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

seen_prefix = '!!seen'
seen_top_prefix = seen_prefix + '-top'
liver_prefix = '!!liver'
liver_top_prefix = liver_prefix + '-top'

helpmsg = f'''------ {PLUGIN_NAME_SHORT} v{PLUGIN_METADATA['version']} ------
一个查看服务器玩家在线(爆肝)和下线(摸鱼)的插件
§d【指令说明】§r
§7{2}§r或§7{4}§r 显示帮助信息
§7{2}§r §e<玩家>§r 查看玩家摸鱼时长
§7{3}§r 查看摸鱼榜
§7{4}§r §e<玩家>§r 查看玩家爆肝时长
§7{5}§r 查看所有在线玩家爆肝时长
§d【额外参数说明】§r
§7{4}§r和§7{5}§r后可添加额外参数
在不添加参数的情况下默认统计非假人玩家数据
（玩家同名假人和玩家shadow都算作假人）
参数如下所示：
§6-a§r 显示全部玩家统计数据(玩家同名假人会独立显示)
§6-m§r 显示全部玩家统计数据(玩家和同名假人会合并显示)
§6-b§r 仅显示假人的统计数据
--------------------------------'''.strip().format(PLUGIN_NAME_SHORT, PLUGIN_METADATA['version'], seen_prefix, seen_top_prefix, liver_prefix, liver_top_prefix)

# Copied from QBM
def print_message(source: CommandSource, msg: str, tell = True, prefix='[Seen] '):
	msg = prefix + msg
	if source.is_player and not tell:
		source.get_server().say(msg)
	else:
		source.reply(msg)

def command_run(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.run_command, command)

def command_suggest(message: str, text: str, command: str):
	return RText(message).set_hover_text(text).set_click_event(RAction.suggest_command, command)

def print_unknown_argument_message(source: CommandSource, error: UnknownArgument):
	print_message(source, command_run(
		'参数错误！请输入§7' + seen_prefix + '§r以获取插件信息'.format(seen_prefix),
		'点击查看帮助',
		seen_prefix
	))

# MCDR compatibility

'''
def on_player_joined(server, player, info):
    t = now_time()
    set_seen(player, t, 'joined')

def on_player_left(server, player):
    t = now_time()
    set_seen(player, t, 'left')
'''

def joined_info(server: ServerInterface, info: Info):
    if info.is_from_server:
        joined_player = re.match(r'(\w+)\[([0-9\.:]+|local)\] logged in with entity id', info.content)
        if joined_player:
            if joined_player.group(2) == 'local':
                return [True, 'bot', joined_player.group(1)]
            else:
                return [True, 'player', joined_player.group(1)]
        return [False]


def seen(server, info, playername):
    joined, left = player_seen(playername)
    if (left and joined) == 0:
        msg = "没有 §e{p}§r 的数据".format(p=playername)
    elif left < joined:
        dt = delta_time(joined)
        ft = formatted_time(dt)
        msg = "§e{p}§r 没有在摸鱼, 已经肝了 §a{t}".format(p=playername, t=ft)
    elif left >= joined:
        dt = delta_time(left)
        ft = formatted_time(dt)
        msg = "§e{p}§r 已经摸了 §6{t}".format(p=playername, t=ft)
    else:
        raise ValueError()
    server.tell(info.player, msg)


def liver(server, source):
    pass


def liver_top(server, info):
    seens = seens_from_file()
    players = seens.keys()

    result = []
    for player in players:
        joined, left = player_seen(player)
        if left < joined:
            result.append([joined, player])
    result.sort()
    for r in result:
        joined, player = r
        dt = delta_time(joined)
        ft = formatted_time(dt)
        msg = "§e{p}§r 已经肝了 §a{t}".format(p=player, t=ft)
        server.tell(info.player, msg)


def seen_top(server, info):
    seens = seens_from_file()
    players = seens.keys()

    result = []
    for player in players:
        joined, left = player_seen(player)
        if left > joined:
            result.append([left, player])
    result.sort()
    top_num = min(len(result), 10)
    for i in range(top_num):
        r = result[i]
        left, player = r
        dt = delta_time(left)
        ft = formatted_time(dt)
        msg = "{i}. §e{p}§r 已经摸了 §6{t}".format(i=i+1, p=player, t=ft)
        server.tell(info.player, msg)


def now_time():
    t = time.time()
    return int(t)


def delta_time(last_seen):
    now = now_time()
    return now - abs(last_seen)


def formatted_time(t):
    t = int(t)
    values = []
    units = ["秒", "分", "小时", "天"]
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
        s = "{v} {u} ".format(v=value, u=unit) + s
    return s


def player_seen(playername):
    seens = seens_from_file()
    seen = seens.get(playername, 0)
    if seen:
        joined = seen.get('joined', 0)
        left = seen.get('left', 0)
        return joined, left
    else:
        return 0, 0


def seen_help(server, player):
    for line in helpmsg.splitlines():
        server.tell(player, line)


def set_seen(playername, time, type):
    seens = seens_from_file()
    player = seens.get(playername)
    if not player:
        seens[playername] = {
            'joined': 0,
            'left': 0,
        }
    seens[playername][type] = time

    save_seens(seens)


def init_file():
    with open("config/seen.json", "w") as f:
        d = {}
        s = json.dumps(d)
        f.write(s)


def seens_from_file():
    if os.path.isfile("seen.json"):
        shutil.move("seen.json", "config/seen.json")
    if not os.path.exists("config/seen.json"):
        init_file()
    with open("config/seen.json", "r") as f:
        seens = json.load(f)
    return seens


def save_seens(seens):
    with open("config/seen.json", "w") as f:
        json_seens = json.dumps(seens)
        f.write(json_seens)

def register_command(server: ServerInterface):
    server.register_command(
        Literal(seen_prefix).
        runs(lambda src: seen_help(server, src.player)).
        on_error(UnknownArgument, lambda src :print_unknown_argument_message(src), handled=True).
        then(QuotableText('player').
            runs(lambda src, ctx: seen(server, src, ctx['player'])))
        )
    server.register_command(
        Literal(seen_top_prefix).
        runs(lambda src: seen_top(server, src)).
        on_error(UnknownArgument, lambda src :print_unknown_argument_message(src), handled=True)
        )
    server.register_command(
        Literal(liver_prefix).
        runs(lambda src: seen_help(server, src.player)).
        on_error(UnknownArgument, lambda src :print_unknown_argument_message(src), handled=True).
        then(QuotableText('player').
            runs(lambda src, ctx: liver(server, src, ctx['player'])))
        )
    server.register_command(
        Literal(liver_top_prefix).
        runs(lambda src: liver_top(server, src)).
        on_error(UnknownArgument, lambda src :print_unknown_argument_message(src), handled=True)
        )
    
def on_load(server: ServerInterface, prev_module):
    server.register_help_message('!!seen', '查看摸鱼榜/爆肝榜帮助')
    server.register_help_message('!!liver', '查看摸鱼榜/爆肝榜帮助')
    server.register_event_listener('mcdr.general_info', lambda info: joined_info(server, info))
    register_command(server)


