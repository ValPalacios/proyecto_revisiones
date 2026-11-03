import { useState, useEffect } from "react";
import { apiRevisiones } from "../services/api";

export default function RevisionesPage() {
  const [revisiones, setRevisiones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [form, setForm] = useState({ titulo: "", nota: "", estado: "pendiente", llamada_id: "" });
  const [editandoId, setEditandoId] = useState(null);

  const cargar = async () => {
    try {
      setCargando(true);
      const data = await apiRevisiones.getRevisiones();
      setRevisiones(data);
    } catch (e) { alert("Error al cargar"); } finally { setCargando(false); }
  };

  useEffect(() => { cargar(); }, []);

  const guardar = async (e) => {
    e.preventDefault();
    const payload = { ...form };
    if (!payload.llamada_id) delete payload.llamada_id;
    else payload.llamada_id = parseInt(payload.llamada_id);

    let res;
    if (editandoId) res = await apiRevisiones.actualizarRevision(editandoId, payload);
    else res = await apiRevisiones.crearRevision(payload);

    if (res.ok) {
      setForm({ titulo: "", nota: "", estado: "pendiente", llamada_id: "" });
      setEditandoId(null);
      cargar();
    } else {
      const err = await res.json();
      alert("Error: " + JSON.stringify(err.detail));
    }
  };

  const editar = (rev) => {
    setForm({ titulo: rev.titulo, nota: rev.nota, estado: rev.estado, llamada_id: rev.llamada_id || "" });
    setEditandoId(rev.id);
  };

  const eliminar = async (id) => {
    if (!window.confirm("¿Eliminar revisión?")) return;
    const res = await apiRevisiones.eliminarRevision(id);
    if (res.status === 204) cargar();
    else alert("Error al eliminar");
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Gestión de Revisiones</h2>
      <form onSubmit={guardar} style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <input placeholder="Título" value={form.titulo} onChange={e => setForm({...form, titulo: e.target.value})} required />
        <input placeholder="Nota" value={form.nota} onChange={e => setForm({...form, nota: e.target.value})} />
        <select value={form.estado} onChange={e => setForm({...form, estado: e.target.value})}>
          <option value="pendiente">Pendiente</option>
          <option value="revisada">Revisada</option>
        </select>
        <input type="number" placeholder="ID Llamada (opcional)" value={form.llamada_id} onChange={e => setForm({...form, llamada_id: e.target.value})} />
        <button type="submit">{editandoId ? "Guardar Cambios" : "Crear"}</button>
        {editandoId && <button type="button" onClick={() => { setEditandoId(null); setForm({ titulo: "", nota: "", estado: "pendiente", llamada_id: "" }); }}>Cancelar</button>}
      </form>

      {cargando ? <p>Cargando...</p> : (
        <table border="1" cellPadding="8" style={{ borderCollapse: "collapse" }}>
          <thead>
            <tr><th>ID</th><th>Título</th><th>Estado</th><th>Llamada ID</th><th>Acciones</th></tr>
          </thead>
          <tbody>
            {revisiones.map(r => (
              <tr key={r.id}>
                <td>{r.id}</td><td>{r.titulo}</td><td>{r.estado}</td><td>{r.llamada_id || "Ninguna"}</td>
                <td>
                  <button onClick={() => editar(r)}>Editar</button>
                  <button onClick={() => eliminar(r.id)}>Eliminar</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}