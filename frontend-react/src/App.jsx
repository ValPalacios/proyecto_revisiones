import { useState } from "react";
import LlamadasPage from "./pages/LlamadasPage";
import RevisionesPage from "./pages/RevisionesPage";

function App() {
  const [vista, setVista] = useState("llamadas");

  return (
    <div>
      <nav style={{ padding: "20px", background: "#eee", display: "flex", gap: "10px" }}>
        <button onClick={() => setVista("llamadas")} disabled={vista === "llamadas"}>Llamadas</button>
        <button onClick={() => setVista("revisiones")} disabled={vista === "revisiones"}>Revisiones</button>
      </nav>
      {vista === "llamadas" ? <LlamadasPage /> : <RevisionesPage />}
    </div>
  );
}

export default App;