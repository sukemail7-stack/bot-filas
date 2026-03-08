import discord
from discord.ext import commands
from discord import app_commands

from config import TOKEN, EMBED_COLOR
from database import get_saldo, add_saldo, remove_saldo, cursor, conn
from views import FilaView


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot ligado como {bot.user}")


# saldo
@bot.tree.command(name="saldo")
async def saldo(interaction: discord.Interaction):

    saldo = get_saldo(interaction.user.id)

    embed = discord.Embed(
        title="💰 Seu saldo",
        description=f"Saldo: **{saldo}**",
        color=EMBED_COLOR
    )

    await interaction.response.send_message(embed=embed)


# addsaldo
@bot.tree.command(name="addsaldo")
@app_commands.checks.has_permissions(administrator=True)
async def addsaldo(interaction: discord.Interaction, usuario: discord.Member, valor: int):

    add_saldo(usuario.id, valor)

    await interaction.response.send_message(f"✅ {valor} adicionados para {usuario.mention}")


# remsaldo
@bot.tree.command(name="remsaldo")
@app_commands.checks.has_permissions(administrator=True)
async def remsaldo(interaction: discord.Interaction, usuario: discord.Member, valor: int):

    remove_saldo(usuario.id, valor)

    await interaction.response.send_message(f"❌ {valor} removidos de {usuario.mention}")


# criar aposta
@bot.tree.command(name="criar_aposta")
async def criar_aposta(
    interaction: discord.Interaction,
    valor: int,
    modo: str,
    descricao: str = "Sem descrição"
):

    modos = {
        "x1": 2,
        "x2": 4,
        "x4": 8
    }

    if modo not in modos:
        await interaction.response.send_message("Modo inválido.", ephemeral=True)
        return

    limite = modos[modo]

    cursor.execute(
        "INSERT INTO apostas (valor, modo, descricao, status) VALUES (?,?,?,?)",
        (valor, modo, descricao, "aberta")
    )
    conn.commit()

    aposta_id = cursor.lastrowid

    embed = discord.Embed(
        title="🔥 Nova aposta criada",
        description=f"""
💰 Valor: **{valor}**
🎮 Modo: **{modo}**
📄 {descricao}

👥 Jogadores: 0/{limite}
""",
        color=EMBED_COLOR
    )

    view = FilaView(aposta_id, valor, limite)

    await interaction.response.send_message(embed=embed, view=view)


# finalizar aposta
@bot.tree.command(name="finalizar_aposta")
@app_commands.checks.has_permissions(administrator=True)
async def finalizar_aposta(
    interaction: discord.Interaction,
    aposta_id: int,
    vencedor: discord.Member
):

    cursor.execute("SELECT valor FROM apostas WHERE id=?", (aposta_id,))
    result = cursor.fetchone()

    if not result:
        await interaction.response.send_message("Aposta não encontrada.")
        return

    valor = result[0]

    cursor.execute("SELECT COUNT(*) FROM participantes WHERE aposta_id=?", (aposta_id,))
    players = cursor.fetchone()[0]

    premio = valor * players

    add_saldo(vencedor.id, premio)

    await interaction.response.send_message(
        f"🏆 {vencedor.mention} venceu a aposta e ganhou **{premio}**"
    )


# cancelar aposta
@bot.tree.command(name="cancelar_aposta")
@app_commands.checks.has_permissions(administrator=True)
async def cancelar_aposta(interaction: discord.Interaction, aposta_id: int):

    cursor.execute("SELECT valor FROM apostas WHERE id=?", (aposta_id,))
    result = cursor.fetchone()

    if not result:
        await interaction.response.send_message("Aposta não encontrada.")
        return

    valor = result[0]

    cursor.execute("SELECT user_id FROM participantes WHERE aposta_id=?", (aposta_id,))
    users = cursor.fetchall()

    for u in users:
        add_saldo(u[0], valor)

    await interaction.response.send_message("❌ Aposta cancelada e saldos devolvidos.")


bot.run(TOKEN)