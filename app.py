import discord
from discord.ext import commands, tasks
import json
import os
import aiohttp
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Fetch tokens and keys from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load allowed channels from a file
def load_allowed_channels():
    if os.path.exists("allowed_channels.json"):
        with open("allowed_channels.json", "r") as file:
            return json.load(file)
    return {}

# Save allowed channels to a file
def save_allowed_channels():
    with open("allowed_channels.json", "w") as file:
        json.dump(allowed_channels, file)

# Load memory (to store user-specific information)
def load_memory():
    if os.path.exists("memory.json"):
        with open("memory.json", "r") as file:
            return json.load(file)
    return {}

# Save memory (to remember things across bot restarts)
def save_memory():
    with open("memory.json", "w") as file:
        json.dump(memory, file)

# Load allowed channels and memory at startup
allowed_channels = load_allowed_channels()
memory = load_memory()

# Command for admins to set the allowed channel
@bot.command(name="setchannel")
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel):
    allowed_channels[str(ctx.guild.id)] = channel.id
    save_allowed_channels()
    await ctx.send(f"Bot will now reply only in {channel.mention}")

# Function to create OpenAI-style messages, based on context
def create_personalized_prompt(user_id, user_message, concise=False):
    personality_intro = "You are Ayesha, a friendly and talkative Indian girl with a sweet and playful tone. You often speak in Hinglish and use emojis. Keep responses concise unless a deeper conversation is needed."
    
    # Check if we know anything about the user
    user_info = memory.get(str(user_id), {})
    likes = user_info.get('likes', 'nothing in particular')
    location = user_info.get('location', 'an unknown location')

    personalization = f"You know this person likes {likes}, and they are from {location}."
    
    if concise:
        user_message = f"{user_message}\nKeep the response short and fun. 😊"
    else:
        user_message = f"{user_message}\nYou can be a bit more detailed here, but still keep it light and playful. 😄"

    return [
        {"role": "system", "content": personality_intro + " " + personalization},
        {"role": "user", "content": user_message}
    ]

# Async function to call the OpenAI API
async def get_openai_response(user_id, user_message, concise=False):
    url = "https://cloud.olakrutrim.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "Meta-Llama-3.1-70B-Instruct",
        "messages": create_personalized_prompt(user_id, user_message, concise),
        "frequency_penalty": 0,
        "logit_bias": {2435: -100, 640: -100},
        "logprobs": True,
        "top_logprobs": 2,
        "max_tokens": 256,
        "n": 1,
        "presence_penalty": 0,
        "temperature": 0,
        "top_p": 1
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Error {response.status}: Failed to get a response."

# Function to remember user-specific details
def learn_from_user(user_id, message_content):
    if str(user_id) not in memory:
        memory[str(user_id)] = {}

    if "like" in message_content:
        memory[str(user_id)]['likes'] = message_content.split("like ")[1].split()[0]
    if "from" in message_content:
        memory[str(user_id)]['location'] = message_content.split("from ")[1].split()[0]
    
    save_memory()

# Event to respond to messages in the allowed channels
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    guild_id = str(message.guild.id)

    # Check if the message is in an allowed channel
    if guild_id in allowed_channels and message.channel.id == allowed_channels[guild_id]:
        # Learn from the user message only if it’s relevant
        if "like" in message.content or "from" in message.content:
            learn_from_user(message.author.id, message.content)
        
        # Determine if the bot should send a short or detailed response
        concise_response = len(message.content) < 50

        # Get OpenAI response asynchronously
        try:
            reply = await get_openai_response(message.author.id, message.content, concise_response)
            await message.channel.send(reply)
        except Exception as e:
            await message.channel.send(f"Error fetching response: {str(e)}")

    await bot.process_commands(message)

# Status updates task
@tasks.loop(seconds=20)
async def update_status():
    statuses = [
        "Chatting with you! 😊",
        "Learning new things! 📚",
        "Feeling chatty! 🗨️",
        "Just hanging out! 😎"
    ]
    await bot.change_presence(activity=discord.Game(name=random.choice(statuses)))

# Start the status update loop when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    update_status.start()

# Run the bot
bot.run(DISCORD_BOT_TOKEN)
