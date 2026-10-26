# Especificación de funcionalidad: Organizador de tareas académicas

**Rama de funcionalidad**: `No creada`

**Fecha de creación**: 2026-10-26

**Estado**: Borrador

**Entrada**: Descripción de la persona usuaria: «Quiero una aplicación para estudiantes de la UPB que les ayude a organizar sus tareas académicas. El estudiante puede registrar sus materias (nombre y color). Puede crear tareas asociadas a una materia, con título, descripción opcional y fecha de entrega. Ve un listado de tareas ordenado por fecha de entrega, donde las tareas vencidas se destacan y las próximas 48 horas aparecen como "urgentes". Puede marcar tareas como completadas y filtrarlas por materia o por estado. En esta primera versión no hay inicio de sesión: es un solo usuario por dispositivo. Todo el contenido de la especificación debe estar en español.»

## Aclaraciones

### Sesión 2026-10-26

- P: ¿Qué debe ocurrir con las tareas asociadas cuando el estudiante intenta borrar una materia? → A: Impedir borrar la materia mientras tenga tareas asociadas.
- P: ¿Cuál debe ser la longitud máxima del nombre de una materia, del título de una tarea y de su descripción? → A: Nombre de materia: 100 caracteres; título de tarea: 150 caracteres; descripción: 2.000 caracteres.
- P: ¿Cómo debe calcularse si una tarea está “urgente”? → A: Es urgente si su fecha y hora límite es posterior al momento actual y ocurre dentro de las siguientes 48 horas, incluyendo exactamente el límite de 48 horas.

## Escenarios de usuario y pruebas

### Historia de usuario 1: Organizar materias y registrar tareas (Prioridad: P1)

Como estudiante de la UPB, quiero registrar mis materias y asociarles tareas con
su fecha de entrega, para reunir mis responsabilidades académicas en un solo lugar.

**Prioridad**: Es la función central del producto: permite crear la información
que el estudiante necesita organizar.

**Prueba independiente**: Registrar una materia y una tarea, y comprobar que la
tarea aparece asociada a esa materia y con sus datos visibles.

**Escenarios de aceptación**:

1. **Dado** que no existe una materia con ese nombre, **cuando** el estudiante
   registra una materia indicando nombre y color, **entonces** la materia queda
   disponible para asociarle tareas y se identifica por su nombre y color.
2. **Dado** que existe una materia, **cuando** el estudiante registra una tarea
   con título y fecha de entrega, **entonces** la tarea aparece asociada a esa
   materia.
3. **Dado** que el estudiante está creando una tarea, **cuando** añade una
   descripción, **entonces** esta se muestra junto con la tarea; la descripción
   puede omitirse.
4. **Dado** que falta el nombre o color de una materia, **cuando** el estudiante
   intenta guardarla, **entonces** se informa qué dato obligatorio debe completar
   y la materia no se registra.
5. **Dado** que falta el título, la materia o la fecha de entrega de una tarea,
   **cuando** el estudiante intenta guardarla, **entonces** se informa qué dato
   obligatorio debe completar y la tarea no se registra.
6. **Dado** que el estudiante ya guardó materias y tareas, **cuando** cierra y
   vuelve a abrir la aplicación en el mismo dispositivo, **entonces** esos datos
   siguen disponibles sin iniciar sesión.
7. **Dado** que el estudiante abre la aplicación en otro dispositivo,
   **cuando** consulta sus materias y tareas, **entonces** los datos del primer
   dispositivo no aparecen allí.

---

### Historia de usuario 2: Consultar prioridades y vencimientos (Prioridad: P2)

Como estudiante, quiero ver mis tareas en orden de entrega y distinguir las
vencidas y urgentes, para priorizar qué debo atender.

**Prioridad**: La priorización temporal permite organizar el trabajo una vez
registradas las tareas.

**Prueba independiente**: Crear tareas con fechas anteriores, dentro de las
próximas 48 horas y posteriores; comprobar su orden y etiquetas temporales.

**Escenarios de aceptación**:

1. **Dado** que hay varias tareas pendientes, **cuando** el estudiante consulta
   el listado, **entonces** se ordenan desde la fecha de entrega más próxima
   hasta la más lejana.
2. **Dado** que una tarea pendiente ya superó su fecha y hora límite, **cuando**
   se muestra el listado, **entonces** la tarea se destaca como vencida.
3. **Dado** que una tarea pendiente vence dentro de las siguientes 48 horas,
   **cuando** se muestra el listado, **entonces** se identifica como urgente.
4. **Dado** que una tarea está completada, **cuando** su fecha de entrega ya
   pasó, **entonces** no se destaca como pendiente vencida.

---

### Historia de usuario 3: Actualizar y filtrar tareas (Prioridad: P3)

Como estudiante, quiero marcar tareas como completadas y filtrar el listado por
materia o estado, para concentrarme en el trabajo que necesito revisar.

**Prioridad**: Completar y filtrar las tareas facilita el seguimiento diario y
reduce el ruido en el listado.

**Prueba independiente**: Completar una tarea y aplicar por separado los filtros
de materia y estado; comprobar que cada resultado corresponde al filtro elegido.

**Escenarios de aceptación**:

1. **Dado** que una tarea está pendiente, **cuando** el estudiante la marca como
   completada, **entonces** su estado cambia a completada.
2. **Dado** que hay tareas de varias materias, **cuando** el estudiante elige una
   materia como filtro, **entonces** solo se muestran tareas asociadas a ella.
3. **Dado** que hay tareas pendientes y completadas, **cuando** el estudiante
   filtra por estado, **entonces** solo se muestran tareas del estado elegido.
4. **Dado** que el estudiante selecciona filtros de materia y estado,
   **cuando** consulta el listado, **entonces** se muestran únicamente las tareas
   que cumplen ambos filtros.
5. **Dado** que todavía no hay materias registradas, **cuando** el estudiante
   consulta el listado, **entonces** ve un aviso comprensible y una opción para
   registrar la primera materia.
6. **Dado** que un filtro no coincide con ninguna tarea, **cuando** se muestra el
   resultado, **entonces** el estudiante ve un aviso comprensible y puede quitar
   el filtro.
7. **Dado** que dos o más tareas tienen la misma fecha y hora límite,
   **cuando** el estudiante consulta el listado varias veces, **entonces** todas
   aparecen y su orden relativo se mantiene estable.
8. **Dado** que el estudiante usa un celular o una computadora, **cuando** crea
   una materia o tarea y consulta el listado, **entonces** puede operar los
   controles y distinguir la información en ambos tipos de pantalla sin depender
   únicamente del color.
9. **Dado** que una materia tiene tareas asociadas, **cuando** el estudiante
   intenta borrarla, **entonces** el sistema impide el borrado y explica que
   primero debe resolver o reasignar sus tareas.

### Casos límite

- Si no hay materias registradas, el listado de materias y tareas informa que
  aún no hay contenido y permite iniciar el registro de una materia.
- No se puede crear una tarea sin título, materia asociada y fecha de entrega.
- No se puede registrar una materia sin nombre y color.
- Una descripción vacía no impide guardar una tarea.
- Cuando dos tareas tienen la misma fecha y hora límite, ambas se muestran y
  conservan un orden estable entre consultas.
- Una tarea que vence exactamente dentro de 48 horas se considera urgente; una
  tarea que vence en un instante posterior no se considera urgente todavía.
- Una tarea cuya fecha y hora límite coincide exactamente con el momento actual
  ya no se considera urgente; si permanece pendiente, se considera vencida.
- Al cambiar el día o la hora, las etiquetas de vencida y urgente se actualizan
  sin que el estudiante tenga que modificar la tarea.
- Si un filtro no coincide con ninguna tarea, se muestra un estado vacío
  comprensible y se permite quitar el filtro.
- Los nombres y descripciones con espacios al inicio o al final se procesan sin
  espacios sobrantes; si después de normalizar un campo obligatorio queda vacío,
  se solicita corregirlo.
- El nombre de una materia no puede superar 100 caracteres, el título de una
  tarea no puede superar 150 caracteres y la descripción no puede superar 2.000
  caracteres; se cuenta el texto después de quitar espacios sobrantes al inicio
  y al final.
- Una materia que tenga tareas asociadas no se puede borrar; el estudiante recibe
  una explicación para que resuelva o reasigne esas tareas antes de intentarlo
  nuevamente.

## Requisitos

### Requisitos funcionales

- **RF-001**: El sistema DEBE permitir registrar una materia con nombre y color.
- **RF-002**: El sistema DEBE validar que el nombre de la materia y su color
  estén presentes; el nombre no puede quedar vacío después de quitar espacios
  sobrantes ni exceder 100 caracteres.
- **RF-003**: El sistema DEBE permitir crear una tarea asociada a una materia
  registrada, con título y fecha de entrega, y una descripción opcional.
- **RF-004**: El sistema DEBE validar que el título no quede vacío después de
  quitar espacios sobrantes y que exista una materia asociada y una fecha de
  entrega válida; el título no puede exceder 150 caracteres y la descripción
  opcional no puede exceder 2.000 caracteres.
- **RF-005**: El sistema DEBE mostrar las tareas ordenadas de la fecha de
  entrega más próxima a la más lejana.
- **RF-006**: El sistema DEBE destacar como vencida cada tarea pendiente cuya
  fecha y hora límite haya llegado o pasado.
- **RF-007**: El sistema DEBE marcar como urgente cada tarea pendiente cuya fecha
  y hora límite sea posterior al momento actual y ocurra dentro de las siguientes
  48 horas, incluyendo exactamente el límite de 48 horas; el cálculo usa horas
  transcurridas, no días calendario.
- **RF-008**: El sistema DEBE dejar de destacar como vencida una tarea cuando se
  marque como completada.
- **RF-009**: El sistema DEBE permitir marcar una tarea pendiente como completada.
- **RF-010**: El sistema DEBE permitir filtrar las tareas por una materia.
- **RF-011**: El sistema DEBE permitir filtrar las tareas por estado, como mínimo
  pendientes o completadas.
- **RF-012**: El sistema DEBE permitir combinar filtros de materia y estado; el
  listado resultante debe cumplir todos los filtros seleccionados.
- **RF-013**: El sistema DEBE conservar las materias y tareas del único usuario
  del dispositivo al cerrar y volver a abrir la aplicación.
- **RF-014**: El sistema NO DEBE requerir inicio de sesión en esta versión y
  DEBE mantener los datos separados por dispositivo, sin sincronización entre
  dispositivos.
- **RF-015**: La interfaz DEBE mostrar estados vacíos comprensibles cuando no
  existan materias o cuando los filtros no devuelvan tareas.
- **RF-016**: El listado de materias y tareas DEBE presentar el color de cada
  materia de forma que ayude a distinguirla y no sea la única indicación de su
  identidad.
- **RF-017**: El registro de materias y tareas, los filtros y el listado DEBEN
  poder utilizarse en celular y computadora; la información y las acciones
  esenciales DEBEN seguir siendo perceptibles y operables en ambos.
- **RF-018**: El sistema DEBE impedir borrar una materia mientras tenga tareas
  asociadas y DEBE explicar que primero es necesario resolver o reasignar esas
  tareas.

### Entidades principales

- **Materia**: asignatura registrada por el estudiante; contiene un nombre y un
  color, y puede asociarse con varias tareas.
- **Tarea**: responsabilidad académica asociada a una materia; contiene título,
  descripción opcional, fecha y hora límite, y estado pendiente o completada.
- **Filtro**: criterio temporal aplicado al listado; puede seleccionar una
  materia, un estado o ambos.

## Criterios de éxito

### Resultados medibles

- **CE-001**: En una prueba de uso, al menos 9 de cada 10 estudiantes pueden
  registrar una materia y una tarea asociada en menos de 2 minutos, sin ayuda.
- **CE-002**: En todas las pruebas de aceptación, el 100 % de las tareas aparece
  en el orden correcto y con el estado temporal correcto para su fecha límite.
- **CE-003**: En todas las pruebas de aceptación, el 100 % de los filtros por
  materia, estado y combinación de ambos muestra únicamente las tareas
  correspondientes.
- **CE-004**: En una prueba con estudiantes, al menos 9 de cada 10 identifican
  correctamente cuáles tareas están vencidas, cuáles son urgentes y cuál es la
  próxima entrega.
- **CE-005**: Después de cerrar y volver a abrir la aplicación en el mismo
  dispositivo, el 100 % de las materias y tareas previamente guardadas sigue
  disponible.
- **CE-006**: El 100 % de los flujos principales puede completarse en pruebas
  tanto en celular como en computadora, y ninguna materia se distingue
  exclusivamente por su color.

## Supuestos

- La fecha de entrega se captura como una fecha y hora local del dispositivo.
  Si se proporciona solo una fecha, la hora límite es el final de ese día en la
  hora local del dispositivo.
- Una tarea está vencida cuando ha llegado o pasado su fecha y hora límite y aún está
  pendiente. Es urgente si está pendiente, su fecha y hora límite es posterior
  al momento actual y ocurre dentro de las próximas 48 horas transcurridas,
  incluyendo el límite exacto de 48 horas.
- La primera versión contempla un único usuario por dispositivo; los datos no
  se comparten ni sincronizan con otros dispositivos.
- No se requiere integrar la aplicación con sistemas académicos externos de la
  UPB en esta versión.
- Esta versión incluye registrar materias y tareas, consultar y filtrar tareas,
  y marcarlas como completadas. La edición, eliminación, recordatorios y
  colaboración no se incluyen porque no fueron solicitados.
- La aplicación se utiliza en celular y computadora, conforme a la constitución
  del proyecto; los controles y la información deben seguir siendo utilizables
  en ambos formatos.
