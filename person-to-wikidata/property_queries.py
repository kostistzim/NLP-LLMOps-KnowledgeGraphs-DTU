"""
Wikidata property queries for person data
Birthday, students, political party, doctoral advisor
"""

from typing import List, Dict, Optional
from wikidata_client import execute_sparql, parse_sparql_results


async def get_birthday(qid: str) -> Optional[str]:
    """
    Get person's date of birth
    
    Args:
        qid: Wikidata QID (e.g., "Q7085")
        
    Returns:
        Birthday in YYYY-MM-DD format or None
    """
    query = f"""
    SELECT ?birthday WHERE {{
      wd:{qid} wdt:P569 ?birthday .
    }}
    """
    
    response = await execute_sparql(query)
    results = parse_sparql_results(response)
    
    if not results:
        return None
    
    # Parse date from "1885-10-07T00:00:00Z" to "1885-10-07"
    date_str = results[0].get("birthday", "")
    return date_str.split("T")[0] if date_str else None


async def get_students(qid: str) -> List[Dict[str, str]]:
    """
    Get person's doctoral students
    
    Args:
        qid: Wikidata QID
        
    Returns:
        List of dicts with 'label' and 'qid' keys
    """
    query = f"""
    SELECT ?student ?studentLabel WHERE {{
      wd:{qid} wdt:P185 ?student .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    """
    
    response = await execute_sparql(query)
    results = parse_sparql_results(response)
    
    students = []
    for result in results:
        student_uri = result.get("student", "")
        student_qid = student_uri.split("/")[-1]
        student_label = result.get("studentLabel", "")
        
        students.append({
            "label": student_label,
            "qid": student_qid
        })
    
    return students


async def get_political_party(qid: str) -> Optional[Dict[str, str]]:
    """
    Get person's political party
    
    Args:
        qid: Wikidata QID
        
    Returns:
        Dict with 'label' and 'qid' or None
    """
    query = f"""
    SELECT ?party ?partyLabel WHERE {{
      wd:{qid} wdt:P102 ?party .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 1
    """
    
    response = await execute_sparql(query)
    results = parse_sparql_results(response)
    
    if not results:
        return None
    
    party_uri = results[0].get("party", "")
    party_qid = party_uri.split("/")[-1]
    party_label = results[0].get("partyLabel", "")
    
    return {
        "label": party_label,
        "qid": party_qid
    }


async def get_doctoral_advisor(qid: str) -> Optional[Dict[str, str]]:
    """
    Get person's doctoral advisor
    
    Args:
        qid: Wikidata QID
        
    Returns:
        Dict with 'label' and 'qid' or None
    """
    query = f"""
    SELECT ?advisor ?advisorLabel WHERE {{
      wd:{qid} wdt:P184 ?advisor .
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 1
    """
    
    response = await execute_sparql(query)
    results = parse_sparql_results(response)
    
    if not results:
        return None
    
    advisor_uri = results[0].get("advisor", "")
    advisor_qid = advisor_uri.split("/")[-1]
    advisor_label = results[0].get("advisorLabel", "")
    
    return {
        "label": advisor_label,
        "qid": advisor_qid
    }


if __name__ == "__main__":
    import asyncio
    
    async def test():
        # Test with Niels Bohr (Q7085)
        qid = "Q7085"
        
        birthday = await get_birthday(qid)
        print(f"Birthday: {birthday}")
        
        students = await get_students(qid)
        print(f"Students: {students[:3]}")  # First 3
        
        # Test with Mette Frederiksen (Q5015)
        qid2 = "Q5015"
        party = await get_political_party(qid2)
        print(f"Political party: {party}")
    
    asyncio.run(test())