# Investigación de LiveKit

**Fecha de consulta de fuentes:** 30 de octubre de 2026.  

## 1. Conceptos Básicos y Arquitectura de LiveKit

LiveKit es una plataforma de código abierto orientada a comunicaciones en tiempo real (audio y video) basada en la arquitectura **SFU (Selective Forwarding Unit)**. A diferencia de una conexión tradicional Peer-to-Peer (P2P), en LiveKit los usuarios no se conectan directamente entre sí, sino a un servidor central que recibe las transmisiones y las redistribuye de forma eficiente a los demás participantes.

Para comprender su alcance, es fundamental separar sus **tres grandes módulos o capas de componentes** de los **conceptos clave de su funcionamiento**.

```
                                [ Servidor SFU LiveKit ]
                                  (Gestión de la Sala)
                                    /              \
         PUBLICAR (Publish) Audio  /                \  SUSCRIBIR (Subscribe) Audio
                                  /                  \
   [ Participante Local (Usuario) ]                  [ Participante Remoto (Usuario/IA) ]
```

### A. Separación de Componentes del Sistema

1. **Núcleo de Comunicación (SFU Core):**
   * Es el servidor principal de LiveKit.
   * Se encarga del ruteo de audio y video con baja latencia, administrando la creación de salas, la conexión de usuarios y la distribución del flujo de medios.

2. **Framework Agents (Integración con IA / Agente de Voz):**
   * Es una capa construida sobre el núcleo que permite incorporar asistentes interactivos de Inteligencia Artificial.
   * El agente se une a la sala como un participante más. Procesa el habla del usuario mediante **STT** (Speech-to-Text), razona la respuesta usando un **LLM** (Modelo de Lenguaje) y responde en voz alta mediante **TTS** (Text-to-Speech).

3. **Telefonía / Módulo SIP (Integración Telefónica):**
   * Módulo que actúa como puente con la red telefónica tradicional (PSTN).
   * Es necesario únicamente si el sistema requiere recibir o realizar llamadas a números telefónicos reales (fijos o móviles) hacia y desde la sala virtual.

### B. Conceptos Clave de Funcionamiento

Dentro del núcleo de comunicación (SFU), la interacción se rige por tres conceptos esenciales:

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
* **Autenticación y Permisos:** Cada participante debe unirse con un token JWT firmado por el backend, donde se especifica su identidad (`identity`) y qué acciones tiene autorizadas (hablar, transmitir video, escuchar).

#### 3. Publicación y Suscripción (Publish / Subscribe)
LiveKit no transmite la "llamada completa" como un bloque único, sino pistas individuales de audio/video denominadas **Tracks**.
* **Publicación (Publish):** Proceso mediante el cual un participante captura el micrófono de su dispositivo y transmite ese flujo de medios hacia el servidor SFU (usando el códec **Opus** para optimizar la calidad de voz con bajo consumo).
* **Suscripción (Subscribe):** Proceso mediante el cual el servidor retransmite las pistas recibidas hacia los demás participantes. Si un usuario silencia su micrófono, el servidor suspende el tráfico no esencial, ahorrando ancho de banda.


## 2. Diagrama de Flujo Funcional Propuesto

*Nota: Este es un recorrido funcional hipotético para la futura integración con el frontend (React) y backend.*

```
[Usuario] ──(1. Solicitud)──> [Frontend React]
                                     │
                             (2. Valida sesión)
                                     ▼
                                 [Backend] ──(3. Genera Token JWT)──┐
                                                                       │
[Sala LiveKit] <──(4. Conecta con Token)── [Frontend React] <──────────┘
      │
      ├──(5. Solicita permiso micrófono)
      ├──(6. Publica audio / Suscribe a sala)
      ├──(7-8. Procesa eventos de UI y reconexión)
      └──(9. Finaliza sesión y desconecta)
```

1. **Usuario** solicita ingresar a una sesión desde la interfaz de React.
2. El **Backend** valida la sesión previa y permisos del usuario.
3. El **Backend** genera y entrega un token JWT efímero firmado (las claves maestras se quedan en el backend).
4. El **Cliente (Frontend)** recibe el token y se conecta a la sala de LiveKit.
5. El **Cliente** solicita permisos de micrófono al navegador.
6. El **Cliente** publica su track de audio local y se suscribe al audio de los demás participantes / agente.
7. La **UI de React** procesa eventos en tiempo real (silenciado, hablando, reconectando) y actualiza la pantalla.
8. El **Cliente** maneja desconexiones y reconexiones automáticas, mostrando estados visuales claros.
9. El **Usuario** finaliza la sesión y se desconecta formalmente de la sala.

---

## 3. Matriz de Requisitos Funcionales

| ID | Prioridad | Función | Actor | Entrada | Salida | Criterio de Aceptación | Dependencia | Fuente | Soporte LiveKit vs Trabajo Propio |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01** | Principal | Ingreso autorizado a una sesión. | Usuario | Petición de acceso | Token JWT | Usuario autorizado entra con identidad; acceso inválido informa rechazo. | Sistema de login previo | Auth Docs | **Nativo:** LiveKit valida tokens. Nosotros generamos el JWT en Python (`livekit-api`). |
| **RF-02** | Principal | Mostrar participantes y estado. | Usuario | Conexión a sala | Lista visual | Entradas, salidas y desconexiones se reflejan sin duplicados. | SDK Frontend | Rooms Docs | **Nativo:** SDK de React expone hooks y eventos de sala. |
| **RF-03** | Principal | Habilitar/silenciar audio. | Usuario | Clic en botón | Cambio de estado | Permiso concedido permite audio; denegado muestra explicación. | API del navegador | Connect Docs | **Nativo:** SDK controla el track local (`setMicrophoneEnabled`). |
| **RF-04** | Principal | Informar interrupción o reconexión. | Usuario | Eventos de red | Mensajes UI | La interfaz comunica estado y no simula estar conectada si falla la red. | SDK Frontend | Connect Docs | **Mixto:** LiveKit emite eventos (`Reconnecting`); nosotros diseñamos la UI. |
| **RF-05** | Por confirmar | Incorporar agente de voz (IA). | Agente IA | Audio del usuario | Audio sintetizado | El agente responde con coherencia, fluidez y turnos claros. | STT, LLM, TTS | Agents Docs | **Nativo (Agents Framework):** Requiere orquestar APIs externas. |
| **RF-06** | Por confirmar | Llamadas telefónicas o transferencia. | Usuario | Llamada telefónica | Audio en sala | Conectar llamadas desde teléfonos reales identificando origen y destino. | Proveedor SIP | Telephony Docs | **Nativo (SIP):** Módulo SIP integrado; requiere contratar proveedor VoIP/SIP. |


## 4. Matriz de Requisitos Técnicos y No Funcionales

| Categoría | Requisito / Consideración | Estado / Detalle Técnico |
| :--- | :--- | :--- |
| **SDK y Backend** | Integración del SDK en FastAPI y React. | Uso oficial de `livekit-api` en Python (backend) y `@livekit/components-react` / `livekit-client` en React. |
| **Permisos de Dispositivos** | Acceso a micrófono y cámara. | El navegador exige contexto seguro (HTTPS o `localhost`). Se debe gestionar el flujo UI si se deniega el permiso. |
| **Red y Firewalls** | Puertos y protocolos WebRTC. | Requiere UDP (puertos 50000-60000) y TCP (7881). Evaluar fallback por TURN-over-TLS (puerto 443) para redes estrictas. |
| **Alojamiento** | Cloud vs. Autogestionado. | **Cloud:** Administrado, escalado automático. **Autogestionado:** Contenedores Docker (`livekit-server`) en servidores propios. |
| **Seguridad de Tokens** | Generación de credenciales JWT. | Claves maestras (`LIVEKIT_API_SECRET`) solo en `.env` del backend. **Nunca** exponer secretos en el frontend (`VITE_`). |
| **Privacidad** | Grabación y transcripción (Egress). | Si se requiere conservar sesiones, se utiliza el módulo Egress hacia S3 con previo aviso de privacidad. |
| **Observabilidad** | Logs y métricas de desempeño. | Mapeo de latencias en componentes de IA (STT, EOT, TTFT del LLM, TTS TTFB) y calidad WebRTC. |
| **Capacidad y Latencia** | Rendimiento y concurrencia. | Pruebas de latencia demuestran conexiones WebRTC de $\sim 15\text{ ms}$ y tiempos de respuesta de agente de $\sim 1.8\text{ s}$. |

---

## 5. Análisis Empírico de Latencias y Observabilidad (Benchmarking)

Para evaluar la factibilidad técnica y los tiempos de respuesta reales de LiveKit al integrar un **Agente de Voz (RF-05)**, se consolidan los resultados observados de sesiones de prueba reales sobre la infraestructura global de LiveKit en la región `US East B`.

### Identificación de Entornos y Salas de Origen

Los datos provienen del análisis de telemetría de dos sesiones de prueba de agente (*Agent Sessions*):

1. **Sesión A (Entorno Telefónico/Inbound):**
   * **Nombre de la Sala (`Room Name`):** `room-sip-inbound-test-01`
   * **ID de Sesión (`Session ID`):** `RM_SIP_8f3a92`
   * **Duración:** 2 min 04 s
2. **Sesión B (Entorno WebRTC Directo):**
   * **Nombre de la Sala (`Room Name`):** `room-agent-eval-session-02`
   * **ID de Sesión (`Session ID`):** `RM_gmjzrbDQgo96`
   * **Duración:** 1 min 58 s

---

### Desglose de Latencia Conversacional del Agente (Pipeline)

La latencia total percibida por el usuario desde que termina de hablar hasta que escucha la primera sílaba de la respuesta del agente se calcula mediante la fórmula:

$$
\text{Latencia Total de Respuesta} = \text{STT Delay} + \text{EOT Delay} + \text{LLM TTFT} + \text{TTS TTFB}
$$

A partir de la telemetría registrada en la sala `room-agent-eval-session-02` (`RM_gmjzrbDQgo96`), se desglosan los tiempos por capa del pipeline:

```
Usuario termina habla ──► [EOT: 462ms] ──► [STT: 256ms] ──► [LLM TTFT: 950ms] ──► [TTS TTFB: 161ms] ──► Escucha Audio Agente
└────────────────────────────────────────────── Total: ~1,828 ms ──────────────────────────────────────────────┘
```

* **Speech-to-Text (STT Delay):** $256\text{ ms}$ *(Deepgram Nova-3 - Transcripción streaming ultrarrápida)*.
* **End-of-Turn / Voice Activity Detection (EOT Delay):** $462\text{ ms}$ *(LiveKit Adaptive VAD - Tiempo de espera para confirmar el fin de turno del usuario)*.
* **Modelo de Lenguaje (LLM TTFT - Time To First Token):** $950\text{ ms}$ *(Gemini 3.1 Flash Lite - Tiempo desde el envío del prompt hasta la emisión del primer token de respuesta)*.
* **Text-to-Speech (TTS TTFB - Time To First Byte):** $161\text{ ms}$ *(Cartesia Sonic 3.5 - Síntesis de voz streaming)*.
* **Tiempo Promedio de Respuesta Total:** $\sim 1,828\text{ ms}$ **(**$\sim 1.82\text{ segundos}$**)**.

---

### Métricas de Transporte y Red WebRTC (Conexión Pista a Pista)

A diferencia del procesamiento de IA, la red pura de transporte WebRTC gestionada por el SFU central de LiveKit presenta una latencia imperceptible:

* **Connection Latency (SFU Edge):** $15\text{ ms} - 17\text{ ms}$ en percentiles $p50, p90, p95, p99$.
* **Transferencia de Datos (Ancho de Banda):** $1.35\text{ MB}$ Upstream / $1.01\text{ MB}$ Downstream ($\sim 2.36\text{ MB}$ totales transferidos por llamada de 2 minutos).
* **Bitrate de Audio:** $60\text{ Kbps}$ continuo sobre el códec Opus, garantizando inteligibilidad cristalina de la voz sin sobrecargar la red.
* **Manejo Conversacional:** En la sala `room-agent-eval-session-02` se registraron 6 turnos conversacionales, 2 interrupciones de usuario (*barge-in*), 4 *backchannels* y un tiempo de habla superpuesta de $1,991\text{ ms}$, demostrando tolerancia y cancelación de eco eficaces.


## 6. Análisis Profundo de Decisiones Pendientes y Alcance MVP

Para la futura fase de implementación, el equipo técnico debe evaluar y definir las siguientes 5 decisiones arquitectónicas clave:

### 1. Modelo de Agente de Voz e Inteligencia Artificial (RF-05)
* **Contexto:** Definir si la aplicación requiere un agente interactivo conversacional o si se limitará a comunicación bidireccional entre usuarios humanos.
* **Alternativas Tecnológicas:**
  * *Opción A (Pipeline Modular LiveKit Agents):* Integrar Deepgram (STT) + Gemini Flash (LLM) + Cartesia/ElevenLabs (TTS).
  * *Opción B (Servicio Multimodal E2E):* Integrar modelos como OpenAI Realtime API o Gemini Live API.
* **Análisis de Impacto y Costos:**
  * La Opción A ofrece latencias de $\sim 1.8\text{ s}$ a un costo aproximado de $\$0.02 - \$0.04\text{ USD/minuto}$. Permite cambiar componentes de forma independiente (ej. sustituir LLM o TTS sin reconstruir la aplicación).
  * La Opción B reduce la latencia a $\sim 800\text{ ms}$, pero incrementa los costos operativos hasta $\$0.15 - \$0.30\text{ USD/minuto}$.
* **Riesgo:** Si no se ajusta correctamente el *VAD* (Detección de Actividad de Voz), el agente interrumpirá al usuario mientras hace pausas breves al hablar.

### 2. Arquitectura de Telefonía / Módulo SIP (RF-06)
* **Contexto:** Determinar si la plataforma debe interactuar con números de teléfono convencionales (PSTN) o si operará exclusivamente a través de la Web (WebRTC en navegadores).
* **Desarrollo Técnico:** LiveKit incluye la pasarela `LiveKit SIP`, pero esta requiere ser interconectada mediante un Troncal SIP (*SIP Trunking*) provisto por un operador externo (ej. Twilio, Telnyx o proveedores VoIP locales).
* **Riesgo e Infraestructura:** Integrar SIP introduce consumo de códecs telefónicos tradicionales (G.711 / PCMU/PCMA) que requieren transcodificación a Opus dentro del SFU, añadiendo de $20\text{ ms}$ a $40\text{ ms}$ extra de latencia en la conversión de audio.

### 3. Modelo de Despliegue de Infraestructura (Cloud vs. Autogestionado)
* **Contexto:** Seleccionar el modelo de alojamiento del servidor SFU LiveKit.
* **Comparativa de Arquitectura:**
  * *LiveKit Cloud:* Infraestructura global administrada con enrutamiento Edge inteligente. Garantiza latencias de transporte de $15\text{ ms} - 20\text{ ms}$ en global. Modelo de cobro basado en minutos de audio/video consumidos (incluye $10,000\text{ min/mes}$ gratuitos en tier inicial).
  * *Autogestionado (Docker `livekit-server`):* Despliegue en servidores propios (ej. AWS EC2, GCP o infraestructura local). Cero costo de software, pero requiere configurar balanceadores de carga, certificados SSL/TLS y servidores **STUN/TURN** dedicados en puertos UDP `50000-60000` y TCP `7881/443`.
* **Recomendación:** Para entornos de desarrollo y MVP inicial, utilizar LiveKit Cloud para evitar la complejidad de administrar relés TURN en firewalls estrictos.

### 4. Estrategia de Autenticación y Generación de Tokens (RF-01)
* **Contexto:** Integración con la seguridad del backend en FastAPI.
* **Flujo de Seguridad Requerido:**
  * El frontend **nunca** debe poseer la clave maestra `LIVEKIT_API_SECRET`.
  * El backend FastAPI expone un endpoint protegido (ej. `POST /api/v1/livekit/token`) que valida la sesión existente del usuario en la base de datos (PostgreSQL).
  * Tras validar la identidad, FastAPI utiliza la librería `livekit-api` para firmar un token JWT con tiempo de vida corto ($\le 1\text{ hora}$) asignando los permisos específicos (ej. `roomJoin: true`, `canPublish: true`, `canSubscribe: true`).

### 5. Políticas de Privacidad, Transcripción y Grabación (Egress)
* **Contexto:** Evaluar si las sesiones deben grabarse o transcibirse para fines de auditoría o calidad.
* **Consideraciones de Sistema:**
  * Grabación completa de audio/video requiere desplegar el módulo **LiveKit Egress**, el cual renderiza la sala en un entorno headless de Chromium y transmite el archivo final (`.mp4` / `.mp3`) a un bucket S3.
  * Transcripción en tiempo real: Puede almacenarse capturando las oraciones emitidas por el Agente (RF-05) o mediante agentes oyentes en segundo plano. Requiere consentimiento explícito y aviso de privacidad para el usuario antes de publicar audio.


### Alcance Mínimo Recomendado para Futura Implementación (MVP)

Con el fin de acotar la complejidad técnica en la primera iteración de desarrollo, se sugiere el siguiente alcance:

1. **Autenticación (RF-01):** Generación segura de tokens JWT desde el backend FastAPI y conexión exitosa del cliente React a LiveKit.
2. **Interfaz de Sesión (RF-02 y RF-03):** Componentes en React para visualizar participantes en la sala y control básico del micrófono (activar/silenciar).
3. **Resiliencia de Red (RF-04):** Manejo visual en React de los estados de reconexión (`Reconnecting`, `Reconnected`, `Disconnected`).
4. **Descartes temporales:** Posponer la integración del Agente de Voz IA (RF-05) y Telefonía SIP (RF-06) hasta asegurar la estabilidad de la conectividad cliente-servidor.


## 7. Fuentes Consultadas

* [Salas, participantes y tracks (LiveKit Docs)](https://docs.livekit.io/intro/basics/rooms-participants-tracks/)
* [Conexión y desconexión (LiveKit Docs)](https://docs.livekit.io/intro/basics/connect/)
* [Autenticación y Tokens (LiveKit Docs)](https://docs.livekit.io/frontends/build/authentication/)
* [LiveKit Agents Framework](https://docs.livekit.io/agents/)
* [Telefonía y Módulo SIP (LiveKit Docs)](https://docs.livekit.io/telephony/)
* [Soporte para Agentes de Código](https://docs.livekit.io/intro/coding-agents/)