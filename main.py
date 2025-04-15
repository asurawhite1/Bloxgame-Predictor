import discord
from discord import app_commands
from discord.ext import commands
import tls_client
import time
import json
import math
import numpy as np
#istg if yall tryna sell this 
token = "PUT YOUR DISCORD BOT TOKEN HERE"
intents = discord.Intents.default()
intents.messages = True
intents.members = True
client = commands.Bot(command_prefix="!", intents=intents)
@client.event
async def on_ready():
    print(f'{client.user} is online now')
    try:
        synced = await client.tree.sync()
        print(f'{len(synced)} command')
    except Exception as e:
        print(e)


class tls_clients:
    def __init__(self):
        self.session = tls_client.Session(client_identifier="chrome_112")
        self.headers = {
            "Referer": "https://bloxgame.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "x-client-version": "1.0.0",
        }

    def validToken(self, auth):
        headers = self.headers.copy()
        headers.update({
            "x-auth-token": auth,
            "User-Agent": "Mozilla/5.0"
        })

        attempts = 0
        while attempts < 5:
            try:
                reps = self.session.get("https://api.bloxgame.com/user", headers=headers)
                if reps.status_code == 200:
                    return reps.json().get('success', False)
            except Exception:
                pass
            attempts += 1
            time.sleep(0.01)
        return False

    def get_profile(self, auth):
        headers = self.headers.copy()
        headers.update({
            "x-auth-token": auth,
            "User-Agent": "Mozilla/5.0"
        })

        while True:
            try:
                reps = self.session.get("https://api.bloxgame.com/user", headers=headers)
                if reps.status_code == 200:
                    profile_data = reps.json()
                    return profile_data
            except Exception:
                pass


def load_tokens():
    try:
        with open('token.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_tokens(tokens):
    with open('token.json', 'w') as f:
        json.dump(tokens, f, indent=4)


@client.tree.command(name="link", description="link your account to bloxgame predictor")
async def link(interaction: discord.Interaction, token: str):
    await interaction.response.defer(ephemeral=True)
    user_id = interaction.user.id
    tokens = load_tokens()
    session = tls_clients()
    if session.validToken(token):
        profile = session.get_profile(token)
        username = profile['user']['username']
        tokens[str(user_id)] = {
            "token": token
        }
        save_tokens(tokens)
        embed = discord.Embed(title="successfully link your account to bloxgame predictor",color=discord.Color.yellow())
        embed.add_field(name="User:", value=f"> <@{interaction.user.id}>", inline=False)
        embed.add_field(name="Linked to user account:", value=f"> ``{username}``", inline=False)
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(
            title="``❌`` invalid token",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)


@client.tree.command(name="unlink", description="remove your acccount from predictor")
async def unlink(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    user_id = interaction.user.id
    tokens = load_tokens()
    if str(user_id) in tokens:
        del tokens[str(user_id)]
        save_tokens(tokens)
        embed = discord.Embed(title="successfully unlink your account from bloxgame predictor")
        await interaction.followup.send(embed=embed)
    else:
        embed = discord.Embed(
            title="``❌`` You didnt link your account yet",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=embed)

class Predictors:
    def __init__(self, auth):
        self.scaler = None
        self.cf_bypass = tls_clients()
        self.session = self.cf_bypass.session
        self.headers = {
            "x-auth-token": str(auth).strip(),
            "Referer": "https://bloxgame.com/",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0",
            "x-client-version": "1.0.0",
        }

    def request(self, url):
        headers = self.headers.copy()
        response = self.session.get(url, headers=headers)
        print(response.text)
        print(response.status_code)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            return "expire"

    def board(self, safespot):
        board = ["❌" for _ in range(25)]
        for pos in safespot:    
            board[pos] = "✅"
        return "\n".join(" ".join(board[i:i + 5]) for i in range(0, 25, 5))

    def check_game(self):
        reps = self.request("https://api.bloxgame.com/games/mines")
        return reps

    def get_history(self, size):
        return self.request(f"https://api.bloxgame.com/games/mines/history?size={size}&page=0").get('data', [])

    def pastgames(self, safe_amount):
        history = self.get_history(24)
        if history:
            safespot = [pos for game in history for pos in game['mineLocations']][:safe_amount]
            board = self.board(safespot=safespot)
            return board

    def Algortihm(self, safe_amount):
        history = self.get_history(24)
        if not history:
            return "None"
        mineLocations = [mine for game in history for mine in game['mineLocations']]
        board = [0] * 25
        for i in range(len(mineLocations) - 1):
            h = abs(mineLocations[i] - mineLocations[i + 1])
            b = min(h + i, 24)
            board[b] += 1
        for i in range(len(mineLocations) - 1):
            h = abs(mineLocations[i] - mineLocations[i + 1])
            b = min(h + (mineLocations[i] - i), 24)
            board[b] += 1
        prediction = max(board) if max(board) > 0 else 1
        board = [value / prediction for value in board]
        safespot = np.argsort(board)[:safe_amount]
        return self.board(safespot=safespot)
# GENERATE BY ChatGPT
    def Logarithm(self, safe_amount):# GENERATE BY ChatGPT
        history = self.get_history(24)# GENERATE BY ChatGPT
        if not history:# GENERATE BY ChatGPT
            return "None"# GENERATE BY ChatGPT
        board = [0] * 25# GENERATE BY ChatGPT
        weights = [1 / math.log(2 + i) for i in range(len(history))]# GENERATE BY ChatGPT
        for idx, game in enumerate(history):# GENERATE BY ChatGPT
            mines = game['mineLocations']# GENERATE BY ChatGPT
            weight = weights[idx]# GENERATE BY ChatGPT
            for mine in mines:# GENERATE BY ChatGPT
                board[mine] += weight# GENERATE BY ChatGPT
        predict = [1 / (1 + math.log(1 + score)) for score in board]# GENERATE BY ChatGPT
        safespot = np.argsort(predict)[:safe_amount]# GENERATE BY ChatGPT
        return self.board(safespot=safespot)# GENERATE BY ChatGPT
# GENERATE BY ChatGPT

@client.tree.command(name="freemines")
@app_commands.choices(
    algorithm=[
        app_commands.Choice(name="pastgames", value="pastgames"),
        app_commands.Choice(name="Algortihm", value="Algortihm"),
        app_commands.Choice(name="Logarithm",value="Logarithm"),
    ]
)
async def predict(interaction: discord.Interaction, algorithm: app_commands.Choice[str], safeamount: int):
    await interaction.response.defer()
    if safeamount <= 0 or safeamount > 25:
        await interaction.followup.send(content="bad boy!, max safeamount should be 24 >:(")
        return
    user_id = str(interaction.user.id)
    tokens = load_tokens()
    token = tokens[user_id]["token"]
    if user_id not in tokens:
        embed = discord.Embed(
            title=f"``❌`` {interaction.user.name},you did not link your account to Predictor yet",
            color=discord.Color.red())
        embed.set_footer(text="Please link your account to Predictor to predict your current mines game!")
        await interaction.followup.send(embed=embed)
        return
    predictor = Predictors(token)
    gamecheck = predictor.check_game()
    if gamecheck == "expire":
        await interaction.followup.send(content="your current token is expired. please link your account to predictor again!")
        return
    elif not gamecheck or not gamecheck.get('hasGame', False):
        await interaction.followup.send(content="Please start a mines game first before predict !")
        return
    
    games = gamecheck.get('game', {})
    Mines = games.get('minesAmount', 'N/A')
    bet_amount = games.get('betAmount', 'N/A')
    uuid = games.get('uuid', 'N/A')
    gamehash = games.get('_id', {}).get('$oid', 'N/A')
    if algorithm.value == "pastgames":
        board = predictor.pastgames(safeamount)
    elif algorithm.value == "Algortihm":
        board = predictor.Algortihm(safeamount)
    elif algorithm.value == "Logarithm":
        board = predictor.Logarithm(safeamount)
    embed = discord.Embed(title="Bloxgame Mines Predictor",color = discord.Color.yellow())
    embed.add_field(name="Prediction", value=f"{board}", inline=False)
    embed.add_field(name="BetAmount", value=f"> ``{bet_amount}``",inline=False)
    embed.add_field(name="Mines", value=f"> ``{Mines}``",inline=False)
    embed.add_field(name="Hash", value=f"> ``{gamehash}``",inline=False)
    embed.add_field(name="UUID", value=f"> ``{uuid}``", inline=False)
    embed.set_footer(text="Note : None of all predictor is 100% or 80% + ! Do not risk your money with predictors !")
    await interaction.followup.send(embed=embed)


@client.tree.command(name="how_to_link", description="show you how to link your account")
async def link(interaction: discord.Interaction):
    embed = discord.Embed(title="Here is qiuck step how to link", description="First go to website bloxgame.com and press f12 to open dev tools then head to application and localstorage\n**in Local Storage copy the _DO_NOT_SHARE_BLOXGAME_TOKEN value and use the /link command and paste it in.**\nand it done!")
    await interaction.response.send_message(embed=embed, ephemeral=True)

client.run(token)
