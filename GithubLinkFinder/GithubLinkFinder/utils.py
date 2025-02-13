from typing import List, Dict

def format_repo_message(repos: List[Dict], query: str) -> str:
    """
    Formate les résultats de recherche pour l'affichage Discord
    
    Args:
        repos (List[Dict]): Liste des dépôts
        query (str): Terme de recherche original
    
    Returns:
        str: Message formaté pour Discord
    """
    message = [f"🔍 Résultats de recherche pour '{query}':"]
    
    for i, repo in enumerate(repos, 1):
        stars = repo.get('stargazers_count', 0)
        description = repo.get('description', 'Pas de description')
        if len(description) > 100:
            description = description[:97] + "..."

        message.append(
            f"\n{i}. **{repo['full_name']}**"
            f"\n⭐ {stars:,} stars"
            f"\n📝 {description}"
            f"\n🔗 {repo['html_url']}\n"
        )

    return '\n'.join(message)
