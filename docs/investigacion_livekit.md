# Investigación de LiveKit (Etapa 4 PENDIENTE TERMINAR)

**Fecha de consulta de fuentes:** 29 de octubre de 2026.  
**Estado:** Investigación funcional para futura implementación. No se ha conectado LiveKit al CRUD actual.

## 1. Conceptos Básicos y Separación de Componentes

LiveKit es una plataforma de código abierto diseñada para comunicaciones en tiempo real (audio y video). Para entender su alcance, es vital separar sus tres grandes componentes, ya que no todo proyecto necesita los tres:

- **Núcleo de comunicación:** Es el servidor principal. Gestiona salas (rooms), participantes y la publicación/suscripción de tracks (flujos de audio o video). Permite que los usuarios se conecten y se escuchen entre sí.
- **Framework Agents:** Es una capa construida sobre el núcleo que permite crear agentes de Inteligencia Artificial. Estos agentes se unen a la sala como un participante más, escuchan a los usuarios usando STT (Speech-to-Text), procesan la información con un LLM (Modelo de Lenguaje) y responden usando TTS (Text-to-Speech).
- **Telefonía / SIP:** Permite conectar llamadas de la red telefónica tradicional (PSTN) a una sala de LiveKit. Se usa si el sistema necesita recibir o realizar llamadas a números reales de teléfono.

## 2. Diagrama de Flujo Propuesto

*Nota: Este es un recorrido funcional hipotético.*

1. **Usuario** solicita ingresar a una sesión desde la interfaz.
2. **[Decisión del equipo]** El backend valida las credenciales del usuario.
3. **Backend** autoriza y entrega un token JWT temporal (las claves secretas se quedan en el backend).
4. **Cliente (Frontend)** recibe el token y conecta con la sala (Room) de LiveKit.
5. **Cliente** solicita permiso de micrófono al navegador.
6. **Cliente** publica su track de audio y se suscribe al audio de los demás.
7. **Cliente / UI** procesa eventos (conectado, desconectado, silenciado) y actualiza la pantalla.
8. **Cliente / UI** maneja desconexiones y reconexiones, mostrando avisos claros.
9. **Usuario** finaliza la sesión y se desconecta de la sala.

## 3. Matriz de Requisitos Funcionales

| ID | Prioridad | Función | Actor | Entrada | Salida | Criterio de aceptación | Dependencia | Fuente | Soporte LiveKit vs Trabajo Propio | Dudas |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| RF-01 | Principal | Ingreso autorizado a una sesión. | Usuario | Petición de acceso | Token JWT | Usuario autorizado entra con identidad; acceso inválido informa rechazo. | Sistema de login previo | Auth Docs | **Nativo:** LiveKit maneja tokens. Nosotros generamos el token en Python. | ¿Cómo vinculamos el login con la generación del token? |
| RF-02 | Principal | Mostrar participantes y estado. | Usuario | Conexión a sala | Lista visual | Entradas, salidas y desconexiones se reflejan sin duplicados. | SDK Frontend | Rooms Docs | **Nativo:** SDK de React maneja los eventos. | - |
| RF-03 | Principal | Habilitar/silenciar audio. | Usuario | Clic en botón | Cambio de estado | Permiso concedido permite audio; denegado muestra explicación. | API del navegador | Connect Docs | **Nativo:** SDK controla el track local. | - |
| RF-04 | Principal | Informar interrupción o reconexión. | Usuario | Eventos del sistema | Mensajes UI | La interfaz comunica estado y no simula estar conectada si falla. | SDK Frontend | Connect Docs | **Mixto:** LiveKit avisa, nosotros diseñamos la UI. | ¿Qué hacer si falla la red a mitad de llamada? |
| RF-05 | Por confirmar | Incorporar agente de voz. | Agente IA | Audio del usuario | Audio del agente | El agente responde con coherencia y turnos. | STT, LLM, TTS | Agents Docs | **Nativo (Agents):** Requiere configurar el modelo. | ¿Qué LLM/STT/TTS usar? ¿Costos? |
| RF-06 | Por confirmar | Llamadas telefónicas o transferencia. | Usuario | Llamada telefónica | Audio en sala | Identificar dirección, actores, destino y proveedor. | Proveedor SIP | Telephony Docs | **Nativo (SIP):** Requiere contratar proveedor. | ¿Realmente se necesitan llamadas reales? |

## 4. Matriz de Requisitos Técnicos y No Funcionales

| Categoría | Requisito / Consideración | Decisiones Pendientes (No inventar cifras) |
| :--- | :--- | :--- |
| **SDK y backend** | Integración de LiveKit en FastAPI y React. | Uso de `livekit-api` en Python y `livekit-client` en React. |
| **Permisos de dispositivos** | Acceso al micrófono y cámara. | El navegador exige HTTPS (o localhost). Hay que manejar el caso en que el usuario deniegue el permiso. |
| **Red** | Puertos y WebRTC. | LiveKit usa UDP. En redes corporativas con firewalls estrictos, puede haber problemas de conexión. |
| **Alojamiento** | Cloud vs Autogestionado. | **Cloud:** Fácil, pero de pago. **Autogestionado:** Usar Docker en servidores propios (requiere administración). *Decisión pendiente.* |
| **Seguridad de tokens** | Generación de claves JWT. | Claves API y Secret guardadas en el `.env` del backend. El frontend recibe tokens limitados. **Nunca** claves secretas en variables `VITE_`. |
| **Privacidad** | Grabación y transcripción. | LiveKit permite grabación. ¿Es legal/necesario? Requiere aviso de privacidad. *Decisión pendiente.* |
| **Observabilidad** | Logs y monitoreo. | En local, revisar logs de Docker. En Cloud, usar el dashboard de LiveKit. |
| **Capacidad/Latencia** | Usuarios simultáneos. | No inventar cifras objetivo. Se debe hacer una prueba de carga antes de lanzar a producción. |

## 5. Decisiones Pendientes y Alcance Mínimo Recomendado

**Decisiones pendientes para el equipo:**
1. ¿El objetivo principal es solo conectar personas entre sí, o necesitamos un Agente de IA que responda (RF-05)?
2. ¿Requerimos integración telefónica (RF-06) o solo llamadas por navegador?
3. ¿Usaremos LiveKit Cloud (pago) o autogestionado (Docker en nuestro servidor)?
4. ¿Cómo autenticaremos a los usuarios antes de generarle el token? (¿Reutilizamos nuestro CRUD actual?).
5. ¿Necesitamos grabar o transcribir las sesiones por temas de calidad o legales?

**Alcance mínimo recomendado:**
*No es un compromiso de implementación, sino una sugerencia para la primera iteración.*
- Conectar a los usuarios a una sala mediante token (RF-01).
- Interfaz básica de silencio y lista de participantes (RF-02, RF-03).
- Manejo de desconexión (RF-04).
- **Descartar temporalmente** Agentes (RF-05) y Telefonía (RF-06) hasta que el núcleo de comunicación funcione sin fallos.

## 6. Fuentes Consultadas
- [Salas, participantes y tracks](https://docs.livekit.io/intro/basics/rooms-participants-tracks/)
- [Conexión y desconexión](https://docs.livekit.io/intro/basics/connect/)
- [Autenticación](https://docs.livekit.io/frontends/build/authentication/)
- [Agents](https://docs.livekit.io/agents/)
- [Telefonía](https://docs.livekit.io/telephony/)
- [Coding agent support](https://docs.livekit.io/intro/coding-agents/)