import discord
from discord import app_commands
import datetime as dt
import string

from froggy_words_sql import add_win, reset_leaderboard, get_leaderboard, get_user_score

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

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

DIRTY_WORD = None
SECRET_WORD = None
PREV_AUTHOR = None
WORD_SETTER = None
TIMEOUT = False

def clean(s):
    return ''.join(filter(lambda x: x not in string.punctuation and x not in string.whitespace, s)).lower()

async def timeout(user):
    if TIMEOUT:
        delta = dt.timedelta(
            minutes=1
        )
        try:
            await user.timeout(delta, reason="🐸")
        except:
            pass


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    global PREV_AUTHOR, SECRET_WORD, WORD_SETTER, DIRTY_WORD
    if message.author == client.user or message.author == PREV_AUTHOR or message.author == WORD_SETTER or not SECRET_WORD:
        return

    if SECRET_WORD == clean(message.content):
        await message.add_reaction("🐸")
        add_win(message.author.id)
        score = get_user_score(message.author.id)
        await message.channel.send(
            f"{message.author.mention} has successfully guessed the secret word: **{DIRTY_WORD}**! Their new score is {score}."
        )
        PREV_AUTHOR = None
        WORD_SETTER = None
        SECRET_WORD = None
        DIRTY_WORD = None
        return

    if SECRET_WORD in clean(message.content):
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
    global SECRET_WORD, WORD_SETTER, PREV_AUTHOR, DIRTY_WORD

    if SECRET_WORD:
        await interaction.response.send_message(
            f"You cannot set a new secret word while a game is active!",
            ephemeral=True
        )
    else:
        SECRET_WORD = clean(secret_word)
        DIRTY_WORD = secret_word
        WORD_SETTER = interaction.user
        PREV_AUTHOR = None
        await interaction.response.send_message(
            f"{interaction.user.mention} has set a new secret word!"
        )

@client.tree.command()
async def clear_secret_word(interaction: discord.Interaction):
    """Clear the current secret word."""
    global SECRET_WORD, WORD_SETTER, PREV_AUTHOR, DIRTY_WORD
    SECRET_WORD = None
    WORD_SETTER = None
    PREV_AUTHOR = None
    DIRTY_WORD = None
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

@client.tree.command()
@app_commands.checks.has_permissions(moderate_members=True)
async def wipe_leaderboard(interaction: discord.Interaction):
    """DANGER: Clear the leaderboard for the game. This cannot be undone!!"""
    reset_leaderboard()
    await interaction.response.send_message(
        f"{interaction.user.mention} has reset the leaderboard."
    )

@client.tree.command()
async def show_leaderboard(interaction: discord.Interaction):
    """Display the leaderboard for the game!"""
    embed = discord.Embed(title="Froggy Words leaderboard:", color=discord.Colour.gold())
    leaderboard = sorted(get_leaderboard(), key=lambda x: x[1], reverse=True)
    for pos, (id, wins) in enumerate(leaderboard):
        member = interaction.guild.get_member(id)
        embed.add_field(name=f"{pos+1} - {member.display_name}", value=f"{wins} words guessed", inline=False)
        if pos+1 > 9:
            break
    await interaction.response.send_message(embed=embed)



# ## Role stuff non-functional, i think it would require a DB, so not doing it.
# @client.tree.command()
# @app_commands.checks.has_permissions(manage_roles=True)
# async def set_winner_role(interaction: discord.Interaction, role: discord.Role):
#     """Set a role to be assigned to the winner of the game. Must be below the bot's role in the hierarchy."""
#     global ROLE
#     role = ROLE
#     await interaction.response.send_message(
#             f"{interaction.user.mention} has set the winning role to {role.mention}"
#     )

# @client.tree.command()
# @app_commands.checks.has_permissions(manage_roles=True)
# async def clear_winner_role(interaction: discord.Interaction):
#     """Clear the role currently set as the winner role."""
#     global ROLE
#     pass


client.setup_hook()
client.run('token')
