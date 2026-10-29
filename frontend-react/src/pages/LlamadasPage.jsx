import { useState } from "react";
import { useLlamadas } from "../hooks/useLlamadas";
import { api } from "../services/api";
import LlamadaForm from "../components/LlamadaForm";

export default function LlamadasPage() {
  const { llamadas, cargando, error, recargar } = useLlamadas();
  const [editando, setEditando] = useState(null);

  const handleGuardar = async (datos) => {
    try {
      let res;
      if (editando) {
        res = await api.actualizarLlamada(editando.id, datos);
      } else {
        res = await api.crearLlamada(datos);
      }

      if (res.ok) {
        setEditando(null);
        recargar();
      } else if (res.status === 422) {
        alert("Datos inválidos. Revisa la duración o el nombre.");
      } else {
        alert("Ocurrió un error al guardar.");
      }
    } catch (err) {
      alert("Error de red al intentar guardar.");
    }
  };

  const handleEliminar = async (id, nombre) => {
    if (!window.confirm(`¿Seguro que quieres eliminar "${nombre}"?`)) return;

    try {
      const res = await api.eliminarLlamada(id);
      if (res.status === 204) {
        alert("Llamada eliminada.");
        recargar();
      } else if (res.status === 409) {
        alert("La llamada tiene revisiones asociadas y no puede eliminarse.");
      } else {
        alert("Error al eliminar.");
      }
    } catch (err) {
      alert("Error de red al intentar eliminar.");
    }
  };

  return (
    <div style={{ padding: "20px", fontFamily: "sans-serif" }}>
      <h1>Gestión de Llamadas Ficticias</h1>
      {cargando && <p>Cargando...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      <LlamadaForm 
        onSave={handleGuardar} 
        llamadaEditando={editando} 
        onCancel={() => setEditando(null)} 
      />

      {!cargando && llamadas.length === 0 && <p>Sin llamadas registradas.</p>}
      
      {llamadas.length > 0 && (
        <table border="1" cellPadding="8" style={{ borderCollapse: "collapse", marginTop: "20px" }}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Nombre Archivo</th>
              <th>Duración (s)</th>
              <th>Fecha de Llamada</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {llamadas.map((llamada) => (
              <tr key={llamada.id}>
                <td>{llamada.id}</td>
                <td>{llamada.nombre_archivo}</td>
                <td>{llamada.duracion_seg}</td>
                <td>{new Date(llamada.fecha_llamada).toLocaleString()}</td>
                <td>
                  <button onClick={() => setEditando(llamada)}>Editar</button>
                  <button onClick={() => handleEliminar(llamada.id, llamada.nombre_archivo)} style={{ marginLeft: "10px" }}>
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}