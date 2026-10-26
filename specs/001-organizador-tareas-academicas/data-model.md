# Modelo de datos: Organizador de tareas académicas

## Materia

Representa una asignatura del estudiante.

| Campo | Tipo conceptual | Reglas |
|---|---|---|
| `id` | Entero identificador | Clave primaria; generado por el sistema. |
| `nombre` | Texto | Obligatorio; quitar espacios al inicio y al final; entre 1 y 100 caracteres. No es único en esta versión. |
| `color` | Texto hexadecimal | Obligatorio; formato `#RRGGBB`. |

### Relaciones y ciclo de vida

- Una materia puede tener cero o más tareas.
- Una materia sin tareas asociadas puede borrarse.
- Una materia con una o más tareas asociadas no puede borrarse; se informa el
  conflicto sin borrar ni modificar las tareas.
- No se incluyen operaciones para editar o borrar tareas ni para reasignarlas en
  esta versión.

## Tarea

Representa una responsabilidad académica.

| Campo | Tipo conceptual | Reglas |
|---|---|---|
| `id` | Entero identificador | Clave primaria; generado por el sistema. |
| `materia_id` | Entero | Obligatorio; referencia a una materia existente. |
| `titulo` | Texto | Obligatorio; quitar espacios al inicio y al final; entre 1 y 150 caracteres. |
| `descripcion` | Texto opcional | Nula o hasta 2.000 caracteres; se recortan espacios externos. |
| `vencimiento_utc` | Instante | Obligatorio; ISO 8601 normalizado a UTC con precisión fija. |
| `zona_horaria` | Identificador IANA | Obligatorio; zona del dispositivo al registrar la tarea, usada para mostrar su hora local. |
| `tipo_vencimiento` | Enumeración | `fecha` si se ingresó solo una fecha; `fecha_hora` si se ingresó también una hora. |
| `fecha_local` | Fecha | Obligatoria solo si `tipo_vencimiento` es `fecha`; conserva el día seleccionado para mostrarlo como tal. |
| `estado` | Enumeración | `pendiente` o `completada`; inicialmente `pendiente`. |

### Reglas de fecha y estado

- La fecha sin hora vence al inicio exclusivo del día local siguiente. Para una
  hora ingresada, el vencimiento representa ese instante local.
- Las fechas locales que no existan en la zona indicada se rechazan con un
  mensaje de validación; no se corrigen silenciosamente.
- Una tarea pendiente está vencida cuando su vencimiento es menor o igual al
  instante actual UTC.
- Una tarea pendiente es urgente cuando su vencimiento es posterior al instante
  actual y menor o igual a 48 horas después.
- Las etiquetas de vencida y urgente se calculan al consultar; no se persisten.
- Al completar una tarea, su estado cambia a `completada` y no se presenta como
  pendiente vencida o urgente.
- La lista se ordena por vencimiento UTC ascendente y, en caso de empate, por
  identificador ascendente.

## Filtro de consulta

No requiere almacenamiento propio. El listado acepta opcionalmente un
identificador de materia y un estado. Cuando ambos están presentes, se aplican
conjuntamente. Solo se permiten los estados definidos para las tareas.

## Persistencia y restricciones

- Dos tablas: `materias` y `tareas`.
- `tareas.materia_id` referencia `materias.id` con clave foránea y borrado
  restringido.
- Activar las claves foráneas en cada conexión SQLite.
- Usar consultas parametrizadas y transacciones breves.
- Guardar la base en la carpeta de datos local del usuario o en la ruta
  explícitamente configurada; no en el directorio de trabajo por defecto.
