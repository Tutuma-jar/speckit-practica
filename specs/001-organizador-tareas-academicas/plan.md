# Plan de implementación: Organizador de tareas académicas

**Rama actual**: `main` | **Fecha**: 2026-10-26 | **Especificación**: [spec.md](spec.md)

**Entrada**: Especificación de funcionalidad en `specs/001-organizador-tareas-academicas/spec.md`

## Resumen

Construir una aplicación web local para que un estudiante registre materias y
tareas, consulte entregas ordenadas, identifique tareas vencidas o urgentes,
marque tareas como completadas y aplique filtros. Se usará un único proyecto
Python 3.12 con FastAPI para la API y los archivos estáticos, SQLite para la
persistencia local, HTML/CSS/JavaScript sin frameworks para la interfaz y pytest
para pruebas automatizadas. La aplicación no requiere cuenta ni servicios
externos.

## Contexto técnico

- **Lenguaje y versión**: Python 3.12; HTML, CSS y JavaScript nativos.
- **Dependencias principales**: FastAPI, Pydantic (incluido con FastAPI), Uvicorn,
  pytest, httpx para `TestClient`, pytest-playwright para pruebas automatizadas
  de interfaz y tzdata para zonas horarias IANA en sistemas que no incluyan la
  base horaria del sistema.
- **Almacenamiento**: SQLite local persistente, con una clave foránea entre
  tareas y materias.
- **Pruebas**: pytest, FastAPI `TestClient` y una base SQLite temporal aislada
  por prueba.
- **Plataforma objetivo**: Python 3.12 y navegador moderno en el mismo
  dispositivo; interfaz adaptable a celular y computadora. El servidor se
  enlaza a `127.0.0.1` y no expone datos a una red externa.
- **Tipo de proyecto**: Aplicación web local de un solo proyecto.
- **Objetivos de rendimiento**: Uso interactivo por una persona y un volumen
  personal de tareas; la especificación no fija una meta numérica ni una carga
  concurrente.
- **Restricciones**: Sin inicio de sesión, sincronización, servicios externos,
  Docker, microservicios, framework de interfaz, ORM ni compilación del frontend.
  Todas las fechas se comparan como instantes UTC; la entrada y presentación
  conservan la zona horaria local. La interfaz usa controles semánticos,
  etiquetas accesibles, foco visible y no comunica estados solo mediante color.
- **Alcance**: Una persona por instalación y dispositivo; materias y tareas
  persistentes; altas y consulta de materias y tareas, borrado de materias solo
  si no tienen tareas asociadas, filtros y acción para completar tareas.
  Edición y eliminación de tareas, recordatorios y colaboración quedan fuera de
  esta versión.

## Revisión de la constitución

### Puerta previa a la investigación

- **Simplicidad primero**: Cumple. Se elige una aplicación, una base SQLite y
  módulos pequeños; no se añaden capas o servicios sin necesidad.
- **Pruebas obligatorias**: Cumple. Los flujos y reglas de negocio tendrán
  pruebas automatizadas con pytest antes de considerarse terminados.
- **Código legible**: Cumple. La estructura limita cada módulo a una
  responsabilidad comprensible y exige documentar decisiones no obvias.
- **Validación de entradas**: Cumple. Las entradas se validan en el servidor y
  se refuerzan con restricciones de base de datos; la validación del navegador
  solo mejora la experiencia.
- **Accesible y responsivo**: Cumple como requisito del diseño de interfaz y
  como escenario de aceptación para celular y computadora.
- **Idioma y criterios académicos**: Cumple. Los documentos y textos visibles
  para estudiantes se redactan en español.

**Resultado de la puerta previa**: Aprobada; no se detectan incumplimientos.

### Revisión posterior al diseño

- **Simplicidad**: Aprobada; un proceso FastAPI, SQLite, una interfaz estática y
  consultas SQL directas.
- **Pruebas y validación**: Aprobadas; pruebas de API, persistencia, límites,
  filtros y fechas con reloj controlable, además de pruebas de navegador para
  los flujos principales en tamaños de celular y computadora, controles
  etiquetados, navegación por teclado y estados no comunicados solo por color.
- **Legibilidad**: Aprobada; módulos pequeños y estructura explícita en el árbol
  del proyecto.
- **Accesibilidad y respuesta adaptable**: Aprobadas como criterios de aceptación
  para ambos tamaños de pantalla; el color no es el único identificador de una
  materia.
- **Documentación en español**: Aprobada; artefactos de diseño y mensajes de la
  aplicación se especifican en español.

**Resultado de la puerta posterior**: Aprobada; el diseño no introduce
incumplimientos ni complejidad injustificada.

## Estructura del proyecto

### Documentación de esta funcionalidad

```text
specs/001-organizador-tareas-academicas/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api.md
└── tasks.md                  # Se genera en la fase /speckit-tasks
```

### Código fuente (raíz del repositorio)

```text
app/
├── main.py                   # Inicio de FastAPI, rutas y archivos estáticos
├── db.py                     # Esquema, conexiones y consultas SQLite
├── schemas.py                # Validación y formas de entrada/salida
├── deadlines.py              # Conversión de fechas y estados temporales
└── static/
    ├── index.html
    ├── styles.css
    └── app.js
tests/
├── conftest.py               # Aplicación y base temporal compartidas
├── test_api.py               # Rutas, validación, filtros y persistencia
├── test_deadlines.py         # Vencimiento, urgencia y límites temporales
└── test_ui.py                # Flujos principales y presentación adaptable
pyproject.toml                # Dependencias, configuración y pytest
```

**Decisión de estructura**: Un solo proyecto en la raíz con el paquete pequeño
`app/`, recursos estáticos y pruebas. La API, la página y sus recursos se sirven
desde el mismo proceso FastAPI. Se omiten carpetas independientes de backend y
frontend, capas de servicios/repositorios, ORM y migraciones dedicadas porque no
son necesarias para este alcance.

La prueba de interfaz usará pytest-playwright y un navegador Chromium instalado
para la ejecución de pruebas; el navegador de prueba no forma parte del
despliegue normal de la aplicación.
