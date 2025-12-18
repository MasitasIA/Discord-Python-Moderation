import discord
from discord.ext import commands
import sys

sys.path.append("..") 
from utils import update_config, get_config

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- EVENTO: ASIGNAR AUTO-ROL ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await get_config(member.guild.id)

        if member.bot:
            # Lógica para Bots
            role_id = config['autorole_bot']
            if role_id:
                role = member.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role)
                    except discord.Forbidden:
                        print(f"Faltan permisos para dar rol de bot en {member.guild.name}")
        else:
            # Lógica para Humanos
            role_id = config['autorole_human']
            if role_id:
                role = member.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role)
                    except discord.Forbidden:
                        print(f"Faltan permisos para dar autorol en {member.guild.name}")

    # --- COMANDOS DE CONFIGURACIÓN ---

    # Comando para ver la ayuda de configuración
    @commands.hybrid_command(name="confighelp", description="Muestra los comandos de configuración disponibles.")
    async def confighelp(self, ctx):
        embed = discord.Embed(
            title="⚙️ Comandos de Configuración",
            description="Lista de comandos para configurar el bot.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Prefijo", value=(
            "`/setprefix [nuevo_prefijo]` - Cambia el prefijo del bot."
        ), inline=False)
        
        embed.add_field(name="Auto-Rol", value=(
            "`/setautorole [rol]` - Establece el rol automático para humanos.\n"
            "`/disableautorole` - Desactiva el auto-rol para humanos.\n"
            "`/setbotrole [rol]` - Establece el rol automático para bots.\n"
            "`/disablebotrole` - Desactiva el auto-rol para bots.\n"
            "`/viewautorole` - Muestra los roles de auto-rol configurados."
        ), inline=False)
        
        await ctx.send(embed=embed)

    # Comando para cambiar el prefijo del bot
    @commands.hybrid_command(name="setprefix", description="Cambia el prefijo del bot.")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix: str):
        await update_config(ctx.guild.id, "prefix", new_prefix)
        
        embed = discord.Embed(title="Prefijo Actualizado", description=f"✅ Nuevo prefijo: `{new_prefix}`", color=0x4D8BD3)
        await ctx.send(embed=embed)

    # Comando para establecer el rol automático para humanos
    @commands.hybrid_command(name="setautorole", description="Establece el rol automático para humanos.")
    @commands.has_permissions(administrator=True)
    async def setautorole(self, ctx, role: discord.Role):
        await update_config(ctx.guild.id, "autorole_human", role.id)
        
        await ctx.send(f"✅ Auto-rol configurado: {role.mention}")

    # Comando para desactivar el rol automático para humanos
    @commands.hybrid_command(name="disableautorole", description="Desactiva el auto-rol.")
    @commands.has_permissions(administrator=True)
    async def disableautorole(self, ctx):
        await update_config(ctx.guild.id, "autorole_human", None)
        await ctx.send("✅ Auto-rol desactivado.")

    # Comando para desactivar el auto-rol para bots
    @commands.hybrid_command(name="disablebotrole", description="Desactiva el auto-rol para bots en este servidor.")
    @commands.has_permissions(administrator=True)
    async def disablebotrole(self, ctx):
        await update_config(ctx.guild.id, "autorole_bot", None)

        embed = discord.Embed(
            title="Auto-Rol Para Bots Desactivado",
            description="✅ Auto-rol para bots desactivado correctamente.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    # Comando para establecer el rol automático para bots
    @commands.hybrid_command(name="setbotrole", description="Establece el rol automático para bots.")
    @commands.has_permissions(administrator=True)
    async def setbotrole(self, ctx, role: discord.Role):
        await update_config(ctx.guild.id, "autorole_bot", role.id)
        
        await ctx.send(f"✅ Auto-rol de bots configurado: {role.mention}")

    # Comando para ver los autoroles configurados
    @commands.hybrid_command(name="viewautorole", description="Muestra los roles de auto-rol configurados en este servidor.")
    @commands.has_permissions(administrator=True)
    async def viewautorole(self, ctx):
        config = await get_config(ctx.guild.id)
        
        human_role_id = config['autorole_human']
        bot_role_id = config['autorole_bot']

        human_role = ctx.guild.get_role(human_role_id) if human_role_id else None
        bot_role = ctx.guild.get_role(bot_role_id) if bot_role_id else None

        embed = discord.Embed(
            title="Roles de Auto-Rol Configurados",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Rol para Humanos",
            value=human_role.mention if human_role else "No configurado",
            inline=False
        )
        embed.add_field(
            name="Rol para Bots",
            value=bot_role.mention if bot_role else "No configurado",
            inline=False
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Config(bot))