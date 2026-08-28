# Documentación de Desarrollo - Dino Rush: Extinction Escape

## Resumen de lo realizado (Día 1)
Hoy hemos transformado un simple código de recuadros de prueba (`scrach.py`) en el núcleo funcional de un juego estilo "Endless Runner" utilizando **Pygame-CE**.

### 1. Sistema de Spritesheets y Animación
- Creamos la función `cargar_spritesheet()` capaz de tomar una imagen cuadriculada (spritesheet), recortarla matemáticamente en fotogramas individuales (frames) y devolver una lista.
- Implementamos **5 estados de animación** distintos cargados desde la carpeta `assets/sprites/`:
  - `IDLE`: Animación de respiración cuando el juego está pausado (Inicio).
  - `RUN`: Animación principal de carrera.
  - `JUMP`: Animación dinámica de 2 cuadros (uno para cuando la velocidad vertical es negativa/subiendo, y otro para cuando es positiva/cayendo).
  - `HURT`: Animación de 4 cuadros que se reproduce **una sola vez** al recibir daño.
  - `DEATH`: Animación de 4 cuadros que se reproduce **una sola vez** y se congela en el último cuadro al perder la partida.

### 2. Máquina de Estados de Partida
- `INICIO`: El juego arranca congelado. El dinosaurio ejecuta la animación `IDLE` hasta que se presiona la Barra Espaciadora.
- `JUGANDO`: Los enemigos se mueven, se aplican las físicas y colisiones.
- `GAME_OVER`: Todo se detiene, aparece texto en pantalla y el dinosaurio queda tirado en el piso. Se presiona 'R' para reiniciar las variables.

### 3. Físicas y Salto Variable
- Agregamos un sistema de gravedad constante y una barrera que actúa de "suelo".
- **Salto Variable**: Al presionar Espacio, se aplica un impulso vertical (-16). Si se suelta la tecla Espacio en pleno ascenso, la velocidad se corta a la mitad. Esto permite al jugador controlar la altura del salto según cuánto tiempo mantenga presionada la tecla (similar a Super Mario o el Dino de Google Chrome).

### 4. Sistema de Daño (Damage & Stumble Logic)
Implementamos el punto 1 y 2 de tu *Game Design Document*:
- Si el jugador choca un obstáculo:
  - **Fase 1 (0 a 2 segundos)**: El dinosaurio entra en estado de dolor (`HURT`), y la velocidad del juego cae al 60%.
  - **Fase 2 (2 a 12 segundos)**: El dinosaurio vuelve a correr (`RUN`), pero el juego se acelera a un modo intenso (150% de velocidad base).
  - **Fase 3 (+12 segundos)**: El juego vuelve a la normalidad al 100%.
- Si el jugador choca **mientras la Fase 1 o Fase 2 están activas**, entra en estado de Game Over reproduciendo la secuencia `HURT -> DEATH`.
- Visualmente representamos el estado de peligro dibujando un rectángulo naranja en el lado izquierdo simulando la Onda Expansiva (Shockwave).

---

## Dónde modificar valores clave en `main.py`
He dejado comentarios específicos en el código, pero aquí tienes una guía rápida:
- **Gravedad y Salto:** Líneas ~58-61. Cambia `gravedad = 0.8` o la fuerza del salto `-16` en la línea 79.
- **Velocidad de Animación:** Línea ~50. `velocidad_animacion = 0.15`. Un número más alto hará que las piernas se muevan más rápido.
- **Velocidad del Enemigo:** Línea ~54. `velocidad_base_enemigo = 6`.
- **Tiempos de Daño:** Líneas ~124. Allí puedes cambiar los `2000` (2 segundos) o `12000` (12 segundos) del modo castigo/intenso.

---

## Hoja de Ruta de Desarrollo (Paso a Paso)

A partir del código base (`scrach.py`), el desarrollo se planificó y ejecutó de manera incremental, respondiendo a los desafíos que planteaba cada mecánica. A continuación se detalla la profundidad técnica y lógica de cada cambio implementado:

### Fase 1: Motor de Animación y Spritesheets
El primer desafío fue dejar atrás las formas geométricas simples (`pygame.draw.rect`) e incorporar assets reales (el *Fish Fellas Assetpack*).
- **Implementación técnica:** Se creó la función fundamental `cargar_spritesheet()`. Esta función toma la ruta de una imagen grande, sus dimensiones internas (columnas y filas), y recorta iterativamente cada sub-imagen (utilizando `subsurface()`).
- **Lógica aplicada:** Se reemplazó el cuadrado azul del protagonista por arreglos de imágenes cargados en memoria. Esto requirió transformar la renderización estática en un proceso dinámico: se creó la variable `frame_actual` (flotante), a la cual se le suma `velocidad_animacion` en cada iteración. Al dibujar, se castea el número a entero para extraer el fotograma exacto, logrando que la ilusión del movimiento (correr, saltar, respirar en el menú) sea fluida e independiente de los cuadros por segundo del juego.

### Fase 2: Motor de Físicas y Sistema de Energía (Doble Salto)
El salto en el código original era inexistente. Se necesitaba simular un entorno físico realista para darle peso y responsividad a las plataformas.
- **Implementación técnica:** Se añadieron dos vectores matemáticos: `gravedad` y `velocidad_y`. La gravedad afecta ininterrumpidamente a la velocidad vertical acelerando la caída, empujando al jugador hacia abajo hasta que el motor detecta una colisión de piso duro (`suelo_y`).
- **Lógica de Doble Salto:** Para añadir profundidad táctica, no solo se incluyó un salto simple asignando un valor negativo a la velocidad, sino que se diseñó un sistema de "cargas" de energía (`saltos_extra`). Al presionar espacio por segunda vez estando en el aire, si el jugador tiene energía disponible, se consume un slot y se sobreescribe el impulso vertical. Esta energía se recarga progresivamente, calculada en base al tiempo y distancia superada (`distancia_recorrida_salto`).

### Fase 3: Profundidad Estética (Parallax) y Obstáculos Procedimentales
El mundo lineal de `scrach.py` (con un fondo plano y un único auto de comportamiento predecible) debía transformarse en un entorno rico y desafiante.
- **Implementación de Parallax:** Se importaron 4 capas de escenario independientes (cielo estrellado, montañas distantes, plano medio y el suelo). A cada capa se le asignó un ratio de movimiento en la matriz `PARALLAX_VELOCIDADES` (`0.5`, `1.0`, `2.0`, `3.5`). Al renderizar, cada capa se imprime dos veces, una detrás de la otra; cuando una imagen cruza por completo la pantalla, el offset se reinicia, creando un loop óptico perfecto de un mundo inmenso.
- **Generación Procedimental:** Se desechó la lógica del "auto rojo". En su lugar se programó una lista estructurada (diccionarios) conteniendo diversos obstáculos con sus respectivas cajas de colisión (hitboxes) ajustadas: anclas altas, rocas chatas, trampas de pinchos. Mediante `random.choice()`, la función `spawn_enemigo()` se encarga de instanciar un reto distinto e impredecible cada vez que la amenaza previa abandona el área visible izquierda.

### Fase 4: Máquina de Estados Finita y Mitigación de Frustración (Vidas)
Para que el prototipo adquiera la estructura de un videojuego completo, era imperativo modularizar el control de flujo (Menu -> Juego -> Derrota/Victoria).
- **Control de Flujo:** Se refactorizó el bloque lógico principal (`while juego_activo`) diviendo los cálculos físicos, el renderizado de HUD y los controles mediante una variable de estado (`estado_partida`). Esto permitió instanciar un Menú Principal estático y una pantalla reactiva de reinicio (`GAME_OVER`), encapsulando y protegiendo la matemática de físicas únicamente en el estado `JUGANDO`.
- **Frames de Invulnerabilidad (i-frames):** La muerte súbita del código base se consideró demasiado punitiva. Se inyectó una variable `vidas = 5` y un booleano barrera `en_peligro`. Al sufrir una intersección de rectángulos (`colliderect`), se guarda el registro temporal exacto (`pygame.time.get_ticks()`). A partir de ahí, durante un umbral de 2000ms el personaje esquiva por código las colisiones subsiguientes, y se aplica un factor alpha a la imagen (parpadeo visual), otorgándole al jugador una ventana de recuperación.

### Fase 5: Gamificación (Estrellas) y Resolución de Historia (La Casa)
Un juego infinito carece de narrativa; era vital incluir métricas de progreso a corto plazo (puntaje) y un objetivo a largo plazo (el escape final).
- **Recolección Armónica:** Se diseñó un gestor de entidades para las estrellas (`lista_estrellas`). Para que no se sintieran rígidas, se aplicó trigonometría real: la función `math.sin()` del tiempo genera un ciclo de ascenso y descenso en el eje Y (flote armónico). La colisión con ellas las inhabilita y engrosa la puntuación.
- **El Final del Viaje (Cinemática):** Se concibió un regresor de meta (`distancia_restante`). Al quebrar el umbral de 0 km, se intercepta la generación del escenario infinito. Los obstáculos dejan de spawnear, el fondo detiene su scroll perpetuo, e ingresa desde el límite derecho el sprite estructural de la casa. En este micro-estado (`LLEGADA`), el control es abstraído del jugador; el dinosaurio realiza un script de carrera predefinido hacia el centro de la fachada de la casa. Al cruzar el umbral pixel-perfect de la puerta, la máquina transiciona al estado triunfal de `VICTORIA`.
