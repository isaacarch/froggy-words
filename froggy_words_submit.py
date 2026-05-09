import discord
from discord import app_commands

import datetime as dt

intents = discord.Intents.default()
intents.message_content = True

MY_GUILD = discord.Object(id=1502751209247740014)

class MyClient(discord.Client):
    user: discord.ClientUser

    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


client = MyClient(intents=intents)

SECRET_WORD = None
PREV_AUTHOR = None
WORD_SETTER = None
TIMEOUT = False

async def timeout(user):
    if TIMEOUT:
        delta = dt.timedelta(
            minutes=1
        )
        await user.timeout(delta, reason="🐸")


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    global PREV_AUTHOR, SECRET_WORD, WORD_SETTER
    if message.author == client.user or message.author == PREV_AUTHOR or message.author == WORD_SETTER or not SECRET_WORD:
        return

    if SECRET_WORD == message.content.lower():
        await message.add_reaction("🐸")
        await message.channel.send(
            f"{message.author.mention} has successfully guessed the secret word: {SECRET_WORD}!"
        )
        PREV_AUTHOR = None
        WORD_SETTER = None
        SECRET_WORD = None
        return

    if SECRET_WORD in message.content.lower():
        await message.add_reaction("🐸")
        await timeout(message.author)
        PREV_AUTHOR = message.author
        return


@client.tree.command()
@app_commands.describe(
    secret_word="The word which members will guess"
)
async def set_secret_word(interaction: discord.Interaction, secret_word: str):
    """Choose a secret word for members to guess together!"""
    global SECRET_WORD, WORD_SETTER, PREV_AUTHOR

    if SECRET_WORD:
        await interaction.response.send_message(
            f"You cannot set a new secret word while a game is active!",
            ephemeral=True
        )
    else:
        SECRET_WORD = secret_word.lower()
        WORD_SETTER = interaction.user
        PREV_AUTHOR = None
        await interaction.response.send_message(
            f"{interaction.user.mention} has set a new secret word!"
        )

@client.tree.command()
async def clear_secret_word(interaction: discord.Interaction):
    """Clear the current secret word."""
    global SECRET_WORD, WORD_SETTER, PREV_AUTHOR
    SECRET_WORD = None
    WORD_SETTER = None
    PREV_AUTHOR = None
    await interaction.response.send_message(
            f"{interaction.user.mention} has cleared the current secret word!"
    )

@client.tree.command()
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout_on_frog(interaction: discord.Interaction, enabled: bool):
    """Timeout users when they trigger the frog (1 minute)"""
    global TIMEOUT
    if enabled:
        TIMEOUT = True
        await interaction.response.send_message(
                f"{interaction.user.mention} has enabled timeouts on correct guesses! Users who trigger the frog's wrath will be timed out for *1 minute*."
        )
    else:
        TIMEOUT = False
        await interaction.response.send_message(
                f"{interaction.user.mention} has disabled timeouts on correct guesses! Users will be spared from the frog's wrath for now..."
        )
    print(f"TIMEOUT={TIMEOUT}")

client.setup_hook()
client.run('token')
