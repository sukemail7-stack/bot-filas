import discord
from discord.ui import View, Button
from database import get_saldo, remove_saldo, cursor, conn

class FilaView(View):

    def __init__(self, aposta_id, valor, limite):
        super().__init__(timeout=None)
        self.aposta_id = aposta_id
        self.valor = valor
        self.limite = limite

    @discord.ui.button(label="Entrar na fila", style=discord.ButtonStyle.green)
    async def entrar(self, interaction: discord.Interaction, button: Button):

        user = interaction.user.id

        cursor.execute("SELECT * FROM participantes WHERE aposta_id=? AND user_id=?", (self.aposta_id, user))
        if cursor.fetchone():
            await interaction.response.send_message("❌ Você já entrou nessa aposta.", ephemeral=True)
            return

        saldo = get_saldo(user)

        if saldo < self.valor:
            await interaction.response.send_message("❌ Saldo insuficiente.", ephemeral=True)
            return

        remove_saldo(user, self.valor)

        cursor.execute("INSERT INTO participantes VALUES (?,?)", (self.aposta_id, user))
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM participantes WHERE aposta_id=?", (self.aposta_id,))
        total = cursor.fetchone()[0]

        if total >= self.limite:

            guild = interaction.guild

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }

            cursor.execute("SELECT user_id FROM participantes WHERE aposta_id=?", (self.aposta_id,))
            users = cursor.fetchall()

            for u in users:
                member = guild.get_member(u[0])
                overwrites[member] = discord.PermissionOverwrite(view_channel=True)

            canal = await guild.create_text_channel(
                name=f"aposta-{self.aposta_id}",
                overwrites=overwrites
            )

            await canal.send("🎮 A fila encheu! Combinen a partida aqui.")

        await interaction.response.send_message("✅ Você entrou na aposta!", ephemeral=True)