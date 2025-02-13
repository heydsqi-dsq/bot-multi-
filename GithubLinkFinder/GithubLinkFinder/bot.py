import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from github_api import search_github_repos
from utils import format_repo_message
from keep_alive import keep_alive
from monitoring import add_log, command_usage

# Charger les variables d'environnement
load_dotenv()

# Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MAX_RESULTS = int(os.getenv('MAX_RESULTS', '5'))

# Initialiser le bot avec le préfixe '+'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='+', intents=intents)

@bot.event
async def on_ready():
    """Événement déclenché quand le bot est prêt"""
    add_log(f'{bot.user} est connecté et prêt!')
    try:
        await bot.change_presence(
            activity=discord.Streaming(
                name="GitHub Search",
                url="https://www.twitch.tv/github"
            )
        )
        synced = await bot.tree.sync()
        add_log(f"Synced {len(synced)} command(s)")
    except Exception as e:
        add_log(f"Erreur lors de la synchronisation des commandes: {e}")

@bot.event
async def on_command(ctx):
    """Enregistre l'utilisation des commandes"""
    command_name = ctx.command.name
    command_usage[command_name] = command_usage.get(command_name, 0) + 1
    add_log(f"Commande '{command_name}' utilisée par {ctx.author}")

@bot.command(name='helpme')
async def help_command(ctx):
    """Affiche la liste des commandes de recherche"""
    embed = discord.Embed(
        title="📚 Liste des Commandes",
        description="Voici les commandes de recherche disponibles :",
        color=0x8B0000  # Rouge foncé
    )

    embed.add_field(
        name="+give <mot clé>",
        value="Recherche des dépôts GitHub correspondant au mot clé.\n"
              "Exemple: `+give python bot`",
        inline=False
    )

    embed.add_field(
        name="+helpme",
        value="Affiche ce message d'aide avec la liste des commandes de recherche.",
        inline=False
    )

    embed.add_field(
        name="+config",
        value="Affiche la liste des commandes de configuration du bot.",
        inline=False
    )

    embed.set_footer(text="Bot GitHub Search")
    await ctx.send(embed=embed)

@bot.command(name='config')
async def config_help(ctx):
    """Affiche la liste des commandes de configuration"""
    embed = discord.Embed(
        title="⚙️ Configuration du Bot",
        description="Voici les commandes de configuration disponibles :",
        color=0x8B0000  # Rouge foncé
    )

    embed.add_field(
        name="+setname <nouveau_nom>",
        value="Change le nom d'affichage du bot.\n"
              "Exemple: `+setname MonBot`",
        inline=False
    )

    embed.add_field(
        name="+setstatus <status>",
        value="Change le statut du bot en stream.\n"
              "Exemple: `+setstatus recherche de repos`",
        inline=False
    )

    embed.add_field(
        name="+setprefix <nouveau_prefix>",
        value="Change le préfixe des commandes.\n"
              "Exemple: `+setprefix !`",
        inline=False
    )

    embed.set_footer(text="Bot GitHub Search - Configuration")
    await ctx.send(embed=embed)

@bot.command(name='setname')
async def set_name(ctx, *, new_name: str = None):
    """Change le nom du bot"""
    if not new_name:
        await ctx.send("❌ Veuillez fournir un nouveau nom. Exemple: `+setname MonBot`")
        return

    try:
        await bot.user.edit(username=new_name)
        await ctx.send(f"✅ Le nom du bot a été changé en '{new_name}'")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Impossible de changer le nom: {str(e)}")

@bot.command(name='setstatus')
async def set_status(ctx, *, status: str = None):
    """Change le statut du bot"""
    if not status:
        await ctx.send("❌ Veuillez fournir un statut. Exemple: `+setstatus recherche de repos`")
        return

    try:
        # Utiliser Streaming avec une URL Twitch
        await bot.change_presence(
            activity=discord.Streaming(
                name=status,
                url="https://www.twitch.tv/github"  # URL Twitch valide requise pour l'icône de stream
            )
        )
        await ctx.send(f"✅ Le statut a été changé en 'En stream : {status}'")
    except Exception as e:
        await ctx.send(f"❌ Impossible de changer le statut: {str(e)}")

@bot.command(name='setprefix')
async def set_prefix(ctx, new_prefix: str = None):
    """Change le préfixe des commandes"""
    if not new_prefix:
        await ctx.send("❌ Veuillez fournir un nouveau préfixe. Exemple: `+setprefix !`")
        return

    try:
        bot.command_prefix = new_prefix
        await ctx.send(f"✅ Le préfixe des commandes a été changé en '{new_prefix}'")
    except Exception as e:
        await ctx.send(f"❌ Impossible de changer le préfixe: {str(e)}")

@bot.command(name='give')
async def give(ctx, *, query: str = None):
    """
    Commande pour rechercher des dépôts GitHub
    Usage: +give <mot clé>
    """
    if not query:
        await ctx.send("❌ Veuillez fournir un terme de recherche. Exemple: `+give python bot`")
        return

    # Message de chargement
    loading_message = await ctx.send("🔍 Recherche en cours...")

    try:
        # Recherche des repos
        repos = await search_github_repos(query, max_results=MAX_RESULTS)

        if not repos:
            await loading_message.edit(content="❌ Aucun résultat trouvé pour votre recherche.")
            return

        # Formater et envoyer les résultats en MP
        response = format_repo_message(repos, query)
        try:
            await ctx.author.send(response)
            await loading_message.edit(content="✅ Les résultats ont été envoyés dans vos messages privés!")
        except discord.Forbidden:
            await loading_message.edit(content="❌ Je ne peux pas vous envoyer de message privé. Veuillez activer les messages privés pour ce serveur.")

    except Exception as e:
        await loading_message.edit(content=f"❌ Une erreur est survenue: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    """Gestion globale des erreurs"""
    error_message = f"Erreur pour la commande '{ctx.command}' : {str(error)}"
    add_log(error_message)

    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Commande inconnue. Utilisez `+helpme` pour voir la liste des commandes disponibles.")
    else:
        await ctx.send(f"❌ Une erreur est survenue: {str(error)}")

# Lancer le bot
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Erreur: Le token Discord n'est pas configuré dans le fichier .env")
        exit(1)

    keep_alive()  # Démarrer le serveur web
    bot.run(DISCORD_TOKEN)