"""
Generic SPARQL client for Wikidata queries
Handles HTTP requests to Wikidata SPARQL endpoint and response parsing
"""

import httpx
from typing import Dict, List, Any


WIKIDATA_SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"


async def execute_sparql(query: str) -> Dict[str, Any]:
    """
    Execute a SPARQL query against Wikidata
    
    Args:
        query: SPARQL query string
        
    Returns:
        Parsed JSON response from Wikidata
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            WIKIDATA_SPARQL_ENDPOINT,
            data={"query": query},
            headers={"Accept": "application/json"}
        )
        response.raise_for_status()
        return response.json()


def parse_sparql_results(response: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Parse SPARQL JSON response into simple list of dicts
    
    Args:
        response: Raw JSON from Wikidata SPARQL endpoint
        
    Returns:
        List of result dictionaries with variable names as keys
    """
    bindings = response.get("results", {}).get("bindings", [])
    
    results = []
    for binding in bindings:
        result = {}
        for var, data in binding.items():
            result[var] = data.get("value", "")
        results.append(result)
    
    return results


if __name__ == "__main__":
    import asyncio
    
    # Test query: Get Niels Bohr's birthday
    test_query = """
    SELECT ?birthday WHERE {
      wd:Q7085 wdt:P569 ?birthday .
    }
    """
    
    async def test():
        response = await execute_sparql(test_query)
        results = parse_sparql_results(response)
        print(f"Results: {results}")
    
    asyncio.run(test())