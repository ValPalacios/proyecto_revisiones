# Investigación de LiveKit 

**Fecha de consulta de fuentes:** 30 de octubre de 2026.  
**Estado:** Investigación funcional para futura implementación. 

## 1. Conceptos Básicos y Separación de Componentes

LiveKit es una plataforma de código abierto diseñada para comunicaciones en tiempo real (audio y video). Para entender su alcance, es vital separar sus tres grandes componentes, ya que no todo proyecto necesita los tres:

- **Núcleo de comunicación:** Es el servidor principal (SFU). Gestiona salas (rooms), participantes y la publicación/suscripción de tracks (flujos de audio o video). Permite que los usuarios se conecten y se escuchen entre sí.
- **Framework Agents:** Es una capa construida sobre el núcleo que permite crear agentes de Inteligencia Artificial. Estos agentes se unen a la sala como un participante más, escuchan a los usuarios usando STT (Speech-to-Text), procesan la información con un LLM (Modelo de Lenguaje) y responden usando TTS (Text-to-Speech).
- **Telefonía / SIP:** Permite conectar llamadas de la red telefónica tradicional (PSTN) a una sala de LiveKit. Se usa si el sistema necesita recibir o realizar llamadas a números reales de teléfono.

## 2. Diagrama de Flujo Propuesto

*Nota: Este es un recorrido funcional hipotético. Los puntos marcados como [Decisión del equipo] deben ser validados.*

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
| RF-06 | Por confirmar | Llamadas telefónicas o transferencia. | Usuario | Llamada telefónica | Audio en sala | Identificar dirección, actores, destino y proveedor. | Proveedor SIP | Telephony Docs | **Nativo (SIP):** Requiere contratar proveedor. | ¿Realmente se necesitan llamadas reales? *Nota: Transferir una conversación no es lo mismo que transferir una llamada telefónica.* |

## 4. Matriz de Requisitos Técnicos y No Funcionales

| Categoría | Requisito / Consideración | Decisiones Pendientes (No inventar cifras) |
| :--- | :--- | :--- |
| **SDK y backend** | Integración de LiveKit en FastAPI y React. | Uso de `livekit-api` en Python y `livekit-client` en React. |
| **Permisos de dispositivos** | Acceso al micrófono y cámara. | El navegador exige HTTPS (o localhost). Hay que manejar el caso en que el usuario deniegue el permiso. |
| **Red** | Puertos y WebRTC. | LiveKit usa UDP (puertos 50000-60000) y TCP (7881). En redes corporativas con firewalls estrictos, puede haber problemas de conexión. |
| **Alojamiento** | Cloud vs Autogestionado. | **Cloud:** Fácil, pero de pago. **Autogestionado:** Usar Docker en servidores propios (requiere administración). *Decisión pendiente.* |
| **Seguridad de tokens** | Generación de claves JWT. | Claves API y Secret guardadas en el `.env` del backend. El frontend recibe tokens limitados. **Nunca** claves secretas en variables `VITE_`. |
| **Privacidad** | Grabación y transcripción. | LiveKit permite grabación (Egress). ¿Es legal/necesario conservar datos? Requiere aviso de privacidad. *Opción por confirmar.* |
| **Observabilidad** | Logs y monitoreo. | En local, revisar logs de Docker. En Cloud, usar el dashboard de LiveKit. |
| **Capacidad/Latencia** | Usuarios simultáneos. | No inventar cifras objetivo. Se debe hacer una prueba de carga antes de lanzar a producción. |

## 5. Decisiones Pendientes y Alcance Mínimo Recomendado

### Decisiones pendientes para el equipo:

1. **Agente de Voz / IA (RF-05):**
   *  Se debe decidir si el alcance se limita a la comunicación P2P entre usuarios humanos o si se integrará un agente de voz interactivo nativo basado en **LiveKit Agents Framework (STT, LLM, TTS)**. Esto requiere definir qué modelos de procesamiento de lenguaje y sintetización de voz se utilizarán, evaluando los costos de API y la latencia en tiempo real[cite: 13].
   **¿El objetivo principal es solo conectar personas entre sí, o necesitamos un Agente de IA que responda (RF-05)?**

2. **Canal de Comunicación e Integración Telefónica (RF-06):**
   * LiveKit proporciona la puerta de enlace técnica (módulo SIP), pero **no es una compañía telefónica**. Se debe definir si la aplicación operará exclusivamente vía WebRTC desde el navegador o si se contratará un proveedor VoIP/SIP externo (ej. Twilio, Telnyx) para recibir y realizar llamadas a números fijos o móviles reales. 
   **¿Requerimos integración telefónica (RF-06) o solo llamadas por navegador?**

3. **Alojamiento de la Infraestructura (Cloud vs. Autogestionado):**
   * Se debe elegir entre instalar y mantener los contenedores de LiveKit Server en servidores propios (lo que brinda control total de datos y costos fijos de servidor, pero exige orquestación, parches de seguridad y certificados) o contratar **LiveKit Cloud**, servicio administrado que elimina la carga operativa y escala automáticamente a cambio de una tarifa basada en minutos consumidos. 
   **¿Usaremos LiveKit Cloud (pago) o autogestionado (Docker en nuestro servidor)?**

4. **Autenticación y Seguridad de Tokens (RF-01):**
   * Es un punto crítico de seguridad. Se debe definir cómo el backend en FastAPI validará la sesión actual en PostgreSQL antes de emitir el token JWT efímero mediante `livekit-api` en Python[cite: 12, 14]. Se debe garantizar que las credenciales maestras (`LIVEKIT_API_SECRET`) residan únicamente en el `.env` del servidor y **nunca se expongan en el frontend React** (`livekit-client`) mediante variables `VITE_`.
   **¿Cómo autenticaremos a los usuarios antes de generarle el token (¿Reutilizamos nuestro CRUD actual?)?**

5. **Privacidad, Grabación y Transcripción:**
   * LiveKit permite la captura de sesiones mediante su módulo de **Egress**. El equipo debe definir si es legalmente necesario o deseable conservar estos archivos de audio/vídeo y generar transcripciones de texto, lo cual exigirá implementar un aviso de privacidad explícito en la interfaz para los usuarios y definir la política de almacenamiento en S3/PostgreSQL.
   **¿Necesitamos grabar o transcribir las sesiones por temas de calidad o legales?**

6. **Grabación, transcripción y conservación de datos:**
   * Se anotan como opciones por confirmar, no como capacidades asumidas del alcance mínimo.

7. **Manejo de Red y Firewalls Corporativos (WebRTC):**
   * Dado que LiveKit opera por defecto en puertos **UDP (50000-60000)** y **TCP (7881)**[cite: 12], **¿cómo gestionaremos las restricciones en redes corporativas con firewalls estrictos[cite: 12]? ¿Se requiere configurar servidores STUN/TURN dedicados[cite: 12]?** WebRTC prioriza UDP para transmitir audio a baja latencia[cite: 12]. Sin embargo, los firewalls corporativos suelen bloquear el tráfico UDP no estándar[cite: 12]. Si no se habilita el fallback por TCP (puerto 7881) o servidores TURN-over-TLS (puerto 443), los usuarios en redes estrictas experimentarán llamadas en silencio o incapacidad absoluta de conectarse[cite: 12].

8. **Experiencia de Usuario en Dispositivos y Permisos (RF-03):**
   * Las APIs del navegador prohíben volver a solicitar el micrófono por código si el usuario presiona "Bloquear"[cite: 12, 14]. La aplicación debe capturar excepciones como `PermissionDeniedError` y mostrar un flujo o alerta explicativa en pantalla con guías visuales para que el usuario sepa cómo reactivar los permisos manualmente desde la barra de direcciones[cite: 12, 14]. 
   **¿Cómo responderá la interfaz de usuario en React cuando el navegador exija **HTTPS** (o localhost) y el usuario deniegue explícitamente los permisos de micrófono y cámara[cite: 12, 14]?**

9. **Estrategia de UI ante Reconexiones e Interrupciones (RF-04):**
   * LiveKit emite eventos automáticos en segundo plano al perder señal, pero no dibuja componentes en pantalla[cite: 13, 14]. Si no vinculamos eventos como `Reconnecting` o `Disconnected` al estado visual de React, el usuario creerá que la llamada sigue activa cuando en realidad el audio se ha congelado[cite: 13, 14]. Dado que el soporte de reconexión es **Mixto** (LiveKit detecta el evento, pero nosotros diseñamos la UI)[cite: 13, 14], **¿cuál será el comportamiento visual de los mensajes de estado en el frontend para evitar que la interfaz simule estar conectada si la red falla[cite: 13, 14]?**

10. **Definición de Pruebas de Capacidad y Latencia:**
    * La especificación técnica exige medir de forma objetiva la capacidad real del servidor antes de publicar el sistema[cite: 12]. Se debe definir qué herramientas o scripts simuladores se usarán para estresar el sistema y evaluar consumo de CPU, memoria y latencia antes de fijar límites operativos[cite: 12]. Dado que la matriz prohíbe **inventar cifras objetivo** de usuarios simultáneos[cite: 12], **¿cuándo y bajo qué escenarios ejecutaremos la prueba de carga en el entorno staging antes de liberar el sistema a producción[cite: 12]?**
    

---

### Alcance mínimo recomendado:
*No es un compromiso de implementación, sino una sugerencia para la primera iteración.*
- Conectar a los usuarios a una sala mediante token validado (RF-01)[cite: 14].
- Interfaz básica de silencio y lista de participantes (RF-02, RF-03)[cite: 14].
- Manejo de estados de desconexión y reconexión en UI (RF-04)[cite: 14].
- **Descartar temporalmente** Agentes (RF-05) y Telefonía (RF-06) hasta que el núcleo de comunicación funcione sin fallos[cite: 13, 14].

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