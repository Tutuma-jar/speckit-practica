# Investigación y decisiones técnicas

**Funcionalidad**: Organizador de tareas académicas

## Aplicación y estructura

- **Decisión**: Mantener un único proyecto Python con `app/main.py`, `app/db.py`,
  `app/schemas.py` y los archivos HTML/CSS/JavaScript en `app/static/`.
- **Justificación**: FastAPI puede servir los recursos estáticos y exponer la API
  desde el mismo proceso. Una estructura pequeña satisface el requisito y la
  constitución de simplicidad.
- **Alternativas consideradas**: Separar backend y frontend, añadir plantillas
  renderizadas por el servidor o incorporar un framework de interfaz. Se
  descartan porque la interfaz estática puede consumir la API directamente y no
  se requiere compilación ni renderizado en servidor.
- **Fuentes**: [FastAPI: archivos estáticos](https://fastapi.tiangolo.com/tutorial/static-files/).

## Persistencia y relaciones

- **Decisión**: Usar SQLite desde la biblioteca estándar `sqlite3`, SQL
  parametrizado y una conexión breve por operación. Activar claves foráneas en
  cada conexión y configurar la relación tarea-materia para restringir el
  borrado de una materia con tareas asociadas.
- **Justificación**: La aplicación es local, de bajo volumen y de una sola
  persona. SQLite proporciona persistencia sin un servicio de base de datos
  adicional. Las consultas parametrizadas protegen el manejo de datos y la clave
  foránea hace cumplir la relación definida.
- **Alternativas consideradas**: Base de datos remota, ORM, conexión global y
  borrado en cascada. No se justifican por el alcance; el borrado en cascada
  además contradiría la política de conservar las tareas asociadas.
- **Ubicación del archivo**: Usar una ruta configurable mediante
  `UPB_TASKS_DB_PATH`; si no se configura, seleccionar una carpeta de datos del
  usuario adecuada al sistema operativo, no el directorio de trabajo.
- **Fuentes**: [SQLite: claves foráneas](https://www.sqlite.org/foreignkeys.html),
  [SQLite: transacciones](https://www.sqlite.org/lang_transaction.html),
  [Python 3.12: sqlite3](https://docs.python.org/3.12/library/sqlite3.html).

## Fechas, zonas horarias y prioridades

- **Decisión**: El navegador enviará la fecha y hora seleccionadas con
  desplazamiento UTC explícito y zona horaria IANA. El servidor normalizará el
  instante a UTC con precisión fija para persistencia, orden y comparación;
  conservará la zona para presentar la hora local. Para una fecha sin hora, el
  vencimiento se representa como el inicio exclusivo del día local siguiente.
  La conversión y clasificación se mantienen en `app/deadlines.py`, una función
  acotada y separada para probar con un instante actual controlado.
- **Justificación**: Un campo de fecha/hora local no identifica por sí solo un
  instante. La normalización a UTC permite ordenar y calcular las próximas 48
  horas transcurridas de forma consistente; conservar la zona permite mostrar
  correctamente las entregas al estudiante.
- **Reglas**: En cada listado, calcular un solo instante actual UTC. Una tarea
  pendiente está vencida si `vencimiento <= ahora`; es urgente si
  `ahora < vencimiento <= ahora + 48 horas`. El instante de vencimiento será
  excluyente al inicio del día siguiente para fechas que no incluyan hora.
  Rechazar fechas locales inexistentes o inconsistentes con su zona y
  desplazamientos, en lugar de desplazarlas silenciosamente. Usar ID como
  segundo criterio de orden.
- **Alternativas consideradas**: Guardar hora local sin zona, asumir la zona del
  servidor o usar días calendario para urgencia. No se eligen porque pueden
  producir instantes ambiguos o contradicen la regla especificada.
- **Fuentes**: [MDN: `datetime-local`](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/datetime-local),
  [Python 3.12: datetime](https://docs.python.org/3.12/library/datetime.html),
  [Python 3.12: zoneinfo](https://docs.python.org/3.12/library/zoneinfo.html).

## Validación y errores

- **Decisión**: Validar los campos de entrada con modelos Pydantic y repetir en
  el servidor las reglas de obligatoriedad, normalización, formato y longitud de
  la especificación. La interfaz puede ofrecer validación adicional, pero no es
  fuente de confianza.
- **Justificación**: Los datos pueden llegar sin pasar por la interfaz. La
  validación del servidor da resultados consistentes para todos los clientes.
- **Reglas de entrada**: Materia con nombre recortado de 1 a 100 caracteres y
  color hexadecimal `#RRGGBB`; tarea con título recortado de 1 a 150 caracteres,
  descripción opcional de hasta 2.000 caracteres, materia existente y
  vencimiento válido.
- **Errores**: `422` para entradas inválidas, `404` para recursos inexistentes y
  `409` cuando una restricción de relación impide borrar una materia asociada.
  Los mensajes para la persona usuaria se presentan en español.
- **Alternativas consideradas**: Confiar solo en atributos HTML o validar
  únicamente restricciones SQLite. No cubren todos los clientes ni las reglas de
  normalización de texto.
- **Fuentes**: [Pydantic: campos](https://docs.pydantic.dev/latest/concepts/fields/),
  [FastAPI: cuerpo de solicitud](https://fastapi.tiangolo.com/tutorial/body/).

## Interfaz web

- **Decisión**: Servir `index.html` en `/`, montar los recursos en `/static` y
  mantener la API bajo `/api`. Usar JavaScript nativo y crear elementos con APIs
  DOM seguras, como `textContent`, para mostrar títulos y descripciones. Usar
  controles semánticos, etiquetas accesibles, foco visible y señales textuales
  además del color.
- **Justificación**: Cumple el stack indicado sin compilación frontend,
  frameworks ni dependencia de plantillas.
- **Alternativas consideradas**: SPA con framework y plantillas del servidor. No
  se justifican para la interfaz de alcance reducido.
- **Privacidad local**: Enlazar el servidor a `127.0.0.1` como valor
  predeterminado; no habilitar CORS ni exposición en red.
- **Fuentes**: [FastAPI: archivos estáticos](https://fastapi.tiangolo.com/tutorial/static-files/).

## Pruebas

- **Decisión**: Usar pytest y `TestClient` con una base SQLite temporal por
  prueba. Separar las pruebas de API y de reglas de vencimiento; permitir que las
  reglas reciban el instante actual para probar límites sin depender del reloj
  real. Añadir pytest-playwright para automatizar los flujos principales,
  navegación por teclado y comprobaciones de interfaz en vistas estrechas y
  anchas.
- **Justificación**: Una base temporal verifica aislamiento y persistencia real
  sin infraestructura externa. Un reloj controlable permite pruebas
  deterministas justo en los límites de vencimiento y urgencia.
- **Alternativas consideradas**: Base en memoria global compartida o pruebas
  manuales como única validación. No bastan para cubrir la persistencia real ni
  la exigencia constitucional de pruebas automatizadas. Playwright agrega un
  navegador de prueba, pero pytest sigue siendo el ejecutor y la dependencia se
  limita al conjunto de pruebas.
- **Fuentes**: [FastAPI: pruebas](https://fastapi.tiangolo.com/tutorial/testing/),
  [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html),
  [pytest: directorios temporales](https://docs.pytest.org/en/stable/how-to/tmp_path.html),
  [Playwright para Python: introducción y complemento de pytest](https://playwright.dev/python/docs/intro).

## Supuestos pendientes de producto

- Los nombres de materias no se consideran únicos en esta versión; cada materia
  tiene un identificador propio. La especificación no define una regla de
  unicidad por nombre.
- Una materia solo se puede borrar si no tiene tareas asociadas. La versión
  actual no contempla borrar ni reasignar tareas, por lo que una materia con
  tareas asociadas permanece protegida.
- La aplicación se ejecuta localmente en el dispositivo que guarda sus datos;
  la interfaz es adaptable a celular y computadora, pero no se incluye
  distribución móvil nativa ni acceso de red compartido.
