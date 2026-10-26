# Tareas: Organizador de tareas académicas

**Documentos de entrada**: Diseño en `specs/001-organizador-tareas-academicas/`

**Prerrequisitos**: `plan.md`, `spec.md`, `research.md`, `data-model.md`,
`contracts/api.md` y `quickstart.md`.

**Pruebas**: Son obligatorias según la Constitución del proyecto; cada historia
incluye pruebas automatizadas antes de su implementación.

**Organización**: Las tareas se agrupan por historia para mantener incrementos
demostrables y comprobables.

## Fase 1: Preparación del proyecto

**Propósito**: Inicializar el único proyecto Python y sus dependencias.

- [X] T001 Crear `pyproject.toml` para Python 3.12 con configuración editable de setuptools, dependencias de ejecución `fastapi`, `uvicorn` y `tzdata`, dependencias de desarrollo `pytest`, `httpx` y `pytest-playwright`, y configuración de pytest.
- [X] T002 [P] Crear el paquete de aplicación en `app/__init__.py` y el directorio de recursos estáticos mediante `app/static/.gitkeep`.
- [X] T003 [P] Crear el paquete de pruebas en `tests/__init__.py`.

---

## Fase 2: Base compartida

**Propósito**: Preparar la persistencia SQLite, el arranque de FastAPI y los
recursos de prueba necesarios antes de las historias.

**Bloqueo**: Las historias no empiezan hasta completar esta fase.

- [X] T004 Implementar en `app/db.py` la ruta de base configurable mediante `UPB_TASKS_DB_PATH`, su valor predeterminado en la carpeta local de datos del usuario, conexiones breves y activación de claves foráneas en cada conexión.
- [X] T005 Inicializar en `app/db.py` las tablas `materias` y `tareas` con los campos, relaciones, nulabilidad y restricciones descritos en `data-model.md`; definir `tareas.materia_id` con borrado restringido y consultas SQLite parametrizadas.
- [X] T006 [P] Crear en `app/main.py` la fábrica FastAPI, configurar la ruta `/` para servir `app/static/index.html`, montar `app/static/` bajo `/static` y establecer el punto de inyección de la ruta de base de datos para pruebas.
- [X] T007 Crear en `tests/conftest.py` fixtures pytest que usen `TestClient` y una base SQLite temporal independiente por prueba, inicializando la aplicación mediante `app/main.py`.

**Punto de control**: la aplicación arranca con la base aislable en pruebas y
queda configurada para servir los recursos estáticos cuando la historia P1 cree
la página principal.

---

## Fase 3: Historia de usuario 1 — Organizar materias y registrar tareas
(Prioridad: P1) — MVP

**Objetivo**: Registrar materias y tareas asociadas, con sus campos obligatorios,
validación de datos y persistencia local.

**Prueba independiente**: Crear una materia y una tarea válida, consultar los
datos guardados y comprobar su asociación; reiniciar la conexión y confirmar que
siguen disponibles. Verificar también campos ausentes, vacíos y fuera de límite.

### Pruebas de la historia 1

- [X] T008 [US1] Escribir en `tests/test_api.py` pruebas de contrato para `GET /api/materias`, `POST /api/materias`, `GET /api/tareas` y `POST /api/tareas`, incluyendo respuestas exitosas, persistencia, materia inexistente y errores `404` y `422`.
- [X] T009 [US1] Escribir en `tests/test_api.py` pruebas de validación para nombre de materia entre 1 y 100 caracteres, título entre 1 y 150 caracteres, descripción opcional de hasta 2.000 caracteres, espacios externos, color `#RRGGBB` y materias con igual nombre pero distinto identificador.

### Implementación de la historia 1

- [X] T010 [US1] Crear en `app/schemas.py` modelos de entrada y salida de Materia y Tarea; respetar literalmente «nombre obligatorio de 1 a 100 caracteres», «color `#RRGGBB`», «título obligatorio de 1 a 150 caracteres» y «descripción opcional de hasta 2.000 caracteres» después de recortar espacios externos.
- [X] T011 [US1] Implementar en `app/db.py` operaciones parametrizadas para crear y listar materias, crear tareas asociadas y listar tareas con los campos de `data-model.md`.
- [X] T012 [US1] Implementar en `app/main.py` `GET /api/materias`, `POST /api/materias`, `GET /api/tareas` y `POST /api/tareas`, con validación, códigos `200`, `201`, `404`, `422` y mensajes de error en español.
- [X] T013 [P] [US1] Crear en `app/static/index.html` formularios etiquetados para registrar materia con nombre y color, y tarea con título, descripción opcional, materia y fecha de entrega.
- [X] T014 [P] [US1] Crear en `app/static/styles.css` estilos base responsivos para los formularios de materias y tareas, con controles legibles, foco visible y diseño utilizable en celular y computadora.
- [X] T015 [US1] Implementar en `app/static/app.js` el envío de los formularios a la API, la carga de materias y tareas iniciales, mensajes de validación en español y creación segura de contenido con APIs DOM que no interpreten texto de usuario como HTML.

**Punto de control**: la historia P1 puede demostrarse sin implementar filtros ni
etiquetas temporales.

---

## Fase 4: Historia de usuario 2 — Consultar prioridades y vencimientos
(Prioridad: P2)

**Objetivo**: Ordenar tareas por vencimiento y distinguir las pendientes vencidas
o urgentes usando horas transcurridas.

**Prueba independiente**: Con una base temporal y un instante actual controlado,
consultar tareas vencidas, que vencen ahora, dentro de 48 horas exactas y después
de 48 horas; comprobar las etiquetas y el orden estable.

### Pruebas de la historia 2

- [ ] T016 [P] [US2] Escribir en `tests/test_deadlines.py` pruebas con reloj controlado para vencimiento igual al instante actual, posterior inmediato, límite exacto de 48 horas, posterior al límite y tareas completadas.
- [ ] T017 [P] [US2] Añadir en `tests/test_api.py` pruebas para el orden ascendente por vencimiento y el desempate estable por identificador en tareas con la misma fecha y hora.
- [ ] T018 [US2] Añadir en `tests/test_api.py` pruebas para fechas-horas con desplazamiento UTC, zona IANA, fecha sin hora interpretada al final del día local y rechazo de fecha local inexistente o inconsistente con la zona.

### Implementación de la historia 2

- [X] T019 [US2] Crear en `app/deadlines.py` funciones para normalizar fechas-horas a UTC, convertir fechas sin hora al inicio exclusivo del día local siguiente y calcular vencida si `vencimiento <= ahora` y urgente si `ahora < vencimiento <= ahora + 48 horas`.
- [X] T020 [US2] Actualizar en `app/db.py` la consulta de tareas para ordenarlas por vencimiento UTC ascendente y luego por identificador ascendente, conservando la precisión fija y la zona horaria para presentación local.
- [X] T021 [US2] Actualizar en `app/schemas.py` la validación de fechas ISO de fecha o fecha-hora con desplazamiento, zona horaria IANA y rechazo de horas locales inexistentes o inconsistentes.
- [X] T022 [US2] Actualizar en `app/main.py` la respuesta del listado para calcular `vencida` y `urgente` a partir de un solo instante UTC por respuesta; mantener ambas falsas para tareas completadas.
- [ ] T023 [P] [US2] Actualizar en `app/static/app.js` la presentación del vencimiento en hora local y las etiquetas textuales «Vencida» y «Urgente», sin comunicar prioridad únicamente por color.
- [ ] T024 [P] [US2] Actualizar en `app/static/styles.css` los estilos distinguibles de vencida y urgente, manteniendo señales textuales, contraste, foco visible y adaptación a celular y computadora.

**Punto de control**: el listado muestra prioridades temporales correctas y
deterministas para una tarea completada o pendiente.

---

## Fase 5: Historia de usuario 3 — Actualizar y filtrar tareas
(Prioridad: P3)

**Objetivo**: Marcar tareas como completadas, filtrar por materia y estado, y
proteger las tareas asociadas al intentar borrar una materia.

**Prueba independiente**: Crear tareas de varias materias y estados, combinar
ambos filtros y comprobar que solo aparecen coincidencias; completar una tarea
y verificar que una materia con tareas no pueda borrarse.

### Pruebas de la historia 3

- [ ] T025 [P] [US3] Añadir en `tests/test_api.py` pruebas para filtrar tareas por materia, por estado y por ambos filtros a la vez, incluyendo resultados vacíos y filtros inválidos.
- [ ] T026 [US3] Añadir en `tests/test_api.py` pruebas para `PATCH /api/tareas/{tarea_id}/completar`, tarea inexistente, completar idempotentemente y `DELETE /api/materias/{materia_id}` para materia vacía, inexistente y con tareas asociadas.

### Implementación de la historia 3

- [ ] T027 [US3] Implementar en `app/db.py` filtros parametrizados por materia y estado, actualización idempotente a `completada` y borrado de materia sin tareas; mantener la clave foránea y la regla «una materia con una o más tareas asociadas no puede borrarse».
- [ ] T028 [US3] Implementar en `app/main.py` filtros opcionales `materia_id` y `estado` en `GET /api/tareas`, `PATCH /api/tareas/{tarea_id}/completar` y `DELETE /api/materias/{materia_id}`, con respuestas `200`, `204`, `404`, `409` y errores en español.
- [ ] T029 [US3] Añadir en `app/static/index.html` controles etiquetados para filtrar por materia y estado, marcar tareas como completadas y solicitar el borrado de materias.
- [ ] T030 [US3] Actualizar en `app/static/app.js` el listado filtrado con intersección de criterios, la acción de completar, el borrado de materias, la explicación del conflicto `409` y estados vacíos con opción clara para quitar filtros.
- [ ] T031 [US3] Actualizar en `app/static/styles.css` la disposición responsiva de filtros, acciones de tarea, estados vacíos y confirmación de conflicto, con operación por teclado y foco visible.

**Punto de control**: los filtros combinados y los cambios de estado se verifican
sin alterar las reglas de vencimiento de la historia P2.

---

## Fase 6: Pulido y validación transversal

**Propósito**: Verificar flujos de extremo a extremo, accesibilidad básica y
documentación de ejecución en el stack acordado.

- [ ] T032 [P] Escribir en `tests/test_ui.py` pruebas Playwright de creación de materia y tarea, validación visible, filtros, completar tarea, conflicto al borrar materia y contenido seguro en vistas de 390 × 844 y 1366 × 768.
- [X] T033 Añadir en `tests/test_ui.py` pruebas de accesibilidad de requisitos: etiquetas accesibles en controles principales, navegación por teclado y nombres o textos que identifiquen materias sin depender solo del color.
- [ ] T034 Actualizar `specs/001-organizador-tareas-academicas/quickstart.md` con la instalación de dependencias de desarrollo, instalación de Chromium para Playwright, ejecución de pytest y arranque local en `127.0.0.1`.
- [ ] T035 Ejecutar `python -m pytest` y corregir cualquier fallo en `tests/test_api.py`, `tests/test_deadlines.py`, `tests/test_ui.py`, `app/main.py`, `app/db.py`, `app/schemas.py`, `app/deadlines.py`, `app/static/index.html`, `app/static/styles.css` o `app/static/app.js` antes de declarar la funcionalidad terminada.
- [ ] T036 Ejecutar los escenarios de `specs/001-organizador-tareas-academicas/quickstart.md` y ajustar ese documento si algún comando o resultado esperado no coincide con el diseño final.

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Preparación (Fase 1)**: no depende de otras fases.
- **Base compartida (Fase 2)**: depende de la preparación y bloquea las
  historias.
- **Historia 1 (Fase 3)**: depende de la base compartida.
- **Historia 2 (Fase 4)**: depende de la historia 1, pues amplía el listado y
  presentación de las tareas creadas.
- **Historia 3 (Fase 5)**: depende de la historia 1 y usa el listado de la
  historia 2; se recomienda implementarla después de la historia 2 para evitar
  cambios simultáneos en `app/main.py` y `app/static/app.js`.
- **Pulido (Fase 6)**: depende de las historias que se quieran entregar.

### Dependencias por historia

- **US1 (P1)**: T008 y T009 definen los casos automatizados; T010–T015
  implementan validación, persistencia, rutas e interfaz después de T004–T007.
- **US2 (P2)**: T016–T018 preceden a T019–T024; depende de los datos y rutas de
  tareas de US1.
- **US3 (P3)**: T025–T026 preceden a T027–T031; depende del modelo y listado de
  tareas introducidos en US1 y ampliados en US2.
- **Pulido**: T032 y T033 comparten `tests/test_ui.py` y se coordinan en una
  edición o se realizan en secuencia. T034 no modifica código y puede prepararse
  en paralelo. T035–T036 se ejecutan al terminar los cambios previos.

### Oportunidades de paralelismo

- **Fase 1**: T002 y T003 son independientes de T001 si las carpetas existen;
  deben finalizar antes de las tareas que escriben en sus paquetes.
- **Fase 2**: T006 puede desarrollarse en paralelo con T004–T005; T007 depende
  de que T006 permita inyectar la base temporal.
- **US1**: T008 y T009 modifican el mismo archivo y se realizan en secuencia.
  T013 y T014 pueden escribirse en paralelo con los módulos Python; T010 es
  independiente de `app/db.py`.
- **US2**: T016 trabaja en `tests/test_deadlines.py`; T017 y T018 comparten
  `tests/test_api.py` y se coordinan en una edición o se realizan en secuencia.
  T019 es independiente en `app/deadlines.py`.
- **US3**: T025 y T026 modifican `tests/test_api.py` y se realizan en secuencia;
  implementación de base, rutas e interfaz se realiza en secuencia por compartir
  responsabilidades.
- **Pulido**: T032 y T033 comparten `tests/test_ui.py` y se coordinan en una
  edición o se realizan en secuencia; T034 puede prepararse en paralelo.

### Ejemplo de ejecución en paralelo: US1

```text
Grupo A: T008 y T009 — pruebas de contrato y validación en tests/test_api.py, en secuencia
Grupo B: T010 — modelos de entrada y salida en app/schemas.py
Grupo C: T013 y T014 — formularios y estilos en app/static/index.html y styles.css
```

### Ejemplo de ejecución en paralelo: US2

```text
Grupo A: T016 — límites temporales en tests/test_deadlines.py
Grupo B: T017 y T018 — orden y fechas de API en tests/test_api.py, en secuencia
```

Tras completar y observar el fallo inicial de las pruebas, implementar T019 en
`app/deadlines.py` antes de continuar con la integración.

## Estrategia de implementación

### MVP primero (solo historia de usuario 1)

1. Completar preparación y base compartida.
2. Implementar US1 con pruebas automatizadas de materia, tarea, validación y
   persistencia.
3. Detenerse en el punto de control y demostrar la creación y consulta local.

### Entrega incremental

1. Añadir US2 y verificar orden, vencimiento y urgencia con reloj controlado.
2. Añadir US3 y verificar filtros combinados, completar tarea y protección al
   borrar materia.
3. Finalizar con pruebas de interfaz, adaptación, accesibilidad básica y guía de
   validación rápida.

## Notas

- `[P]` indica tareas en archivos distintos y sin dependencias pendientes.
- `[US1]`, `[US2]` y `[US3]` enlazan cada tarea con la historia de usuario.
- Las pruebas automatizadas son obligatorias por la Constitución; no se omiten
  aunque el template las describa como opcionales.
- Todos los elementos de la lista conservan checkbox, identificador secuencial
  y ruta concreta del archivo afectado.
