# Checklist de experiencia de usuario y validación de datos: Organizador de tareas académicas

**Propósito**: Revisar la calidad, claridad e integridad de los requisitos de experiencia de usuario y validación de datos.
**Creado**: 2026-10-26
**Funcionalidad**: [spec.md](../spec.md)

**Nota**: Este checklist personalizado evalúa la redacción de los requisitos; no comprueba la implementación.
**Responsabilidad de revisión**: El checklist pertenece a quien revisa los requisitos. Marcar un ítem `[x]` solo cuando determine que el criterio de calidad de requisitos está satisfecho.
**Significado de las marcas**: `[x]` significa que se revisó y aprobó la calidad del requisito; no significa que la funcionalidad esté implementada.

## Integridad de los requisitos de experiencia de usuario

- [ ] CHK001 ¿Están definidos los elementos y datos que cada tarea debe presentar para que el estudiante identifique su materia, título, fecha límite y estado? [Completeness, Spec §Historia de usuario 2, RF-005–RF-008]
- [ ] CHK002 ¿Se especifica cómo comunicar visual y textualmente los estados de tarea vencida y urgente, además de indicar qué cálculo los determina? [Clarity, Spec §RF-006–RF-008]
- [ ] CHK003 ¿Están definidos los requisitos de navegación, etiquetas accesibles, foco visible y operación por teclado para todos los controles interactivos? [Gap, Constitución §Principios fundamentales; Plan §Revisión posterior al diseño]
- [ ] CHK004 ¿Se establecen criterios concretos para decidir si los formularios, filtros y listado son utilizables en celular y computadora, más allá de nombrar ambos dispositivos? [Measurability, Spec §RF-017, CE-006]
- [ ] CHK005 ¿Se define qué información alternativa al color identifica cada materia y cómo se distingue entre materias con nombres iguales? [Completeness, Spec §RF-016; Ambiguity, Spec §RF-001]
- [ ] CHK006 ¿Son coherentes los estados vacíos y las acciones ofrecidas cuando no hay materias o cuando un filtro no produce resultados? [Consistency, Spec §RF-015, Historia de usuario 3]
- [ ] CHK007 ¿Se especifica cómo informar errores de validación y conflictos de guardado de forma que el estudiante pueda corregir el dato correspondiente? [Gap, Spec §RF-002, RF-004, RF-018]
- [ ] CHK008 ¿Se define si el estudiante puede revertir por error una tarea marcada como completada, o se declara esa posibilidad fuera del alcance? [Gap, Spec §RF-009; Assumption §Alcance]

## Claridad y cobertura de la validación de datos

- [ ] CHK009 ¿Están definidos los límites mínimo y máximo del nombre de materia, incluido si el conteo ocurre antes o después de normalizar espacios? [Clarity, Spec §RF-002, Casos límite]
- [ ] CHK010 ¿Están definidos los límites y reglas de normalización del título y la descripción, incluida la diferencia entre descripción vacía y ausente? [Clarity, Spec §RF-004, Casos límite]
- [ ] CHK011 ¿Se especifican los valores y el formato aceptados para el color de una materia, más allá de exigir que no esté vacío? [Gap, Spec §RF-001, RF-002]
- [ ] CHK012 ¿Se especifica qué formatos de fecha y hora son válidos y cómo se comunica una fecha imposible o mal formada? [Completeness, Spec §RF-003, RF-004; Assumption §Fecha de entrega]
- [ ] CHK013 ¿Son compatibles entre sí las reglas de fecha local, zona horaria, fechas sin hora, vencimiento y ventana urgente de 48 horas? [Consistency, Spec §RF-006–RF-007, Assumptions]
- [ ] CHK014 ¿Se define qué pasa al enviar una materia o una tarea que ya alcanzó exactamente el límite de longitud, y al excederlo por un carácter? [Edge Case, Spec §RF-002, RF-004]
- [ ] CHK015 ¿Se especifica cómo tratar entradas compuestas solo por espacios y espacios externos en cada campo, incluida la descripción opcional? [Completeness, Spec §Casos límite, RF-002, RF-004]
- [ ] CHK016 ¿Se define el comportamiento de la validación cuando se referencia una materia inexistente o cuando falla el guardado local? [Gap, Spec §RF-003, RF-013]

## Consistencia, escenarios y trazabilidad

- [ ] CHK017 ¿Es consistente impedir el borrado de materias con tareas con las instrucciones de resolver o reasignar esas tareas, si borrar y reasignar tareas están fuera del alcance? [Conflict, Spec §RF-018, Casos límite; Assumptions §Alcance]
- [ ] CHK018 ¿Se define si dos materias pueden tener el mismo nombre y cómo el estudiante distingue cuál seleccionar al crear o filtrar tareas? [Ambiguity, Spec §RF-001, RF-003, RF-010]
- [ ] CHK019 ¿Están cubiertos los flujos de error, corrección y reintento para crear materias, crear tareas, filtrar y completar tareas? [Coverage, Spec §Historias de usuario 1–3, RF-002–RF-012]
- [ ] CHK020 ¿Los criterios de éxito permiten evaluar objetivamente comprensión de estados, finalización de tareas y uso adaptable, sin depender de una valoración vaga? [Measurability, Spec §CE-001–CE-006]

## Notas

- Marcar un ítem `[x]` solo cuando la revisión confirme que el requisito está completo, claro, consistente y comprobable.
- Mantener los hallazgos como comentarios sobre los requisitos; este checklist no es un plan de pruebas de implementación.
- La lista de calidad integrada `requirements.md` tiene un ciclo de vida independiente y no se modifica mediante este checklist.
- Los ítems hacen referencia a la especificación, el plan o la constitución para facilitar su rastreo.
