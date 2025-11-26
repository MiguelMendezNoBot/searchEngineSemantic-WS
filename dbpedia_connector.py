from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from typing import List, Dict, Optional
import streamlit as st
import re

class DBpediaConnector:
    """Conector mejorado para consultas a DBpedia con soporte para instancias"""
    
    def __init__(self):
        self.endpoint_online = "https://dbpedia.org/sparql"
        self.sparql = SPARQLWrapper(self.endpoint_online)
        self.sparql.setReturnFormat(JSON)
        self.sparql.setTimeout(30)
        self.timeout = 30
        self.sparql.addCustomHttpHeader("User-Agent", "Mozilla/5.0")
    
    def limpiar_html(self, texto):
        """
        Limpia etiquetas HTML del texto de DBpedia
        """
        if not texto:
            return texto
        
        # Remover etiquetas <B> y </B>
        texto = re.sub(r'<B>', '', texto, flags=re.IGNORECASE)
        texto = re.sub(r'</B>', '', texto, flags=re.IGNORECASE)
        
        # Remover otras etiquetas HTML comunes
        texto = re.sub(r'<[^>]+>', '', texto)
        
        # Limpiar espacios múltiples
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def is_online(self) -> bool:
        """Verifica si hay conexión a DBpedia"""
        try:
            response = requests.get(self.endpoint_online, timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def buscar_instancias_de_clase(self, clase: str, limit: int = 20) -> List[Dict]:
        """
        Busca INSTANCIAS de una clase específica en DBpedia
        
        Args:
            clase: Nombre de la clase (ej: "Cryptocurrency", "Blockchain")
            limit: Número máximo de resultados
        
        Returns:
            Lista de instancias encontradas
        """
        # Query para encontrar instancias de una clase
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?instancia ?label ?abstract ?thumbnail
        WHERE {{
            # Buscar instancias que sean de tipo relacionado con la clase
            {{
                ?instancia rdf:type dbo:{clase} .
            }}
            UNION
            {{
                ?instancia rdf:type ?tipo .
                ?tipo rdfs:label ?tipoLabel .
                FILTER(CONTAINS(LCASE(STR(?tipoLabel)), "{clase.lower()}"))
            }}
            
            ?instancia rdfs:label ?label .
            OPTIONAL {{ ?instancia dbo:abstract ?abstract . }}
            OPTIONAL {{ ?instancia dbo:thumbnail ?thumbnail . }}
            
            FILTER(LANG(?label) = "en")
            FILTER(LANG(?abstract) = "en" || !BOUND(?abstract))
        }}
        LIMIT {limit}
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setTimeout(30)
            results = self.sparql.query().convert()
            
            instancias = []
            for result in results["results"]["bindings"]:
                instancia = {
                    "uri": result.get("instancia", {}).get("value", ""),
                    "label": self.limpiar_html(result.get("label", {}).get("value", "Sin nombre")),
                    "abstract": self.limpiar_html(result.get("abstract", {}).get("value", "Sin descripción"))[:300] + "...",
                    "thumbnail": result.get("thumbnail", {}).get("value", "")
                }
                instancias.append(instancia)
            
            return instancias
            
        except Exception as e:
            st.warning(f"Error en consulta SPARQL: {e}")
            return []
    
    def buscar_instancias_relacionadas(self, termino: str) -> List[Dict]:
        """
        Busca instancias RELACIONADAS con un término
        Más flexible que buscar por clase exacta
        
        Args:
            termino: Término de búsqueda (ej: "Bitcoin", "Exchange")
        
        Returns:
            Lista de instancias relacionadas
        """
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT DISTINCT ?instancia ?label ?abstract ?tipo
        WHERE {{
            ?instancia rdfs:label ?label .
            OPTIONAL {{ ?instancia dbo:abstract ?abstract . }}
            OPTIONAL {{ ?instancia rdf:type ?tipo . }}
            
            # Buscar en el label o en categorías
            FILTER(
                CONTAINS(LCASE(?label), "{termino.lower()}") ||
                EXISTS {{ ?instancia dct:subject ?cat . FILTER(CONTAINS(LCASE(STR(?cat)), "{termino.lower()}")) }}
            )
            
            FILTER(LANG(?label) = "en")
            FILTER(LANG(?abstract) = "en" || !BOUND(?abstract))
        }}
        LIMIT 15
        """
        
        try:
            self.sparql.setQuery(query)
            self.sparql.setTimeout(30)
            results = self.sparql.query().convert()
            
            instancias = []
            for result in results["results"]["bindings"]:
                tipo = result.get("tipo", {}).get("value", "")
                tipo_simple = tipo.split("/")[-1] if tipo else "Unknown"
                
                instancia = {
                    "uri": result.get("instancia", {}).get("value", ""),
                    "label": self.limpiar_html(result.get("label", {}).get("value", "Sin nombre")),
                    "abstract": self.limpiar_html(result.get("abstract", {}).get("value", "Sin descripción"))[:250] + "...",
                    "tipo": tipo_simple
                }
                instancias.append(instancia)
            
            return instancias
            
        except Exception as e:
            st.warning(f"Error buscando instancias: {e}")
            return []
    
    def obtener_instancias_con_propiedades(self, clase: str) -> List[Dict]:
        """
        Obtiene instancias CON sus propiedades principales
        Ideal para mostrar información detallada
        
        Args:
            clase: Clase a buscar (ej: "Cryptocurrency")
        
        Returns:
            Lista de instancias con propiedades
        """
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbp: <http://dbpedia.org/property/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?instancia ?label ?abstract ?creator ?releaseDate
        WHERE {{
            ?instancia rdf:type dbo:{clase} .
            ?instancia rdfs:label ?label .
            
            OPTIONAL {{ ?instancia dbo:abstract ?abstract . }}
            OPTIONAL {{ ?instancia dbo:creator ?creator . }}
            OPTIONAL {{ ?instancia dbp:released ?releaseDate . }}
            
            FILTER(LANG(?label) = "en")
            FILTER(LANG(?abstract) = "en" || !BOUND(?abstract))
        }}
        LIMIT 10
        """
        
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            instancias = []
            for result in results["results"]["bindings"]:
                instancia = {
                    "uri": result.get("instancia", {}).get("value", ""),
                    "label": self.limpiar_html(result.get("label", {}).get("value", "")),
                    "abstract": self.limpiar_html(result.get("abstract", {}).get("value", ""))[:300] + "...",
                    "creator": result.get("creator", {}).get("value", "Desconocido"),
                    "releaseDate": result.get("releaseDate", {}).get("value", "Desconocido")
                }
                instancias.append(instancia)
            
            return instancias
            
        except Exception as e:
            st.warning(f"Error obteniendo propiedades: {e}")
            return []
    
    def buscar_con_api_rest(self, termino: str) -> List[Dict]:
        """
        Búsqueda usando la API REST de DBpedia Lookup
        Ahora incluye el tipo de cada instancia y limpia HTML
        
        Args:
            termino: Término a buscar
        
        Returns:
            Lista de resultados con tipo
        """
        try:
            url = f"https://lookup.dbpedia.org/api/search?query={termino}&format=json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                resultados = []
                
                for item in data.get("docs", [])[:10]:
                    # Extraer tipo principal
                    tipos = item.get("type", [])
                    tipo_principal = tipos[0].split("/")[-1] if tipos else "Unknown"
                    
                    # Limpiar label y abstract
                    label_raw = item.get("label", ["Sin título"])[0] if isinstance(item.get("label"), list) else item.get("label", "Sin título")
                    abstract_raw = item.get("comment", [""])[0] if item.get("comment") else ""
                    
                    resultado = {
                        "uri": item.get("resource", [""])[0] if isinstance(item.get("resource"), list) else item.get("resource", ""),
                        "label": self.limpiar_html(label_raw),
                        "abstract": self.limpiar_html(abstract_raw)[:300] + "..." if abstract_raw else "Sin descripción",
                        "categories": item.get("category", [])[:3] if item.get("category") else [],
                        "tipo": tipo_principal,
                        "tipos_completos": tipos[:3] if len(tipos) > 1 else []
                    }
                    resultados.append(resultado)
                
                return resultados
            else:
                st.warning(f"Error en API: {response.status_code}")
                return []
                
        except Exception as e:
            st.error(f"Error con API REST: {e}")
            return []
    
    def buscar_por_categoria(self, categoria: str) -> List[Dict]:
        """
        Busca instancias en una CATEGORÍA específica de DBpedia
        Útil para encontrar todas las criptomonedas, exchanges, etc.
        
        Args:
            categoria: Categoría a buscar (ej: "Cryptocurrencies")
        
        Returns:
            Lista de recursos en esa categoría
        """
        query = f"""
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT DISTINCT ?instancia ?label ?abstract
        WHERE {{
            ?instancia dct:subject ?cat .
            ?instancia rdfs:label ?label .
            OPTIONAL {{ ?instancia dbo:abstract ?abstract . }}
            
            FILTER(CONTAINS(LCASE(STR(?cat)), "{categoria.lower()}"))
            FILTER(LANG(?label) = "en")
            FILTER(LANG(?abstract) = "en" || !BOUND(?abstract))
        }}
        LIMIT 20
        """
        
        try:
            self.sparql.setQuery(query)
            results = self.sparql.query().convert()
            
            instancias = []
            for result in results["results"]["bindings"]:
                instancia = {
                    "uri": result.get("instancia", {}).get("value", ""),
                    "label": self.limpiar_html(result.get("label", {}).get("value", "")),
                    "abstract": self.limpiar_html(result.get("abstract", {}).get("value", ""))[:200] + "..."
                }
                instancias.append(instancia)
            
            return instancias
            
        except Exception as e:
            st.warning(f"Error buscando por categoría: {e}")
            return []
    
    def buscar_simple(self, termino: str) -> List[Dict]:
        """
        Búsqueda simple y directa en DBpedia con limpieza de HTML
        """
        query = f"""
        SELECT DISTINCT ?resource ?label
        WHERE {{
            ?resource rdfs:label ?label .
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
                # Si no hay resultados exactos, intentar búsqueda parcial
                query2 = f"""
                SELECT DISTINCT ?resource ?label
                WHERE {{
                    ?resource rdfs:label ?label .
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
                label = self.limpiar_html(result.get("label", {}).get("value", ""))
                
                # Obtener abstract en consulta separada más simple
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
                abstract_limpio = self.limpiar_html(abstract)
                return abstract_limpio[:400] + "..." if len(abstract_limpio) > 400 else abstract_limpio
            return ""
        except:
            return ""


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