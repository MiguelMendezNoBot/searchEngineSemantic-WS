# 🔍 Semantic Search Engine for Cryptocurrencies

Motor de búsqueda semántico basado en ontologías OWL para consultas sobre criptomonedas.

## 📋 Descripción

Este proyecto utiliza **Owlready2** para trabajar con ontologías y **Streamlit** para crear una interfaz web interactiva que permite realizar búsquedas semánticas sobre información de criptomonedas.

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.8 o superior instalado
- pip (gestor de paquetes de Python)
- Git instalado

### Paso 1: Clonar el repositorio

```bash
git clone git@github.com:MiguelMendezNoBot/searchEngineSemantic-WS.git
cd searchEngineSemantic-WS
```

**Alternativa con HTTPS:**
```bash
git clone https://github.com/MiguelMendezNoBot/searchEngineSemantic-WS.git
cd searchEngineSemantic-WS
```

### Paso 2: Crear entorno virtual

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

✅ Verás `(venv)` al inicio de tu línea de comandos cuando esté activado.

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará automáticamente:
- streamlit
- owlready2

### Paso 4: Verificar la instalación

```bash
pip list
```

Deberías ver `streamlit` y `owlready2` en la lista.

## ▶️ Ejecutar la Aplicación

Con el entorno virtual activado, ejecuta:

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

**Para detener la aplicación:** Presiona `Ctrl + C` en la terminal.

## 🔄 Comandos Útiles

### Desactivar entorno virtual
```bash
deactivate
```

### Activar entorno virtual (sesiones posteriores)

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### Actualizar dependencias
```bash
pip install --upgrade -r requirements.txt
```

## 📁 Estructura del Proyecto

```
searchEngineSemantic-WS/
├── app.py                  # ⭐ Aplicación principal de Streamlit
├── criptomonedas.owl       # ⭐ Ontología OWL
├── requirements.txt        # Dependencias del proyecto
├── README.md              # Documentación
├── .gitignore             # Archivos ignorados por Git
└── venv/                  # Entorno virtual (NO se sube a Git)
```

**Nota:** La carpeta `venv/` se crea localmente y no se sube al repositorio.

## 🛠️ Tecnologías Utilizadas

- **Python 3.x** - Lenguaje de programación
- **Streamlit** - Framework para la interfaz web interactiva
- **Owlready2** - Librería para trabajar con ontologías OWL y razonamiento semántico

## 📦 Dependencias

Las dependencias se instalan automáticamente desde `requirements.txt`:

```
streamlit
owlready2
```

## 👤 Autor

Miguel Méndez

**GitHub:** [@MiguelMendezNoBot](https://github.com/MiguelMendezNoBot)

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## 🎓 Proyecto Académico

Este proyecto fue desarrollado como parte del curso de Web Semánticas - UMSS Sexto Semestre.