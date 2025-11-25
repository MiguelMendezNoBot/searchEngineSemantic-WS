import streamlit as st
from owlready2 import *
import os

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
    </style>
""", unsafe_allow_html=True)

# ==================== TÍTULO ====================
st.title("🔍 Buscador Semántico de Criptomonedas")
st.markdown("### Ontología OWL - Web Semántica")
st.markdown("---")

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

def mostrar_info_individuo(individuo):
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
            # Formatear valores
            if isinstance(valores, list):
                valores_str = ", ".join([str(v) for v in valores])
            else:
                valores_str = str(valores)
            
            st.write(f"**{prop.name}:** {valores_str}")
    
    if not propiedades_encontradas:
        st.info("No hay propiedades adicionales definidas")
    
    st.markdown("---")

# ==================== SIDEBAR ====================
st.sidebar.header("⚙️ Configuración")

# Cargar ontología
archivo_owl = st.sidebar.text_input(
    "📁 Archivo OWL:", 
    value="criptomonedas.owl",
    help="Nombre del archivo OWL en la carpeta del proyecto"
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
- **Explorar:** Navega por toda la ontología
""")

# ==================== TIPO DE BÚSQUEDA ====================
tipo_busqueda = st.radio(
    "🔎 Selecciona el tipo de búsqueda:",
    ["🔤 Búsqueda por nombre", "📂 Búsqueda por clase", "🗂️ Explorar ontología"],
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
        st.write("")  # Espaciador
        st.write("")  # Espaciador
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
                
                # Mostrar resultados en columnas
                for ind in encontrados:
                    with st.container():
                        mostrar_info_individuo(ind)
            else:
                st.warning(f"⚠️ No se encontraron resultados para '{termino}'")
                st.info("💡 Intenta con otro término o explora la ontología para ver qué hay disponible")

# ==================== BÚSQUEDA POR CLASE ====================
elif tipo_busqueda == "📂 Búsqueda por clase":
    st.subheader("📂 Búsqueda por clase")
    
    # Obtener lista de clases
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

# ==================== EXPLORAR ONTOLOGÍA ====================
else:  # Explorar ontología
    st.subheader("🗂️ Explorar ontología completa")
    
    # Tabs para organizar
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

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; padding: 2rem;'>
    <p>🎓 Proyecto de Web Semántica - Buscador Semántico de Criptomonedas</p>
    <p>Desarrollado con Streamlit y Owlready2</p>
</div>
""", unsafe_allow_html=True)