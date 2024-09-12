import discord
from discord.ext import commands
import asyncio
import time
import atexit  # For graceful shutdown
import dotenv

dotenv.load_dotenv(".env")
# Load token and other settings from environment variables
TOKEN = dotenv.get_key(".env", "BOT_TOKEN")
CHANNEL_ID = int(dotenv.get_key(".env", "CHANNEL_ID"))
MAX_TALK_DURATION = int(dotenv.get_key(".env", "MAX_TALK_DURATION"))

# Set up the bot with necessary intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store user talk time and monitored/extended users
user_talk_time = {}
monitored_users = set()
extended_time_users = set()

# Store mute duration and last mute time for each user
user_mute_duration = {}  # Track mute durations for users
muted_users = set()  # Track currently muted users
mute_threshold = 60  # Time threshold to increment mute duration (seconds)
base_mute_duration = 30  # Base mute duration (5 minutes)


# Function: Connect to a Voice Channel
async def connect_to_channel(guild):
    """Connect the bot to the voice channel if it's not already connected"""
    voice_channel = discord.utils.get(guild.voice_channels, id=CHANNEL_ID)
    
    if not voice_channel:
        return None

    # Check if the bot is already connected to a voice channel
    voice_client = discord.utils.get(bot.voice_clients, guild=guild)
    
    if voice_client and voice_client.is_connected():
        # If already connected to the correct voice channel, return the current voice client
        if voice_client.channel == voice_channel:
            return voice_client
        else:
            # Move to the correct voice channel if connected elsewhere
            await voice_client.move_to(voice_channel)
            return voice_client
    else:
        # Connect to the voice channel if not already connected
        try:
            voice_client = await voice_channel.connect(timeout=30.0)
            return voice_client
        except discord.errors.ClientException as e:
            print(f"Error connecting to voice channel: {e}")
            return None


# Function: Monitor User's Speech Time
async def monitor_user(member, voice_client):
    """Monitor the user's speech time in a voice channel"""
    start_time = time.time()
    user_talk_time[member.id] = start_time
    allowed_time = MAX_TALK_DURATION

    while member.voice and member.voice.channel:
        elapsed_time = time.time() - start_time

        # Extend time if the user said "C'est important"
        if member.id in extended_time_users:
            allowed_time = MAX_TALK_DURATION * 2

        # Mute the user if they exceed the allowed time
        if elapsed_time > allowed_time:
            #If member is already muted do nothing
            if member not in muted_users:
                await member.edit(mute=True)
                print(f"Muted {member.name} for exceeding talk time")

                # Add to the muted users set for tracking
                muted_users.add(member)
            # Handle auto unmute and increment mute duration
            await handle_mute(member)
            break

        await asyncio.sleep(1)

    # Disconnect the bot when done
    await voice_client.disconnect()


# Function: Handle mute duration and automatic unmute
async def handle_mute(member):
    """Handle auto unmute and increment mute duration"""
    current_time = time.time()
    last_mute_time = user_mute_duration.get(member.id, {}).get('last_mute_time', 0)
    mute_duration = user_mute_duration.get(member.id, {}).get('duration', base_mute_duration)

    # Increment mute duration if muted too soon
    if current_time - last_mute_time < mute_threshold:
        mute_duration *= 2  # Double the mute duration
        print(f"Incrementing mute duration for {member.name} to {mute_duration / 60} minutes")

    # Schedule the unmute
    await asyncio.sleep(mute_duration)
    await member.edit(mute=False)
    print(f"{member.name} has been unmuted after {mute_duration / 60} minutes.")

    # Update mute data
    user_mute_duration[member.id] = {
        'duration': mute_duration,
        'last_mute_time': time.time()
    }

    # Remove user from muted users
    muted_users.discard(member)


# Function: Unmute all users (called during shutdown)
async def unmute_all():
    print("Unmute All")
    """Unmute all currently muted users"""
    for member in muted_users.copy():
        print(member.name)
        try:
            await member.edit(mute=False)
            print(f"Unmuted {member.name} during shutdown")
        except Exception as e:
            print(f"Error unmuting {member.name}: {e}")


# Command: Ping (for testing)
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


# Command: Monitor a User
@bot.command()
async def monitor(ctx, member: discord.Member):
    """Command to monitor a user in a voice channel"""
    if member.id not in monitored_users:
        monitored_users.add(member.id)
        guild = ctx.guild

        # Connect to the channel and monitor the user
        voice_client = await connect_to_channel(guild)
        if voice_client:
            await ctx.send(f"{member.name} is now being monitored.")
            await monitor_user(member, voice_client)
        else:
            await ctx.send("Failed to connect to the voice channel.")
    else:
        await ctx.send(f"{member.name} is already being monitored.")


# Command: Unmonitor a User
@bot.command()
async def unmonitor(ctx, member: discord.Member):
    """Command to remove a user from the monitor list"""
    if member.id in monitored_users:
        monitored_users.remove(member.id)
        await ctx.send(f"{member.name} is no longer being monitored.")
    else:
        await ctx.send(f"{member.name} is not currently being monitored.")


# Command: Unmute a User
@bot.command()
async def unmute(ctx, member: discord.Member):
    """Command to manually unmute a user"""
    await member.edit(mute=False)
    await ctx.send(f"{member.name} has been unmuted.")


# Event: On Bot Ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')


# Event: On Voice State Update
@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state changes"""
    if member.id in monitored_users and after.channel and not after.self_mute:
        guild = member.guild
        
        # Attempt to connect or retrieve the existing voice connection
        voice_client = await connect_to_channel(guild)

        # If the user is being monitored, track their voice time
        if voice_client:
            await monitor_user(member, voice_client)


# Graceful Shutdown Handler: Unmute everyone when the bot stops
@bot.event
async def on_shutdown():
    """Ensure all muted users are unmuted when bot shuts down"""
    await unmute_all()

# Use atexit to trigger unmute if shutdown unexpectedly
atexit.register(lambda: asyncio.run(unmute_all()))


# Run the bot
bot.run(TOKEN)
