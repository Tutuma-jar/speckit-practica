const subjectForm = document.querySelector("#subject-form");
const taskForm = document.querySelector("#task-form");
const subjectSelect = document.querySelector("#task-subject");
const subjectList = document.querySelector("#subject-list");
const taskList = document.querySelector("#task-list");
const listMessage = document.querySelector("#list-message");
const taskSubmit = document.querySelector("#task-submit");
const subjectMessage = document.querySelector("#subject-message");
const taskMessage = document.querySelector("#task-message");

function showMessage(element, message, kind = "") {
  element.textContent = message;
  if (kind) {
    element.dataset.kind = kind;
  } else {
    delete element.dataset.kind;
  }
}

async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body?.error?.mensaje || "No fue posible guardar los datos.");
  }
  return body;
}

function renderSubjects(subjects) {
  subjectList.replaceChildren();
  subjectSelect.replaceChildren();

  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.textContent = "Selecciona una materia";
  subjectSelect.append(placeholder);

  for (const subject of subjects) {
    const card = document.createElement("article");
    card.className = "subject-card";

    const swatch = document.createElement("span");
    swatch.className = "subject-swatch";
    swatch.style.backgroundColor = subject.color;
    swatch.setAttribute("aria-hidden", "true");

    const details = document.createElement("div");
    const name = document.createElement("p");
    name.className = "subject-name";
    name.textContent = subject.nombre;
    const color = document.createElement("p");
    color.className = "subject-color";
    color.textContent = `Color ${subject.color}`;
    details.append(name, color);
    card.append(swatch, details);
    subjectList.append(card);

    const option = document.createElement("option");
    option.value = String(subject.id);
    option.textContent = `${subject.nombre} (${subject.color})`;
    subjectSelect.append(option);
  }

  taskSubmit.disabled = subjects.length === 0;
}

function renderTasks(tasks) {
  taskList.replaceChildren();
  for (const task of tasks) {
    const card = document.createElement("article");
    card.className = "task-card";

    const subject = document.createElement("p");
    subject.className = "task-subject";
    subject.textContent = task.materia_nombre;

    const title = document.createElement("h3");
    title.textContent = task.titulo;

    const deadline = document.createElement("p");
    deadline.className = "task-meta";
    deadline.textContent = `Entrega: ${task.vencimiento}`;

    card.append(subject, title);
    if (task.descripcion) {
      const description = document.createElement("p");
      description.textContent = task.descripcion;
      card.append(description);
    }
    card.append(deadline);
    taskList.append(card);
  }
}

async function refreshLists() {
  const [subjects, tasks] = await Promise.all([
    requestJson("/api/materias"),
    requestJson("/api/tareas"),
  ]);
  renderSubjects(subjects);
  renderTasks(tasks);

  if (subjects.length === 0) {
    showMessage(listMessage, "Aún no hay materias. Registra la primera para comenzar.");
  } else if (tasks.length === 0) {
    showMessage(listMessage, "Todavía no hay tareas registradas.");
  } else {
    showMessage(listMessage, "");
  }
}

function localDateTimeWithOffset(dateValue, timeValue) {
  const localDateTime = new Date(`${dateValue}T${timeValue}`);
  if (Number.isNaN(localDateTime.getTime())) {
    throw new Error("La fecha y hora de entrega no son válidas.");
  }

  const offsetMinutes = -localDateTime.getTimezoneOffset();
  const sign = offsetMinutes >= 0 ? "+" : "-";
  const absoluteOffset = Math.abs(offsetMinutes);
  const offsetHours = String(Math.floor(absoluteOffset / 60)).padStart(2, "0");
  const offsetRemainder = String(absoluteOffset % 60).padStart(2, "0");
  return `${dateValue}T${timeValue}:00${sign}${offsetHours}:${offsetRemainder}`;
}

subjectForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(subjectForm);
  showMessage(subjectMessage, "");

  try {
    await requestJson("/api/materias", {
      method: "POST",
      body: JSON.stringify({
        nombre: formData.get("nombre"),
        color: formData.get("color"),
      }),
    });
    subjectForm.reset();
    document.querySelector("#subject-color").value = "#3366cc";
    await refreshLists();
    showMessage(subjectMessage, "Materia guardada.", "success");
  } catch (error) {
    showMessage(subjectMessage, error.message, "error");
  }
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(taskForm);
  showMessage(taskMessage, "");

  try {
    const timeValue = formData.get("hora");
    const deadline = timeValue
      ? localDateTimeWithOffset(formData.get("fecha"), timeValue)
      : formData.get("fecha");
    await requestJson("/api/tareas", {
      method: "POST",
      body: JSON.stringify({
        materia_id: Number(formData.get("materia_id")),
        titulo: formData.get("titulo"),
        descripcion: formData.get("descripcion") || null,
        vencimiento: deadline,
        zona_horaria: Intl.DateTimeFormat().resolvedOptions().timeZone,
      }),
    });
    taskForm.reset();
    await refreshLists();
    showMessage(taskMessage, "Tarea guardada.", "success");
  } catch (error) {
    showMessage(taskMessage, error.message, "error");
  }
});

refreshLists().catch((error) => {
  showMessage(listMessage, `No se pudieron cargar tus datos: ${error.message}`, "error");
});
