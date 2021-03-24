# Seen & Liver Refreshed

Seen & Liver Refreshed (short as SeenR) is a [MCDReforged](https://github.com/Fallen-Breath/MCDReforged) plugin to show laziness ranking. This plugin is the refresh version for [MCD Seen](https://github.com/TISUnion/Seen/) from Pandaria and Fallen_Breath.

  **English** | [简体中文(Simplified Chinese)](https://github.com/ra1ny-yuki/mcdr_seen_refreshed/blob/main/README_zh.md)

## Requirement

[MCDReforged](https://github.com/Fallen-Breath/MCDReforged) >= 1.0.0

## Difference to MCD Seen

Supported identifying [Carpet](https://github.com/gnembon/fabric-carpet) bot, and added data correction system to prevent severe data error.

After player joined and left, this plugin will check if this player is bot. This identification is based on server output information, which will mark all the players spawned with `/player *** spawn` or `/player *** shadow` command as bot accurately. 

## Configuration

If you've ever used mcd seen before, this plugin can auto read the data file from it and identify the bot in the file. This identification will only mark some specific player names, such as 'Alex', and the player names with 'bot_' prefix as carpet bot. Less accurate than the join&left bot check but it works. You may need to have the file checked to prevent the human player to be marked as bot wrongly.

And you need to make sure there is available rcon connection between MCDRefored and server. The plugin need rcon to correct player data. If you don't know how to configurate rcon, please [check here](https://mcdreforged.readthedocs.io/en/latest/configure.html?highlight=rcon#rcon).

Config file path and log file path can be configured in plugin file. Data file path, command prefix and several other can be configured in config file, config and log file will be generated automatically on the plugin first load.

## Command

1. `!!seen` Show help message.

2. `!!seen <player>` Querying offline time of `<player>`

3. `!!liver <player>` Querying online time of `<player>`

4. `!!seen-top` Show the laziness rank (Offline time rank).

5. `!!liver` Show the hard-working rank (Online time rank).

   

## Additional Arguments

`!!seen-top` and `!!liver` will show the player data omit bot if no additional argument is given. 

Add `-all` to show all the player data, add `-merge` to show all the player data (Human player and bot data will be merged. For seen rank will only show the more lazy one.), add `-bot` to show the data of bot only.

To prevent too much message to sweep your chat panel, `!!seen-top` will only show the 10 laziest ones on the rank. You can add `-full` to get full rank.