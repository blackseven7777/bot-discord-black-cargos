import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from database import *
import os

# 🔐 TOKEN
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ ERRO: TOKEN não encontrado!")

# 🔥 INTENTS
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔄 CONVERTER TEMPO (d, h, m)
def converter_tempo(tempo_str):
    unidade = tempo_str[-1]
    valor = int(tempo_str[:-1])

    if unidade == "d":
        return timedelta(days=valor)
    elif unidade == "h":
        return timedelta(hours=valor)
    elif unidade == "m":
        return timedelta(minutes=valor)
    else:
        raise ValueError("Use: d, h ou m")

@bot.event
async def on_ready():
    print(f'✅ Bot online como {bot.user}')
    verificar_expiracoes.start()

# 👑 CRIAR CÓDIGO
@bot.command()
@commands.has_permissions(administrator=True)
async def criarcodigo(ctx, codigo: str, cargo: discord.Role, max_usos: int, tempo: str):
    try:
        delta = converter_tempo(tempo)
        validade = datetime.now() + delta

        criar_codigo(codigo.upper(), cargo.id, max_usos, validade.isoformat())

        await ctx.send(f"✅ Código criado! Duração: {tempo}")
    except Exception as e:
        await ctx.send("❌ Erro ao criar código.")
        print(e)

# 👤 RESGATAR
@bot.command()
async def resgatar(ctx, codigo: str):
    data = pegar_codigo(codigo.upper())

    if not data:
        await ctx.send("❌ Código inválido!")
        return

    codigo_db, cargo_id, usos, max_usos, validade = data

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

    # salva data exata de expiração
    expira_em = datetime.fromisoformat(validade)
    registrar_uso(ctx.author.id, codigo, cargo.id, expira_em.isoformat())

    await ctx.send(f"✅ {ctx.author.mention}, você recebeu {cargo.name}!")

# 🔁 REMOVER CARGO AUTOMATICO
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
                    print(f"🔻 Removido cargo de {membro.name}")

            remover_registro(user_id, codigo)

# 🚀 START
bot.run(TOKEN)
