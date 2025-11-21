"""
Entity linking: Person name → Wikidata QID
Uses Wikidata Search API for fuzzy matching
"""

import httpx
from typing import Optional


async def find_person_qid(name: str) -> Optional[str]:
    """
    Find Wikidata QID for a person by name using Search API
    
    Args:
        name: Person's name (e.g., "Niels Bohr")
        
    Returns:
        QID string (e.g., "Q7085") or None if not found
    """
    url = "https://www.wikidata.org/w/api.php"
    params = {
        "action": "wbsearchentities",
        "search": name,
        "language": "en",
        "type": "item",
        "limit": 5,
        "format": "json"
    }
    
    headers = {
        "User-Agent": "PersonToWikidata/1.0 (DTU Course Project; Educational Use)"
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
    
    results = data.get("search", [])
    
    if not results:
        return None
    
    for result in results:
        description = result.get("description", "").lower()
        if any(word in description for word in ["politician", "scientist", "physicist", "prime minister", "researcher", "person"]):
            return result["id"]
    
    return results[0]["id"]


if __name__ == "__main__":
    import asyncio
    
    async def test():
        qid = await find_person_qid("Niels Bohr")
        print(f"Niels Bohr QID: {qid}")
        
        qid2 = await find_person_qid("Mette Frederiksen")
        print(f"Mette Frederiksen QID: {qid2}")
        
        qid3 = await find_person_qid("Bohr")
        print(f"Bohr (fuzzy) QID: {qid3}")
    
    asyncio.run(test())