# Seen & Liver Refreshed

[英语(English)](https://github.com/ra1ny-yuki/mcdr-seen-refreshed)|**简体中文**

Seen & Liver Refreshed (缩写为SeenR) 是一个用于显示爆肝摸鱼榜的 [MCDReforged](https://github.com/Fallen-Breath/MCDReforged)  插件.  该插件重置自 Pandaria和 Fallen_Breath开发的[MCD Seen](https://github.com/TISUnion/Seen/) .

## 和MCD Seen的区别

[MCDReforged](https://github.com/Fallen-Breath/MCDReforged) >= 1.0.0

## Difference to MCD Seen

支持了识别[Carpet](https://github.com/gnembon/fabric-carpet)假人, 并且添加了纠错系统以避免严重的数据错误。

玩家加入后，插件会检查其是否为地毯假人。该识别基于服务端的标准输出信息，将会准确的将所有使用`/player *** spawn` 或 `/player *** shadow` 产生的假人标记为假人。 

## 插件配置

若你曾使用过mcd_seen, 该插件将自动读取并转换它的配置文件，并且识别并标记文件内记录的bot, 该识别是通过检查像是Alex这种特定的玩家名称以及含有'bot_'前缀的玩家。该识别并不像玩家上下线时的检测一般准确但起码它能用, 所以你用本插件查询了第一次信息之后应该检查一下文件里是否有玩家被标记错了。

此外，你还需要确保服务端和MCDR之间有有效的rcon链接。本插件需要rcon来检查玩家数据。若你不知道如何配置rcon，请[点此查看](https://mcdreforged.readthedocs.io/zh_CN/latest/configure.html?highlight=rcon#rcon)。

配置文件和日志文件路径可在插件文件中修改。数据文件和插件的指令前缀等其他一些配置信息需要在配置文件中配置。日志文件和配置文件将会在插件首次加载时自动生成。

## 指令

1. `!!seen` 显示帮助信息

2. `!!seen <player>` 查询玩家`<player>`的摸鱼时间

3. `!!liver <player>` 查询玩家`<player>`的爆肝时间

4. `!!seen-top` 查询摸鱼时间榜(下线时间榜)

5. `!!liver` 查询爆肝时间榜(上线时间榜)

   

## 额外参数

若未添加额外参数, `!!seen-top` 和 `!!liver` 将会默认显示不含假人的玩家数据。

添加`-all`显示所有玩家数据, `-merge`显示所有玩家数据（玩家和假人数据将会被混起来，在摸鱼榜上仅会显示假人和真人中咕的更久的一个, `-bot`仅显示假人数据。

为防止信息刷屏, `!!seen-top`将仅显示榜上十名摸鱼最久的玩家。添加`-full`以显示完整榜单。
