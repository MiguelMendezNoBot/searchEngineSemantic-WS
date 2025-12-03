from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from typing import List, Dict, Optional
import streamlit as st

class DBpediaConnector:
    """Conector para consultas a DBpedia (online y offline)"""
    
    def __init__(self):
        self.endpoint_online = "https://dbpedia.org/sparql"
        self.sparql = SPARQLWrapper(self.endpoint_online)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(30)
        self.timeout = 30
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0")
    
    def is_online(self) -> bool:
        """Verifica si hay conexión a DBpedia"""
        try:
            response = requests.get(self.endpoint_online, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def buscar_criptomoneda(self, nombre: str) -> Optional[Dict]:
        """
        Busca información de una criptomoneda en DBpedia
        
        Args:
            nombre: Nombre de la criptomoneda (ej: "Bitcoin", "Ethereum")
        
        Returns:
            Diccionario con información o None si no se encuentra
        """
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT DISTINCT ?resource ?label ?abstract ?thumbnail ?website
        WHERE {{
            ?resource rdfs:label ?label .
            OPTIONAL {{ ?resource dbo:abstract ?abstract . }}
            OPTIONAL {{ ?resource dbo:thumbnail ?thumbnail . }}
            OPTIONAL {{ ?resource foaf:homepage ?website . }}
            
            # Filtrar solo entidades relacionadas con criptomonedas
            {{
                ?resource dct:subject ?subject .
                FILTER(
                    REGEX(STR(?subject), "Cryptocurrencies", "i") ||
                    REGEX(STR(?subject), "Blockchain", "i") ||
                    REGEX(STR(?subject), "Digital_currencies", "i")
                )
            }}
            UNION
            {{
                ?resource rdf:type ?type .
                FILTER(
                    REGEX(STR(?type), "Cryptocurrency", "i") ||
                    REGEX(STR(?type), "DigitalCurrency", "i")
                )
            }}
            
            FILTER (
                (LCASE(STR(?label)) = "{nombre.lower()}" ||
                 CONTAINS(LCASE(STR(?label)), "{nombre.lower()}")) &&
                LANG(?label) = "en"
            )
        }}
        LIMIT 5
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setTimeout(15)
            results = self.sparql.query().convert()
            
            if results["results"]["bindings"]:
                return self._procesar_resultados(results)
            return None
            
        except Exception as e:
            st.error(f"Error en consulta DBpedia: {e}")
            return None
    
    def buscar_relacionados(self, concepto: str) -> List[Dict]:
        """
        Busca conceptos relacionados con criptomonedas en DBpedia
        
        Args:
            concepto: Concepto a buscar (ej: "blockchain", "smart contract")
        
        Returns:
            Lista de recursos relacionados
        """
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT DISTINCT ?resource ?label ?comment
        WHERE {{
            ?resource rdfs:label ?label .
            OPTIONAL {{ ?resource rdfs:comment ?comment . }}
            
            # Filtrar solo entidades relacionadas con criptomonedas
            {{
                ?resource dct:subject ?subject .
                FILTER(
                    REGEX(STR(?subject), "Cryptocurrencies", "i") ||
                    REGEX(STR(?subject), "Blockchain", "i") ||
                    REGEX(STR(?subject), "Digital_currencies", "i")
                )
            }}
            
            FILTER (
                CONTAINS(LCASE(?label), "{concepto.lower()}") &&
                LANG(?label) = "en"
            )
        }}
        LIMIT 10
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setTimeout(15)
            results = self.sparql.query().convert()
            return self._procesar_lista_resultados(results)
            
        except Exception as e:
            st.error(f"Error buscando relacionados: {e}")
            return []
    
    def obtener_propiedades(self, recurso_uri: str) -> Dict:
        """
        Obtiene todas las propiedades de un recurso específico
        
        Args:
            recurso_uri: URI del recurso en DBpedia
        
        Returns:
            Diccionario con propiedades y valores
        """
        query = f"""
        SELECT ?property ?value
        WHERE {{
            <{recurso_uri}> ?property ?value .
        }}
        LIMIT 50
        """
        
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            propiedades = {}
            for result in results["results"]["bindings"]:
                prop = result["property"]["value"].split("/")[-1]
                val = result["value"]["value"]
                propiedades[prop] = val
            
            return propiedades
            
        except Exception as e:
            st.error(f"Error obteniendo propiedades: {e}")
            return {}
    
    def buscar_por_tipo(self, tipo: str = "Cryptocurrency") -> List[Dict]:
        """
        Busca recursos por tipo/categoría relacionados con criptomonedas
        
        Args:
            tipo: Tipo de recurso (ej: "Cryptocurrency", "Blockchain")
        
        Returns:
            Lista de recursos del tipo especificado
        """
        query = f"""
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT DISTINCT ?resource ?label ?abstract
        WHERE {{
            ?resource rdfs:label ?label .
            OPTIONAL {{ ?resource dbo:abstract ?abstract }}
            
            # Filtrar por tipo específico relacionado con criptomonedas
            ?resource rdf:type dbo:{tipo} .
            
            FILTER(LANG(?label) = "en")
        }}
        LIMIT 20
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setTimeout(15)
            results = self.sparql.query().convert()
            return self._procesar_lista_resultados(results)
            
        except Exception as e:
            st.error(f"Error buscando por tipo: {e}")
            return []
    
    def buscar_simple(self, termino: str) -> List[Dict]:
        """
        Búsqueda simple en DBpedia filtrada para criptomonedas
        
        Args:
            termino: Término a buscar
        
        Returns:
            Lista de resultados
        """
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT DISTINCT ?resource ?label
        WHERE {{
            ?resource rdfs:label ?label .
            
            # Filtrar solo entidades relacionadas con criptomonedas
            {{
                ?resource dct:subject ?subject .
                FILTER(
                    REGEX(STR(?subject), "Cryptocurrencies", "i") ||
                    REGEX(STR(?subject), "Blockchain", "i") ||
                    REGEX(STR(?subject), "Digital_currencies", "i") ||
                    REGEX(STR(?subject), "Bitcoin", "i") ||
                    REGEX(STR(?subject), "Ethereum", "i")
                )
            }}
            UNION
            {{
                ?resource rdf:type ?type .
                FILTER(
                    REGEX(STR(?type), "Cryptocurrency", "i") ||
                    REGEX(STR(?type), "DigitalCurrency", "i") ||
                    REGEX(STR(?type), "Blockchain", "i")
                )
            }}
            
            FILTER (
                LCASE(?label) = "{termino.lower()}" &&
                LANG(?label) = "en"
            )
        }}
        LIMIT 5
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setTimeout(30)
            self.sparql.setRequestMethod('GET')
            results = self.sparql.query().convert()
            
            if not results["results"]["bindings"]:
                query2 = f"""
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX dct: <http://purl.org/dc/terms/>
                
                SELECT DISTINCT ?resource ?label
                WHERE {{
                    ?resource rdfs:label ?label .
                    
                    {{
                        ?resource dct:subject ?subject .
                        FILTER(
                            REGEX(STR(?subject), "Cryptocurrencies", "i") ||
                            REGEX(STR(?subject), "Blockchain", "i") ||
                            REGEX(STR(?subject), "Digital_currencies", "i")
                        )
                    }}
                    UNION
                    {{
                        ?resource rdf:type ?type .
                        FILTER(
                            REGEX(STR(?type), "Cryptocurrency", "i") ||
                            REGEX(STR(?type), "DigitalCurrency", "i")
                        )
                    }}
                    
                    FILTER (
                        CONTAINS(LCASE(?label), "{termino.lower()}") &&
                        LANG(?label) = "en"
                    )
                }}
                LIMIT 10
                """
                self.sparql.setQuery(query2)
                results = self.sparql.query().convert()
            
            resultados = []
            for result in results["results"]["bindings"]:
                uri = result.get("resource", {}).get("value", "")
                label = result.get("label", {}).get("value", "")
                
                abstract = self._obtener_abstract_simple(uri)
                
                item = {
                    "uri": uri,
                    "label": label,
                    "abstract": abstract if abstract else "Sin descripción disponible"
                }
                resultados.append(item)
            
            return resultados
            
        except Exception as e:
            st.error(f"Error en búsqueda simple: {str(e)}")
            return []
    
    def _obtener_abstract_simple(self, uri: str) -> str:
        """Obtiene el abstract de un recurso específico"""
        query = f"""
        SELECT ?abstract
        WHERE {{
            <{uri}> dbo:abstract ?abstract .
            FILTER (LANG(?abstract) = "en")
        }}
        LIMIT 1
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setTimeout(10)
            results = self.sparql.query().convert()
            
            if results["results"]["bindings"]:
                abstract = results["results"]["bindings"][0].get("abstract", {}).get("value", "")
                return abstract[:400] + "..." if len(abstract) > 400 else abstract
            return ""
        except:
            return ""
    
    def _procesar_resultados(self, results: Dict) -> Dict:
        """Procesa resultados de consulta SPARQL"""
        if not results["results"]["bindings"]:
            return None
        
        primer_resultado = results["results"]["bindings"][0]
        
        return {
            "uri": primer_resultado.get("resource", {}).get("value", ""),
            "label": primer_resultado.get("label", {}).get("value", ""),
            "abstract": primer_resultado.get("abstract", {}).get("value", "No hay descripción disponible"),
            "thumbnail": primer_resultado.get("thumbnail", {}).get("value", ""),
            "website": primer_resultado.get("website", {}).get("value", ""),
            "creator": primer_resultado.get("creator", {}).get("value", ""),
            "date": primer_resultado.get("date", {}).get("value", "")
        }
    
    def _procesar_lista_resultados(self, results: Dict) -> List[Dict]:
        """Procesa lista de resultados SPARQL"""
        lista = []
        
        for result in results["results"]["bindings"]:
            item = {
                "uri": result.get("resource", {}).get("value", ""),
                "label": result.get("label", {}).get("value", ""),
                "comment": result.get("comment", {}).get("value", "")[:200] + "..."
                if result.get("comment", {}).get("value", "") else ""
            }
            lista.append(item)
        
        return lista


class DBpediaOffline:
    """Manejo de datos DBpedia en modo offline (cache)"""
    
    def __init__(self, cache_file: str = "dbpedia_cache.json"):
        self.cache_file = cache_file
        self.cache = self._cargar_cache()
    
    def _cargar_cache(self) -> Dict:
        """Carga cache de consultas previas"""
        try:
            import json
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _guardar_cache(self):
        """Guarda cache en archivo"""
        import json
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=2, ensure_ascii=False)
    
    def agregar_al_cache(self, clave: str, datos: Dict):
        """Agrega datos al cache"""
        self.cache[clave] = datos
        self._guardar_cache()
    
    def obtener_del_cache(self, clave: str) -> Optional[Dict]:
        """Obtiene datos del cache"""
        return self.cache.get(clave)
    
    def buscar_en_cache(self, termino: str) -> List[Dict]:
        """Busca en cache por término"""
        resultados = []
        for clave, datos in self.cache.items():
            if termino.lower() in clave.lower():
                resultados.append(datos)
        return resultados