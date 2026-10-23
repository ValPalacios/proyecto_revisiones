const API_URL = "/llamadas";
const lista = document.getElementById("lista-llamadas");
const form = document.getElementById("form-llamada");
const estadoDiv = document.getElementById("mensaje-estado");
const btnCancelar = document.getElementById("btn-cancelar");
const btnGuardar = document.getElementById("btn-guardar");

function mostrarEstado(msg, tipo) {
    estadoDiv.textContent = msg;
    estadoDiv.className = `estado ${tipo}`;
}

async function cargarLlamadas() {
    mostrarEstado("Cargando...", "");
    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error("Error al cargar");
        const data = await res.json();
        
        lista.innerHTML = "";
        if (data.length === 0) {
            mostrarEstado("Sin llamadas registradas.", "");
            return;
        }
        mostrarEstado("", "");
        
        data.forEach(llamada => {
            const li = document.createElement("li");
            
            const infoDiv = document.createElement("div");
            // Usamos textContent para evitar inyecciones HTML
            const titulo = document.createElement("strong");
            titulo.textContent = llamada.nombre_archivo;
            infoDiv.appendChild(titulo);
            infoDiv.appendChild(document.createTextNode(` (ID: ${llamada.id}) - ${llamada.duracion_seg} seg - ${new Date(llamada.fecha_llamada).toLocaleString()}`));
            
            const divAcciones = document.createElement("div");
            divAcciones.className = "acciones-llamada";
            
            const btnEditar = document.createElement("button");
            btnEditar.textContent = "Editar";
            btnEditar.onclick = () => prepararEdicion(llamada);
            
            const btnEliminar = document.createElement("button");
            btnEliminar.textContent = "Eliminar";
            btnEliminar.className = "btn-eliminar";
            btnEliminar.onclick = () => eliminarLlamada(llamada.id, llamada.nombre_archivo);
            
            divAcciones.appendChild(btnEditar);
            divAcciones.appendChild(btnEliminar);
            
            li.appendChild(infoDiv);
            li.appendChild(divAcciones);
            lista.appendChild(li);
        });
    } catch (error) {
        mostrarEstado("No se pudo cargar. ¿Está la API encendida?", "error");
    }
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    btnGuardar.disabled = true;
    
    const id = document.getElementById("llamada-id").value;
    const fechaLocal = document.getElementById("fecha_llamada").value;
    
    // Convertimos la fecha local a ISO 8601 con zona horaria
    const fechaObjeto = new Date(fechaLocal);
    
    const datos = {
        nombre_archivo: document.getElementById("nombre_archivo").value,
        duracion_seg: parseInt(document.getElementById("duracion_seg").value),
        fecha_llamada: fechaObjeto.toISOString()
    };

    const metodo = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/${id}` : API_URL;

    try {
        const res = await fetch(url, {
            method: metodo,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(datos)
        });

        if (res.ok) {
            form.reset();
            document.getElementById("llamada-id").value = "";
            btnCancelar.hidden = true;
            btnGuardar.textContent = "Crear Llamada";
            mostrarEstado("Guardado con éxito.", "exito");
            cargarLlamadas();
        } else {
            mostrarEstado("Error de validación. Revisa los datos.", "error");
        }
    } catch (error) {
        mostrarEstado("Error de red al intentar guardar.", "error");
    } finally {
        btnGuardar.disabled = false;
    }
});

function prepararEdicion(llamada) {
    document.getElementById("llamada-id").value = llamada.id;
    document.getElementById("nombre_archivo").value = llamada.nombre_archivo;
    document.getElementById("duracion_seg").value = llamada.duracion_seg;
    
    // Formatear fecha para el input datetime-local
    const fecha = new Date(llamada.fecha_llamada);
    fecha.setMinutes(fecha.getMinutes() - fecha.getTimezoneOffset());
    document.getElementById("fecha_llamada").value = fecha.toISOString().slice(0, 16);
    
    btnGuardar.textContent = "Guardar Cambios";
    btnCancelar.hidden = false;
}

btnCancelar.onclick = () => {
    form.reset();
    document.getElementById("llamada-id").value = "";
    btnGuardar.textContent = "Crear Llamada";
    btnCancelar.hidden = true;
    mostrarEstado("", "");
};

async function eliminarLlamada(id, nombre) {
    if (!confirm(`¿Estás seguro de eliminar la llamada "${nombre}"?`)) return;

    try {
        const res = await fetch(`${API_URL}/${id}`, { method: "DELETE" });
        if (res.status === 204) {
            mostrarEstado("Llamada eliminada.", "exito");
            cargarLlamadas();
        } else if (res.status === 409) {
            mostrarEstado("La llamada tiene revisiones asociadas y no puede eliminarse.", "error");
        } else {
            mostrarEstado("Error al eliminar.", "error");
        }
    } catch (error) {
        mostrarEstado("Error de red al eliminar.", "error");
    }
}

// Cargar al inicio
cargarLlamadas();