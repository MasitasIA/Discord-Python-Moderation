import discord
from discord.ext import commands
import sys

# Importamos las funciones desde la carpeta anterior
sys.path.append("..") 
from utils import load_json, save_json

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- EVENTOS ---

    # Evento de logs para baneos
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        logchannels = load_json("logchannels.json")
        channel_id = logchannels.get(str(guild.id))
        
        if not channel_id:
            return
        
        channel = guild.getchannel(channel_id)
        if not channel:
            return
        
        ban_entry = None
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if entry.target.id == user.id:
                ban_entry = entry
                break
        
        embed = discord.Embed(
            title="🔨 Usuario Baneado",
            description=f"**{user.name}** ha sido baneado del servidor.",
            color=discord.Color.red()
        )

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
        logchannels = load_json("logchannels.json")
        channel_id = logchannels.get(str(member.guild.id))
        
        if not channel_id:
            return

        channel = member.guild.get_channel(channel_id)
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

    # --- COMANDOS DE LOGS ---
    
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