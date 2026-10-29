const API_URL = "http://localhost:8000";

export const api = {
  getLlamadas: async () => {
    const res = await fetch(`${API_URL}/llamadas`);
    if (!res.ok) throw new Error("Error al cargar");
    return res.json();
  },
  crearLlamada: async (data) => {
    const res = await fetch(`${API_URL}/llamadas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res;
  },
  actualizarLlamada: async (id, data) => {
    const res = await fetch(`${API_URL}/llamadas/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return res;
  },
  eliminarLlamada: async (id) => {
    const res = await fetch(`${API_URL}/llamadas/${id}`, {
      method: "DELETE",
    });
    return res;
  }
};