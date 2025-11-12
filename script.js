const API_BASE = "http://127.0.0.1:8000";
const API_RESERVAS = `${API_BASE}/reservas`;
const API_CANCHAS = `${API_BASE}/canchas`;
const API_PAGOS = `${API_BASE}/pagos`;

// Espera a DOM ready
document.addEventListener("DOMContentLoaded", () => {
  setMinDate();
  cargarCanchasYPagos();     // carga dinámicamente las opciones del select
  cargarReservas();
  document.querySelector("#formReserva").addEventListener("submit", guardarReserva);
  document.querySelector("#filtroCancha").addEventListener("change", cargarReservas);
  document.querySelector("#btnMenu")?.addEventListener("click", toggleMenu);
});

function toggleMenu(){
  const menu = document.getElementById("menu");
  if(!menu) return;
  menu.classList.toggle("open");
}

// Guarda reserva: construye el objeto con cancha_id y pago_id
async function guardarReserva(e) {
  e.preventDefault();
  const msg = document.querySelector("#msgReserva");

  const data = {
    nombre: document.querySelector("#nombre").value.trim(),
    email: document.querySelector("#email").value.trim(),
    cancha_id: parseInt(document.querySelector("#cancha").value) || null,
    fecha: document.querySelector("#fecha").value,
    hora: document.querySelector("#hora").value,
    duracion: parseInt(document.querySelector("#duracion").value),
    jugadores: parseInt(document.querySelector("#jugadores").value),
    pago_id: parseInt(document.querySelector("#pago").value) || null
  };

  // Validaciones básicas
  if(!data.cancha_id){
    msg.textContent = "❌ Seleccioná una cancha válida.";
    msg.className = "msg msg--error";
    return;
  }
  if(!data.pago_id){
    msg.textContent = "❌ Seleccioná un método de pago válido.";
    msg.className = "msg msg--error";
    return;
  }

  try {
    const resp = await fetch(API_RESERVAS, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (resp.ok) {
      const nuevo = await resp.json();
      msg.textContent = "✅ Reserva registrada correctamente.";
      msg.className = "msg msg--ok";
      document.querySelector("#formReserva").reset();
      setMinDate(); // volver a fijar mínimo
      cargarReservas();
      setTimeout(()=> msg.textContent = "", 4000);
    } else {
      const err = await resp.json();
      msg.textContent = "❌ " + (err.detail || "Error al registrar la reserva.");
      msg.className = "msg msg--error";
    }
  } catch (error) {
    console.error(error);
    msg.textContent = "⚠ No se pudo conectar con el servidor.";
    msg.className = "msg msg--error";
  }
}

// Carga canchas y pagos desde la API y llena los <select>
async function cargarCanchasYPagos() {
  // CARGA CANCHAS
  try {
    const resp = await fetch(API_CANCHAS);
    const canchas = await resp.json();
    const select = document.querySelector("#cancha");
    if(select){
      const placeholder = select.querySelector('option[value=""]') ? select.querySelector('option[value=""]').outerHTML : '<option value="">Seleccioná una opción</option>';
      select.innerHTML = placeholder;
      canchas.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = `${c.nombre} (${c.capacidad} pers.)`;
        select.appendChild(opt);
      });
    }
  } catch (err) {
    console.error("Error cargando canchas:", err);
  }

  // CARGA PAGOS
  try {
    const resp2 = await fetch(API_PAGOS);
    const pagos = await resp2.json();
    const selectPago = document.querySelector("#pago");
    if(selectPago){
      const placeholder = selectPago.querySelector('option[value=""]') ? selectPago.querySelector('option[value=""]').outerHTML : '<option value="">Seleccioná</option>';
      selectPago.innerHTML = placeholder;
      pagos.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.id;
        opt.textContent = p.metodo;
        selectPago.appendChild(opt);
      });
    }
  } catch (err) {
    console.error("Error cargando pagos:", err);
  }

  // También actualizo el filtro de canchas
  const filtro = document.querySelector("#filtroCancha");
  if(filtro){
    const current = filtro.value;
    filtro.innerHTML = '<option value="todas">Todas</option>';
    try{
      const resp = await fetch(API_CANCHAS);
      const canchas2 = await resp.json();
      canchas2.forEach(c => {
        const opt = document.createElement("option");
        opt.value = c.id;
        opt.textContent = c.nombre;
        filtro.appendChild(opt);
      });
      filtro.value = current || "todas";
    }catch(e){
      console.error("Error cargando filtro de canchas", e);
    }
  }
}

// Cargar reservas y mostrarlas
async function cargarReservas() {
  const tbody = document.querySelector("#tablaReservas tbody");
  tbody.innerHTML = "<tr><td colspan='6'>Cargando...</td></tr>";
  try {
    let url = API_RESERVAS;
    const filtro = document.querySelector("#filtroCancha");
    if(filtro && filtro.value && filtro.value !== "todas"){
      url += `?cancha_id=${encodeURIComponent(filtro.value)}`;
    }
    const resp = await fetch(url);
    const data = await resp.json();
    if (!Array.isArray(data) || data.length === 0) {
      tbody.innerHTML = "<tr><td colspan='6'>No hay reservas.</td></tr>";
      return;
    }
    tbody.innerHTML = "";
    data.forEach(r => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${r.cancha_nombre}</td>
        <td>${r.fecha}</td>
        <td>${r.hora}</td>
        <td>${r.duracion} min</td>
        <td>${r.usuario_nombre}</td>
        <td>
          <button class="btn btn--small" onclick="eliminarReserva(${r.id})">Eliminar</button>
        </td>`;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
    tbody.innerHTML = "<tr><td colspan='6'>Error al cargar las reservas.</td></tr>";
  }
}

// 🔐 Eliminar reserva (con contraseña de administrador)
async function eliminarReserva(id) {
  if (!confirm("¿Eliminar esta reserva?")) return;

  const adminKey = prompt("Ingrese la contraseña de administrador para eliminar:");
  if (!adminKey) return alert("Acción cancelada.");

  try {
    const resp = await fetch(`${API_RESERVAS}/${id}`, {
      method: "DELETE",
      headers: { "admin_key": adminKey }
    });

    if (resp.ok) {
      alert("✅ Reserva eliminada correctamente.");
    } else {
      const err = await resp.json();
      alert("❌ " + (err.detail || "Error al eliminar la reserva."));
    }
  } catch (err) {
    console.error(err);
    alert("⚠ No se pudo conectar al servidor.");
  }
  cargarReservas();
}

function setMinDate() {
  const fechaInput = document.querySelector('#fecha');
  if(!fechaInput) return;
  const hoy = new Date();
  const yyyy = hoy.getFullYear();
  const mm = String(hoy.getMonth() + 1).padStart(2, "0");
  const dd = String(hoy.getDate()).padStart(2, "0");
  fechaInput.min = `${yyyy}-${mm}-${dd}`;
}