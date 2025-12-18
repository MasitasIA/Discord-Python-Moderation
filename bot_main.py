import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from utils import init_db, get_config

# --- CONFIGURACIÓN INICIAL ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

async def get_prefix(bot, message):
    if not message.guild:
        return "!"
    config = await get_config(message.guild.id)
    return config['prefix'] or "!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True 

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

# --- SISTEMA DE CARGA DE COGS ---
async def load_extensions():
    """Carga automáticamente todos los archivos .py dentro de la carpeta cogs/"""
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"⚙️  Cog cargado: {filename}")
            except Exception as e:
                print(f"❌ Error cargando {filename}: {e}")

# --- EVENTOS PRINCIPALES ---
@bot.event
async def on_ready():
    print(f'✅ Bot conectado como: {bot.user.name} (ID: {bot.user.id})')
    await init_db()
    await load_extensions()
    
    try:
        synced = await bot.tree.sync()
        print(f"🔄 Se han sincronizado {len(synced)} comandos slash.")
    except Exception as e:
        print(f"❌ Error al sincronizar: {e}")
    
    await bot.change_presence(activity=discord.Game(name="Moderando el servidor"))

@bot.event
async def on_guild_join(guild):
    await get_config(guild.id)
    print(f"Nuevo servidor: {guild.name}")

@bot.event
async def on_guild_remove(guild):
    print(f"El bot ha sido removido del servidor: {guild.name}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("⛔ No tienes permisos.", ephemeral=True)
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Faltan argumentos.", ephemeral=True)
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Error en comando: {error}")

# --- COMANDOS DE ADMINISTRACIÓN DEL BOT ---

# Comando para ver la ayuda del bot
@bot.hybrid_command(name="bothelp", description="Muestra los comandos disponibles del bot.")
async def help(ctx):
    embed = discord.Embed(
        title="🤖 Ayuda del Bot",
        description="Lista de comandos disponibles.",
        color=discord.Color.blue()
    )
    embed.add_field(name="⚙️ Configuración", value="`/confighelp` - Muestra los comandos de configuración.", inline=False)
    embed.add_field(name="🛡️ Moderación", value="`/modhelp` - Muestra los comandos de moderación.", inline=False)
    embed.add_field(name="📜 Logs", value="`/loghelp` - Muestra los comandos de logs.", inline=False)
    embed.add_field(name="👋 Welcome", value="`/welcomehelp` - Muestra los comandos de bienvenida.", inline=False)
    
    await ctx.send(embed=embed)

# --- EJECUCIÓN DEL BOT ---
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ El token de Discord no está configurado.")