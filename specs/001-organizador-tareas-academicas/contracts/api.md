# Contrato de interfaz HTTP

Todos los mensajes y errores dirigidos al estudiante están en español. La página
estática se sirve desde el mismo origen que la API. Las rutas de datos tienen el
prefijo `/api`.

## Formatos comunes

- Los cuerpos de solicitud y las respuestas usan JSON con nombres de campos en
  español.
- Los identificadores son enteros positivos.
- `vencimiento` acepta una fecha ISO (`AAAA-MM-DD`) o una fecha-hora ISO 8601
  con desplazamiento UTC; `zona_horaria` es un identificador IANA. Una fecha
  sin hora se interpreta como el final de ese día en la zona indicada. Las horas
  locales inexistentes o inconsistentes con la zona se rechazan.
- Materias: nombre obligatorio de 1 a 100 caracteres tras recortar espacios;
  color `#RRGGBB`.
- Tareas: título obligatorio de 1 a 150 caracteres; descripción opcional de
  hasta 2.000 caracteres; materia y vencimiento obligatorios.
- Estado: `pendiente` o `completada`.

## Recursos

### `GET /api/materias`

Lista las materias existentes.

**Respuesta `200`**:

```json
[
  { "id": 1, "nombre": "Matemáticas", "color": "#3366CC" }
]
```

### `POST /api/materias`

Crea una materia.

**Solicitud**:

```json
{ "nombre": "Matemáticas", "color": "#3366CC" }
```

**Respuesta `201`**: objeto de materia creado, con `id`.

### `DELETE /api/materias/{materia_id}`

Borra una materia que no tenga tareas asociadas.

- **Respuesta `204`**: materia borrada.
- **Respuesta `404`**: materia inexistente.
- **Respuesta `409`**: la materia tiene tareas asociadas; no se borra ni se
  alteran esas tareas.

### `GET /api/tareas`

Lista tareas ordenadas por vencimiento más próximo y, en caso de empate, por
identificador ascendente.

**Filtros opcionales**:

- `materia_id`: identificador de materia.
- `estado`: `pendiente` o `completada`.

Al combinar filtros, se deben cumplir ambos.

**Respuesta `200`**:

```json
[
  {
    "id": 8,
    "materia_id": 1,
    "materia_nombre": "Matemáticas",
    "materia_color": "#3366CC",
    "titulo": "Taller",
    "descripcion": null,
    "vencimiento": "2026-10-27T13:00:00-04:00",
    "estado": "pendiente",
    "vencida": false,
    "urgente": true
  }
]
```

Las propiedades `vencida` y `urgente` se calculan al generar la respuesta. No
pueden ser verdaderas simultáneamente. Las tareas completadas tienen ambas en
`false`. Para tareas de solo fecha, `vencimiento` se devuelve como la fecha local
original (`AAAA-MM-DD`).

### `POST /api/tareas`

Crea una tarea pendiente asociada a una materia existente.

**Solicitud**:

```json
{
  "materia_id": 1,
  "titulo": "Taller",
  "descripcion": "Resolver los ejercicios indicados",
  "vencimiento": "2026-10-27T13:00:00-04:00",
  "zona_horaria": "America/Bogota"
}
```

**Respuesta `201`**: objeto de tarea creado, incluidos `id` y `estado`.
Para un vencimiento de solo fecha, `vencimiento` puede ser `"2026-10-27"`; la
fecha corresponde al día local indicado por `zona_horaria`.

### `PATCH /api/tareas/{tarea_id}/completar`

Marca como completada una tarea pendiente. No acepta cambios de título,
descripción, materia o vencimiento.

- **Respuesta `200`**: tarea actualizada con estado `completada`.
- **Respuesta `404`**: tarea inexistente.
- Completar una tarea ya completada no cambia otros datos y devuelve su estado
  `completada`.

## Errores

Los errores tienen una forma legible y uniforme:

```json
{
  "error": {
    "codigo": "validacion",
    "mensaje": "El título no puede superar 150 caracteres."
  }
}
```

- `422`: solicitud incompleta, formato inválido o límite de campo excedido.
- `404`: materia o tarea no existente.
- `409`: conflicto de integridad, por ejemplo borrar una materia con tareas.
- `500`: fallo inesperado; el cliente presenta un mensaje genérico en español y
  el servidor conserva el detalle para diagnóstico, sin exponerlo en la interfaz.

## Interfaz estática

- `GET /`: devuelve la página principal.
- `/static/styles.css` y `/static/app.js`: recursos estáticos de la interfaz.
