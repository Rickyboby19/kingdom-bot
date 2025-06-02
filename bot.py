import json
import random
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

players = []
roles_pool = []
started = False

# Charger les rôles depuis le fichier JSON
with open('roles.json', 'r', encoding='utf-8') as f:
    ALL_ROLES = json.load(f)

# Répartition des rôles selon le nombre de joueurs
ROLE_DISTRIBUTION = {
    1: {"assassin": 1},
    5: {"king": 1, "assassin": 2, "renegade": 1, "knight": 1},
    6: {"king": 1, "knight": 1, "bandit": 2, "assassin": 2},
    7: {"king": 1, "knight": 1, "bandit": 2, "assassin": 2, "renegade": 1},
    8: {"king": 1, "knight": 1, "bandit": 2, "assassin": 3, "renegade": 1},
    9: {"king": 1, "knight": 2, "bandit": 3, "assassin": 3}
}

def role_message(role):
    msg = f"**Ton rôle : {role['name']}**\n"
    msg += f"🎯 Victoire : {role.get('win_condition', 'Non précisée')}\n"
    msg += f"💀 Défaite : {role.get('lose_condition', 'Non précisée')}\n"
    msg += f"🧠 Pouvoir : {role['ability']}"
    return msg

async def send_role_dm(player, role, ctx):
    try:
        if "image" in role:
            image_path = f"images/{role['image']}"
            file = discord.File(image_path, filename=role["image"])

            embed = discord.Embed(title=f"Ton rôle : {role['name']}", color=discord.Color.blue())
            embed.add_field(name="🎯 Victoire", value=role.get("win_condition", "Non précisée"), inline=False)
            embed.add_field(name="💀 Défaite", value=role.get("lose_condition", "Non précisée"), inline=False)
            embed.add_field(name="🧠 Pouvoir", value=role.get("ability", "Aucun"), inline=False)
            embed.set_image(url=f"attachment://{role['image']}")

            await player.send(embed=embed, file=file)
        else:
            content = role_message(role)
            await player.send(content)
    except:
        await ctx.send(f"Je ne peux pas envoyer un MP à {player.display_name}.")

@bot.command()
async def join(ctx):
    if ctx.author in players:
        await ctx.send(f"{ctx.author.display_name}, tu es déjà dans la partie.")
    else:
        players.append(ctx.author)
        await ctx.send(f"{ctx.author.display_name} a rejoint la partie.")

@bot.command()
async def start(ctx):
    global players, started, roles_pool
    if started:
        await ctx.send("Une partie est déjà en cours.")
        return
    n = len(players)
    if n not in ROLE_DISTRIBUTION:
        await ctx.send("Nombre de joueurs non pris en charge (5 à 9).")
        return

    started = True
    role_counts = ROLE_DISTRIBUTION[n]
    roles_pool = []

    for role_type, count in role_counts.items():
        chosen = random.sample(ALL_ROLES[role_type], count)
        roles_pool.extend(chosen)

    random.shuffle(roles_pool)

    for player, role in zip(players, roles_pool):
        await send_role_dm(player, role, ctx)

    await ctx.send("Les rôles ont été distribués par message privé.")

@bot.command()
async def resend(ctx):
    global players, started, roles_pool
    if not started:
        await ctx.send("Aucune partie n'est en cours.")
        return

    for player, role in zip(players, roles_pool):
        await send_role_dm(player, role, ctx)

    await ctx.send("Les rôles ont été redistribués en message privé.")

@bot.command()
async def reshuffle(ctx):
    global players, started, roles_pool
    if not started:
        await ctx.send("Aucune partie n'est en cours.")
        return

    n = len(players)
    role_counts = ROLE_DISTRIBUTION[n]
    roles_pool = []

    for role_type, count in role_counts.items():
        chosen = random.sample(ALL_ROLES[role_type], count)
        roles_pool.extend(chosen)

    random.shuffle(roles_pool)

    for player, role in zip(players, roles_pool):
        await send_role_dm(player, role, ctx)

    await ctx.send("Les rôles ont été re-mélangés et envoyés par message privé.")

@bot.command()
async def reset(ctx):
    global players, started, roles_pool
    players = []
    roles_pool = []
    started = False
    await ctx.send("La partie a été réinitialisée.")

# Lancer le bot
import os
bot.run(os.getenv("DISCORD_TOKEN"))