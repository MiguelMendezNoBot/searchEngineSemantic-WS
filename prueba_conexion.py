from SPARQLWrapper import SPARQLWrapper, JSON

# 1. Configurar la conexión
sparql = SPARQLWrapper("https://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

# 2. Una consulta muy simple y específica (sin filtros pesados)
print("📡 Conectando con DBpedia...")
query = """
    SELECT ?abstract ?thumbnail
    WHERE {
        <http://dbpedia.org/resource/Ethereum> rdfs:comment ?abstract .
        OPTIONAL { <http://dbpedia.org/resource/Ethereum> dbo:thumbnail ?thumbnail }
        FILTER (lang(?abstract) = 'en')
    }
    LIMIT 1
"""

sparql.setQuery(query)

try:
    # 3. Intentar bajar los datos
    results = sparql.query().convert()
    print("✅ ¡ÉXITO! Se encontró respuesta:")
    for result in results["results"]["bindings"]:
        print("Descripción encontrada:", result["abstract"]["value"][:50], "...")
        if "thumbnail" in result:
            print("Imagen encontrada:", result["thumbnail"]["value"])
        else:
            print("Sin imagen, pero con datos.")
            
except Exception as e:
    print("❌ ERROR DE CONEXIÓN:")
    print(e)