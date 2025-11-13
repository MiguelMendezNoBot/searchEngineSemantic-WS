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

## 🐛 Solución de Problemas

### Error: "streamlit: command not found"
- Asegúrate de tener el entorno virtual activado
- Reinstala: `pip install streamlit`

### Error al cargar criptomonedas.owl
- Verifica que el archivo esté en la raíz del proyecto
- Revisa las rutas en `app.py`

### Error de permisos en Windows
- Ejecuta PowerShell como administrador
- O usa: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 🌐 Deploy en Producción

### Opción 1: Streamlit Community Cloud (Recomendado - Gratis)

1. Asegúrate de que tu proyecto esté en GitHub
2. Ve a [share.streamlit.io](https://share.streamlit.io)
3. Inicia sesión con tu cuenta de GitHub
4. Click en "New app"
5. Selecciona tu repositorio: `MiguelMendezNoBot/searchEngineSemantic-WS`
6. Rama: `main`
7. Archivo principal: `app.py`
8. Click en "Deploy"

### Opción 2: Render

1. Ve a [render.com](https://render.com)
2. Conecta tu repositorio de GitHub
3. Selecciona "Web Service"
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### Opción 3: Railway

1. Ve a [railway.app](https://railway.app)
2. Conecta tu repositorio
3. Railway detectará automáticamente que es un proyecto Python
4. Despliega automáticamente

## 👤 Autor

Miguel Méndez

**GitHub:** [@MiguelMendezNoBot](https://github.com/MiguelMendezNoBot)

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit tus cambios:
   ```bash
   git commit -m 'Add: Amazing Feature'
   ```
4. Push a la rama:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Abre un Pull Request

## 📞 Contacto y Soporte

Si tienes preguntas, problemas o sugerencias:

- 🐛 Abre un [Issue](https://github.com/MiguelMendezNoBot/searchEngineSemantic-WS/issues)
- 💬 Inicia una [Discussion](https://github.com/MiguelMendezNoBot/searchEngineSemantic-WS/discussions)

## 📚 Recursos Adicionales

- [Documentación de Streamlit](https://docs.streamlit.io)
- [Documentación de Owlready2](https://owlready2.readthedocs.io)
- [Guía de Ontologías OWL](https://www.w3.org/TR/owl2-overview/)

---

⭐ **Si este proyecto te fue útil, considera darle una estrella en GitHub!**

---

## 🎓 Proyecto Académico

Este proyecto fue desarrollado como parte del curso de Web Semánticas - UMSS Sexto Semestre.