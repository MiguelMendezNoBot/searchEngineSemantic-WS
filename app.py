import streamlit as st
from owlready2 import *
import os
from dbpedia_connector import DBpediaConnector, DBpediaOffline

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
    
    # Mostrar propiedades locales
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
        st.info("No hay propiedades adicionales definidas en la ontología local")
    
    # Enriquecer con DBpedia si está habilitado
    if enriquecer_dbpedia:
        with st.expander("🌐 Información adicional de DBpedia", expanded=False):
            mostrar_info_dbpedia(individuo.name)
    
    st.markdown("---")

def mostrar_info_dbpedia(nombre_cripto):
    """Muestra información enriquecida desde DBpedia"""
    
    if conexion_online:
        with st.spinner(f"🔍 Buscando '{nombre_cripto}' en DBpedia..."):
            # Intentar con API REST primero (más rápida)
            resultados = dbpedia.buscar_con_api_rest(nombre_cripto)
            
            if resultados:
                datos = resultados[0]  # Tomar el primer resultado
                
                # Guardar en cache
                cache_offline.agregar_al_cache(nombre_cripto, datos)
                
                st.markdown('<div class="dbpedia-box">', unsafe_allow_html=True)
                st.markdown("**🔗 Fuente:** DBpedia (Online - API REST)")
                
                st.write(f"**{datos.get('label', nombre_cripto)}**")
                
                if datos.get("abstract"):
                    st.write("**Descripción:**")
                    st.write(datos["abstract"])
                
                if datos.get("categories"):
                    st.write(f"**📂 Categorías:** {', '.join(datos['categories'])}")
                
                if datos.get("uri"):
                    st.markdown(f"[🔗 Ver más en DBpedia]({datos['uri']})")
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("ℹ️ No se encontró información adicional en DBpedia")
    else:
        # Modo offline: buscar en cache
        st.info("🔌 Modo Offline: Buscando en cache local...")
        datos_cache = cache_offline.obtener_del_cache(nombre_cripto)
        
        if datos_cache:
            st.markdown('<div class="dbpedia-box">', unsafe_allow_html=True)
            st.markdown("**💾 Fuente:** Cache Local (Offline)")
            
            st.write(f"**{datos_cache.get('label', nombre_cripto)}**")
            
            if datos_cache.get("abstract"):
                st.write("**Descripción:**")
                st.write(datos_cache["abstract"])
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ Sin datos en cache para este término")

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

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Ayuda")
st.sidebar.info("""
**Tipos de búsqueda:**
- **Por nombre:** Busca individuos que contengan el término
- **Por clase:** Lista todos los individuos de una clase específica
- **DBpedia:** Búsqueda extendida en DBpedia
- **Explorar:** Navega por toda la ontología

**Nota:** Con conexión a internet, los resultados se enriquecen automáticamente con DBpedia.

**Términos sugeridos para DBpedia:**
- Bitcoin
- Ethereum  
- Blockchain
- Cryptocurrency
- Smart contract
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
            encontrados = []
            for individuo in onto.individuals():
                if termino.lower() in individuo.name.lower():
                    encontrados.append(individuo)
            
            if encontrados:
                st.success(f"✅ Se encontraron **{len(encontrados)}** resultados para '{termino}':")
                st.markdown("---")
                
                for ind in encontrados:
                    with st.container():
                        mostrar_info_individuo(ind, enriquecer_dbpedia=enriquecer)
            else:
                st.warning(f"⚠️ No se encontraron resultados para '{termino}'")

# ==================== BÚSQUEDA POR CLASE ====================
elif tipo_busqueda == "📂 Búsqueda por clase":
    st.subheader("📂 Búsqueda por clase")
    
    clases = sorted([cls.name for cls in onto.classes() if hasattr(cls, 'name')])
    
    if not clases:
        st.warning("No se encontraron clases en la ontología")
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
                    for c in onto.classes():
                        if c.name == clase_seleccionada:
                            clase = c
                            break

                if clase:
                    instancias = list(clase.instances())
                else:
                    instancias = []
                
                if instancias:
                    st.success(f"✅ Se encontraron **{len(instancias)}** instancias de la clase '{clase_seleccionada}':")
                    st.markdown("---")
                    
                    for inst in instancias:
                        mostrar_info_individuo(inst, enriquecer_dbpedia=enriquecer)
                else:
                    st.info(f"ℹ️ No hay instancias definidas para la clase '{clase_seleccionada}'")
            
            except Exception as e:
                st.error(f"❌ Error al buscar instancias: {e}")

# ==================== BÚSQUEDA EN DBPEDIA ====================
elif tipo_busqueda == "🌐 Búsqueda en DBpedia":
    st.subheader("🌐 Búsqueda en DBpedia")
    
    if not conexion_online:
        st.warning("⚠️ Sin conexión a internet. Mostrando resultados del cache local.")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        termino_dbpedia = st.text_input(
            "Buscar en DBpedia:",
            placeholder="Ejemplo: Ethereum, Smart Contract, DeFi...",
            key="busqueda_dbpedia"
        )
    with col2:
        st.write("")
        st.write("")
        buscar_dbpedia_btn = st.button("🌐 Buscar", type="primary", use_container_width=True)
    
    if buscar_dbpedia_btn and termino_dbpedia:
        if conexion_online:
            with st.spinner("🔍 Consultando DBpedia..."):
                # PRIMERO intentar con API REST (más rápida)
                st.info("🚀 Usando DBpedia Lookup API...")
                resultados_api = dbpedia.buscar_con_api_rest(termino_dbpedia)
                
                if resultados_api:
                    st.success(f"✅ Se encontraron {len(resultados_api)} resultados para '{termino_dbpedia}'")
                    
                    # Mostrar primer resultado destacado
                    st.markdown("### 📌 Resultado Principal")
                    principal = resultados_api[0]
                    
                    st.markdown(f"**{principal.get('label', 'Sin título')}**")
                    st.write(principal.get('abstract', 'Sin descripción'))
                    
                    if principal.get('categories'):
                        st.write(f"**📂 Categorías:** {', '.join(principal['categories'])}")
                    
                    if principal.get('uri'):
                        st.markdown(f"[🔗 Ver en DBpedia]({principal['uri']})")
                    
                    # Guardar en cache
                    cache_offline.agregar_al_cache(termino_dbpedia, principal)
                    
                    # Mostrar otros resultados
                    if len(resultados_api) > 1:
                        st.markdown("---")
                        st.markdown("### 🔗 Otros Resultados Relacionados")
                        
                        for idx, resultado in enumerate(resultados_api[1:6], 1):
                            with st.expander(f"#{idx} - {resultado.get('label', 'Sin título')}"):
                                st.write(resultado.get('abstract', 'Sin descripción'))
                                if resultado.get('categories'):
                                    st.write(f"**Categorías:** {', '.join(resultado['categories'])}")
                                if resultado.get('uri'):
                                    st.markdown(f"[🔗 Ver en DBpedia]({resultado['uri']})")
                
                else:
                    # Si API REST falla, intentar SPARQL
                    st.info("🔄 Intentando con consulta SPARQL...")
                    resultados_sparql = dbpedia.buscar_simple(termino_dbpedia)
                    
                    if resultados_sparql:
                        st.success(f"✅ Se encontraron {len(resultados_sparql)} resultados")
                        
                        for idx, resultado in enumerate(resultados_sparql, 1):
                            with st.expander(f"#{idx} - {resultado.get('label', 'Sin título')}"):
                                st.write(resultado.get('abstract', 'Sin descripción'))
                                if resultado.get('uri'):
                                    st.markdown(f"[🔗 Ver en DBpedia]({resultado['uri']})")
                    else:
                        st.warning(f"⚠️ No se encontró información para '{termino_dbpedia}' en DBpedia")
                        st.info("💡 Intenta con términos en inglés como: Bitcoin, Ethereum, Blockchain, Cryptocurrency")
        else:
            # Modo offline
            resultados_cache = cache_offline.buscar_en_cache(termino_dbpedia)
            
            if resultados_cache:
                st.info(f"💾 Mostrando {len(resultados_cache)} resultados del cache local")
                
                for datos in resultados_cache:
                    st.markdown("---")
                    st.markdown(f"**{datos.get('label', 'Sin título')}**")
                    st.write(datos.get("abstract", "")[:300] + "...")
            else:
                st.warning("⚠️ Sin conexión y sin datos en cache para este término")

# ==================== EXPLORAR ONTOLOGÍA ====================
else:
    st.subheader("🗂️ Explorar ontología completa")
    
    tab1, tab2, tab3 = st.tabs(["📚 Clases", "🔗 Propiedades", "📄 Todos los individuos"])
    
    with tab1:
        st.markdown("### 📚 Clases disponibles en la ontología")
        clases = sorted([cls.name for cls in onto.classes() if hasattr(cls, 'name')])
        
        if clases:
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
            
            filtro = st.text_input("🔍 Filtrar individuos:", placeholder="Escribe para filtrar...")
            
            individuos_filtrados = individuos
            if filtro:
                individuos_filtrados = [ind for ind in individuos if filtro.lower() in ind.name.lower()]
            
            if individuos_filtrados:
                for ind in sorted(individuos_filtrados, key=lambda x: x.name):
                    mostrar_info_individuo(ind, enriquecer_dbpedia=enriquecer)
            else:
                st.warning("No se encontraron individuos con ese filtro")
        else:
            st.warning("⚠️ No hay individuos en la ontología")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p>🎓 Proyecto de Web Semántica - Buscador Semántico de Criptomonedas</p>
    <p>Desarrollado con Streamlit, Owlready2 y DBpedia</p>
</div>
""", unsafe_allow_html=True)