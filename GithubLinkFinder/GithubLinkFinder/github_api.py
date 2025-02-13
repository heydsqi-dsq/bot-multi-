import os
import aiohttp
from typing import List, Dict

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_API_URL = "https://api.github.com/search/repositories"

async def search_github_repos(query: str, max_results: int = 5) -> List[Dict]:
    """
    Recherche des dépôts GitHub via l'API
    
    Args:
        query (str): Terme de recherche
        max_results (int): Nombre maximum de résultats à retourner
    
    Returns:
        List[Dict]: Liste des dépôts trouvés
    """
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'

    params = {
        'q': query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': max_results
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GITHUB_API_URL, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['items'][:max_results]
                elif response.status == 403:
                    raise Exception("Limite de requêtes GitHub atteinte. Réessayez plus tard.")
                else:
                    raise Exception(f"Erreur API GitHub: {response.status}")
    except aiohttp.ClientError as e:
        raise Exception(f"Erreur de connexion à l'API GitHub: {str(e)}")
    except Exception as e:
        raise Exception(f"Erreur inattendue: {str(e)}")
