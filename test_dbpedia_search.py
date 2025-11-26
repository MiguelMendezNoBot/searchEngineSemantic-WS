#!/usr/bin/env python3
"""
Test script to verify DBpedia search functionality works without timeouts.
This script tests the SPARQL queries used in the semantic search engine.
"""

import time
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed, EndPointInternalError

def test_dbpedia_search(termino, limite=5, timeout_seconds=60):
    """
    Test DBpedia search functionality with timeout verification.

    Args:
        termino (str): Search term
        limite (int): Maximum number of results
        timeout_seconds (int): Timeout in seconds

    Returns:
        tuple: (success, results, error_message, elapsed_time)
    """
    start_time = time.time()

    try:
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        sparql.setReturnFormat(JSON)

        # Simplified query with REGEX on rdfs:label for better performance
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?entity ?label ?comment
        WHERE {{
            ?entity rdfs:label ?label .
            OPTIONAL {{ ?entity rdfs:comment ?comment . FILTER(LANG(?comment) = "en") }}
            FILTER(LANG(?label) = "en")
            FILTER(REGEX(?label, "{termino}", "i"))
        }}
        ORDER BY ?label
        LIMIT {limite}
        """

        sparql.setQuery(query)
        results = sparql.query().convert()

        entidades = []
        for result in results["results"]["bindings"]:
            comment_value = result.get('comment', {}).get('value', 'No description available')
            entidad = {
                'uri': result['entity']['value'],
                'label': result['label']['value'],
                'comment': comment_value[:300] + "..." if len(comment_value) > 300 else comment_value,
            }
            entidades.append(entidad)

        elapsed_time = time.time() - start_time
        return True, entidades, None, elapsed_time

    except EndPointInternalError as e:
        elapsed_time = time.time() - start_time
        if "timeout" in str(e).lower() or "time" in str(e).lower():
            return False, [], f"Timeout error: {str(e)}", elapsed_time
        else:
            return False, [], f"Endpoint error: {str(e)}", elapsed_time

    except QueryBadFormed as e:
        elapsed_time = time.time() - start_time
        return False, [], f"Query malformed: {str(e)}", elapsed_time

    except Exception as e:
        elapsed_time = time.time() - start_time
        return False, [], f"Unexpected error: {str(e)}", elapsed_time

def run_tests():
    """Run comprehensive tests for DBpedia search functionality."""
    print("Testing DBpedia Search Functionality")
    print("=" * 50)

    # Test terms related to cryptocurrencies
    test_terms = [
        "bitcoin",
        "ethereum",
        "cryptocurrency",
        "blockchain",
        "exchange"
    ]

    all_passed = True
    total_tests = len(test_terms)

    for i, term in enumerate(test_terms, 1):
        print(f"\nTest {i}/{total_tests}: Searching for '{term}'")
        print("-" * 30)

        success, results, error, elapsed_time = test_dbpedia_search(term, limite=3)

        if success:
            print(f"SUCCESS: Found {len(results)} results in {elapsed_time:.2f} seconds")
            if results:
                print("   Sample results:")
                for j, entidad in enumerate(results[:2], 1):  # Show first 2 results
                    print(f"   {j}. {entidad['label']} - {entidad['comment'][:100]}...")
        else:
            print(f"FAILED: {error}")
            print(f"   Time elapsed: {elapsed_time:.2f} seconds")
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("ALL TESTS PASSED: DBpedia search works without timeouts!")
    else:
        print("SOME TESTS FAILED: Check for timeout or connectivity issues.")
    print("=" * 50)

    return all_passed

if __name__ == "__main__":
    try:
        success = run_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        exit(1)