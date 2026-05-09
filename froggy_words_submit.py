import discord
from discord import app_commands

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

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    global PREV_AUTHOR, SECRET_WORD
    if message.author == client.user or message.author == PREV_AUTHOR or message.author == WORD_SETTER or not SECRET_WORD:
        return

    if SECRET_WORD == message.content:
        await message.add_reaction("🐸")
        await message.channel.send(
            f"{message.author.mention} has successfully guessed the secret word: {SECRET_WORD}!"
        )
        PREV_AUTHOR = message.author
        SECRET_WORD = None
        return

    if SECRET_WORD in message.content:
        await message.add_reaction("🐸")
        PREV_AUTHOR = message.author
        return


@client.tree.command()
@app_commands.describe(
    secret_word="The word which members will guess"
)
async def set_secret_word(interaction: discord.Interaction, secret_word: str):
    """Choose a secret word for members to guess together!"""
    global SECRET_WORD, WORD_SETTER

    if SECRET_WORD:
        await interaction.response.send_message(
            f"You cannot set a new secret word while a game is active!",
            ephemeral=True
        )
    else:
        SECRET_WORD = secret_word
        WORD_SETTER = interaction.user
        await interaction.response.send_message(
            f"{interaction.user.mention} has set a new secret word!"
        )

@client.tree.command()
async def clear_secret_word(interaction: discord.Interaction):
    """Clear the current secret word."""
    global SECRET_WORD
    SECRET_WORD = None
    await interaction.response.send_message(
            f"{interaction.user.mention} has cleared the current secret word!"
    )

client.setup_hook()
client.run('token')
