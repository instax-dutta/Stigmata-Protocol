import discord
from discord.ext import commands, tasks
import json
import os
import random
from dotenv import load_dotenv
from krutrim_cloud import KrutrimCloud
from krutrim_cloud.lib.utils import convert_base64_to_PIL_img

# Load environment variables
load_dotenv()

# Fetch tokens and keys from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

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

# Create output directory if it doesn't exist
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# Command for admins to set the allowed channel
@bot.command(name="setchannel")
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel):
    allowed_channels[str(ctx.guild.id)] = channel.id
    save_allowed_channels()
    await ctx.send(f"Ayesha will now reply only in {channel.mention}")

# Function to create personalized messages for KrutrimCloud
def create_personalized_prompt(user_id, user_message, concise=False):
    personality_intro = "You are Tina, a friendly and supportive girlfriend chatbot. You speak in a warm and caring tone, always encouraging and uplifting. Keep your responses light-hearted and engaging."

    # Check if we know anything about the user
    user_info = memory.get(str(user_id), {})
    likes = user_info.get('likes', 'nothing specific')

    personalization = f"You know this person likes {likes}."

    if concise:
        user_message = f"{user_message}\nRespond in one line and keep it simple. 😊"
    else:
        user_message = f"{user_message}\nYou can be a bit more detailed here, but keep it light. 😄"

    return [
        {"role": "system", "content": personality_intro + " " + personalization},
        {"role": "user", "content": user_message}
    ]

# Async function to call the KrutrimCloud API for text responses
async def get_krutir_response(user_id, user_message, concise=False):
    client = KrutrimCloud()
    model_name = "Meta-Llama-3.1-70B-Instruct"
    messages = create_personalized_prompt(user_id, user_message, concise)

    try:
        response = client.chat.completions.create(model=model_name, messages=messages)
        return response.choices[0].message.content  # type:ignore
    except Exception as e:
        return f"Error fetching response: {str(e)}"

# Async function to generate images using KrutrimCloud
async def generate_image(prompt):
    client = KrutrimCloud()
    try:
        stable_diffusion_response = client.images.generations.diffusion(
            model_name="diffusion1XL",
            image_height=1024,
            image_width=1024,
            prompt=prompt
        )

        if stable_diffusion_response.error:
            return f"Error generating image: {stable_diffusion_response.error}"

        # Access each generated image
        images = []
        for data in stable_diffusion_response.data:
            PIL_img = convert_base64_to_PIL_img(data["b64_json"])
            # Save the image to a file or send it directly
            image_path = os.path.join(output_dir, f"image_{random.randint(1, 10000)}.png")
            PIL_img.save(image_path)
            images.append(image_path)

        return images
    except Exception as exc:
        return f"Exception: {exc}"

# Function to remember user-specific details
def learn_from_user(user_id, message_content):
    if str(user_id) not in memory:
        memory[str(user_id)] = {}

    if "like" in message_content:
        memory[str(user_id)]['likes'] = message_content.split("like ")[1].split()[0]
    
    save_memory()

# Event to respond to messages in the allowed channels
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages from the bot itself

    guild_id = str(message.guild.id)

    # Check if the message is in an allowed channel
    if guild_id in allowed_channels and message.channel.id == allowed_channels[guild_id]:
        # Learn from the user message
        learn_from_user(message.author.id, message.content)

        # Check if the user is asking for an image of the bot
        if "image of yourself" in message.content.lower() or \
           "send me a picture of you" in message.content.lower() or \
           "show me you" in message.content.lower():
            await message.reply("Aw, sweetie, I'm a chatbot, I don't have a physical body, but I'm always here for you in spirit! 💕")
            return

        # Check if the user is asking for an image using a command or keywords
        if message.content.startswith("!generateimage ") or \
           "create an image of" in message.content.lower() or \
           "draw" in message.content.lower() or \
           "generate a picture of" in message.content.lower():
            prompt = message.content.split(" ", 1)[1] if message.content.startswith("!generateimage ") else message.content
            images = await generate_image(prompt)
            if isinstance(images, list):
                for image_path in images:
                    await message.channel.send(file=discord.File(image_path))
            else:
                await message.reply(images)  # Send error message if any
            return

        # Determine if the bot should send a short or detailed response
        concise_response = len(message.content) < 50

        # Get KrutrimCloud response asynchronously
        try:
            reply = await get_krutir_response(message.author.id, message.content, concise_response)
            await message.reply(reply)  # Use the reply method to respond to the specific message
        except Exception as e:
            await message.reply(f"Error fetching response: {str(e)}")

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
