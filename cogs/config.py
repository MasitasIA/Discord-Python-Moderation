import discord
from discord.ext import commands
import sys

sys.path.append("..") 
from utils import load_json, save_json

class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- EVENTO: ASIGNAR AUTO-ROL ---
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            # Lógica para Bots
            botroles = load_json("botroles.json")
            role_id = botroles.get(str(member.guild.id))
            if role_id:
                role = member.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role)
                    except discord.Forbidden:
                        print(f"Faltan permisos para dar rol de bot en {member.guild.name}")
        else:
            # Lógica para Humanos
            autoroles = load_json("autoroles.json")
            role_id = autoroles.get(str(member.guild.id))
            if role_id:
                role = member.guild.get_role(role_id)
                if role:
                    try:
                        await member.add_roles(role)
                    except discord.Forbidden:
                        print(f"Faltan permisos para dar autorol en {member.guild.name}")

    # --- COMANDOS DE CONFIGURACIÓN ---

    # Circuito para cambiar el prefijo del bot
    @commands.hybrid_command(name="setprefix", description="Cambia el prefijo del bot.")
    @commands.has_permissions(administrator=True)
    async def setprefix(self, ctx, new_prefix: str):
        prefixes = load_json("prefixes.json")
        prefixes[str(ctx.guild.id)] = new_prefix
        save_json("prefixes.json", prefixes)
        
        embed = discord.Embed(title="Prefijo Actualizado", description=f"✅ Nuevo prefijo: `{new_prefix}`", color=0x4D8BD3)
        await ctx.send(embed=embed)

    # Comando para establecer el rol automático para humanos
    @commands.hybrid_command(name="setautorole", description="Establece el rol automático para humanos.")
    @commands.has_permissions(administrator=True)
    async def setautorole(self, ctx, role: discord.Role):
        autoroles = load_json("autoroles.json")
        autoroles[str(ctx.guild.id)] = role.id
        save_json("autoroles.json", autoroles)
        
        await ctx.send(f"✅ Auto-rol configurado: {role.mention}")

    #  Comando para desactivar el rol automático para humanos
    @commands.hybrid_command(name="disableautorole", description="Desactiva el auto-rol.")
    @commands.has_permissions(administrator=True)
    async def disableautorole(self, ctx):
        autoroles = load_json("autoroles.json")
        if str(ctx.guild.id) in autoroles:
            autoroles.pop(str(ctx.guild.id))
            save_json("autoroles.json", autoroles)
            await ctx.send("✅ Auto-rol desactivado.")
        else:
            await ctx.send("⚠️ No había auto-rol configurado.")

# Comando para desactivar el auto-rol para bots
    @commands.hybrid_command(name="disablebotrole", description="Desactiva el auto-rol para bots en este servidor.")
    @commands.has_permissions(administrator=True)
    async def disablebotrole(self, ctx):
        botroles = load_json("botroles.json")

        if str(ctx.guild.id) in botroles:
            botroles.pop(str(ctx.guild.id))
            save_json("botroles.json", botroles)

            embed = discord.Embed(
                title="Auto-Rol Para Bots Desactivado",
                description="✅ Auto-rol para bots desactivado correctamente.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Auto-Rol Para Bots No Configurado",
                description="⚠️ No había ningún auto-rol para bots configurado.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)

    # Comando para establecer el rol automático para bots
    @commands.hybrid_command(name="setbotrole", description="Establece el rol automático para bots.")
    @commands.has_permissions(administrator=True)
    async def setbotrole(self, ctx, role: discord.Role):
        botroles = load_json("botroles.json")
        botroles[str(ctx.guild.id)] = role.id
        save_json("botroles.json", botroles)
        
        await ctx.send(f"✅ Auto-rol de bots configurado: {role.mention}")

    # Comando para ver los autoroles configurados
    @commands.hybrid_command(name="viewautorole", description="Muestra los roles de auto-rol configurados en este servidor.")
    @commands.has_permissions(administrator=True)
    async def viewautorole(self, ctx):
        autoroles = load_json("autoroles.json")
        botroles = load_json("botroles.json")
        human_role_id = autoroles.get(str(ctx.guild.id))
        bot_role_id = botroles.get(str(ctx.guild.id))

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