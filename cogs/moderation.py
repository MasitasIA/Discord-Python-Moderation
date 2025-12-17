import discord
from discord.ext import commands
import sys
from datetime import timedelta

sys.path.append("..") 

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- COMANDOS DE MODERACIÓN ---

    # Comando para expulsar a un miembro
    @commands.hybrid_command(name="kick", description="Expulsa a un miembro.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "Razón no especificada"):
        if member == ctx.author: 
            return await ctx.send("No puedes expulsarte a ti mismo.")
        try:
            await member.kick(reason=reason)
            await ctx.send(embed=discord.Embed(title="Usuario Expulsado", description=f"👢 **{member.name}** expulsado.", color=discord.Color.orange()))
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes.")

    # Comando para banear a un miembro
    @commands.hybrid_command(name="ban", description="Banea a un miembro.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "Razón no especificada"):
        if member == ctx.author: 
            return await ctx.send("No puedes banearte a ti mismo.")
        try:
            await member.ban(reason=reason)
            await ctx.send(embed=discord.Embed(title="Usuario Baneado", description=f"🔨 **{member.name}** baneado.", color=discord.Color.red()))
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos suficientes.")

    # Comando para desbanear a un usuario por nombre o ID
    @commands.hybrid_command(name="unban", description="Desbanea a un usuario por nombre o ID.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, user_input: str):
        banned_users = [entry async for entry in ctx.guild.bans()]
        found_entry = None
        if user_input.isdigit():
            for entry in banned_users:
                if entry.user.id == int(user_input):
                    found_entry = entry
                    break
        if not found_entry:
            for entry in banned_users:
                if entry.user.name == user_input:
                    found_entry = entry
                    break
        if found_entry:
            await ctx.guild.unban(found_entry.user)
            await ctx.send(embed=discord.Embed(title="Usuario Desbaneado", description=f"✅ **{found_entry.user.name}** desbaneado.", color=discord.Color.green()))
        else:
            await ctx.send(f"❌ No encontré a nadie baneado con: `{user_input}`.")

    # Comando para aislar a un usuario (timeout)
    @commands.hybrid_command(name="timeout", description="Aísla a un usuario.")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason: str = "Sin razón"):
        if member.top_role >= ctx.author.top_role: 
            return await ctx.send("❌ Rol insuficiente.")
        try:
            await member.timeout(timedelta(minutes=minutes), reason=reason)
            await ctx.send(embed=discord.Embed(title="Usuario Aislado", description=f"🤐 **{member.name}** muteado {minutes} min.", color=discord.Color.yellow()))
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos.")

    # Comando para borrar mensajes
    @commands.hybrid_command(name="clear", description="Borra mensajes.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1: 
            deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 **{len(deleted)-1}** mensajes borrados.", delete_after=5)

async def setup(bot):
    await bot.add_cog(Moderation(bot))