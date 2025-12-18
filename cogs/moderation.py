import discord
from discord.ext import commands
import sys
from datetime import timedelta

sys.path.append("..") 

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- COMANDOS DE MODERACIÓN ---

    # Comando para ver los comandos de moderación
    @commands.hybrid_command(name="modhelp", description="Muestra los comandos de moderación disponibles.")
    async def modhelp(self, ctx):
        embed = discord.Embed(
            title="🛡️ Comandos de Moderación",
            description="Lista de herramientas disponibles para moderadores.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Usuarios", value=(
            "`/kick [user] [razón]` - Expulsa a un miembro.\n"
            "`/ban [user] [razón]` - Banea a un miembro.\n"
            "`/unban [id]` - Desbanea a un usuario.\n"
            "`/timeout [user] [min] [razón]` - Aísla a un usuario.\n"
            "`/untimeout [user]` - Quita el aislamiento.\n"
            "`/nick [user] [nombre]` - Cambia el apodo (o resetea).\n"
            "`/userinfo [user]` - Ver datos de la cuenta."
        ), inline=False)
        
        embed.add_field(name="Chat y Canales", value=(
            "`/clear [cantidad]` - Borra mensajes.\n"
            "`/lock` - Bloquea el canal actual.\n"
            "`/unlock` - Desbloquea el canal actual.\n"
            "`/slowmode [segundos]` - Pone modo lento."
        ), inline=False)
        
        await ctx.send(embed=embed)

    # --- COMANDOS SOBRE USUARIOS ---

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

    # Comando para quitar el aislamiento (untimeout)
    @commands.hybrid_command(name="untimeout", description="Quita el aislamiento a un usuario.")
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: discord.Member):
        try:
            await member.timeout(None)
            await ctx.send(embed=discord.Embed(title="Aislamiento Quitado", description=f"✅ **{member.name}** ya no está aislado.", color=discord.Color.green()))
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos.")

    # Comando para cambiar el apodo de un usuario
    @commands.hybrid_command(name="nick", description="Cambia el apodo de un usuario. Deja vacío para resetear.")
    @commands.has_permissions(manage_nicknames=True)
    async def nick(self, ctx, member: discord.Member, *, name: str = None):
        if member.top_role >= ctx.author.top_role: 
            return await ctx.send("❌ Rol insuficiente.")
        try:
            await member.edit(nick=name)
            msg = f"✅ Apodo cambiado a **{name}**" if name else "✅ Apodo reseteado al original."
            embed = discord.Embed(
                title="Apodo Actualizado", 
                description=msg, 
                color=discord.Color.green())
            
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos.")

    # Comando para ver información de un usuario
    @commands.hybrid_command(name="userinfo", description="Muestra información detallada de un usuario.")
    @commands.has_permissions(manage_messages=True)
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        
        embed = discord.Embed(title=f"Información de {member.name}", color=member.color)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="🆔 ID", value=member.id, inline=True)
        embed.add_field(name="📅 Cuenta Creada", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="📥 Se unió al servidor", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name=f"🎭 Roles ({len(roles)})", value=" ".join(roles) if roles else "Ninguno", inline=False)
        
        await ctx.send(embed=embed)

    # --- COMANDOS DE CHAT Y CANALES ---

    # Comando para borrar mensajes
    @commands.hybrid_command(name="clear", description="Borra mensajes.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1: 
             await ctx.send("Debes borrar al menos 1 mensaje.")
             return
        
        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 **{len(deleted)-1}** mensajes borrados.", delete_after=5)

    # Comando para bloquear un canal
    @commands.hybrid_command(name="lock", description="Bloquea el canal para que nadie pueda escribir.")
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=discord.Embed(title="🔒 Canal Bloqueado", description="Nadie puede escribir hasta nuevo aviso.", color=discord.Color.red()))

    # Comando para desbloquear un canal
    @commands.hybrid_command(name="unlock", description="Desbloquea el canal para que todos puedan escribir.")
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(embed=discord.Embed(title="🔓 Canal Desbloqueado", description="Todos pueden escribir de nuevo.", color=discord.Color.green()))

    # Comando para poner modo lento en un canal
    @commands.hybrid_command(name="slowmode", description="Establece el modo lento del chat (en segundos).")
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, seconds: int):
        await ctx.channel.edit(slowmode_delay=seconds)
        if seconds > 0:
            await ctx.send(f"🐢 Modo lento activado: **{seconds} segundos**.")
        else:
            await ctx.send("🐇 Modo lento desactivado.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))