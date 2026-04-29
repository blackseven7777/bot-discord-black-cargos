import discord
from discord.ext import commands, tasks
import json
from datetime import datetime
from database import *

with open("config.json") as f:
    config = json.load(f)

# 🔥 INTENTS CORRETOS (IMPORTANTE)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot online como {bot.user}')
    verificar_expiracoes.start()

# CRIAR CÓDIGO (ADMIN)
@bot.command()
@commands.has_permissions(administrator=True)
async def criarcodigo(ctx, codigo: str, cargo: discord.Role, max_usos: int, dias: int):
    try:
        criar_codigo(codigo.upper(), cargo.id, max_usos, dias)
        await ctx.send("✅ Código criado!")
    except Exception as e:
        await ctx.send("❌ Erro ao criar código.")
        print(e)

# RESGATAR CÓDIGO
@bot.command()
async def resgatar(ctx, codigo: str):
    data = pegar_codigo(codigo.upper())

    if not data:
        await ctx.send("❌ Código inválido!")
        return

    codigo, cargo_id, usos, max_usos, validade = data

    if datetime.now() > datetime.fromisoformat(validade):
        await ctx.send("⛔ Código expirado!")
        return

    if usos >= max_usos:
        await ctx.send("⚠️ Código esgotado!")
        return

    cargo = ctx.guild.get_role(cargo_id)

    if not cargo:
        await ctx.send("❌ Cargo não encontrado!")
        return

    await ctx.author.add_roles(cargo)
    usar_codigo(codigo)

    dias_restantes = (datetime.fromisoformat(validade) - datetime.now()).days
    registrar_uso(ctx.author.id, codigo, cargo.id, dias_restantes)

    await ctx.send(f"✅ {ctx.author.mention}, você recebeu o cargo {cargo.name}!")

# LOOP: REMOVE CARGO AUTOMATICAMENTE
@tasks.loop(minutes=1)
async def verificar_expiracoes():
    dados = pegar_expiracoes()

    for user_id, codigo, cargo_id, expira_em in dados:
        if datetime.now() >= datetime.fromisoformat(expira_em):

            for guild in bot.guilds:
                membro = guild.get_member(user_id)
                cargo = guild.get_role(cargo_id)

                if membro and cargo:
                    await membro.remove_roles(cargo)
                    print(f"Removido cargo de {membro.name}")

            remover_registro(user_id, codigo)

bot.run(config["token"])