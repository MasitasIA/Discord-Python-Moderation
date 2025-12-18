import discord
from discord.ext import commands
import sys

# Importamos las funciones desde la carpeta anterior
sys.path.append("..") 
from utils import load_json, save_json

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_log_channel(self, guild):
        logchannels = load_json("logchannels.json")
        channel_id = logchannels.get(str(guild.id))
        if channel_id:
            return guild.get_channel(channel_id)
        return None

    # --- EVENTOS DE MODERACIÓN ---

    # Evento de logs para baneos
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        channel = await self.get_log_channel(guild)
        if not channel: 
            return
        
        ban_entry = None
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                ban_entry = entry
                break
        
        embed = discord.Embed(title="🔨 Usuario Baneado", color=discord.Color.red())
        embed.add_field(name="Usuario", value=f"{user.name} (ID: {user.id})", inline=False)
        if ban_entry:
            embed.add_field(name="Razón", value=ban_entry.reason or "No especificada", inline=False)
            embed.add_field(name="Moderador", value=ban_entry.user.mention, inline=True)
        
        await channel.send(embed=embed)

        # Evento de logs para desbaneos
        @commands.Cog.listener()
        async def on_member_unban(self, guild, user):
            channel = await self.get_log_channel(guild)
            if not channel: 
                return

            embed = discord.Embed(title="🕊️ Usuario Desbaneado", 
                                  description=f"**{user.name}** ha sido desbaneado del servidor.", 
                                  color=discord.Color.green())
            await channel.send(embed=embed)

        if ban_entry:
            embed.add_field(name="Razón", value=ban_entry.reason or "No especificada", inline=False)
            embed.add_field(name="Moderador", value=ban_entry.user.mention, inline=True)
        else:
            embed.add_field(name="Razón", value="No encontrada (Posiblemente hecha por otro bot o muy antigua)", inline=False)

        embed.set_footer(text=f"ID: {user.id}")

        await channel.send(embed=embed)

    # Evento de logs para expulsiones
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = await self.get_log_channel(member.guild)
        if not channel: 
            return
        
        kick_entry = None
        async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
            if entry.target.id == member.id:
                kick_entry = entry
                break
        
        if kick_entry:
            embed = discord.Embed(
                title="👢 Miembro Expulsado",
                description=f"**{member.name}** ha sido expulsado del servidor.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Razón:", value=kick_entry.reason or "No especificada", inline=False)
            embed.add_field(name="Moderador:", value=kick_entry.user.mention, inline=True)
            embed.set_footer(text=f"ID: {member.id}")

        await channel.send(embed=embed)

    # --- EVENTOS DE CHAT ---

    # Evento de logs para mensajes eliminados
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: 
            return
        if not message.guild: 
            return 
        channel = await self.get_log_channel(message.guild)
        if not channel: 
            return

        embed = discord.Embed(title="🗑️ Mensaje Borrado", color=discord.Color.dark_red())
        embed.add_field(name="Autor", value=message.author.mention, inline=True)
        embed.add_field(name="Canal", value=message.channel.mention, inline=True)
        content = message.content if message.content else "*[Solo Imagen/Archivo]*"
        embed.add_field(name="Contenido", value=content, inline=False)

        await channel.send(embed=embed)

    # Evento de logs para mensajes editados
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot: 
            return
        if not before.guild: 
            return
        # Si el contenido es igual (ej: discord carga un link), ignoramos
        if before.content == after.content: 
            return

        channel = await self.get_log_channel(before.guild)
        if not channel: 
            return

        embed = discord.Embed(title="✏️ Mensaje Editado", color=discord.Color.blue())
        embed.add_field(name="Autor", value=before.author.mention, inline=True)
        embed.add_field(name="Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="Antes", value=before.content or "*[Vacio]*", inline=False)
        embed.add_field(name="Después", value=after.content or "*[Vacio]*", inline=False)
        # Añadimos un link para ir al mensaje editado
        embed.add_field(name="Ir al mensaje", value=f"[Click Aquí]({after.jump_url})", inline=False)

        await channel.send(embed=embed)

    # --- COMANDOS DE LOGS ---

    # Comando para ver la ayuda de logs
    @commands.hybrid_command(name="loghelp", description="Muestra qué eventos registra el sistema de logs.")
    async def loghelp(self, ctx):
        embed = discord.Embed(
            title="📜 Sistema de Logs",
            description="El bot registrará automáticamente los siguientes eventos en el canal configurado:",
            color=discord.Color.blue()
        )
        embed.add_field(name="🛡️ Moderación", value="• Baneos\n• Desbaneos\n• Expulsiones (Kicks)", inline=True)
        embed.add_field(name="💬 Chat", value="• Mensajes Borrados\n• Mensajes Editados", inline=True)
        
        embed.set_footer(text="Canal actual: Usa /viewlogchannel")
        await ctx.send(embed=embed)

    # Comando para establecer el canal de logs
    @commands.hybrid_command(name="setlogchannel", description="Establece el canal de logs del servidor.")
    @commands.has_permissions(administrator=True)
    async def setlogchannel(self, ctx, channel: discord.TextChannel):
        logchannels = load_json("logchannels.json")
        logchannels[str(ctx.guild.id)] = channel.id
        save_json("logchannels.json", logchannels)

        embed = discord.Embed(
            title="Canal de Logs Establecido",
            description=f"✅ Canal de logs establecido a {channel.mention}.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    # Comando para ver el canal de logs actual
    @commands.hybrid_command(name="viewlogchannel", description="Muestra el canal de logs actual del servidor.")
    @commands.has_permissions(administrator=True)
    async def viewlogchannel(self, ctx):
        logchannels = load_json("logchannels.json")
        channel_id = logchannels.get(str(ctx.guild.id))
        if channel_id:
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="Canal de Logs Actual",
                    description=f"📢 El canal de logs actual es {channel.mention}.",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ El canal de logs configurado ya no existe.")
        else:
            await ctx.send("❌ No hay ningún canal de logs configurado para este servidor.")

    # Comando para desactivar el canal de logs
    @commands.hybrid_command(name="disablelogchannel", description="Desactiva el canal de logs del servidor.")
    @commands.has_permissions(administrator=True)
    async def disablelogchannel(self, ctx):
        logchannels = load_json("logchannels.json")
        if str(ctx.guild.id) in logchannels:
            logchannels.pop(str(ctx.guild.id))
            save_json("logchannels.json", logchannels)

            embed = discord.Embed(
                title="Canal de Logs Desactivado",
                description="✅ Canal de logs desactivado correctamente.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("❌ No hay ningún canal de logs configurado para este servidor.")

async def setup(bot):
    await bot.add_cog(Logs(bot))