# Investigación de LiveKit

**Fecha de consulta de fuentes:** 30 de octubre de 2026.  
**Estado:** Investigación funcional para futura implementación.  


## 1. Conceptos Básicos y Arquitectura de LiveKit

LiveKit es una plataforma de código abierto orientada a comunicaciones en tiempo real (audio y video) basada en la arquitectura **SFU (Selective Forwarding Unit)**. A diferencia de una conexión tradicional Peer-to-Peer (P2P), en LiveKit los usuarios no se conectan directamente entre sí, sino a un servidor central que recibe las transmisiones y las redistribuye de forma eficiente a los demás participantes.

Para comprender su alcance, es fundamental separar sus **tres grandes módulos o capas de componentes** de los **conceptos clave de su funcionamiento**.

### A. Separación de Componentes del Sistema

No todo proyecto requiere los tres módulos; el alcance depende de las necesidades del sistema:

1. **Núcleo de Comunicación (SFU Core):**
   * Es el servidor principal de LiveKit.
   * Se encarga del ruteo de audio y video con muy baja latencia, administrando la creación de salas, la conexión de usuarios y la distribución del flujo de medios entre ellos.

2. **Framework Agents (Integración con IA):**
   * Es una capa opcional construida sobre el núcleo que permite incorporar asistentes interactivos de Inteligencia Artificial.
   * El agente se une a la sala como un participante más. Procesa el habla del usuario mediante **STT** (Speech-to-Text), razona la respuesta usando un **LLM** (Modelo de Lenguaje) y responde en voz alta mediante **TTS** (Text-to-Speech).

3. **Telefonía / SIP (Integración Telefónica):**
   * Módulo que actúa como puente con la red telefónica tradicional (PSTN).
   * Es necesario únicamente si el sistema requiere recibir o realizar llamadas a números telefónicos reales (fijos o móviles) hacia y desde la sala virtual.


### B. Conceptos Clave de Funcionamiento

Dentro del núcleo de comunicación (SFU), la interacción se rige por tres conceptos esenciales:

```text
                                [ Servidor SFU LiveKit ]
                                  (Gestión de la Sala)
                                    /              \
         PUBLICAR (Publish) Audio  /                \  SUSCRIBIR (Subscribe) Audio
                                  /                  \
   [ Participante Local (Usuario) ]                  [ Participante Remoto (Usuario/IA) ]
```

#### 1. Sala (Room)
Es el contenedor lógico o "espacio de reunión virtual" independiente.
* **Aislamiento:** Todo lo que se transmite en una sala queda acotado a ella; los participantes de otras salas no tienen acceso al flujo de datos.
* **Ciclo de vida:** Se crea dinámicamente cuando ingresa el primer participante con un token válido y se destruye (o entra en reposo) al quedar vacía.
* **Gestión de estado:** Mantiene el registro de usuarios conectados, sus metadatos y el estado de la sesión.

#### 2. Participante (Participant)
Corresponde a cualquier entidad (humana o automatizada) conectada a una sala.
* **Tipos:**
  * **Local vs. Remoto:** En el frontend, el usuario actual es el *LocalParticipant* (envía medios), mientras que los demás conectados son *RemoteParticipants* (reciben medios).
  * **Humanos vs. Agentes de IA:** Para el servidor, tanto una persona desde un navegador como un Agente de IA son participantes con las mismas capacidades de interacción.
* **Autenticación y Permisos:** Cada participante debe unirse con un token JWT firmado por el backend (FastAPI), donde se especifica su identidad (`identity`) y qué acciones tiene autorizadas (hablar, transmitir video, escuchar).

#### 3. Publicación y Suscripción (Publish / Subscribe)
LiveKit no transmite la "llamada completa" como un bloque único, sino pistas individuales de audio/video denominadas **Tracks**.

* **Publicación (Publish):**
  * Proceso mediante el cual un participante captura el micrófono/cámara de su dispositivo y transmite ese flujo de medios hacia el servidor SFU.
  * El audio se empaqueta preferentemente con el códec **Opus**, que optimiza la calidad de voz manteniendo un consumo de ancho de banda muy bajo.
  * Solo puede ser ejecutado si el token JWT otorgado por el backend lo autoriza.

* **Suscripción (Subscribe):**
  * Proceso mediante el cual el servidor retransmite las pistas recibidas hacia los demás participantes.
  * El SDK gestiona por defecto la suscripción automática a los tracks de audio presentes en la sala.
  * **Optimización de red:** Si un usuario silencia su micrófono o no está emitiendo audio, el servidor suspende el tráfico no esencial hacia los clientes, ahorrando ancho de banda y batería en el dispositivo.



## 2. Diagrama de Flujo Propuesto

*Nota: Este es un recorrido funcional hipotético. Los puntos marcados como [Decisión del equipo] deben ser validados.*

```text
[Usuario] ──(1. Solicitud)──> [Frontend React]
                                     │
                             (2. Valida sesión) [Decisión del equipo]
                                     ▼
                            [Backend FastAPI] ──(3. Genera Token JWT)──┐
                                                                       │
[Sala LiveKit] <──(4. Conecta con Token)── [Frontend React] <──────────┘
      │
      ├──(5. Solicita permiso micrófono)
      ├──(6. Publica audio / Suscribe a sala)
      ├──(7-8. Procesa eventos de UI y reconexión)
      └──(9. Finaliza sesión y desconecta)
```

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

| ID | Prioridad | Función | Actor | Entrada | Salida | Criterio de Aceptación | Dependencia | Fuente | Soporte LiveKit vs Trabajo Propio | Dudas |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01** | Principal | Ingreso autorizado a una sesión. | Usuario | Petición de acceso | Token JWT | Usuario autorizado entra con identidad; acceso inválido informa rechazo. | Sistema de login previo | Auth Docs | **Nativo:** LiveKit valida tokens. Nosotros generamos el token JWT en Python. | ¿Cómo vinculamos la sesión actual con la generación del token? |
| **RF-02** | Principal | Mostrar participantes y estado. | Usuario | Conexión a sala | Lista visual | Entradas, salidas y desconexiones se reflejan sin duplicados. | SDK Frontend | Rooms Docs | **Nativo:** SDK de React expone hooks y eventos de sala. | - |
| **RF-03** | Principal | Habilitar/silenciar audio. | Usuario | Clic en botón | Cambio de estado | Permiso concedido permite audio; denegado muestra explicación. | API del navegador | Connect Docs | **Nativo:** SDK controla el track local. | - |
| **RF-04** | Principal | Informar interrupción o reconexión. | Usuario | Eventos del sistema | Mensajes UI | La interfaz comunica estado y no simula estar conectada si falla la red. | SDK Frontend | Connect Docs | **Mixto:** LiveKit emite eventos; nosotros diseñamos los componentes visuales de UI. | ¿Qué comportamiento tendrá la UI ante caídas prolongadas? |
| **RF-05** | Por confirmar | Incorporar agente de voz. | Agente IA | Audio del usuario | Audio del agente | El agente responde con coherencia, fluidez y turnos claros. | STT, LLM, TTS | Agents Docs | **Nativo (Agents Framework):** Requiere orquestar servicios externoss. | ¿Qué modelos usar de STT/LLM/TTS y cuáles son sus costos? |
| **RF-06** | Por confirmar | Llamadas telefónicas o transferencia. | Usuario | Llamada telefónica | Audio en sala | Conectar llamadas desde teléfonos reales identificando origen y destino. | Proveedor SIP | Telephony Docs | **Nativo (SIP):** Módulo SIP integrado; requiere contratar proveedor VoIP/SIP. | ¿Se requiere telefonía real o solo comunicación WebRTC? |



## 4. Matriz de Requisitos Técnicos y No Funcionales

| Categoría | Requisito / Consideración | Decisiones Pendientes (No inventar cifras) |
| :--- | :--- | :--- |
| **SDK y Backend** | Integración del SDK en FastAPI y React. | Uso oficial de `livekit-api` en Python (backend) y `livekit-client` / `@livekit/components-react` en React. |
| **Permisos de Dispositivos** | Acceso a micrófono y cámara. | El navegador exige contexto seguro (HTTPS o localhost). Se debe gestionar el flujo UI en caso de rechazo del permiso. |
| **Red y Firewalls** | Puertos y protocolos WebRTC. | LiveKit requiere UDP (puertos 50000-60000) y TCP (7881). Evaluar fallback por TURN-over-TLS (puerto 443) para redes corporativas estrictas. |
| **Alojamiento** | Cloud vs. Autogestionado. | **Cloud:** Administrado, escalado automático, de pago por minuto. **Autogestionado:** Contenedores Docker en servidores propios. |
| **Seguridad de Tokens** | Generación de credenciales JWT. | Claves maestras (`LIVEKIT_API_SECRET`) solo en `.env` del backend. **Nunca** exponer secretos en frontend (`VITE_`). |
| **Privacidad** | Grabación y transcripción (Egress). | Evaluar si es legal o necesario conservar sesiones. Requiere aviso explícito de privacidad y almacenamiento en S3/PostgreSQL. |
| **Observabilidad** | Logs y monitoreo del sistema. | En local: logs de Docker y FastAPI. En producción: dashboard de LiveKit Cloud o métricas de Prometheus + Grafana. |
| **Capacidad y Latencia** | Rendimiento y concurrencia. | Pendiente acordar y ejecutar pruebas de carga (`livekit-bench`) para establecer límites reales de usuarios e infraestructura. |


## 5. Decisiones Pendientes y Alcance Mínimo Recomendado

### Decisiones pendientes para el equipo:

1. **Agente de Voz / IA (RF-05):**
   * Definir si la aplicación será únicamente P2P entre personas o si integrará un agente interactivo mediante **LiveKit Agents Framework** (STT + LLM + TTS), evaluando latencia global y costos por minuto de API.
   * *Pregunta clave:* ¿El objetivo principal es solo conectar usuarios entre sí o requiere un Agente de IA interactivo?

2. **Canal de Comunicación e Integración Telefónica (RF-06):**
   * LiveKit proporciona la puerta de enlace técnica (SIP), pero **no es un proveedor telefónico**. Se debe definir si basta con WebRTC en navegador o si se contratara un proveedor SIP/VoIP (ej. Twilio, Telnyx).
   * *Pregunta clave:* ¿Se requiere integrar telefonía tradicional o solo comunicación vía navegador?

3. **Alojamiento de Infraestructura (Cloud vs. Autogestionado):**
   * Elegir entre desplegar el servidor LiveKit en infraestructura propia vía Docker (control total de datos, costo fijo, mayor mantenimiento) o contratar **LiveKit Cloud** (servicio gestionado, costo por consumo).
   * *Pregunta clave:* ¿Se usará LiveKit Cloud o servidor autogestionado con Docker?

4. **Autenticación y Seguridad de Tokens (RF-01):**
   * Definir el flujo mediante el cual FastAPI validará la sesión previa del usuario antes de otorgar el JWT efímero mediante `livekit-api`.
   * *Pregunta clave:* ¿Cómo se reutilizará el backend actual para validar permisos antes de emitir tokens?

5. **Privacidad, Grabación y Transcripción:**
   * LiveKit permite la captura mediante su módulo **Egress**. El equipo debe definir si es necesario guardar audio/video o transcripciones por temas legales o de calidad.
   * *Pregunta clave:* ¿Es necesario implementar almacenamiento de grabaciones y avisos de privacidad?

6. **Manejo de Red y Firewalls Corporativos:**
   * Dado que WebRTC prioriza UDP (puertos 50000-60000), se debe evaluar si se requieren servidores STUN/TURN dedicados o fallback por TCP (puerto 7881) para clientes tras firewalls estrictos.

7. **Experiencia de Usuario y Permisos del Navegador (RF-03):**
   * Diseñar la respuesta de la interfaz ante excepciones como `PermissionDeniedError` cuando el usuario bloquee el micrófono, guiándolo para restablecer los permisos desde el navegador.

8. **Estrategia de UI ante Reconexiones e Interrupciones (RF-04):**
   * Vincular eventos como `Reconnecting` o `Disconnected` a estados visuales claros en React para evitar que la interfaz aparente estar activa si se pierde la conexión.

9. **Definición de Pruebas de Capacidad y Latencia:**
   * Acordar el plan de pruebas de estrés (benchmarking) en entorno staging antes de definir cifras límites de usuarios concurrentes.


### Alcance Mínimo Recomendado (MVP)

*Sugerencia para la primera iteración de implementación (no constituye un compromiso definitivo):*

* Conectar a los usuarios a una sala mediante token JWT validado por el backend (RF-01).
* Interfaz en React con lista de participantes y control básico de silencio/micrófono (RF-02, RF-03).
* Manejo visual claro de estados de desconexión y reconexión en la interfaz (RF-04).
* **Descartar temporalmente:** Agentes de IA (RF-05) e integración telefónica SIP (RF-06) hasta consolidar el núcleo de comunicación.


## 6. Fuentes Consultadas

- [Salas, participantes y tracks (LiveKit Docs)](https://docs.livekit.io/intro/basics/rooms-participants-tracks/)
- [Conexión y desconexión (LiveKit Docs)](https://docs.livekit.io/intro/basics/connect/)
- [Autenticación y Tokens (LiveKit Docs)](https://docs.livekit.io/frontends/build/authentication/)
- [LiveKit Agents Framework](https://docs.livekit.io/agents/)
- [Telefonía y Módulo SIP (LiveKit Docs)](https://docs.livekit.io/telephony/)
- [Soporte para Agentes de Código](https://docs.livekit.io/intro/coding-agents/)