# Sistema de Seguridad Visual Industrial
**Proyecto de Instrumentación Virtual | Versión 1.0 (Release Industrial)**

Este proyecto implementa una solución de **Visión Artificial aplicada a la Seguridad Industrial**. El sistema actúa como un sensor óptico inteligente capaz de detectar intrusiones en zonas de alto riesgo (celdas robóticas, tableros eléctricos) sin necesidad de barreras físicas o sensores infrarrojos costosos.

---

## 🏗 Arquitectura del Software (Nivel Industrial)

El diseño sigue una filosofía de sistemas modulares, separando claramente la adquisición, el procesamiento y la lógica de decisión, simulando la estructura de un PLC o sistema SCADA.

### **Capa 1 – Adquisición de Video (`CameraManager`)**
*   **Función:** Interfaz con hardware de captura (Cámaras USB/Industriales).
*   **Características:** Autodetección de dispositivos, control de resolución y manejo de errores de desconexión.
*   **Tecnología:** OpenCV backend (DirectShow/MSMF).

### **Capa 2 – Preprocesamiento (`ProcessingEngine`)**
*   **Función:** Acondicionamiento de señal visual.
*   **Procesos:** Conversión a escala de grises, filtrado Gaussiano para ruido eléctrico/térmico, y normalización de iluminación.

### **Capa 3 – Modelo de Referencia (`StateManager: COLD`)**
*   **Función:** Calibración del entorno seguro.
*   **Lógica:** Captura una "línea base" del fondo estático. Permite recalibración manual ante cambios de luz (Reset).

### **Capa 4 – Detección de Cambio (`ProcessingEngine`)**
*   **Función:** Comparación diferencial en tiempo real.
*   **Algoritmo:** Sustracción de fondo (`absdiff`) + Umbralización binaria (`threshold`) + Extracción de contornos.

### **Capa 5 – Análisis por Zonas (`ZoneManager`)**
*   **Función:** Filtrado espacial de eventos.
*   **Lógica:** Solo genera eventos si el cambio ocurre INTERNAMENTE en un polígono definido por el usuario (ROI). Ignora movimiento en pasillos seguros.

### **Capa 6 – Lógica de Estados (`DecisionEngine`)**
*   **Estados:**
    *   `COLD` (Seguro/Mantenimiento): Sistema pasivo, permite configuración.
    *   `HOT` (Vigilancia/Producción): Sistema activo, dispara alarmas ante intrusiones.

### **Capa 7 – Interfaz Hombre-Máquina (`UIRenderer`)**
*   **HMI:** Panel de control visual con botones en tiempo real (ACTIVAR, RESET, OPCIONES).
*   **Feedback:** Visualización de zonas (Rojo/Verde), alarmas visuales y contadores de eventos.

### **Capa 8 – Persistencia (JSON)**
*   **Función:** Almacenamiento no volátil de la configuración de zonas.
*   **Recuperación:** Permite reiniciar el sistema manteniendo la delimitación de seguridad.

---

## � Diagrama a Bloques del Sistema

```
┌──────────────┐
│ Cámara USB   │
└──────┬───────┘
       │
┌──────▼───────┐
│ Adquisición  │
│ de Video     │
└──────┬───────┘
       │
┌──────▼───────┐
│ Preprocesa-  │
│ miento       │
└──────┬───────┘
       │
┌──────▼───────┐        ┌──────────────┐
│ Modelo de    │◄──────►│ Estado COLD  │
│ Referencia   │        └──────────────┘
└──────┬───────┘
       │
┌──────▼───────┐
│ Detección de │
│ Movimiento   │
└──────┬───────┘
       │
┌──────▼───────┐
│ Análisis de  │
│ Zonas        │
└──────┬───────┘
       │
┌──────▼───────┐
│ Lógica de    │
│ Seguridad    │
└──────┬───────┘
       │
┌──────▼───────┐
│ Interfaz     │
│ Gráfica HMI  │
└──────┬───────┘
       │
┌──────▼───────┐
│ Persistencia │
│ JSON         │
└──────────────┘
```

---

## 📝 Pseudocódigo de Control (Lógica Principal)

```text
INICIAR SISTEMA
CARGAR configuración (Zonas, Parámetros)
ABRIR cámara seleccionada

ESTADO ← COLD

MIENTRAS sistema activo:
    frame ← capturar_video()

    frame_proc ← preprocesar(frame)

    SI zoom_activado:
        frame_proc ← aplicar_zoom(frame_proc)

    SI ESTADO = COLD:
        mostrar_interfaz(frame_proc)
        SI operador_presiona_ACTIVAR:
            referencia ← frame_proc
            ESTADO ← HOT

    SI ESTADO = HOT:
        diferencia ← abs(frame_proc - referencia)
        mascara ← umbralizar(diferencia)

        contornos ← encontrar_contornos(mascara)

        PARA cada contorno:
            SI area(contorno) > AREA_MINIMA:
                SI contorno_intersecta_zona_prohibida:
                    generar_alerta_visual()
                    incrementar_contador()

        mostrar_interfaz_vigilancia(frame_proc)

    leer_eventos_mouse_teclado()

CERRAR cámara
GUARDAR configuración
TERMINAR
```

---

## 🎮 Manual de Operación (HMI)

El sistema cuenta con una interfaz gráfica operada 100% mediante Mouse, diseñada para pantallas táctiles o estaciones de trabajo.

### Panel de Control Principal
*   **`[ ACTIVAR ]`**: Pasa el sistema a estado **HOT**. Toma la imagen actual como referencia segura.
*   **`[ RESET ]`**: Regresa a estado **COLD**. Detiene alarmas y permite mantenimiento.
*   **`[ OPCIONES ]`**: Despliega el menú de ingeniería para ajuste de parámetros.
*   **`[ SALIR ]`**: Cierre controlado de la aplicación.

### Configuración de Ingeniería (Menú Opciones)
*   **CAMARA ID**: Selección del dispositivo de entrada.
*   **SENSIBILIDAD (Threshold)**: Umbral de diferencia de pixel (0-255). Mayor valor = Menos sensible a ruido de luz.
*   **AREA MINIMA**: Filtro de tamaño de objeto. Evita falsos positivos por insectos o polvo.
*   **ZOOM / CALIDAD**: Ajuste de ROI digital y filtros de mejora (Sharpening).
*   **PROCESADOR**: Selección de hardware de cómputo (CPU vs GPU OpenCL).

### Definición de Zonas (Setup)
1.  En estado **COLD**, hacer **Click Izquierdo** sobre el video para marcar vértices del polígono de seguridad.
2.  Hacer **Click Derecho** para cerrar el polígono.
3.  Pulsar tecla **`S`** para guardar la configuración en disco.

---

## 🗣️ Guion de Defensa Oral

Para la presentación del proyecto:

### 1. Introducción
> "Este proyecto implementa un sistema de seguridad visual industrial basado únicamente en visión por computadora. El objetivo es detectar intrusiones en zonas críticas definidas por el usuario, sin sensores físicos adicionales, usando solo una cámara estándar."

### 2. Problema Industrial
> "En la industria existen zonas que deben permanecer libres durante operación: celdas robóticas, áreas de mantenimiento o líneas energizadas. Normalmente se usan sensores costosos o barreras físicas. Este sistema ofrece una alternativa flexible y de bajo costo."

### 3. Arquitectura
> "El sistema está dividido en adquisición, procesamiento, detección, análisis por zonas y lógica de seguridad. Opera en dos estados: COLD para calibración segura y HOT para vigilancia activa, similar a procedimientos industriales reales."

### 4. Demostración (Acción)
> "Voy a definir una zona prohibida... (Dibujar zona).
> El sistema está en COLD, por lo tanto aprende el fondo... (Click ACTIVAR).
> Cambio a HOT.
> Al ingresar un objeto, el sistema detecta la intrusión únicamente dentro de la zona definida."
> *(Mostrar detección)*.

### 5. Aplicación Industrial
> "Este sistema puede integrarse como pre-filtro visual para PLCs, sistemas SCADA o grabadores industriales, reduciendo falsas alarmas y costos de implementación."

### 6. Cierre
> "Es un sistema escalable, configurable en tiempo real y completamente demostrable."

---
*Escuela Superior de Ingeniería Mecánica y Eléctrica (IPN)*
