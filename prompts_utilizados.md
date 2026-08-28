# Prompts Utilizados (Método Socrático)

A continuación, se detalla la progresión de prompts utilizados para guiar el desarrollo del juego, partiendo del código base en `scrach.py` hacia la versión final de `main.py`. Las respuestas de la IA están formuladas con el método socrático: en lugar de dar el código servido, guía al estudiante mediante preguntas y conceptos para que deduzca la implementación real.

---

### Prompt Inicial de Contexto (Instrucción al Sistema)
**Prompt 0 (Usuario):**
> "Actúa como un profesor de programación experto en Python y Pygame. Estoy haciendo un proyecto para el colegio partiendo de un código base llamado `scrach.py`. Quiero que me guíes paso a paso para mejorarlo usando el método socrático. **Regla de oro:** Bajo ninguna circunstancia debes escribirme el código completo ni darme la solución directa. En su lugar, debes explicarme los conceptos teóricos y hacerme preguntas lógicas que me obliguen a razonar cómo estructurar el código y qué conceptos o funciones de la librería estándar debo utilizar. Guíame un paso a la vez."

**Respuesta de la IA (Método Socrático):**
> "¡Entendido! Me parece una forma excelente de aprender. Estaré aquí para guiarte como tu tutor virtual. Analizaremos juntos la lógica y te haré las preguntas correctas para que tú mismo descubras cómo construir las mecánicas de tu juego, paso a paso. Cuando estés listo, dime cuál es la primera mejora que quieres agregar a tu código base y empezaremos a razonarla."

---

### Fase 1: Carga de Assets y Animaciones (Fish Fellas Assetpack)
**Prompt 1 (Usuario):**
> "Tengo un código base con rectángulos (`scrach.py`). Encontré un pack llamado 'Fish Fellas Assetpack' y quiero usar esos sprites (el 'Handsome guy' y el 'Hornfish'). ¿Cómo hago que el personaje se vea animado usando varias imágenes que vienen pegadas en una sola imagen grande (un spritesheet) en lugar de dibujar un cuadrado azul?"

**Respuesta de la IA (Método Socrático):**
> "¡Qué buen assetpack! Si tienes todas las animaciones en una sola hoja, piensa en cómo recortarías una foto grande en partes iguales más pequeñas. En Pygame, una vez que cargas la imagen con `pygame.image.load()`, puedes usar un método llamado `subsurface()` que recorta un área rectangular específica. 
> Si sabes que cada fotograma (frame) del 'Handsome guy' mide 48 píxeles de ancho por 32 de alto, ¿cómo podrías estructurar un bucle `for` (recorriendo filas y columnas) para calcular las coordenadas (X, Y) de cada recorte y guardarlos ordenadamente en una lista como `sprites_run` o `sprites_idle`?"

---

### Fase 2: Movimiento Físico y Doble Salto (Energía)
**Prompt 2 (Usuario):**
> "Pude hacer la función `cargar_spritesheet`. Ahora el personaje necesita saltar. En mi código original `personaje_y` siempre es fijo (`ALTO_PANTALLA - 110`), salvo que choque. Quiero que al apretar la barra espaciadora salte, y si está en el aire y tengo energía (`saltos_extra`), pueda hacer un 'doble salto'."

**Respuesta de la IA (Método Socrático):**
> "Para lograr un salto realista, necesitas imitar la física del mundo real. Si el personaje salta hacia arriba, su posición en el eje Y debe disminuir, pero una fuerza de gravedad debe empujarlo de vuelta hacia abajo constantemente. 
> ¿Qué te parece si creamos una variable `velocidad_y` y otra llamada `gravedad`? En cada frame le sumas la gravedad a la velocidad. Cuando presiones espacio, ¿qué valor negativo le asignarías a `velocidad_y` para impulsarlo hacia arriba? 
> Y para el doble salto, ¿cómo verificarías con un `if` que la posición del personaje no está tocando el `suelo_y` y que `saltos_extra > 0` antes de volver a impulsarlo?"

---

### Fase 3: Efecto Parallax y Obstáculos Aleatorios
**Prompt 3 (Usuario):**
> "La gravedad (`0.8`) y el salto (`-16`) quedaron perfectos. Ahora quiero que el fondo no sea un color liso, sino que tenga 4 capas (distintas imagenes) que se muevan a distinta velocidad para dar profundidad (efecto parallax). Y en vez de un solo auto rojo (`auto_x`), quiero que aparezcan obstáculos aleatorios como anclas, rejas o piedras del assetpack."

**Respuesta de la IA (Método Socrático):**
> "El efecto parallax da muchísima profundidad. Si la capa más lejana se mueve muy lento y la capa frontal rápido, podrías usar una lista de multiplicadores de velocidad, por ejemplo `[0.5, 1.0, 2.0, 3.5]`. Si tienes un desplazamiento u `offset` para cada capa, ¿cómo lo actualizarías multiplicando la velocidad de tu enemigo/escenario por estos valores?
> Para los obstáculos, si tienes una lista de diccionarios (`tipos_enemigos`) que contienen el ancho, alto y la imagen del obstáculo, ¿qué función de la librería estándar `random` podrías invocar para elegir un obstáculo distinto cada vez que el anterior cruza el margen izquierdo de la pantalla?"

---

### Fase 4: Máquina de Estados, Vidas y 'Frames' de Peligro
**Prompt 4 (Usuario):**
> "Usé `random.choice(tipos_enemigos)` para la función `spawn_enemigo()` y funcionó. Pero ahora, si toco un obstáculo pierdo de inmediato como en el original. Quiero tener 5 vidas, y si me pegan, quedar en estado de 'peligro' un par de segundos parpadeando sin recibir más daño. Además, quiero separar el juego para que primero haya un Menú Principal (`estado_partida = "MENU_PRINCIPAL"`)."

**Respuesta de la IA (Método Socrático):**
> "Para separar el menú del juego en sí, estás pensando correctamente: necesitas una 'Máquina de Estados'. Usando esa variable `estado_partida`, ¿cómo reestructurarías el bucle principal (`while juego_activo`) para que dibuje el menú si el estado es 'MENU_PRINCIPAL' y actualice la física solo si es 'JUGANDO'?
> En cuanto a las vidas, si agregas una variable booleana `en_peligro = False`, al detectar un `colliderect` podrías cambiarla a `True` y registrar el tiempo exacto con `pygame.time.get_ticks()`. Piensa en esto: ¿cómo calcularías en los siguientes frames la diferencia de tiempo transcurrido para que, pasados 2000 milisegundos, `en_peligro` vuelva a ser `False` y recuperes la velocidad normal?"

---

### Fase 5: Estrellas Flotantes y la Victoria (Casa Final)
**Prompt 5 (Usuario):**
> "La lógica de `tiempo_actual - tiempo_inicio_peligro < 2000` funcionó bárbaro para la invulnerabilidad. Finalmente, quiero sumar puntos agarrando estrellas flotantes, y que haya una meta física: un contador `distancia_restante` que empiece en 10.0 km y baje de a poco. Al llegar a 0 km, el fondo deja de avanzar, aparece una casa (`img_casatb`) desde la derecha, y cuando el personaje cruza su puerta, el estado pasa a 'VICTORIA'."

**Respuesta de la IA (Método Socrático):**
> "¡Excelente cierre para el juego! Para las estrellas, como necesitas que floten suavemente de arriba a abajo, ¿te imaginas cómo usar la función matemática `math.sin()` modificando ligeramente el eje Y de cada estrella en cada iteración?
> Por otro lado, si `distancia_restante` se reduce en cada frame, ¿qué condición lógica usarías para saber que llegó el momento de hacer que la variable `casa_scroll_x` empiece a entrar en la pantalla? 
> Una vez que la casa se ha detenido en su posición final, y el personaje avanza hacia ella automáticamente, ¿cómo compararías la coordenada `personaje_x` con la posición de la puerta de la casa (usando `img_mediacasa`) para desencadenar el ansiado `estado_partida = "VICTORIA"`?"
