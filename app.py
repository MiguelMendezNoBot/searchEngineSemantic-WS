import streamlit as st
from owlready2 import *
import os
from dbpedia_connector import DBpediaConnector, DBpediaOffline

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    requests = None
    REQUESTS_AVAILABLE = False

try:
    from SPARQLWrapper import SPARQLWrapper, JSON
    SPARQL_AVAILABLE = True
except ImportError:
    SPARQLWrapper = None
    SPARQL_AVAILABLE = False

from urllib.parse import quote

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Buscador Semántico de Criptomonedas",
    page_icon="🔍",
    layout="wide"
)

# ==================== ESTILOS CSS ====================
st.markdown("""
    <style>
    .main {
        padding-top: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    h1 {
        color: #1f77b4;
    }
    .resultado-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .dbpedia-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)

# ==================== TÍTULO ====================
st.title("🔍 Buscador Semántico de Criptomonedas")
st.markdown("### Ontología OWL + DBpedia - Web Semántica")
st.markdown("---")

# ==================== INICIALIZAR CONECTORES ====================
@st.cache_resource
def inicializar_dbpedia():
    """Inicializa el conector de DBpedia"""
    return DBpediaConnector()

@st.cache_resource
def inicializar_cache():
    """Inicializa el cache offline"""
    return DBpediaOffline()

dbpedia = inicializar_dbpedia()
cache_offline = inicializar_cache()

# Verificar conexión
conexion_online = dbpedia.is_online()

# ==================== FUNCIONES ====================

@st.cache_resource
def cargar_ontologia(archivo):
    """Cargar la ontología OWL"""
    try:
        ruta_completa = os.path.abspath(archivo)
        onto = get_ontology(f"file://{ruta_completa}").load()
        return onto, None
    except Exception as e:
        return None, str(e)

def mostrar_info_individuo(individuo, enriquecer_dbpedia=False):
    """Mostrar información detallada de un individuo"""
    st.markdown(f"### 📄 {individuo.name}")

    # Mostrar tipos/clases
    tipos = [cls.name for cls in individuo.is_a if hasattr(cls, 'name')]
    if tipos:
        st.write(f"**🏷️ Tipo:** {', '.join(tipos)}")

    # Mostrar propiedades
    propiedades_encontradas = False
    for prop in individuo.get_properties():
        valores = prop[individuo]
        if valores:
            propiedades_encontradas = True
            if isinstance(valores, list):
                valores_str = ", ".join([str(v) for v in valores])
            else:
                valores_str = str(valores)
            st.write(f"**{prop.name}:** {valores_str}")

    if not propiedades_encontradas:
        st.info("No hay propiedades adicionales definidas")

    st.markdown("---")

def buscar_en_dbpedia(termino, limite=10):
    """Buscar entidades en DBpedia usando SPARQL queries"""
    if not SPARQL_AVAILABLE:
        return [], "SPARQLWrapper no está instalado. Instala SPARQLWrapper para usar búsquedas en DBpedia."

    try:
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        sparql.setReturnFormat(JSON)

        # Query to search for entities with label matching the term
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT DISTINCT ?entity ?label ?comment ?thumbnail
        WHERE {{
            ?entity rdfs:label ?label .
            OPTIONAL {{ ?entity rdfs:comment ?comment . FILTER(LANG(?comment) = "en") }}
            OPTIONAL {{ ?entity dbo:thumbnail ?thumbnail }}
            FILTER(LANG(?label) = "en")
            FILTER(REGEX(?label, "{termino}", "i"))
        }}
        ORDER BY ?label
        LIMIT {limite}
        """

        sparql.setQuery(query)
        results = sparql.query().convert()

        # Debug print to see what DBpedia SPARQL returns
        print("DBpedia SPARQL response (explore):", results)

        entidades = []
        for result in results["results"]["bindings"]:
            comment_value = result.get('comment', {}).get('value', 'No description available')
            entidad = {
                'uri': result['entity']['value'],
                'label': result['label']['value'],
                'comment': comment_value[:300] + "..." if len(comment_value) > 300 else comment_value,
                'thumbnail': result.get('thumbnail', {}).get('value', None),
                'founding_date': None,  # SPARQL query doesn't include founding date
                'website': None  # SPARQL query doesn't include website
            }
            entidades.append(entidad)

        return entidades, None

    except Exception as e:
        return [], f"Error connecting to DBpedia: {str(e)}"

def obtener_detalles_dbpedia(uri):
    """Obtener detalles completos de una entidad DBpedia usando SPARQL"""
    if not SPARQL_AVAILABLE:
        return None, "SPARQLWrapper no está instalado. Instala SPARQLWrapper para obtener detalles de DBpedia."

    try:
        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
        sparql.setReturnFormat(JSON)

        # Query to get details for a specific entity
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>

        SELECT ?label ?comment ?thumbnail ?foundingDate ?website
        WHERE {{
            <{uri}> rdfs:label ?label .
            OPTIONAL {{ <{uri}> rdfs:comment ?comment . FILTER(LANG(?comment) = "en") }}
            OPTIONAL {{ <{uri}> dbo:thumbnail ?thumbnail }}
            OPTIONAL {{ <{uri}> dbo:foundingDate ?foundingDate }}
            OPTIONAL {{ <{uri}> foaf:homepage ?website }}
            FILTER(LANG(?label) = "en")
        }}
        LIMIT 1
        """

        sparql.setQuery(query)
        results = sparql.query().convert()

        # Debug print to see what DBpedia SPARQL returns
        print("DBpedia SPARQL response (details):", results)

        if results["results"]["bindings"]:
            result = results["results"]["bindings"][0]
            return {
                'label': result['label']['value'],
                'comment': result.get('comment', {}).get('value', 'No description available'),
                'thumbnail': result.get('thumbnail', {}).get('value', None),
                'founding_date': result.get('foundingDate', {}).get('value', None),
                'website': result.get('website', {}).get('value', None),
                'types': []  # SPARQL query doesn't include types in this simple query
            }, None
        else:
            return None, "No se encontraron detalles para esta entidad"
    except Exception as e:
        return None, f"Error al obtener detalles de DBpedia: {str(e)}"

def importar_entidad_dbpedia(onto, entidad, archivo_owl):
    """Importar una entidad DBpedia como instancia en la ontología"""
    try:
        # Determinar la clase apropiada (por simplicidad, usar Criptomoneda para entidades relacionadas)
        if hasattr(onto, 'Criptomoneda'):
            clase = onto.Criptomoneda
        else:
            # Si no existe, intentar crear la clase o usar una clase base
            with onto:
                clase = types.new_class("Criptomoneda", (Thing,))

        # Crear nombre único para la instancia
        nombre_instancia = entidad['label'].replace(' ', '_').replace('-', '_').lower()

        # Verificar si ya existe
        if hasattr(onto, nombre_instancia):
            return False, f"La instancia '{nombre_instancia}' ya existe en la ontología"

        # Crear la instancia
        instancia = clase(nombre_instancia)

        # Agregar propiedades si existen
        if hasattr(onto, 'descripcion') and entidad.get('comment'):
            instancia.descripcion = entidad['comment']

        if hasattr(onto, 'website') and entidad.get('website'):
            instancia.website = entidad['website']

        if hasattr(onto, 'fechaCreación') and entidad.get('founding_date'):
            instancia.fechaCreación = entidad['founding_date']

        # Agregar nombre si existe
        if hasattr(onto, 'nombre'):
            instancia.nombre = entidad['label']

        # Guardar la ontología con ruta absoluta
        ruta_completa = os.path.abspath(archivo_owl)
        onto.save(file=ruta_completa)

        return True, f"Entidad '{entidad['label']}' importada exitosamente como instancia de {clase.name}"
    except Exception as e:
        return False, f"Error al importar entidad: {str(e)}"

def mostrar_info_dbpedia(entidad, onto=None, archivo_owl=None):
    """Mostrar información detallada de una entidad DBpedia"""
    st.markdown(f"### 🌐 {entidad['label']}")

    # Thumbnail si existe
    if entidad.get('thumbnail'):
        try:
            st.image(entidad['thumbnail'], width=150)
        except:
            st.warning("No se pudo cargar la imagen")

    # Descripción
    if entidad.get('comment'):
        st.write(f"**📝 Descripción:** {entidad['comment']}")

    # Fecha de fundación
    if entidad.get('founding_date'):
        st.write(f"**📅 Fecha de fundación:** {entidad['founding_date']}")

    # Website
    if entidad.get('website'):
        st.write(f"**🌐 Website:** [{entidad['website']}]({entidad['website']})")

    # URI de DBpedia
    st.write(f"**🔗 DBpedia URI:** [{entidad['uri']}]({entidad['uri']})")

    # Botón para importar a ontología
    if onto and archivo_owl:
        if st.button("💾 Importar a Ontología", key=f"import_{entidad['uri'].split('/')[-1]}"):
            with st.spinner("Importando entidad..."):
                exito, mensaje = importar_entidad_dbpedia(onto, entidad, archivo_owl)
                if exito:
                    st.success(mensaje)
                    st.cache_resource.clear()  # Limpiar cache para recargar ontología
                else:
                    st.error(mensaje)

    st.markdown("---")

# ==================== SIDEBAR ====================
st.sidebar.header("⚙️ Configuración")

# Estado de conexión
if conexion_online:
    st.sidebar.success("✅ Conectado a DBpedia")
else:
    st.sidebar.warning("🔌 Modo Offline (Sin conexión)")

# Cargar ontología
archivo_owl = st.sidebar.text_input(
    "📁 Archivo OWL:", 
    value="criptomonedas.owl",
    help="Nombre del archivo OWL en la carpeta del proyecto"
)

# Opción para enriquecer con DBpedia
enriquecer = st.sidebar.checkbox(
    "🌐 Enriquecer con DBpedia",
    value=True,
    help="Agrega información de DBpedia a los resultados"
)

# Botón para recargar
if st.sidebar.button("🔄 Recargar Ontología"):
    st.cache_resource.clear()

# Intentar cargar
onto, error = cargar_ontologia(archivo_owl)

if error:
    st.sidebar.error(f"❌ Error al cargar: {error}")
    st.error(f"""
    ### ⚠️ No se pudo cargar la ontología
    
    **Error:** {error}
    
    **Soluciones:**
    1. Verifica que el archivo `{archivo_owl}` esté en la misma carpeta que `app.py`
    2. Asegúrate de que el archivo sea un OWL válido exportado desde Protégé
    3. Intenta con otro nombre de archivo
    """)
    st.stop()
else:
    st.sidebar.success("✅ Ontología cargada correctamente")
    
    # Estadísticas
    num_clases = len(list(onto.classes()))
    num_propiedades = len(list(onto.properties()))
    num_individuos = len(list(onto.individuals()))
    
    st.sidebar.markdown("### 📊 Estadísticas")
    st.sidebar.metric("Clases", num_clases)
    st.sidebar.metric("Propiedades", num_propiedades)
    st.sidebar.metric("Individuos", num_individuos)

# Modo de búsqueda
st.sidebar.markdown("---")
modo_busqueda = st.sidebar.radio(
    "🔍 Modo de búsqueda:",
    ["🏠 Local (Ontología)", "🌐 DBpedia", "🔄 Híbrido (Local + DBpedia)"],
    help="Selecciona el origen de los datos para la búsqueda"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Ayuda")
st.sidebar.info("""
**Tipos de búsqueda:**
- **Por nombre:** Busca individuos que contengan el término
- **Por clase:** Lista todos los individuos de una clase específica
- **DBpedia:** Búsqueda extendida en DBpedia
- **Explorar:** Navega por toda la ontología

**Modos de búsqueda:**
- **🏠 Local:** Solo busca en la ontología cargada
- **🌐 DBpedia:** Solo busca en DBpedia (base de datos abierta)
- **🔄 Híbrido:** Combina resultados locales y de DBpedia
""")

# Test de conexión
if st.sidebar.button("🧪 Probar DBpedia"):
    with st.sidebar:
        with st.spinner("Probando API REST..."):
            test_results = dbpedia.buscar_con_api_rest("Bitcoin")
            if test_results:
                st.success(f"✅ API REST: {len(test_results)} resultados")
                st.write(f"Encontrado: {test_results[0].get('label', 'N/A')}")
            else:
                st.warning("⚠️ API REST no responde")
                
                # Intentar SPARQL como fallback
                with st.spinner("Probando SPARQL..."):
                    test_sparql = dbpedia.buscar_simple("Bitcoin")
                    if test_sparql:
                        st.success(f"✅ SPARQL: {len(test_sparql)} resultados")
                    else:
                        st.error("❌ Ambos métodos fallaron")

# ==================== TIPO DE BÚSQUEDA ====================
tipo_busqueda = st.radio(
    "🔎 Selecciona el tipo de búsqueda:",
    ["🔤 Búsqueda por nombre", "📂 Búsqueda por clase", "🌐 Búsqueda en DBpedia", "🗂️ Explorar ontología"],
    horizontal=True
)

st.markdown("---")

# ==================== BÚSQUEDA POR NOMBRE ====================
if tipo_busqueda == "🔤 Búsqueda por nombre":
    st.subheader("🔤 Búsqueda por nombre")

    col1, col2 = st.columns([3, 1])
    with col1:
        termino = st.text_input(
            "Ingrese el término de búsqueda:",
            placeholder="Ejemplo: bitcoin, exchange, blockchain...",
            key="busqueda_nombre"
        )
    with col2:
        st.write("")
        st.write("")
        buscar_btn = st.button("🔍 Buscar", type="primary", use_container_width=True)

    if buscar_btn and termino:
        with st.spinner("Buscando..."):
            resultados_locales = []
            resultados_dbpedia = []

            # Búsqueda local (si no es modo DBpedia-only)
            if modo_busqueda != "🌐 DBpedia":
                for individuo in onto.individuals():
                    if termino.lower() in individuo.name.lower():
                        resultados_locales.append(individuo)

            # Búsqueda en DBpedia (si no es modo local-only)
            if modo_busqueda != "🏠 Local (Ontología)":
                entidades_dbpedia, error_dbpedia = buscar_en_dbpedia(termino)
                if error_dbpedia:
                    st.warning(f"⚠️ Error al buscar en DBpedia: {error_dbpedia}")
                resultados_dbpedia = entidades_dbpedia

            # Mostrar resultados
            total_resultados = len(resultados_locales) + len(resultados_dbpedia)

            if total_resultados > 0:
                st.success(f"✅ Se encontraron **{total_resultados}** resultados para '{termino}':")
                st.markdown("---")

                # Resultados locales
                if resultados_locales:
                    st.markdown("### 🏠 Resultados de la Ontología Local")
                    for ind in resultados_locales:
                        with st.container():
                            mostrar_info_individuo(ind)

                # Resultados DBpedia
                if resultados_dbpedia:
                    st.markdown("### 🌐 Resultados de DBpedia")
                    for entidad in resultados_dbpedia:
                        with st.container():
                            mostrar_info_dbpedia(entidad, onto, archivo_owl)

            else:
                st.warning(f"⚠️ No se encontraron resultados para '{termino}'")
                if modo_busqueda == "🏠 Local (Ontología)":
                    st.info("💡 Intenta con otro término o explora la ontología para ver qué hay disponible")
                elif modo_busqueda == "🌐 DBpedia":
                    st.info("💡 Intenta con términos relacionados con criptomonedas, blockchain o finanzas")
                else:
                    st.info("💡 Intenta con otro término en ambos orígenes de datos")

# ==================== BÚSQUEDA POR CLASE ====================
elif tipo_busqueda == "📂 Búsqueda por clase":
    st.subheader("📂 Búsqueda por clase")

    if modo_busqueda == "🏠 Local (Ontología)" or modo_busqueda == "🔄 Híbrido (Local + DBpedia)":
        # Obtener lista de clases locales
        clases = sorted([cls.name for cls in onto.classes() if hasattr(cls, 'name')])

        if not clases:
            st.warning("No se encontraron clases en la ontología local")
            if modo_busqueda == "🏠 Local (Ontología)":
                st.stop()

        col1, col2 = st.columns([3, 1])
        with col1:
            clase_seleccionada = st.selectbox(
                "Seleccione una clase:",
                clases,
                key="clase_select"
            )
        with col2:
            st.write("")
            st.write("")
            buscar_clase_btn = st.button("📋 Listar instancias", type="primary", use_container_width=True)

        if buscar_clase_btn and clase_seleccionada:
            with st.spinner(f"Buscando instancias de {clase_seleccionada}..."):
                try:
                    clase = onto.search_one(iri=f"*{clase_seleccionada}")
                    if clase is None:
                        clase = onto.search_one(label=clase_seleccionada)
                    if clase is None:
                        for c in onto.classes():
                            if c.name == clase_seleccionada:
                                clase = c
                                break

                    if clase:
                        instancias = list(clase.instances())
                    else:
                        st.error(f"No se pudo encontrar la clase '{clase_seleccionada}'")
                        instancias = []

                    if instancias:
                        st.success(f"✅ Se encontraron **{len(instancias)}** instancias de la clase '{clase_seleccionada}':")
                        st.markdown("---")

                        # Mostrar en columnas si hay muchas
                        if len(instancias) > 3:
                            cols = st.columns(2)
                            for idx, inst in enumerate(instancias):
                                with cols[idx % 2]:
                                    with st.container():
                                        mostrar_info_individuo(inst)
                        else:
                            for inst in instancias:
                                mostrar_info_individuo(inst)
                    else:
                        st.info(f"ℹ️ No hay instancias definidas para la clase '{clase_seleccionada}'")
                        st.markdown("""
                        **Esto puede significar:**
                        - La clase existe pero aún no tiene individuos
                        - Necesitas poblar tu ontología con más datos
                        """)

                except Exception as e:
                    st.error(f"❌ Error al buscar instancias: {e}")

    if modo_busqueda == "🌐 DBpedia" or modo_busqueda == "🔄 Híbrido (Local + DBpedia)":
        if modo_busqueda == "🌐 DBpedia":
            st.markdown("---")

        # Búsqueda por tipo en DBpedia
        tipos_dbpedia = [
            "Cryptocurrency", "Blockchain", "Digital_currency",
            "Cryptocurrency_exchange", "Financial_service", "Company"
        ]

        col1, col2 = st.columns([3, 1])
        with col1:
            tipo_seleccionado = st.selectbox(
                "Seleccione un tipo en DBpedia:",
                tipos_dbpedia,
                key="tipo_dbpedia_select"
            )
        with col2:
            st.write("")
            st.write("")
            buscar_tipo_btn = st.button("🌐 Buscar en DBpedia", type="primary", use_container_width=True)

        if buscar_tipo_btn and tipo_seleccionado:
            if not SPARQL_AVAILABLE:
                st.error("SPARQLWrapper no está instalado. Instala SPARQLWrapper para buscar en DBpedia.")
            else:
                with st.spinner(f"Buscando entidades de tipo '{tipo_seleccionado}' en DBpedia..."):
                    try:
                        # Usar SPARQL query para buscar por tipo
                        sparql = SPARQLWrapper("https://dbpedia.org/sparql")
                        sparql.setReturnFormat(JSON)

                        query = f"""
                        PREFIX dbo: <http://dbpedia.org/ontology/>
                        PREFIX dbr: <http://dbpedia.org/resource/>
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                        SELECT DISTINCT ?entity ?label ?comment ?thumbnail
                        WHERE {{
                            ?entity rdf:type dbo:{tipo_seleccionado} .
                            ?entity rdfs:label ?label .
                            OPTIONAL {{ ?entity rdfs:comment ?comment . FILTER(LANG(?comment) = "en") }}
                            OPTIONAL {{ ?entity dbo:thumbnail ?thumbnail }}
                            FILTER(LANG(?label) = "en")
                        }}
                        ORDER BY ?label
                        LIMIT 20
                        """

                        sparql.setQuery(query)
                        results = sparql.query().convert()

                        # Debug print to see what DBpedia SPARQL returns
                        print("DBpedia SPARQL response:", results)

                        entidades = []
                        for result in results["results"]["bindings"]:
                            comment_value = result.get('comment', {}).get('value', 'No description available')
                            entidad = {
                                'uri': result['entity']['value'],
                                'label': result['label']['value'],
                                'comment': comment_value[:300] + "..." if len(comment_value) > 300 else comment_value,
                                'thumbnail': result.get('thumbnail', {}).get('value', None),
                                'founding_date': None
                            }
                            entidades.append(entidad)

                        if entidades:
                            st.success(f"✅ Se encontraron **{len(entidades)}** entidades de tipo '{tipo_seleccionado}' en DBpedia:")
                            st.markdown("---")

                            for entidad in entidades:
                                with st.container():
                                    mostrar_info_dbpedia(entidad, onto, archivo_owl)
                        else:
                            st.info(f"ℹ️ No se encontraron entidades de tipo '{tipo_seleccionado}' en DBpedia")

                    except requests.exceptions.Timeout:
                        st.error("La consulta excedió el tiempo límite.")
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Error de conexión con DBpedia: {str(e)}")
                    except Exception as e:
                        st.error(f"❌ Error al buscar en DBpedia: {e}")

# ==================== EXPLORAR ONTOLOGÍA ====================
else:  # Explorar ontología
    st.subheader("🗂️ Explorar datos")

    if modo_busqueda == "🏠 Local (Ontología)":
        # Tabs para organizar ontología local
        tab1, tab2, tab3 = st.tabs(["📚 Clases", "🔗 Propiedades", "📄 Todos los individuos"])

        with tab1:
            st.markdown("### 📚 Clases disponibles en la ontología")
            clases = sorted([cls.name for cls in onto.classes() if hasattr(cls, 'name')])

            if clases:
                # Mostrar en columnas
                cols = st.columns(3)
                for idx, cls_name in enumerate(clases):
                    with cols[idx % 3]:
                        st.markdown(f"- **{cls_name}**")
            else:
                st.info("No hay clases definidas")

        with tab2:
            st.markdown("### 🔗 Propiedades definidas")

            data_props = [p.name for p in onto.data_properties() if hasattr(p, 'name')]
            object_props = [p.name for p in onto.object_properties() if hasattr(p, 'name')]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 📊 Data Properties")
                if data_props:
                    for prop in sorted(data_props):
                        st.markdown(f"- {prop}")
                else:
                    st.info("No hay data properties definidas")

            with col2:
                st.markdown("#### 🔗 Object Properties")
                if object_props:
                    for prop in sorted(object_props):
                        st.markdown(f"- {prop}")
                else:
                    st.info("No hay object properties definidas")

        with tab3:
            st.markdown("### 📄 Todos los individuos")
            individuos = list(onto.individuals())

            if individuos:
                st.info(f"Total de individuos: {len(individuos)}")

                # Búsqueda rápida dentro de individuos
                filtro = st.text_input("🔍 Filtrar individuos:", placeholder="Escribe para filtrar...")

                individuos_filtrados = individuos
                if filtro:
                    individuos_filtrados = [ind for ind in individuos if filtro.lower() in ind.name.lower()]

                if individuos_filtrados:
                    # Mostrar en columnas
                    if len(individuos_filtrados) > 4:
                        cols = st.columns(2)
                        for idx, ind in enumerate(sorted(individuos_filtrados, key=lambda x: x.name)):
                            with cols[idx % 2]:
                                with st.container():
                                    mostrar_info_individuo(ind)
                    else:
                        for ind in sorted(individuos_filtrados, key=lambda x: x.name):
                            mostrar_info_individuo(ind)
                else:
                    st.warning("No se encontraron individuos con ese filtro")
            else:
                st.warning("⚠️ No hay individuos en la ontología")
                st.markdown("""
                ### ¿Qué hacer?

                Tu ontología tiene clases pero no tiene instancias (individuos). Para poblarla:

                1. **Opción 1:** Agregar individuos manualmente en Protégé
                2. **Opción 2:** Importar datos desde DBpedia
                3. **Opción 3:** Usar scripts para generar instancias automáticamente
                """)

    elif modo_busqueda == "🌐 DBpedia":
        st.markdown("### 🌐 Explorar DBpedia - Entidades relacionadas con criptomonedas")

        # Categorías para explorar
        categorias = {
            "Cryptocurrency": "Criptomonedas",
            "Blockchain": "Tecnología Blockchain",
            "Digital_currency": "Monedas digitales",
            "Cryptocurrency_exchange": "Exchanges de Criptomonedas",
            "Financial_service": "Servicios financieros",
            "Company": "Empresas"
        }

        # Tabs para diferentes categorías
        tabs = st.tabs(list(categorias.values()))

        for idx, (tipo, nombre) in enumerate(categorias.items()):
            with tabs[idx]:
                st.markdown(f"### {nombre}")

                if st.button(f"🔍 Explorar {nombre.lower()}", key=f"explore_{tipo}"):
                    if not SPARQL_AVAILABLE:
                        st.error("SPARQLWrapper no está instalado. Instala SPARQLWrapper para explorar DBpedia.")
                    else:
                        with st.spinner(f"Buscando entidades de tipo {nombre.lower()}..."):
                            try:
                                # Usar SPARQL query para explorar por tipo
                                sparql = SPARQLWrapper("https://dbpedia.org/sparql")
                                sparql.setReturnFormat(JSON)

                                query = f"""
                                PREFIX dbo: <http://dbpedia.org/ontology/>
                                PREFIX dbr: <http://dbpedia.org/resource/>
                                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                                SELECT DISTINCT ?entity ?label ?comment
                                WHERE {{
                                    ?entity rdf:type dbo:{tipo} .
                                    ?entity rdfs:label ?label .
                                    OPTIONAL {{ ?entity rdfs:comment ?comment . FILTER(LANG(?comment) = "en") }}
                                    FILTER(LANG(?label) = "en")
                                }}
                                ORDER BY ?label
                                LIMIT 15
                                """

                                sparql.setQuery(query)
                                results = sparql.query().convert()

                                entidades = []
                                for result in results["results"]["bindings"]:
                                    comment_value = result.get('comment', {}).get('value', 'No description available')
                                    entidad = {
                                        'uri': result['entity']['value'],
                                        'label': result['label']['value'],
                                        'comment': comment_value[:200] + "..." if len(comment_value) > 200 else comment_value
                                    }
                                    entidades.append(entidad)

                                if entidades:
                                    for entidad in entidades:
                                        with st.container():
                                            st.markdown(f"**{entidad['label']}**")
                                            st.write(entidad['comment'])
                                            st.markdown(f"[🔗 Ver en DBpedia]({entidad['uri']})")
                                            st.markdown("---")
                                else:
                                    st.info(f"No se encontraron entidades de tipo {nombre.lower()}")

                            except requests.exceptions.Timeout:
                                st.error("La consulta excedió el tiempo límite.")
                            except requests.exceptions.RequestException as e:
                                st.error(f"❌ Error de conexión con DBpedia: {str(e)}")
                            except Exception as e:
                                st.error(f"❌ Error al explorar DBpedia: {e}")

    else:  # Híbrido
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🏠 Ontología Local")
            num_clases = len(list(onto.classes()))
            num_individuos = len(list(onto.individuals()))
            st.metric("Clases", num_clases)
            st.metric("Individuos", num_individuos)

        with col2:
            st.markdown("### 🌐 DBpedia")
            # Estadísticas de DBpedia - usando aproximación ya que Lookup API no proporciona conteos
            st.metric("Criptomonedas", "N/A")

        st.markdown("---")
        st.info("💡 Usa los otros tipos de búsqueda para explorar datos específicos de ambos orígenes")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p>🎓 Proyecto de Web Semántica - Buscador Semántico de Criptomonedas</p>
    <p>Desarrollado con Streamlit, Owlready2 y DBpedia</p>
</div>
""", unsafe_allow_html=True)