import { useState, useEffect } from "react";
import { api } from "../services/api";

export function useLlamadas() {
  const [llamadas, setLlamadas] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState(null);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError(null);
      const data = await api.getLlamadas();
      setLlamadas(data);
    } catch (err) {
      setError("No se pudo cargar la lista. ¿Está el backend encendido?");
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  return { llamadas, cargando, error, recargar: cargarDatos };
}