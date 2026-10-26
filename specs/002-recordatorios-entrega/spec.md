# Especificación de funcionalidad: Recordatorios de entrega

**Rama de funcionalidad**: `No creada`

**Fecha de creación**: 2026-10-26

**Estado**: Borrador

**Entrada**: Descripción de la persona usuaria: «Agregar recordatorios: el estudiante recibe una notificación un día antes de la fecha de entrega de cada tarea pendiente.»

## Escenarios de usuario y pruebas

### Historia de usuario 1: Recibir un recordatorio de entrega (Prioridad: P1)

Como estudiante de la UPB, quiero recibir una notificación un día antes de la
fecha de entrega de cada tarea pendiente, para tener tiempo de prepararme y
evitar olvidarla.

**Por qué esta prioridad**: El aviso oportuno es el valor central de esta
funcionalidad y debe demostrarse de forma independiente.

**Prueba independiente**: Crear una tarea pendiente con vencimiento futuro,
conceder permiso para recibir notificaciones y comprobar que se emite un único
aviso en el momento acordado, con el título, la materia y la fecha de entrega
correctos.

**Escenarios de aceptación**:

1. **Dado** que una tarea pendiente tiene una fecha de entrega y el estudiante
   autorizó las notificaciones y el organizador está abierto, **cuando** llega
   el instante situado exactamente 24 horas antes del vencimiento,
   **entonces** el estudiante recibe una notificación que identifica la tarea,
   la materia y la fecha de entrega.
2. **Dado** que una tarea está completada antes del momento de su recordatorio,
   **cuando** llega ese momento, **entonces** no se envía una notificación para
   esa tarea.
3. **Dado** que el permiso para notificar no está disponible o fue denegado,
   **cuando** el estudiante consulta la configuración de recordatorios,
   **entonces** recibe una explicación y puede seguir usando las demás
   funciones del organizador.
4. **Dado** que el organizador no está abierto cuando llega el instante del
   recordatorio, **cuando** el estudiante vuelve a abrirlo después,
   **entonces** no recibe una notificación tardía para ese aviso.

### Historia de usuario 2: Gestionar permisos y casos límite (Prioridad: P2)

Como estudiante, quiero conocer y controlar si las notificaciones están
habilitadas, para saber si puedo confiar en los recordatorios.

**Por qué esta prioridad**: El aviso depende de la autorización del estudiante y
de las capacidades del dispositivo; su estado debe ser comprensible.

**Prueba independiente**: Probar los estados de permiso autorizado, pendiente y
denegado, y una tarea cuyo momento de recordatorio ya pasó al crearla.

**Escenarios de aceptación**:

1. **Dado** que las notificaciones no están autorizadas, **cuando** el estudiante
   activa los recordatorios, **entonces** el sistema solicita autorización y
   muestra si quedó concedida o denegada.
2. **Dado** que una tarea se crea después del momento previsto para su
   recordatorio, **cuando** se guarda, **entonces** no se envía una notificación
   inmediata ni un aviso tardío para esa tarea.

### Casos límite

- Si el estudiante completa una tarea antes del recordatorio, no debe recibir el
  aviso de esa tarea.
- Si una tarea se completa después de que se envió el aviso, no debe enviarse
  otro aviso por el mismo vencimiento.
- Si se crea una tarea cuando su momento de recordatorio ya pasó, no se envía
  un aviso inmediato ni tardío.
- Si el organizador está cerrado en el momento del aviso, no se recupera esa
  notificación al volver a abrirlo.
- Las tareas con solo fecha usan su vencimiento existente: el final del día
  local seleccionado; el recordatorio ocurre exactamente 24 horas antes de ese
  instante.
- Si se revoca el permiso de notificaciones, el sistema informa que los avisos
  podrían no mostrarse y mantiene disponibles las demás funciones.
- Los recordatorios se entregan únicamente mientras el organizador está
  abierto y el permiso de notificación está concedido.
- Cada recordatorio se envía 24 horas exactas antes del instante de vencimiento.
- Si el momento del recordatorio ya pasó al crear la tarea, se omite el aviso.

## Requisitos

### Requisitos funcionales

- **RF-001**: El sistema DEBE permitir al estudiante habilitar los recordatorios
  de entrega y solicitar permiso para enviar notificaciones.
- **RF-002**: El sistema DEBE programar un recordatorio por cada tarea pendiente
  para el instante situado exactamente 24 horas antes de su vencimiento.
- **RF-003**: El sistema DEBE identificar en la notificación el título de la
  tarea, su materia y su fecha de entrega.
- **RF-004**: El sistema NO DEBE enviar un recordatorio pendiente si la tarea se
  completó antes del momento del aviso.
- **RF-005**: El sistema DEBE informar si los recordatorios no pueden enviarse
  por falta de permiso o por limitaciones del dispositivo, sin impedir el uso
  de otras funciones.
- **RF-006**: El sistema DEBE enviar el recordatorio únicamente si el
  organizador está abierto y el permiso de notificación está concedido en el
  instante previsto.
- **RF-007**: El sistema NO DEBE recuperar ni enviar más tarde un recordatorio
  omitido porque el organizador estaba cerrado cuando llegó su instante.
- **RF-008**: El sistema NO DEBE enviar una notificación inmediata ni tardía
  para una tarea creada después del instante de su recordatorio.
- **RF-009**: Para tareas ingresadas solo con fecha, el sistema DEBE calcular el
  recordatorio 24 horas antes del vencimiento al final del día local
  correspondiente.

### Entidades principales

- **Recordatorio**: aviso asociado a una tarea pendiente, con un momento
  previsto, estado de autorización y resultado de entrega.
- **Tarea**: tarea existente del organizador, con título, materia, fecha de
  entrega, zona horaria y estado pendiente o completada.

## Criterios de éxito

### Resultados medibles

- **CE-001**: El 100 % de las tareas pendientes cuyo recordatorio ocurre con el
  organizador abierto y el permiso concedido recibe un único aviso exactamente
  24 horas antes del vencimiento.
- **CE-002**: El 100 % de las tareas completadas antes del momento del aviso no
  genera una notificación.
- **CE-003**: En pruebas de aceptación, el 100 % de las notificaciones muestra
  el título, la materia y la fecha de entrega correspondientes.
- **CE-004**: Cuando el organizador está cerrado al llegar el instante de aviso,
  no se entrega una notificación tardía al volver a abrirlo.
- **CE-005**: Cuando no se dispone de permiso o capacidad de notificación, el
  estudiante puede identificar la causa y seguir usando las funciones
  principales del organizador.

## Supuestos

- Esta funcionalidad amplía el organizador local de tareas académicas de la
  UPB; incorpora recordatorios a su alcance anterior, sin cambiar el registro,
  consulta o finalización de tareas.
- Depende de las tareas, sus estados, vencimientos y zonas horarias definidos en
  la [especificación del organizador académico](../001-organizador-tareas-academicas/spec.md).
- Se aplica un recordatorio a cada tarea pendiente y no se repite después de
  enviarlo.
- La zona horaria del recordatorio coincide con la zona horaria guardada en la
  tarea.
- Las notificaciones se muestran mientras el organizador está abierto; la
  entrega en segundo plano con el organizador cerrado no forma parte de esta
  funcionalidad.
- «Un día antes» significa exactamente 24 horas antes del instante de
  vencimiento, no el día calendario anterior a una hora fija.
- Si una tarea se crea después de su momento previsto de recordatorio, no recibe
  una notificación inmediata ni tardía.
