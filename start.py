"""
Archivo de inicio para el deploy en Render.
Importa la aplicación FastAPI desde la estructura del proyecto.
"""

from src.api.main import app
import os
import sys

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar la aplicación FastAPI

# Configurar para producción
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
