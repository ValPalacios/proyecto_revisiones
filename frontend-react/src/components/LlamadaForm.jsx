import { useState, useEffect } from "react";

export default function LlamadaForm({ onSave, llamadaEditando, onCancel }) {
  const [nombre, setNombre] = useState("");
  const [duracion, setDuracion] = useState("");
  const [fecha, setFecha] = useState("");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (llamadaEditando) {
      setNombre(llamadaEditando.nombre_archivo);
      setDuracion(llamadaEditando.duracion_seg);
      // Convertimos la fecha UTC a local para el input datetime-local
      const d = new Date(llamadaEditando.fecha_llamada);
      d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
      setFecha(d.toISOString().slice(0, 16));
    } else {
      setNombre("");
      setDuracion("");
      setFecha("");
    }
  }, [llamadaEditando]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    
    // Convertimos la fecha local a ISO con zona horaria
    const fechaObjeto = new Date(fecha);
    const datos = {
      nombre_archivo: nombre,
      duracion_seg: parseInt(duracion),
      fecha_llamada: fechaObjeto.toISOString()
    };

    await onSave(datos);
    setIsSaving(false);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: "20px", display: "flex", flexDirection: "column", gap: "10px", maxWidth: "400px", padding: "10px", border: "1px solid #ccc" }}>
      <h3>{llamadaEditando ? "Editar Llamada" : "Nueva Llamada"}</h3>
      <div>
        <label>Nombre del archivo: </label>
        <input type="text" value={nombre} onChange={(e) => setNombre(e.target.value)} required />
      </div>
      <div>
        <label>Duración (seg): </label>
        <input type="number" value={duracion} onChange={(e) => setDuracion(e.target.value)} required min="1" max="86400" />
      </div>
      <div>
        <label>Fecha y hora local: </label>
        <input type="datetime-local" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
      </div>
      <div style={{ display: "flex", gap: "10px", marginTop: "10px" }}>
        <button type="submit" disabled={isSaving}>{isSaving ? "Guardando..." : "Guardar"}</button>
        {llamadaEditando && <button type="button" onClick={onCancel}>Cancelar</button>}
      </div>
    </form>
  );
}