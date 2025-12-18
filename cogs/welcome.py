import discord
from discord.ext import commands
import sys

# Importamos las funciones desde la carpeta anterior
sys.path.append("..") 
from utils import load_json, save_json

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- EVENTOS ---

    # Evento de bienvenida
    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcomemessages = load_json("welcomemessages.json")
        welcomelogchannels = load_json("welcomelogchannels.json")
        channel_id = welcomelogchannels.get(str(member.guild.id))

        raw_message = welcomemessages.get(str(member.guild.id), "¡Bienvenido al servidor, {mencion}!")
        welcome_message = raw_message.replace("{usuario}", member.name) \
                                     .replace("{mencion}", member.mention) \
                                     .replace("{servidor}", member.guild.name) \
                                     .replace("{id}", str(member.id))

        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="Bienvenido al Servidor",
                    description=welcome_message,
                    color=discord.Color.green()
                )
                if member.avatar:
                    embed.set_thumbnail(url=member.avatar.url)
                await channel.send(embed=embed)

    # Evento de despedida
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        farewellmessages = load_json("farewellmessages.json")
        welcomelogchannels = load_json("welcomelogchannels.json")
        channel_id = welcomelogchannels.get(str(member.guild.id))

        raw_message = farewellmessages.get(str(member.guild.id), "¡{usuario} se ha ido del servidor!")
        farewell_message = raw_message.replace("{usuario}", member.name) \
                                      .replace("{mencion}", member.mention) \
                                      .replace("{servidor}", member.guild.name) \
                                      .replace("{id}", str(member.id))

        if channel_id:
            channel = member.guild.get_channel(channel_id)
            if channel:
                await channel.send(farewell_message)

    # --- COMANDOS ---
    
    # Comando para ver la ayuda de Bienvenida/Despedida
    @commands.hybrid_command(name="welcomehelp", description="Muestra la ayuda del sistema de bienvenida y despedida.")
    async def welcomehelp(self, ctx):
        embed = discord.Embed(
            title="Ayuda del Sistema de Bienvenida y Despedida",
            description="Estos son los comandos disponibles para configurar los mensajes y canales de bienvenida y despedida:",
            color=discord.Color.blue()
        )
        embed.add_field(name="• `/setwelcomelogchannel <canal>`", value="Establece el canal donde se enviarán los mensajes de bienvenida y despedida.", inline=False)
        embed.add_field(name="• `/disablewelcomelogchannel`", value="Desactiva el canal de bienvenida y despedida.", inline=False)
        embed.add_field(name="• `/viewwelcomelogchannel`", value="Muestra el canal de bienvenida y despedida configurado.", inline=False)
        embed.add_field(name="• `/setwelcomemessage <mensaje>`", value="Establece el mensaje de bienvenida para nuevos miembros.", inline=False)
        embed.add_field(name="• `/setfarewellmessage <mensaje>`", value="Establece el mensaje de despedida para miembros que se van.", inline=False)
        embed.add_field(name="Variables Disponibles", value="Puedes usar las siguientes variables en tus mensajes:\n"
                                                          "• `{mencion}` → @Usuario\n"
                                                          "• `{usuario}` → NombreDelUsuario\n"
                                                          "• `{servidor}` → Nombre del Servidor\n"
                                                          "• `{id}` → ID del Usuario", inline=False)
        await ctx.send(embed=embed)

    # Comando para establecer el canal de Bienvenida/Despedida
    @commands.hybrid_command(name="setwelcomelogchannel", description="Establece el canal de bienvenida y despedida del servidor.")
    @commands.has_permissions(administrator=True)
    async def setwelcomelogchannel(self, ctx, channel: discord.TextChannel):
        welcomelogchannels = load_json("welcomelogchannels.json")
        welcomelogchannels[str(ctx.guild.id)] = channel.id
        save_json("welcomelogchannels.json", welcomelogchannels)
        
        embed = discord.Embed(
            title="Canal de Bienvenida/Despedida Establecido",
            description=f"✅ Canal de bienvenida y despedida establecido a {channel.mention}.",
            color=discord.Color.blue()
        )
        
        await ctx.send(embed=embed)

    # Comando para desactivar el canal de Bienvenida/Despedida
    @commands.hybrid_command(name="disablewelcomelogchannel", description="Desactiva el canal de bienvenida y despedida del servidor.")
    @commands.has_permissions(administrator=True)
    async def disablewelcomelogchannel(self,ctx):
        welcomelogchannels = load_json("welcomelogchannels.json")
        if str(ctx.guild.id) in welcomelogchannels:
            welcomelogchannels.pop(str(ctx.guild.id))
            save_json("welcomelogchannels.json", welcomelogchannels)
            
            embed = discord.Embed(
                title="Canal de Bienvenida/Despedida Desactivado",
                description="✅ Canal de bienvenida y despedida desactivado correctamente.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando para ver el canal de Bienvenida/Despedida configurado
    @commands.hybrid_command(name="viewwelcomelogchannel", description="Muestra el canal de bienvenida y despedida configurado en este servidor.")
    @commands.has_permissions(administrator=True)
    async def viewwelcomelogchannel(self, ctx):
        welcomelogchannels = load_json("welcomelogchannels.json")
        channel_id = welcomelogchannels.get(str(ctx.guild.id))
        if channel_id:
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="Canal de Bienvenida/Despedida Configurado",
                    description=f"✅ Canal actual: {channel.mention}",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="Canal de Bienvenida/Despedida No Encontrado",
                    description="⚠️ El canal configurado ya no existe.",
                    color=discord.Color.orange()
                )
        else:
            embed = discord.Embed(
                title="Canal de Bienvenida/Despedida No Configurado",
                description="⚠️ No hay ningún canal de bienvenida y despedida configurado.",
                color=discord.Color.orange()
            )

        await ctx.send(embed=embed)

    # Comando para establecer el mensaje de bienvenida
    @commands.hybrid_command(name="setwelcomemessage", description="Establece el mensaje de bienvenida para nuevos miembros.")
    @commands.has_permissions(administrator=True)
    async def setwelcomemessage(self, ctx, *, message: str):
        welcomemessages = load_json("welcomemessages.json")
        welcomemessages[str(ctx.guild.id)] = message
        save_json("welcomemessages.json", welcomemessages)

        embed = discord.Embed(
            title="Mensaje de Bienvenida Establecido",
            description="✅ Has configurado el nuevo mensaje de bienvenida.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Mensaje Configurado:", value=message, inline=False)
        
        # Le explicamos al usuario cómo funciona
        embed.add_field(
            name="Variables disponibles:", 
            value="Puedes usar estas palabras y se cambiarán automáticamente:\n"
                "• `{mencion}` → @Usuario\n"
                "• `{usuario}` → NombreDelUsuario\n"
                "• `{servidor}` → Nombre del Servidor\n"
                "• `{id}` → ID del Usuario",
            inline=False
        )
        # Ejemplo de cómo se verá
        preview = message.replace("{usuario}", ctx.author.name)\
                        .replace("{mencion}", ctx.author.mention)\
                        .replace("{servidor}", ctx.guild.name)\
                        .replace("{id}", str(ctx.author.id))
                        
        embed.add_field(name="Vista Previa (Ejemplo):", value=preview, inline=False)

        await ctx.send(embed=embed)

    # Comando para establecer el mensaje de despedida
    @commands.hybrid_command(name="setfarewellmessage", description="Establece el mensaje de despedida para miembros que se van.")
    @commands.has_permissions(administrator=True)
    async def setfarewellmessage(self, ctx, *, message: str):
        farewellmessages = load_json("farewellmessages.json")
        farewellmessages[str(ctx.guild.id)] = message
        save_json("farewellmessages.json", farewellmessages)

        embed = discord.Embed(
            title="Mensaje de Despedida Establecido",
            description="✅ Has configurado el nuevo mensaje de despedida.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Mensaje Configurado:", value=message, inline=False)
        
            # Le explicamos al usuario cómo funciona
        embed.add_field(
            name="Variables disponibles:", 
            value="Puedes usar estas palabras y se cambiarán automáticamente:\n"
                "• `{mencion}` → @Usuario\n"
                "• `{usuario}` → NombreDelUsuario\n"
                "• `{servidor}` → Nombre del Servidor\n"
                "• `{id}` → ID del Usuario",
            inline=False
        )
        # Ejemplo de cómo se verá
        preview = message.replace("{usuario}", ctx.author.name)\
                        .replace("{mencion}", ctx.author.mention)\
                        .replace("{servidor}", ctx.guild.name)\
                        .replace("{id}", str(ctx.author.id))
                        
        embed.add_field(name="Vista Previa (Ejemplo):", value=preview, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))