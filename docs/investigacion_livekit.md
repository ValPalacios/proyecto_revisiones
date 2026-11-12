# Investigación Funcional de LiveKit

**Fecha de consulta de fuentes:** 12 de noviembre de 2026.  
**Estado:** Investigación funcional   



## 1. Conceptos Básicos y Separación de Componentes

LiveKit es una infraestructura de código abierto para comunicaciones en tiempo real (audio y video) basada en arquitectura **SFU (Selective Forwarding Unit)**. En lugar de que cada usuario envíe su audio directamente a todos los demás (P2P), los participantes se conectan a un servidor central que recibe y distribuye los flujos de medios.

### A. Conceptos fundamentales del núcleo
* **Sala (Room):** Espacio virtual aislado donde ocurre la sesión. Se crea dinámicamente cuando entra el primer participante autorizado y se cierra cuando todos salen.
* **Participante (Participant):** Cualquier entidad conectada a la sala (un usuario en navegador, una app móvil o un agente automatizado). Cada participante tiene una identidad única (`identity`) y permisos definidos en su token de acceso.
* **Publicación y Suscripción de Audio (Publish / Subscribe):** LiveKit transmite pistas individuales (*Tracks*). **Publicar** es enviar el audio del micrófono local hacia la sala; **Suscribirse** es recibir y reproducir el audio que otros participantes están publicando.

### B. Separación de componentes (no todo proyecto requiere los tres)
1. **Núcleo de comunicación (SFU):** El servidor base. Gestiona salas, participantes y el enrutamiento de pistas de audio/video en tiempo real. Es el único componente indispensable para conectar personas.
2. **Framework Agents:** Capa opcional para incorporar agentes de IA que participan en la sala como un usuario más, escuchando mediante STT (*Speech-to-Text*), procesando con un LLM y respondiendo con voz mediante TTS (*Text-to-Speech*).
3. **Telefonía / SIP:** Módulo opcional que actúa como pasarela para conectar llamadas de la red telefónica tradicional (PSTN) con una sala de LiveKit.


## 2. Flujo Funcional Propuesto (Recorrido de Usuario y Sistema)

*Nota: El recorrido describe el comportamiento esperado a validar. Las etiquetas **[Hipótesis]** indican supuestos de diseño y **[Decisión del equipo]** señalan definiciones pendientes.*

```text
[Usuario] ──(1. Solicita acceso)──> [Frontend] ──(2. Valida sesión [Decisión])──> [Backend]
                                                                                      │
[Sala LiveKit] <──(4. Conecta con JWT)── [Frontend] <──(3. Emite Token limitado)──────┘
      │
      ├──(5. Solicita permiso de micrófono al navegador)
      ├──(6. Publica track de audio local / Se suscribe a tracks remotos)
      ├──(7. Procesa eventos de sala: entradas, salidas, mute [Hipótesis UI])
      ├──(8. Detecta caída de red -> Muestra reconexión o error claro [Decisión UI])
      └──(9. Usuario finaliza sesión -> Cierra conexión y libera micrófono)
```

1. **Solicitud de acceso:** El usuario selecciona entrar a una sesión desde la interfaz.
2. **[Decisión del equipo] Validación de identidad:** El backend verifica si el usuario tiene sesión activa y permisos para entrar a esa sala específica.
3. **Emisión de token:** El backend firma un token JWT temporal con permisos acotados (ej. solo audio, sala específica) usando su clave secreta (nunca expuesta en el cliente).
4. **Conexión a la sala:** El cliente recibe el token y establece conexión WebRTC con la sala de LiveKit.
5. **Permiso de hardware:** El navegador solicita al usuario autorización para usar el micrófono.
6. **Publicación y suscripción:** Si concede permiso, el cliente publica su pista de audio y se suscribe automáticamente al audio de los demás participantes.
7. **[Hipótesis] Sincronización de estado:** La interfaz escucha eventos del SDK para actualizar en tiempo real quién está conectado y quién tiene el micrófono silenciado.
8. **[Decisión del equipo] Manejo de interrupciones:** Ante pérdida de red, el SDK intenta reconectar mientras la interfaz informa el estado real al usuario sin simular que la llamada sigue activa.
9. **Cierre de sesión:** El usuario presiona salir, el cliente se desconecta de la sala y libera el acceso al micrófono.


## 3. Matriz de Requisitos Funcionales 

| ID | Prioridad | Función | Actor | Entrada | Salida | Criterio de Aceptación | Dependencia | Fuente Oficial | Soporte LiveKit vs. Trabajo Propio | Dudas Abiertas |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RF-01** | Principal | Permitir ingreso autorizado a una sesión/sala. | Usuario | Solicitud de ingreso a sala | Token JWT temporal y conexión a sala | El usuario autorizado entra con su nombre/ID; si el token expira o es inválido, se rechaza el acceso y se muestra mensaje claro. | Sistema de autenticación en backend | [Authentication](https://docs.livekit.io/frontends/build/authentication/) | **Mixto:** LiveKit valida el JWT; **nosotros** construimos el endpoint que valida permisos y firma el token. | ¿Cómo se vinculará la sesión actual del sistema con la emisión del token? |
| **RF-02** | Principal | Mostrar participantes y estado de conexión. | Usuario | Eventos de sala (conexión/desconexión) | Lista visual actualizada de participantes | Al entrar o salir alguien, la lista se actualiza en tiempo real sin duplicar usuarios ni dejar "fantasmas" tras desconexiones. | Conexión activa a sala (RF-01) | [Rooms, participants, and tracks](https://docs.livekit.io/intro/basics/rooms-participants-tracks/) | **Mixto:** El SDK de LiveKit emite eventos de participantes; **nosotros** diseñamos y renderizamos la interfaz. | ¿Se mostrarán roles diferenciados (ej. moderador vs. invitado)? |
| **RF-03** | Principal | Habilitar/silenciar audio y escuchar participantes autorizados. | Usuario | Clic en control de micrófono / permiso navegador | Audio publicado y recepción de audio remoto | Con permiso concedido, el audio se transmite y se refleja el estado *mute/unmute*; si el usuario bloquea el micrófono, se muestra guía para habilitarlo. | Permisos WebRTC del navegador (HTTPS/localhost) | [Connect to a room](https://docs.livekit.io/intro/basics/connect/) | **Nativo (SDK):** LiveKit gestiona captura, publicación y suscripción de pistas; **nosotros** implementamos controles y alertas de permiso. | ¿Qué alternativa tendrá el usuario si entra sin micrófono (modo solo escucha)? |
| **RF-04** | Principal | Informar interrupción, reconectar o finalizar de forma comprensible. | Usuario | Eventos de red (`Reconnecting`, `Disconnected`) | Alerta visual de estado y cierre limpio | La UI bloquea o marca visualmente el estado de reconexión; si la caída es definitiva, cierra la vista de sala y notifica el motivo. | SDK Frontend | [Connect to a room](https://docs.livekit.io/intro/basics/connect/) | **Mixto:** LiveKit detecta estados de red y reintenta conexión; **nosotros** diseñamos los avisos visuales y pantallas de salida. | ¿Cuánto tiempo esperará la UI reconectando antes de dar por terminada la sesión? |
| **RF-05** | Por confirmar | Incorporar agente de voz y sus estados. | Agente IA | Audio publicado por el usuario | Respuesta de voz sintetizada del agente | El agente detecta turnos de habla, responde coherentemente y detiene su audio si el usuario lo interrumpe. | Proveedores externos de STT, LLM y TTS | [LiveKit Agents](https://docs.livekit.io/agents/) | **Nativo (Framework):** LiveKit provee el ciclo de turnos e interrupciones; **nosotros** programamos la lógica del agente y conectamos modelos. | ¿El caso de uso requiere IA o solo comunicación entre personas? ¿Qué proveedores se aprobarán? |
| **RF-06** | Por confirmar | Llamadas telefónicas o transferencia. | Usuario / Operador | Llamada entrante o saliente PSTN | Audio bidireccional integrado en la sala | Se identifica dirección (entrante/saliente), destino y estado de la llamada telefónica dentro de la sesión. | Troncal SIP y proveedor VoIP externo | [LiveKit Telephony](https://docs.livekit.io/telephony/) | **Nativo (Módulo SIP):** LiveKit traduce SIP a WebRTC; **nosotros** contratamos el proveedor telefónico y configuramos reglas de enrutamiento. | ¿Se requieren llamadas a números reales? *(Nota: transferir una sala web no equivale a transferir una llamada telefónica)*. |


## 4. Matriz de Requisitos Técnicos y No Funcionales

| Categoría | Consideración Técnica | Estado / Definición a Acordar (Sin cifras inventadas) |
| :--- | :--- | :--- |
| **SDK y Backend** | Integración de librerías oficiales en el stack del proyecto. | Backend en Python con `livekit-api` para generación de tokens; Frontend en React con `livekit-client` y `@livekit/components-react`. |
| **Permisos de Dispositivos** | Restricciones de seguridad de navegadores modernos para acceso a micrófono. | Exige contexto seguro (**HTTPS** en producción o `localhost` en desarrollo). Si el usuario deniega el permiso, el navegador impide volver a pedirlo por código; la UI debe mostrar instrucciones manuales. |
| **Red y Conectividad** | Tráfico WebRTC en tiempo real a través de firewalls y NAT. | LiveKit utiliza UDP (rango de puertos `50000-60000`) y TCP (`7881`). En redes corporativas restrictivas donde se bloquea UDP, se debe acordar el uso de servidores TURN/TLS (puerto `443`). |
| **Alojamiento** | Modelo de despliegue del servidor LiveKit. | **Por decidir:** **LiveKit Cloud** (servicio administrado, escalado automático, costo por uso) frente a **Autogestionado** (despliegue propio mediante contenedores, requiere mantenimiento, certificados SSL y configuración de red). *(Nota: usar contenedores es una decisión operativa, no una función del usuario).* |
| **Seguridad de Tokens** | Protección de credenciales y control de acceso granular. | `LIVEKIT_API_KEY` y `LIVEKIT_API_SECRET` residen exclusivamente en variables de entorno del backend. **Prohibido** incluir secretos en variables `VITE_` del frontend. Tokens con tiempo de expiración corto y permisos mínimos necesarios (*VideoGrants*). |
| **Privacidad y Datos** | Grabación de audio/video y transcripciones (módulo *Egress*). | **Opción por confirmar:** No se asume grabación en el alcance inicial. Si se activa, requiere definir políticas de retención, almacenamiento seguro y aviso explícito de consentimiento al usuario. |
| **Observabilidad** | Trazabilidad de sesiones, errores de conexión y eventos. | **Por acordar:** Uso del panel de analíticas/eventos en LiveKit Cloud o exportación de logs estructurados y métricas en despliegue propio para diagnosticar desconexiones. |
| **Capacidad y Latencia** | Concurrencia máxima por sala y tiempos de respuesta aceptables. | **A acordar mediante pruebas:** No se fijan cifras teóricas. El equipo debe definir el número esperado de participantes simultáneos y ejecutar pruebas de carga antes de pasar a producción. |


## 5. Decisiones Pendientes y Alcance Mínimo Recomendado

### Decisiones pendientes para el equipo
1. **Alcance funcional (¿Solo humanos o con Agente IA?):** Definir si el objetivo inicial es únicamente comunicación de voz entre usuarios (RF-01 a RF-04) o si requiere un agente conversacional (RF-05), lo cual añade dependencias externas de STT/LLM/TTS y costos variables por minuto.
2. **Necesidad de telefonía real (RF-06):** Confirmar si los usuarios interactuarán exclusivamente desde el navegador web o si es obligatorio recibir/realizar llamadas desde números telefónicos tradicionales mediante un proveedor SIP.
3. **Modelo de infraestructura:** Decidir entre **LiveKit Cloud** (menor esfuerzo operativo y soporte TURN incluido) o **servidor propio** (mayor control de infraestructura, pero exige configurar puertos WebRTC, certificados y mantenimiento).
4. **Mecanismo de autorización:** Definir qué regla de negocio en el backend determinará qué usuario puede solicitar un token para qué sala.
5. **Política de grabación y privacidad:** Confirmar si las sesiones deben quedar grabadas o transcritas (Egress) o si el audio es estrictamente efímero.
6. **Criterios de capacidad y calidad:** Acordar cuántos usuarios simultáneos debe soportar el sistema en su primera fase y cuál será el flujo visual cuando un usuario tenga mala conexión o bloquee su micrófono.

### Alcance mínimo recomendado (Primera iteración sugerida)
*Nota: Esta propuesta orienta la futura planificación técnica y no constituye un compromiso cerrado de implementación.*

* **Incluir en MVP:**
  * Generación segura de tokens JWT acotados desde el backend (RF-01).
  * Conexión a sala desde React con lista de participantes en tiempo real (RF-02).
  * Control de micrófono (*mute/unmute*) con manejo claro de errores de permisos en navegador (RF-03).
  * Indicadores visuales de estado de conexión, reconexión y salida limpia de la sala (RF-04).
* **Posponer para fases posteriores:**
  * Agentes de voz con IA (RF-05), integración telefónica SIP (RF-06) y grabación/transcripción de sesiones (Egress), hasta validar que el flujo base de audio funciona de forma estable.


## 6. Fuentes Consultadas

* [LiveKit Documentation — Rooms, participants, and tracks](https://docs.livekit.io/intro/basics/rooms-participants-tracks/)
* [LiveKit Documentation — Connect to a room](https://docs.livekit.io/intro/basics/connect/)
* [LiveKit Documentation — Authentication & Access Tokens](https://docs.livekit.io/frontends/build/authentication/)
* [LiveKit Documentation — Agents Framework](https://docs.livekit.io/agents/)
* [LiveKit Documentation — Telephony & SIP](https://docs.livekit.io/telephony/)