from asyncio.windows_events import NULL
import discord
from discord import channel
from discord import message
from discord import emoji
from discord.ext import commands, tasks
from discord.ext.commands.core import has_permissions
from discord.ext.commands.errors import MissingPermissions
from discord.message import Message
from discord.utils import get
from random import randint
from datetime import datetime, timedelta

quoteSource = ["*The Orange* by Wendy Cope",
"\'The Adventure Zone: Balance\' ep 23",
"\'The Adventure Zone: Balance\' ep 47",
"\'The Adventure Zone: Balance\' ep 64",
"Hayao Miyazaki",
"*Good Bones* by Maggie Smith",
"@cupcakelogic on tumblr",
"@mossypositivity on tumblr",
"a friend of mine",
"\'Welcome to Night Vale\' ep 45.5",
"Vincent van Gogh",
"\'Saturday Sun\' by Vance Joy",
"*A Hat Full of Sky* by Terry Pratchett",
"*Thief of Time* by Terry Pratchett",
"Adam J. Kurtz",
"*End Poem* by Julian Gough",
"*The Thing Is* by Ellen Bass",
"*Wild Geese* by Mary Oliver",
"*Why I Wake Up Early* by Mary Oliver"
]

quoteText = ["\"I love you. I'm glad I exist.\"",
"\"I have a beating heart! I'm multidimensional! I'm a fully realized creation!\"",
"\"You're going to be amazing.\"",
"\"Our capacity for love increases with each person we cross paths with throughout our lives and with each moment we spend with those people.\"",
"\"Yet, even amidst the hatred and carnage, life is still worth living. It is possible for wonderful encounters and beautiful things to exist.\"",
"\"This place could be beautiful, right? You could make this place beautiful.\"",
"\"No need to be best. Only good and kind.\"",
"\"I take up space and that is okay, because so do the trees and the mushrooms and the moon. And that is okay.\"",
"\"Don't worry about being great, you already are great.\"",
"\"You are beautiful when you do beautiful things.\"",
"\"If I am worth anything later, I am worth something now. For wheat is wheat, even if people think it is a grass in the beginning.\"",
"\"No ray of sunlight's ever lost.\"",
"\"Why do you go away? So that you can come back. So that you can see the place you came from with new eyes and extra colors. And the people there see you differently, too. Coming back to where you started is not the same as never leaving.\""
"\"When in doubt, choose to live.\"",
"\"The world is big and I am not but I am still enough.\"",
"\"And the universe said I love you because you are love.\"",
"\"[The thing is] to love life, to love it even when you have no stomach for it\"",
"\"You do not have to be good... You only have to let the soft animal of your body love what it loves.\"",
"\"Hello, sun in my face. Hello you who made the morning and spread it over the fields... Watch, now, how I start the day in happiness, in kindness.\"",
]

client = discord.Client()
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="$", intents=intents)
target_channel_id = 869680381752922164
bot.lotl_role_name =""
bot.role_message_id = 0
bot.role_emoji = ""

timeInMinutes = 1
bot.getRandomTime = False
timeRange = [0, 0]

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

# call and response
@bot.listen()
async def on_message(message):
    content = message.content.lower()
    if content.startswith('hello lotl'):
        await message.channel.send('hi!')

    if content.startswith('goodbye lotl'):
        await message.channel.send('goodbye!')

#create reminders
@tasks.loop(minutes=timeInMinutes)
async def reminder():
    "Shows self-care reminders"
    message_channel = bot.get_channel(target_channel_id)
    role = get(message_channel.guild.roles, name=bot.lotl_role_name)
    
    if bot.lotl_role_name != "":
        role = get(message_channel.guild.roles, name=bot.lotl_role_name)
        await message_channel.send('{} remember to drink water!'.format(role.mention))
    else:
        await message_channel.send('reminder role not set up! use createRole \{channelID\} \{emote\} \{role name\} to set up')
        reminder.stop()

    if bot.getRandomTime:
        reminder.change_interval(minutes=randint(int(timeRange[0]), int(timeRange[1])))

@reminder.before_loop
async def before():
    await bot.wait_until_ready()

#set time
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def setTime(ctx, *, arg):
    "Sets time between reminders to specified number of minutes"
    bot.getRandomTime = False
    reminder.change_interval(minutes=int(arg))
    outputText = 'reminders will now appear every ' + str(arg) + ' minutes'
    await ctx.send(outputText)

@setTime.error
async def setTime_error(error, ctx):
    if isinstance(error, MissingPermissions):
        await ctx.send('you do not have permission to perform this action')

@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def setTimeRange(ctx, *, arg):
    "Sets time between reminders to random number of minutes"
    bot.getRandomTime = True
    timeRange = str(arg).split()
    newTime = randint(int(timeRange[0]), int(timeRange[1]))
    reminder.change_interval(minutes=newTime)
    outputText = 'reminders will now appear between ' + str(timeRange[0]) + ' and ' + str(timeRange[1]) + ' minutes'
    await ctx.send(outputText)

# enable/disable reminders
@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def enableReminders(ctx):
    "Disables self-care reminders"
    if reminder.is_running() == True:
        nextReminder = reminder.next_iteration + timedelta(hours=-4)
        await ctx.send('reminders already enabled. next one appearing at ' + nextReminder.strftime("%H:%M:%S"))
    if reminder.is_running() == False:
        reminder.start()
        await ctx.send('reminders enabled')

@enableReminders.error
async def enableReminders_error(error, ctx):
    if isinstance(error, MissingPermissions):
        await ctx.send('you do not have permission to perform this action')


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def disableReminders(ctx):
    "Disables self-care reminders"
    if reminder.is_running() == True:
        reminder.stop()
        await ctx.send('reminders disabled')

@disableReminders.error
async def disableReminders_error(error, ctx):
    if isinstance(error, MissingPermissions):
        await ctx.send('you do not have permission to perform this action')

#send quote
@bot.command()
async def quote(ctx):
    "Shows a random quote"
    index = randint(0, len(quoteSource) - 1)
    quote_text = '> {}\n-{}'.format(quoteText[index], quoteSource[index])
    await ctx.send(quote_text)

@bot.command
async def help(ctx):
    await ctx.send(str(bot.all_commands))

@bot.command()
@commands.has_permissions(administrator=True)
async def createRole(ctx, *, arg):
    "Creates role for reminders to ping"
    channelID_emoji_role = str(arg).split()
    channel = bot.get_channel(int(channelID_emoji_role[0]))
    if channelID_emoji_role[2] != "":
        bot.lotl_role_name = channelID_emoji_role[2]
    role = await ctx.guild.create_role(name=bot.lotl_role_name)
    message = await channel.send('> {} \t {}'.format(channelID_emoji_role[1], role.mention))
    bot.role_message_id = message.id
    bot.role_emoji = channelID_emoji_role[1]
    await message.add_reaction('{}'.format(bot.role_emoji))

@createRole.error
async def createRole_error(error, ctx):
    if isinstance(error, MissingPermissions):
        await ctx.send('you do not have permission to perform this action')

@bot.event
async def on_reaction_add(reaction, user):
    "Gives reminder role on reaction"
    if reaction.message.id == bot.role_message_id:
        if reaction.emoji == bot.role_emoji:
            role = get(reaction.message.guild.roles, name=bot.lotl_role_name)
            if role not in user.roles:
                await user.add_roles(role)

@bot.event
async def on_reaction_remove(reaction, user):
    "Removes reminder role on reaction"
    if reaction.message.id == bot.role_message_id:
        if reaction.emoji == bot.role_emoji:
            role = get(reaction.message.guild.roles, name=bot.lotl_role_name)
            if role in user.roles:
                await user.remove_roles(role)

@bot.command()
@commands.has_permissions(administrator=True)
async def addReaction(ctx, *, arg):
    "Add reaction to message"
    messageID_emoji = str(arg).split()
    messageID = int(messageID_emoji[0])
    message = await discord.TextChannel.fetch_message(ctx, id=messageID)

    await message.add_reaction('{}'.format(messageID_emoji[1]))

@addReaction.error
async def addReaction_error(error, ctx):
    if isinstance(error, MissingPermissions):
        await ctx.send('you do not have permission to perform this action')


bot.run('ODY5Njc3NjEyMjc5MTY1MDg5.YQBsZA.HGVc8SNrG3oJ-BnNy6IBEFO_X7k')
