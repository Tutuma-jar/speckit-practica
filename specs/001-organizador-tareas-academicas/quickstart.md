# Guía de validación rápida

Esta guía se ejecutará cuando el proyecto incluya la implementación. Los comandos
son para PowerShell en Windows y se ejecutan desde la raíz del repositorio.

## Requisitos previos

- Python 3.12 disponible como `py -3.12`.
- Navegador web moderno.
- Conexión a Internet solo para instalar las dependencias iniciales.

## Preparar el entorno

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

El proyecto debe declarar FastAPI, Uvicorn y tzdata como dependencias de
ejecución, y pytest, httpx y pytest-playwright como dependencias de desarrollo.
La primera preparación también instala Chromium para las pruebas de interfaz:

```powershell
python -m playwright install chromium
```

## Ejecutar las pruebas

```powershell
python -m pytest
```

**Resultado esperado**: todas las pruebas pasan, incluyendo creación de materias
y tareas, límites de campos, persistencia en SQLite, filtros, protección de
materias asociadas, cálculos de fecha límite y recorridos principales en vistas
de celular y computadora.

## Ejecutar la aplicación

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abrir `http://127.0.0.1:8000` en el navegador.

**Resultado esperado**: la página se carga en español y permite completar los
flujos principales sin iniciar sesión. El servidor escucha solo en el
dispositivo local.

## Escenarios de aceptación

1. Crear una materia con nombre y color, y luego una tarea con título,
   descripción opcional y fecha de entrega.
2. Verificar que un nombre vacío, un título vacío o campos que superen sus
   límites se rechazan con una explicación.
3. Crear tareas vencidas, con vencimiento exactamente ahora, en menos de 48
   horas, exactamente en 48 horas y después de 48 horas. Verificar las etiquetas
   y el orden. Las pruebas automatizadas controlan el reloj para validar los
   instantes exactos.
4. Aplicar por separado y en combinación los filtros de materia y estado;
   marcar una tarea pendiente como completada.
5. Borrar una materia sin tareas y comprobar que desaparece; intentar borrar una
   materia con tareas y comprobar que se conserva junto con estas y que se
   informa el motivo.
6. Ejecutar las pruebas de navegador con vistas de 390 × 844 y 1366 × 768;
   confirmar que los controles siguen siendo operables, tienen etiquetas
   accesibles, permiten navegación por teclado y que el color no es el único
   indicador de materia.

El contrato HTTP está en [contracts/api.md](contracts/api.md) y las entidades y
reglas de persistencia en [data-model.md](data-model.md).
