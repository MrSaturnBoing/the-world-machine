
from interactions import *
from interactions.api.events import MemberAdd, Ready, MessageCreate
import interactions.ext.prefixed_commands as prefixed_commands

from utilities.dev_commands import execute_dev_command
from database import ServerData, create_connection
from config_loader import *
import load_commands
import os
import random
import utilities.profile.profile_viewer as view
from modules.textbox import TextboxModule

print('\nStarting The World Machine... 1/4')
intents = Intents.DEFAULT | Intents.MESSAGE_CONTENT | Intents.MESSAGES | Intents.GUILD_MEMBERS | Intents.GUILDS

client = Client(
    intents=intents,
    disable_dm_commands=True,
    send_command_tracebacks=False
)

prefixed_commands.setup(client, default_prefix='*')

print("\nLoading Commands... - - - - - 2/3")

load_commands.load_commands(client)

async def pick_avatar():
    get_avatars = os.listdir('bot/images/profile_pictures')
    random_avatar = random.choice(get_avatars)

    avatar = File('bot/images/profile_pictures/' + random_avatar)

    await client.user.edit(avatar=avatar)
    return random_avatar


@listen(Ready)
async def on_ready():
    
    ### space for testing
    # return
    ### space for testing
    
    print("\nFinalizing... - - - - - - - - 3/3")
    
    create_connection()
    
    print('Database Connected')

    await client.change_presence(status=Status.ONLINE, activity=Activity(type=ActivityType.CUSTOM, name=load_config('status')))
    await view.load_badges()

    if load_config('do-avatar-rolling', ignore_None=True): 
        print("Rolling avatar", end=" ... ")
        if client.user.id == int(load_config('bot-id')):
            used = await pick_avatar()
            print(f"used {used}")
        else:
            try:
                await client.user.edit(avatar=File('bot/images/unstable.png'))
                print("used unstable")
            except:
                print("failure")
                pass
        
    print("\n- - - - - - - - - - - - - - - - -")
    print("\n   The World Machine is ready!\n\n")

# Whenever a user joins a guild...
@listen(MemberAdd)
async def on_guild_join(event: MemberAdd):
    if client.user.id != int(load_config('bot-id')):
        return
    
    if event.member.bot:
        return
    
    # Check to see if we should generate a welcome message
    server_data: ServerData = await ServerData(event.guild_id).fetch()
    
    if not server_data.welcome_message:
        return

    # Generate welcome textbox.
    await TextboxModule.generate_welcome_message(event.guild, event.member, server_data.welcome_message)
    
@listen(MessageCreate)
async def on_message_create(event: MessageCreate):
    await execute_dev_command(event.message)

client.start(load_config('token'))