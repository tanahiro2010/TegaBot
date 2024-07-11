# Discord
import discord
import discord.app_commands as commands
# About YouTube Api
import requests
from googleapiclient.discovery import build
# Other
import json
import time

# Config
Config_path = './config/config.json'
Role_name = "reception-alert"
Channel_name = "Tega-alert"


with open(file=Config_path, mode='r', encoding='utf-8') as f:
    config = json.load(f)
    f.close()

# Functions

def open_config():
    try:
        with open(Config_path, mode='r', encoding='utf-8') as f:
            config_temp = json.load(f)
            print(config_temp)
            return config_temp
    except FileNotFoundError as e:
        print(e)
        return False
    except json.decoder.JSONDecodeError as e:
        print(e)
        return False

def save_discord_config(data: json):
    config_now = open_config()
    if not config_now is False:
        config_now['guilds_config'] = data
        with open(Config_path, mode='w', encoding='utf-8') as f:
            json.dump(config_now, f, indent=2)
    else:
        exit()
    return

async def create_role(guild: discord.Guild, name: str, color: discord.Color = discord.Color.green()):
    role = await guild.create_role(name=name, color=color)
    return role

async def create_channel(guild: discord.Guild, name: str):
    channel = await guild.create_text_channel(
        name=name
    )
    return channel

# Main

# API's config
discord_config = config['Discord']
token = discord_config['token']

youtube_config = config['YouTube']
Api_key = youtube_config['API_Key']

guilds_config = config['guilds_config']

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = commands.CommandTree(client=bot)

# YouTube Objects
youtube = build(
    serviceName='youtube',
    version='v3',
    developerKey=Api_key
)


# Discord event
@bot.event
async def on_ready():
    print('Logged in as name:{}'.format(bot.user.name))

    text = ""

    for guild in bot.guilds:
        name = guild.name
        id = guild.id

        if not str(id) in guilds_config.keys():
            print('New server!!\nName: {}\nId: {}'.format(name, id))
            try:
                role = await create_role(guild, Role_name)
                channel = await create_channel(guild, Channel_name)
            except Exception as e:
                print(e)
                exit()
            guilds_config[id] = {
                "role": role.id,
                "channel": channel.id
            }
            print('Role_id : {}'.format(role.id))
            print('Channel_id : {}'.format(channel.id))
            save_discord_config(guilds_config)

        text += 'Name: {}\nID: {}\n'.format(name, id)

    text = text[:-2]
    print('Join Servers ==========')
    print(text)
    print('=======================')

    return

@bot.event
async def on_message(message: discord.Message):
    content = message.content
    print(content)
    if message.author == bot.user:
        return
    if content == "!update":
        await tree.sync()
        embed = discord.Embed(
            title="Update",
            description="Commands synced.",
            colour=discord.Colour.green()
        )
        await message.channel.send(embed=embed)


@bot.event
async def on_guild_join(guild: discord.Guild):
    if not str(guild.id) in guilds_config:
        try:
            role: discord.Role = await create_role(
                guild=guild,
                name=Role_name
            )
            channel: discord.TextChannel = await create_channel(
                guild=guild,
                name=Channel_name
            )
        except Exception as e:
            print(e)
            embed = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await guild.channels[0].send(embed=embed)
            await guild.leave()
            return

        role_id = role.id
        channel_id = channel.id

        guilds_config[guild.id] = {
            "role": role_id,
            "channel": channel_id
        }
        save_discord_config(guilds_config)

        embed = discord.Embed(
            title="Joined Server",
            description="This bot is to send about youtube video.",
            color=discord.Color.green()
        )
        await guild.get_channel(channel_id).send(embed=embed)

    return


# Bot commands
@tree.command(
    name="reception-alert",
    description="If select True, set reception-alert role.If select False, unfasten reception-alert role."
)
@commands.describe(
    select="True or False"
)
async def reception_alert(ctx: discord.Interaction.response, select: bool):
    await ctx.response.defer()
    guild = ctx.guild
    guild_id = guild.id
    guild_config = guilds_config[str(guild_id)]
    role_id = guild_config['role']
    role = guild.get_role(role_id)
    member: discord.Member = ctx.user
    if select is True:
        try:
            await member.add_roles(role)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed)
            return

        embed = discord.Embed(
            title="Reception Alert",
            description="<@{}>さん！通知がオンになりました！！".format(member.id),
            color=discord.Color.green()
        )
        message = await ctx.followup.send(embed=embed)
        time.sleep(5)
        await message.delete()
        return
    else:
        try:
            await member.remove_roles(role)
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description=str(e),
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed)
            return
        embed = discord.Embed(
            title="Reception Alert",
            description="<@{}>さんのロールが外されました".format(member.id),
            color=discord.Color.green()
        )
        message = await ctx.followup.send(embed=embed)
        time.sleep(5)
        await message.delete()
        pass

@tree.command(
    name="set-time-of-schedule",
    description="Set up scheduled execution of tasks."
)
@commands.describe(
    minutes="How many minutes do you want the task to run?"
)
async def set_time_of_schedule(ctx: discord.Interaction.response, minutes: int):
    await ctx.response.defer()
    minute: int = 60*minutes
    config = open_config()
    config['time'] = minute
    with open(file=Config_path, mode='w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    embed = discord.Embed(
        title="Set Scheduled Task",
        description="End set scheduled execution of tasks.",
        color=discord.Color.green()
    )
    message = await ctx.followup.send(embed=embed)
    time.sleep(5)
    await message.delete()
    return

@tree.command(
    name="add_youtube_channel",
    description="Test"
)
@commands.describe(
    channel_id="YouTube Channel ID. Don't include '@'"
)
async def add_youtube_channel(ctx: discord.Interaction.response, channel_id: str):
    await ctx.response.defer()
    guild = ctx.guild
    guild_id = guild.id
    guild_config = guilds_config[str(guild_id)]
    print(guild_config)
    channels = guilds_config[str(guild_id)]['YouTube_channels']
    if not channel_id in channels:
        guilds_config[str(guild_id)]['YouTube_channels'].append(channel_id)
        save_discord_config(guilds_config)
        try:
            Channel_info = youtube.channels().list(
                id=channel_id,
                part='snippet,statistics',
                maxResults=10
            ).execute()
        except Exception as e:
            embed = discord.Embed(
                title="Error",
                description="### This channel is not found.\n{}".format(str(e)),
                color=discord.Color.red()
            )
            await ctx.followup.send(embed=embed)
            return
        print(Channel_info)
        embed = discord.Embed(
            title="Add YouTube Channel",
            description="### Add channel.\nName: {}\nCustomId: {}".format(Channel_info['items'][0]['snippet']['title'], Channel_info['items'][0]['snippet']['customUrl']),
            color=discord.Color.green()
        )
        await ctx.followup.send(embed=embed)
        return
    else:
        embed = discord.Embed(
            title="Error",
            description="This channel is Already registered.",
            color=discord.Color.red()
        )
        await ctx.followup.send(embed=embed)
        return


@tree.command(
    name="get_channel_id",
    description="Get the channel ID for use in the add_youtube_channel command."
)
@commands.describe(
    channel_name="Please input channel id. (For example, If channel url is https://youtube.com/@tanahiro2010, channel name is tanahiro2010.)"
)
async def get_channel_id(ctx: discord.Interaction.response, channel_name: str):
    await ctx.response.defer()
    response = youtube.search().list(
        q=channel_name,
        type='channel',
        part='snippet',
        maxResults=10
    ).execute()
    print(response)
    keys = response.keys()

    if not "items" in keys:
        embed = discord.Embed(
            title="Not Found",
            description="This channel is not registered.",
            color=discord.Color.red()
        )
        await ctx.followup.send(embed=embed)
        return
    else:
        text = ""
        for item in response["items"]:
            channel_id = item['id']['channelId']
            Channel_info = youtube.channels().list(
                id=channel_id,
                part='snippet,statistics',
                maxResults=10
            ).execute()
            text += "### Channel_name: {}\nChannel_ID: {}\n".format(Channel_info['items'][0]['snippet']['title'], channel_id)
        embed = discord.Embed(
            title="YouTube Channel Info",
            description=text,
            color=discord.Color.green()
        )
        await ctx.followup.send(embed=embed)

bot.run(token=token)