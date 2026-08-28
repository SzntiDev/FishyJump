import pygame
import sys
import random
import math

# ---------- Constantes ----------
ANCHO_PANTALLA = 800
ALTO_PANTALLA = 450
FPS = 60

COLOR_CIELO = (135, 206, 235)

# ---------- Variables del Personaje ----------
personaje_x = 100
personaje_y = ALTO_PANTALLA - 150

# ---------- Funciones ----------

def cargar_spritesheet(ruta_imagen, ancho_frame, alto_frame, columnas, filas):
    """
    Carga un spritesheet y lo recorta en una lista de fotogramas individuales.
    """
    spritesheet = pygame.image.load(ruta_imagen).convert_alpha()
    frames = []
    
    for fila in range(filas):
        for col in range(columnas):
            x = col * ancho_frame
            y = fila * alto_frame
            # Recortamos un rectangulo de la imagen original
            rectangulo_recorte = pygame.Rect(x, y, ancho_frame, alto_frame)
            frame = spritesheet.subsurface(rectangulo_recorte)
            frames.append(frame)
            
    return frames

# ---------- Inicialización ----------
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pantalla_juego = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Dino Rush: Extinction Escape")
reloj = pygame.time.Clock()

# ---------- Carga de Música ----------
try:
    pygame.mixer.music.load("assets/sprites/Fish Fellas Assetpack/Soundtracks/Fish_Fellas_Soundtrack.mp3")
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1) # -1 para loop infinito
except Exception as e:
    print(f"Error cargando soundtrack: {e}")

# ---------- Superficie para Fog Rojo (Vignette) ----------

# Cargando sprites de "Fish Fellas Assetpack"
sprites_idle = []
sprites_run = []
sprites_jump = []
sprites_hurt = []
sprites_death = []

def seleccionar_personaje(tipo):
    global sprites_idle, sprites_run, sprites_jump, sprites_hurt, sprites_death
    if tipo == "azul": # Handsome guy in sneakers
        base_path = "assets/sprites/Fish Fellas Assetpack/Sprites/Characters/Handsome guy in sneakers/"
        sprites_idle  = cargar_spritesheet(base_path + "Handsome_guy_in_sneakers_idle.png",    48, 32, 2, 1)
        sprites_run   = cargar_spritesheet(base_path + "Handsome_guy_in_sneakers_walk.png",    48, 32, 6, 1)
        _jumpfall     = cargar_spritesheet(base_path + "Handsome_guy_in_sneakers_jumpfall.png", 48, 32, 4, 1)
        sprites_jump  = [_jumpfall[3], _jumpfall[2]]
        sprites_hurt  = cargar_spritesheet(base_path + "Handsome_guy_in_sneakers_damaged.png", 48, 32, 4, 1)
        sprites_death = cargar_spritesheet(base_path + "Handsome_guy_in_sneakers_damaged.png", 48, 32, 4, 1)
    else: # verde (Hornfish)
        base_path = "assets/sprites/Fish Fellas Assetpack/Sprites/Characters/Hornfish/"
        sprites_idle  = cargar_spritesheet(base_path + "Hornfish-idle.png", 64, 48, 4, 1)
        sprites_run   = cargar_spritesheet(base_path + "Hornfish_walk.png", 64, 48, 6, 1)
        # Hornfish no tiene animacion de salto, reusamos el primer frame de walk y el ultimo
        sprites_jump  = [sprites_run[0], sprites_run[4]] #sprites_run[2],
        sprites_hurt  = cargar_spritesheet(base_path + "Hornfish_damaged.png", 64, 48, 3, 1)
        sprites_death = cargar_spritesheet(base_path + "Hornfish_damaged.png", 64, 48, 3, 1)

# Por defecto cargamos azul para no tener variables vacías
seleccionar_personaje("azul")

# Cargar animación de sangre (spritesheet 1_100x100px.png tiene 18 frames en una grilla de 6x6)
try:
    sprites_sangre = cargar_spritesheet("assets/sprites/hurt/1_100x100px.png", 100, 100, 6, 6)[:18]
except Exception:
    sprites_sangre = []

# Cargar VFX de correr y saltar
try:
    _frames_run = cargar_spritesheet("assets/sprites/Fish Fellas Assetpack/vfx/SmokeFX Lite SpriteSheet 1A-7.png", 64, 64, 9, 1)
    # Escalar particulas x1.5 (96x96)
    vfx_run = [pygame.transform.scale(f, (96, 96)) for f in _frames_run]
except Exception as e:
    print("Error cargando VFX Run:", e)
    vfx_run = []

try:
    _frames_jump = cargar_spritesheet("assets/sprites/Fish Fellas Assetpack/vfx/SmokeFX Lite SpriteSheet 4A-3.png", 64, 61, 63, 1)
    # Escalar particulas x1.5 (96x91)
    vfx_jump = [pygame.transform.scale(f, (96, 91)) for f in _frames_jump]
except Exception as e:
    print("Error cargando VFX Jump:", e)
    vfx_jump = []

lista_vfx = [] # Lista para almacenar partículas activas
ultimo_paso = -1

# ---------- Variables de Estado de la Partida ----------
estado_partida = "MENU_PRINCIPAL" # "MENU_PRINCIPAL", "INICIO", "JUGANDO", "GAME_OVER", "PAUSA", "AJUSTES"
estado_previo_ajustes = "MENU_PRINCIPAL"
estado_actual = "IDLE" # Animación del dinosaurio: "IDLE", "RUN", "JUMP"
frame_actual = 0
velocidad_animacion = 0.15 # Qué tan rápido cambia el frame
velocidad_animacion_run = 0.25 # Animación de RUN más rápida

# Cargar imágenes de UI de vida
img_vidas = []
for i in range(1, 7):
    try:
        img = pygame.image.load(f"assets/sprites/Fish Fellas Assetpack/Sprites/UI/health{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (int(img.get_width()*1.3), int(img.get_height()*1.3)))
        img_vidas.append(img)
    except Exception:
        pass

# Cargar imágenes de UI de energía (saltos dobles)
img_energia = []
for i in range(1, 7):
    try:
        img = pygame.image.load(f"assets/sprites/Fish Fellas Assetpack/Sprites/UI/energy{i}.png").convert_alpha()
        img = pygame.transform.scale(img, (int(img.get_width()*1.3), int(img.get_height()*1.3)))
        img_energia.append(img)
    except Exception:
        pass

try:
    img_chselect = pygame.image.load("assets/sprites/Fish Fellas Assetpack/Sprites/UI/chselect.png").convert_alpha()
    # Sin escalar: tamaño original (más pequeño)
    
    img_casatb = pygame.image.load("assets/sprites/Fish Fellas Assetpack/Sprites/Objects/casatb.png").convert_alpha()
    img_casatb = pygame.transform.scale(img_casatb, (img_casatb.get_width()*2, img_casatb.get_height()*2))
    
    img_mediacasa = pygame.image.load("assets/sprites/Fish Fellas Assetpack/Sprites/Objects/mediacasa.png").convert_alpha()
    img_mediacasa = pygame.transform.scale(img_mediacasa, (img_mediacasa.get_width()*2, img_mediacasa.get_height()*2))
except:
    img_chselect = None
    img_casatb = None
    img_mediacasa = None

# ---------- Imágenes de Estrellas (Puntos) ----------
sprites_estrellas = []
datos_estrellas = [
    {"ruta": "assets/sprites/Fish Fellas Assetpack/Sprites/Other/star-blue.png", "puntos": 10, "velocidad_y": 0.02, "amplitud": 30},
    {"ruta": "assets/sprites/Fish Fellas Assetpack/Sprites/Other/star-green.png", "puntos": 20, "velocidad_y": 0.03, "amplitud": 45},
    {"ruta": "assets/sprites/Fish Fellas Assetpack/Sprites/Other/star-purple.png", "puntos": 50, "velocidad_y": 0.04, "amplitud": 60},
    {"ruta": "assets/sprites/Fish Fellas Assetpack/Sprites/Other/Stars - copia.png", "puntos": 100, "velocidad_y": 0.06, "amplitud": 80}
]

try:
    for data in datos_estrellas:
        # 16x13 cada frame, 4 frames
        frames = cargar_spritesheet(data["ruta"], 16, 13, 4, 1)
        # Escalar x2 para que se vean mejor
        frames = [pygame.transform.scale(f, (32, 26)) for f in frames]
        sprites_estrellas.append(frames)
except Exception as e:
    print(f"Error cargando estrellas: {e}")

# ---------- Carga de UI y Fuentes Personalizadas ----------
try:
    fuente_grande = pygame.font.Font("assets/sprites/Fish Fellas Assetpack/Fonts/PixelifySans-Bold.ttf", 48)
    fuente_chica = pygame.font.Font("assets/sprites/Fish Fellas Assetpack/Fonts/PixelifySans-Bold.ttf", 24)
except Exception:
    fuente_grande = pygame.font.SysFont("arial", 48, bold=True)
    fuente_chica = pygame.font.SysFont("arial", 24)

try:
    img_banner = pygame.image.load("assets/sprites/Fish Fellas Assetpack/Sprites/Other/title_banner.png").convert_alpha()
    img_banner = pygame.transform.scale(img_banner, (300, 80))
    
    # --- Funciones Auxiliares para Menús de Texto ---
    def obtener_rects_menu(opciones, y_inicial=220, espaciado=50):
        rects = {}
        for i, opc in enumerate(opciones):
            texto = fuente_chica.render(opc, True, (255, 255, 255))
            r = texto.get_rect(center=(175, y_inicial + i * espaciado))
            r.inflate_ip(30, 20) # Area de click más grande
            rects[opc] = r
        return rects

    def dibujar_panel_menu(titulo, opciones, rects_opciones, y_inicial=220, incluir_banner=False):
        overlay = pygame.Surface((350, ALTO_PANTALLA), pygame.SRCALPHA)
        overlay.fill((0, 40, 120, 180)) # Rectángulo azul semitransparente
        pantalla_juego.blit(overlay, (0, 0))
        
        if incluir_banner and img_banner:
            x_b = (350 - img_banner.get_width()) // 2
            pantalla_juego.blit(img_banner, (x_b, 40))
        elif titulo:
            sombra = fuente_grande.render(titulo, True, (0, 0, 50))
            txt_t = fuente_grande.render(titulo, True, (255, 255, 255))
            rect_t = txt_t.get_rect(center=(175, 100))
            pantalla_juego.blit(sombra, (rect_t.x + 2, rect_t.y + 2))
            pantalla_juego.blit(txt_t, rect_t)
            
        mx, my = pygame.mouse.get_pos()
        for opc in opciones:
            rect = rects_opciones[opc]
            color = (255, 255, 0) if rect.collidepoint(mx, my) else (255, 255, 255)
            txt_opc = fuente_chica.render(opc, True, color)
            pantalla_juego.blit(txt_opc, txt_opc.get_rect(center=rect.center))

except Exception as e:
    print(f"Error cargando UI botones/banner: {e}")
    img_banner = None
    def obtener_rects_menu(*args, **kwargs): return {}
    def dibujar_panel_menu(*args, **kwargs): pass

# Placeholders de pantallas (reemplaza None con tu imagen cargada)
img_pantalla_inicio = None    # [PLACEHOLDER INICIO]
img_pantalla_gameover = None  # [PLACEHOLDER GAME OVER]
img_pantalla_victoria = None  # [PLACEHOLDER VICTORIA]

# ---------- Variables de Peligro (Damage System) ----------
vidas = 5 # 5 golpes hasta morir
en_peligro = False
tiempo_inicio_peligro = 0

# ---------- Variables de Doble Salto (Energía) ----------
saltos_extra = 5 # 5 saltos dobles disponibles
distancia_recorrida_salto = 0.0 # Acumulador para recargar (cada 0.5)
ha_hecho_doble_salto = False # Solo un doble salto por vez en el aire

# ---------- Variables de Puntos ----------
puntuacion = 0
lista_estrellas = [] # {'x', 'base_y', 'tipo', 'frame_float'}

velocidad_base_enemigo = 12 # [MODIFICAR AQUÍ] Para hacer el juego más rápido o lento en general

distancia_restante = 1.0 # 1 km recorrido

# ---------- Variables de Física ----------
suelo_y = ALTO_PANTALLA - 150
personaje_y = suelo_y
velocidad_y = 0
gravedad = 0.8 # [MODIFICAR AQUÍ] Si quieres que caiga más rápido o flote más

# ---- Variables de la casa (scroll continuo) ----
# La casa empieza lejos a la derecha y se acerca con el mundo.
CASA_MARGEN_BORDE = 50
_ancho_casa = img_casatb.get_width() if img_casatb else 380
CASA_X_FINAL = ANCHO_PANTALLA - _ancho_casa - CASA_MARGEN_BORDE
casa_scroll_x = float(ANCHO_PANTALLA + 800)  # empieza fuera de pantalla

# ---------- Variables de Entorno ----------
# Cargamos imágenes de entorno para parallax
# Velocidades de scroll: capa 1 (más lejana, lenta) -> capa 4 (más cercana, rápida)
PARALLAX_VELOCIDADES = [0.5, 1.0, 2.0, 3.5]  # multiplicador sobre velocidad_base_enemigo
img_fondos_capas = []
parallax_offsets = [0.0, 0.0, 0.0, 0.0]  # posición horizontal actual de cada capa
offset_x_suelo = 0.0  # posición horizontal del suelo
try:
    rutas_fondos = [
        "assets/sprites/Fish Fellas Assetpack/Sprites/Background/Background1.png",
        "assets/sprites/Fish Fellas Assetpack/Sprites/Background/Background2.png",
        "assets/sprites/Fish Fellas Assetpack/Sprites/Background/Background3.png",
        "assets/sprites/Fish Fellas Assetpack/Sprites/Background/Background4.png"
    ]
    for ruta in rutas_fondos:
        img = pygame.image.load(ruta).convert_alpha()
        img = pygame.transform.scale(img, (ANCHO_PANTALLA, ALTO_PANTALLA))
        img_fondos_capas.append(img)
    img_fondo = img_fondos_capas[0]
except Exception as e:
    print(f"Error cargando fondo: {e}")
    img_fondo = None
    img_fondos_capas = []

# ---------- Suelo desde Tilemap ----------
# Tilemap.png  -> tile para la fila superior del suelo
# Tilemap2.png -> tile para rellenar el resto del suelo
TILE_SIZE = 32
TILE_SCALE = 3         # escala a 32x32px
TILE_SIZE_SCALED = TILE_SIZE * TILE_SCALE

try:
    _base_tiles = "assets/sprites/Fish Fellas Assetpack/Sprites/Tilemap/"
    tile_suelo = pygame.transform.scale(
        pygame.image.load(_base_tiles + "Tilemap.png").convert_alpha(),
        (TILE_SIZE_SCALED, TILE_SIZE_SCALED)
    )
    # Pre-generar superficie del suelo tileada (todas las filas usan Tilemap.png)
    suelo_alto_px = max(ALTO_PANTALLA - (suelo_y + 90), TILE_SIZE_SCALED)
    img_suelo_tileado = pygame.Surface((ANCHO_PANTALLA, suelo_alto_px), pygame.SRCALPHA)
    for ty_off in range(0, suelo_alto_px, TILE_SIZE_SCALED):
        for tx in range(0, ANCHO_PANTALLA, TILE_SIZE_SCALED):
            img_suelo_tileado.blit(tile_suelo, (tx, ty_off))
except Exception as e:
    print(f"Error cargando tilemap de suelo: {e}")
    img_suelo_tileado = None


# ---------- Objetos y Decoraciones ----------
_base_obj = "assets/sprites/Fish Fellas Assetpack/Sprites/Objects/"

# Cargar Obstáculos
tipos_enemigos = []
obstaculos_files = [
    ("ancla", "ancla.png"),
    ("piedra1", "piedra1.png"),
    ("piedra2", "piedra2.png"),
    ("piedra3", "piedra3.png"),
    ("piedra4", "piedra4.png"),
    ("pinchogrande", "pinchogrande.png"),
    ("pinchos", "pinchos.png"),
    ("reja", "reja.png")
]
for nombre, archivo in obstaculos_files:
    try:
        img = pygame.image.load(_base_obj + archivo).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width()*3, img.get_height()*3))
        # Limitar la altura para que el jugador pueda saltarlo (máx ~120px)
        if img.get_height() > 120:
            factor = 120.0 / img.get_height()
            img = pygame.transform.scale(img, (int(img.get_width() * factor), 120))
            
        tipos_enemigos.append({
            "nombre": nombre,
            "ancho": img.get_width(),
            "alto": img.get_height(),
            "color": (255, 0, 0),
            "imagen": img
        })
    except Exception as e:
        print(f"Error cargando {archivo}: {e}")

if not tipos_enemigos:
    # Fallback
    tipos_enemigos = [{"nombre": "error", "ancho": 32, "alto": 32, "color": (255, 0, 0), "imagen": None}]

# Cargar Decoraciones (Algas y Corales)
tipos_decoraciones = []
decoraciones_files = [
    "alga1.png", "alga2.png", "alga3.png", "alga4.png", 
    "coralamarillo.png", "coralrojo.png", "coralvioleta.png"
]
for f in decoraciones_files:
    try:
        img = pygame.image.load(_base_obj + f).convert_alpha()
        img = pygame.transform.scale(img, (img.get_width()*2, img.get_height()*2))
        tipos_decoraciones.append(img)
    except Exception:
        pass

lista_decoraciones = []

enemigo_actual = random.choice(tipos_enemigos)
enemigo_ancho = enemigo_actual["ancho"]
enemigo_alto = enemigo_actual["alto"]
enemigo_x = ANCHO_PANTALLA
enemigo_y = suelo_y + 96 - enemigo_alto # A ras del suelo
velocidad_enemigo = velocidad_base_enemigo

def spawn_enemigo():
    global enemigo_actual, enemigo_ancho, enemigo_alto, enemigo_x, enemigo_y
    enemigo_actual = random.choice(tipos_enemigos)
    enemigo_ancho = enemigo_actual["ancho"]
    enemigo_alto = enemigo_actual["alto"]
    enemigo_x = ANCHO_PANTALLA
    enemigo_y = suelo_y + 96 - enemigo_alto
    
    # Spawn de estrella menos frecuente (40% de probabilidad)
    if random.random() < 0.4:
        spawn_estrella()

def spawn_estrella():
    if not sprites_estrellas: return
    tipo_indice = random.randint(0, len(sprites_estrellas) - 1)
    base_y = random.randint(suelo_y - 160, suelo_y - 80)
    
    # Colocar justo en el medio del intervalo entre este enemigo y el siguiente
    mitad_distancia = (ANCHO_PANTALLA + enemigo_ancho) // 2
    
    lista_estrellas.append({
        "x": ANCHO_PANTALLA + mitad_distancia,
        "base_y": base_y,
        "y": base_y,
        "tipo": tipo_indice,
        "frame_float": 0.0,
        "tiempo_flote": 0.0,
        "activa": True
    })

# ---------- Bucle Principal ----------
juego_activo = True

while juego_activo:
    reloj.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            juego_activo = False
            
        # Selección de personaje y botones con el mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mx, my = evento.pos
            if estado_partida == "MENU_PRINCIPAL":
                rects = obtener_rects_menu(["Comenzar Partida", "Ajustes"], y_inicial=240)
                if rects["Comenzar Partida"].collidepoint(mx, my):
                    estado_partida = "INICIO"
                elif rects["Ajustes"].collidepoint(mx, my):
                    estado_partida = "AJUSTES"
                    estado_previo_ajustes = "MENU_PRINCIPAL"
            elif estado_partida == "AJUSTES":
                rects = obtener_rects_menu(["Volumen", "Dificultad", "Cambiar Personaje", "Volver"], y_inicial=200)
                if rects["Cambiar Personaje"].collidepoint(mx, my):
                    estado_partida = "INICIO"
                elif rects["Volver"].collidepoint(mx, my):
                    estado_partida = estado_previo_ajustes
            elif estado_partida == "PAUSA":
                rects = obtener_rects_menu(["Continuar", "Ajustes", "Menú Principal"], y_inicial=200)
                if rects["Continuar"].collidepoint(mx, my):
                    estado_partida = "JUGANDO"
                elif rects["Ajustes"].collidepoint(mx, my):
                    estado_partida = "AJUSTES"
                    estado_previo_ajustes = "PAUSA"
                elif rects["Menú Principal"].collidepoint(mx, my):
                    estado_partida = "MENU_PRINCIPAL"
            elif estado_partida == "INICIO":
                if mx < ANCHO_PANTALLA // 2:
                    seleccionar_personaje("azul")
                else:
                    seleccionar_personaje("verde")
                
                if estado_previo_ajustes == "PAUSA":
                    estado_partida = "PAUSA"
                else:
                    estado_partida = "JUGANDO"
                    estado_actual = "RUN"
                    frame_actual = 0
            elif estado_partida in ("GAME_OVER", "VICTORIA"):
                rects = obtener_rects_menu(["Reintentar", "Menú Principal"], y_inicial=250)
                if rects["Reintentar"].collidepoint(mx, my):
                    estado_partida = "JUGANDO"
                    estado_actual = "RUN"
                    personaje_x = 100
                    personaje_y = suelo_y
                    velocidad_y = 0
                    spawn_enemigo()
                    en_peligro = False
                    vidas = 5
                    distancia_restante = 1.0
                    saltos_extra = 5
                    distancia_recorrida_salto = 0.0
                    ha_hecho_doble_salto = False
                    puntuacion = 0
                    lista_estrellas.clear()
                    velocidad_enemigo = velocidad_base_enemigo
                    casa_scroll_x = float(ANCHO_PANTALLA + 800)
                elif rects["Menú Principal"].collidepoint(mx, my):
                    estado_partida = "MENU_PRINCIPAL"

        # Si el jugador presiona una tecla
        if evento.type == pygame.KEYDOWN:
            if estado_partida == "JUGANDO":
                if evento.key == pygame.K_ESCAPE:
                    estado_partida = "PAUSA"
                elif evento.key == pygame.K_SPACE:
                    if personaje_y >= suelo_y:
                        # Salto normal
                        velocidad_y = -16 # [MODIFICAR AQUÍ] Fuerza del salto (número más negativo = salta más alto)
                        estado_actual = "JUMP"
                        frame_actual = 0
                        ha_hecho_doble_salto = False
                    elif saltos_extra > 0 and not ha_hecho_doble_salto:
                        # Doble salto
                        velocidad_y = -16
                        estado_actual = "JUMP"
                        frame_actual = 0
                        saltos_extra -= 1
                        ha_hecho_doble_salto = True
            elif estado_partida in ("GAME_OVER", "VICTORIA"):
                if evento.key == pygame.K_r:
                    # Reiniciar variables para jugar de nuevo
                    estado_partida = "JUGANDO"
                    estado_actual = "RUN"
                    personaje_x = 100
                    personaje_y = suelo_y
                    velocidad_y = 0
                    spawn_enemigo()
                    en_peligro = False
                    vidas = 5
                    distancia_restante = 10.0
                    saltos_extra = 5
                    distancia_recorrida_salto = 0.0
                    ha_hecho_doble_salto = False
                    puntuacion = 0
                    lista_estrellas.clear()
                    velocidad_enemigo = velocidad_base_enemigo
                    casa_scroll_x = float(ANCHO_PANTALLA + 800)
                
        # Si el jugador suelta una tecla
        if evento.type == pygame.KEYUP:
            if evento.key == pygame.K_SPACE and velocidad_y < 0 and estado_partida == "JUGANDO":
                velocidad_y /= 2 

    # --- LÓGICA PRINCIPAL ---
    if estado_partida in ("JUGANDO", "LLEGADA"):
        # Física
        velocidad_y += gravedad
        personaje_y += velocidad_y

        # Colisión con el suelo
        if personaje_y >= suelo_y:
            personaje_y = suelo_y
            velocidad_y = 0
            if estado_actual == "JUMP": 
                estado_actual = "RUN"
                frame_actual = 0
                if vfx_jump:
                    lista_vfx.append({
                        'x': personaje_x + 72 - 48, # Centrado en el personaje (96/2=48)
                        'y': suelo_y + 96 - 91, # A ras del suelo con el nuevo alto de 91
                        'frames': vfx_jump,
                        'frame_actual': 0.0,
                        'velocidad_anim': 0.5,
                        'tipo': 'jump'
                    })

    if estado_partida == "JUGANDO":
        dist_step = 0.03 / FPS
        distancia_restante -= dist_step
        if distancia_restante <= 0:
            distancia_restante = 0
            estado_partida = "LLEGADA"
            velocidad_y = 0
            enemigo_x = -enemigo_ancho  # ocultar obstáculo al pasar a llegada
            
        # Lógica de recarga de doble salto
        if saltos_extra < 5:
            distancia_recorrida_salto += dist_step
            if distancia_recorrida_salto >= 0.5:
                saltos_extra += 1
                distancia_recorrida_salto -= 0.5 # Conservar el exceso

        # Temporizador de Recuperación de Peligro (Multifase)
        if en_peligro:
            tiempo_actual = pygame.time.get_ticks()
            tiempo_transcurrido = tiempo_actual - tiempo_inicio_peligro
            
            if tiempo_transcurrido < 2000: # Fase 1: 2 segundos Lento / Vulnerable
                velocidad_enemigo = velocidad_base_enemigo * 0.6
            else: # Vuelve a la normalidad
                en_peligro = False
                velocidad_enemigo = velocidad_base_enemigo

        # Actualizar scroll parallax (solo mientras jugamos)
        for i in range(len(parallax_offsets)):
            parallax_offsets[i] += velocidad_enemigo * PARALLAX_VELOCIDADES[i] / velocidad_base_enemigo
            if parallax_offsets[i] >= ANCHO_PANTALLA:
                parallax_offsets[i] -= ANCHO_PANTALLA
                
        # Scroll del suelo (se mueve a la misma velocidad que el enemigo)
        offset_x_suelo += velocidad_enemigo
        if offset_x_suelo >= ANCHO_PANTALLA:
            offset_x_suelo -= ANCHO_PANTALLA

        # Lógica de Decoraciones
        if tipos_decoraciones and random.random() < 0.03: # 3% probabilidad por frame
            img_deco = random.choice(tipos_decoraciones)
            lista_decoraciones.append({
                "img": img_deco,
                "x": ANCHO_PANTALLA + random.randint(0, 50),
                "y": suelo_y + 90 - img_deco.get_height()
            })
            
        for deco in lista_decoraciones:
            deco["x"] -= velocidad_enemigo # Se mueven junto con el suelo
            
        # Limpiar decoraciones que salieron de pantalla
        lista_decoraciones = [d for d in lista_decoraciones if d["x"] > -150]

        # Lógica de Estrellas
        for estrella in lista_estrellas:
            if not estrella["activa"]: continue
            estrella["x"] -= velocidad_enemigo
            data = datos_estrellas[estrella["tipo"]]
            estrella["tiempo_flote"] += data["velocidad_y"]
            estrella["y"] = estrella["base_y"] + math.sin(estrella["tiempo_flote"]) * data["amplitud"]
            estrella["frame_float"] += 0.15
            if estrella["frame_float"] >= 4:
                estrella["frame_float"] = 0.0
                
            rect_estrella = pygame.Rect(estrella["x"], estrella["y"], 32, 26)
            rect_personaje = pygame.Rect(personaje_x + 20, personaje_y + 20, 56, 76)
            if rect_personaje.colliderect(rect_estrella):
                estrella["activa"] = False
                puntuacion += data["puntos"]
                
        # Limpiar estrellas inactivas o fuera de pantalla
        lista_estrellas = [e for e in lista_estrellas if e["x"] > -50 and e["activa"]]

        # La casa solo aparece cuando falta poco (<=0.12 km)
        # Mientras no es el momento, la mantenemos fuera de pantalla
        if distancia_restante <= 0.052:
            casa_scroll_x -= velocidad_enemigo
            if casa_scroll_x < CASA_X_FINAL:
                casa_scroll_x = CASA_X_FINAL
        else:
            casa_scroll_x = float(ANCHO_PANTALLA + 800)  # mantener fuera de pantalla

        # Lógica del Enemigo
        enemigo_x -= velocidad_enemigo
        # No spawnear si la casa ya está cerca (zona de 300px antes de la casa)
        if enemigo_x < -enemigo_ancho:
            if casa_scroll_x > ANCHO_PANTALLA + 300:
                spawn_enemigo()
            else:
                enemigo_x = -enemigo_ancho  # la casa está cerca, no spawnear

        # Detección de Colisiones
        rect_personaje = pygame.Rect(personaje_x + 20, personaje_y + 20, 56, 76) 
        rect_enemigo = pygame.Rect(enemigo_x, enemigo_y, enemigo_ancho, enemigo_alto)
        
        if rect_personaje.colliderect(rect_enemigo):
            if not en_peligro and estado_partida == "JUGANDO":
                vidas -= 1
                en_peligro = True
                tiempo_inicio_peligro = pygame.time.get_ticks()
                estado_actual = "HURT"
                frame_actual = 0
                enemigo_x = -enemigo_ancho # Ocultar enemigo tras chocar
                
                if vidas <= 0:
                    estado_partida = "GAME_OVER"

    if estado_partida == "LLEGADA":
        # Jugador avanza solo hacia la casa (ya fija en CASA_X_FINAL)
        personaje_x += velocidad_base_enemigo * 0.4
        estado_actual = "RUN"
        # Desaparecer cuando el personaje cruce la mitad horizontal de mediacasa (la fachada)
        if img_mediacasa and img_casatb:
            _frente_x = int(casa_scroll_x) + img_casatb.get_width() - img_mediacasa.get_width()
            _umbral_entrada = _frente_x + img_mediacasa.get_width() // 2
            if personaje_x + 72 > _umbral_entrada:  # +72 = centro del sprite del personaje (144/2)
                estado_partida = "VICTORIA"
        else:
            _ancho_c = img_casatb.get_width() if img_casatb else 380
            if personaje_x > CASA_X_FINAL + _ancho_c - 80:
                estado_partida = "VICTORIA"

    # --- DIBUJADO ---
    if img_fondos_capas:
        # Parallax: cada capa se dibuja dos veces para lograr scroll infinito
        for i, capa in enumerate(img_fondos_capas):
            offset_x = int(parallax_offsets[i])
            pantalla_juego.blit(capa, (-offset_x, 0))                          # copia izquierda
            pantalla_juego.blit(capa, (ANCHO_PANTALLA - offset_x, 0))          # copia derecha
    elif img_fondo:
        pantalla_juego.blit(img_fondo, (0, 0))
    else:
        pantalla_juego.fill((135, 206, 235)) # Cielo por defecto

    # Dibujar Suelo (tiles del tilemap)
    suelo_top = suelo_y + 90
    if img_suelo_tileado:
        # Dibujamos dos veces desplazado para efecto infinito
        offset_s = int(offset_x_suelo)
        pantalla_juego.blit(img_suelo_tileado, (-offset_s, suelo_top))
        pantalla_juego.blit(img_suelo_tileado, (ANCHO_PANTALLA - offset_s, suelo_top))
    else:
        rect_suelo = pygame.Rect(0, suelo_top, ANCHO_PANTALLA, ALTO_PANTALLA - suelo_top)
        pygame.draw.rect(pantalla_juego, (70, 140, 70), rect_suelo)
        
    # Dibujar Decoraciones
    for deco in lista_decoraciones:
        pantalla_juego.blit(deco["img"], (deco["x"], deco["y"]))

    # Dibujar Estrellas
    for estrella in lista_estrellas:
        if estrella["activa"] and sprites_estrellas:
            indice = int(estrella["frame_float"])
            img_estrella = sprites_estrellas[estrella["tipo"]][indice]
            pantalla_juego.blit(img_estrella, (estrella["x"], estrella["y"]))

    # (Onda Expansiva naranja eliminada a pedido del usuario)

    # Elegimos qué lista de frames usar según nuestro estado actual de animación
    if estado_partida == "INICIO":
        lista_sprites = sprites_idle
        estado_actual = "IDLE"
    else:
        if estado_actual == "IDLE":
            lista_sprites = sprites_idle
        elif estado_actual == "RUN":
            lista_sprites = sprites_run
        elif estado_actual == "JUMP":
            lista_sprites = sprites_jump
        elif estado_actual == "HURT":
            lista_sprites = sprites_hurt
        elif estado_actual == "DEATH":
            lista_sprites = sprites_death

    # Lógica de Animación
    # Para JUMP: sprites_jump[0] = subiendo (frame 3 del jumpfall), sprites_jump[1] = cayendo (frame 4)
    if estado_actual == "JUMP" and estado_partida == "JUGANDO":
        
        if velocidad_y < 0:
            indice_frame = 0  # subiendo: sprite 3 del jumpfall
        else:
            indice_frame = 1  # cayendo:  sprite 4 del jumpfall
    else:
        # Avanzamos la animación
        if estado_actual == "RUN":
            frame_actual += velocidad_animacion_run
            paso_actual = int(frame_actual)
            if paso_actual in (0, 3) and paso_actual != ultimo_paso:
                ultimo_paso = paso_actual
                if vfx_run and estado_partida in ("JUGANDO", "LLEGADA"):
                    lista_vfx.append({
                        'x': personaje_x + 72 - 48 - 15, # Atrás del personaje ajustado a escala
                        'y': suelo_y + 96 - 96,
                        'frames': vfx_run,
                        'frame_actual': 0.0,
                        'velocidad_anim': 0.4,
                        'tipo': 'run'
                    })
        else:
            frame_actual += velocidad_animacion
        if frame_actual >= len(lista_sprites):
            # Comportamiento al terminar una animación
            if estado_actual == "HURT":
                if estado_partida == "GAME_OVER":
                    estado_actual = "DEATH" # Secuencia fatal: HURT -> DEATH
                    frame_actual = 0
                    lista_sprites = sprites_death
                else:
                    estado_actual = "RUN" # Fin del dolor, vuelve a correr
                    frame_actual = 0
                    lista_sprites = sprites_run
            elif estado_actual == "DEATH":
                # Loop de la animación de muerte
                frame_actual = 0
            else:
                # Animaciones normales (IDLE, RUN) hacen loop
                frame_actual = 0
        
        indice_frame = int(frame_actual)

    # Dibujar la casa (parte trasera) - visible desde JUGANDO con scroll
    if estado_partida in ("JUGANDO", "LLEGADA", "VICTORIA") and img_casatb:
        casa_draw_x = int(casa_scroll_x)
        casa_draw_y = suelo_y + 90 - img_casatb.get_height() + 20  # +20 para conectar con el suelo
        pantalla_juego.blit(img_casatb, (casa_draw_x, casa_draw_y))

    # Actualizar y dibujar VFX
    vfx_activos = []
    for vfx in lista_vfx:
        vfx['frame_actual'] += vfx['velocidad_anim']
        if vfx['frame_actual'] < len(vfx['frames']):
            if estado_partida == "JUGANDO":
                vfx['x'] -= velocidad_enemigo
            pantalla_juego.blit(vfx['frames'][int(vfx['frame_actual'])], (vfx['x'], vfx['y']))
            vfx_activos.append(vfx)
    lista_vfx = vfx_activos

    # 3. Dibujar personaje
    # En VICTORIA ya no se dibuja porque entró a la casa
    if estado_partida != "VICTORIA":
        imagen_a_dibujar = pygame.transform.scale(lista_sprites[indice_frame], (144, 96))
        
        # Efecto de parpadeo (transparencia) durante invulnerabilidad
        if en_peligro:
            tiempo_actual = pygame.time.get_ticks()
            tiempo_transcurrido = tiempo_actual - tiempo_inicio_peligro
            if tiempo_transcurrido < 2000:
                if (tiempo_transcurrido // 150) % 2 == 0:
                    imagen_a_dibujar.set_alpha(100)
                    
        pantalla_juego.blit(imagen_a_dibujar, (personaje_x, personaje_y))

    # Dibujar la media casa (frente/derecha) sobre el personaje
    if estado_partida in ("JUGANDO", "LLEGADA", "VICTORIA") and img_mediacasa and img_casatb:
        casa_draw_x = int(casa_scroll_x)
        casa_draw_y = suelo_y + 90 - img_casatb.get_height() + 20  # mismo offset
        frente_x = casa_draw_x + img_casatb.get_width() - img_mediacasa.get_width()
        pantalla_juego.blit(img_mediacasa, (frente_x, casa_draw_y))

    # 3.5 Dibujar efecto de sangre si corresponde (ahora sobre el personaje)
    if estado_actual == "HURT" and sprites_sangre:
        # Calcular el frame de la sangre proporcional al avance de la animación de HURT
        indice_sangre = min(int((frame_actual / len(lista_sprites)) * len(sprites_sangre)), len(sprites_sangre) - 1)
        imagen_sangre = pygame.transform.scale(sprites_sangre[indice_sangre], (120, 120))
        # Dibujarlo sobre el dinosaurio, centrado
        pantalla_juego.blit(imagen_sangre, (personaje_x - 12, personaje_y - 12))

    # 4. Dibujar enemigo
    if estado_partida != "INICIO":
        rect_enemigo = pygame.Rect(enemigo_x, enemigo_y, enemigo_ancho, enemigo_alto)
        if enemigo_actual.get("imagen") is not None:
            pantalla_juego.blit(enemigo_actual["imagen"], (enemigo_x, enemigo_y))
        else:
            pygame.draw.rect(pantalla_juego, enemigo_actual.get("color", (220, 40, 40)), rect_enemigo)

    # 5. Dibujar UI (Textos y Vida)
    if img_vidas:
        indice_vida = max(0, min(5, 5 - vidas))
        pantalla_juego.blit(img_vidas[indice_vida], (20, 20))
        
    # Dibujar UI Energía (Doble Salto)
    if img_energia:
        indice_energia = max(0, min(5, 5 - saltos_extra))
        # Dibujamos a la derecha de la barra de vida, asumiendo un ancho de ~150px
        ancho_vida = img_vidas[0].get_width() if img_vidas else 150
        pantalla_juego.blit(img_energia[indice_energia], (20 + ancho_vida + 10, 20))

    if estado_partida in ("JUGANDO", "LLEGADA"):
        # Panel compacto sin borde, km y pts uno al lado del otro
        fuente_hud = pygame.font.Font("assets/sprites/Fish Fellas Assetpack/Fonts/PixelifySans-Bold.ttf", 28) if fuente_grande else pygame.font.SysFont("arial", 28, bold=True)
        txt_km  = fuente_hud.render(f"{max(0, distancia_restante):.2f} km", True, (255, 255, 255))
        txt_pts = fuente_hud.render(f"{puntuacion} pts", True, (255, 215, 0))
        # Sombras
        somb_km  = fuente_hud.render(f"{max(0, distancia_restante):.2f} km", True, (0, 0, 0))
        somb_pts = fuente_hud.render(f"{puntuacion} pts", True, (50, 40, 0))
        
        pad = 8
        sep = 12
        panel_w = txt_km.get_width() + txt_pts.get_width() + sep + pad * 2
        panel_h = max(txt_km.get_height(), txt_pts.get_height()) + pad * 2
        panel_ui = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_ui.fill((0, 0, 0, 130))
        pantalla_juego.blit(panel_ui, (ANCHO_PANTALLA - panel_w - 10, 10))
        
        x_km  = ANCHO_PANTALLA - panel_w - 10 + pad
        x_pts = x_km + txt_km.get_width() + sep
        y_txt = 10 + pad
        # Sombras de 1px
        pantalla_juego.blit(somb_km,  (x_km  + 1, y_txt + 1))
        pantalla_juego.blit(somb_pts, (x_pts + 1, y_txt + 1))
        pantalla_juego.blit(txt_km,   (x_km,  y_txt))
        pantalla_juego.blit(txt_pts,  (x_pts, y_txt))

    if estado_partida == "MENU_PRINCIPAL":
        opciones = ["Comenzar Partida", "Ajustes"]
        rects = obtener_rects_menu(opciones, y_inicial=260)
        dibujar_panel_menu("", opciones, rects, y_inicial=260, incluir_banner=True)

    elif estado_partida == "AJUSTES":
        opciones = ["Volumen", "Dificultad", "Cambiar Personaje", "Volver"]
        rects = obtener_rects_menu(opciones, y_inicial=200)
        dibujar_panel_menu("AJUSTES", opciones, rects, y_inicial=200)

    elif estado_partida == "PAUSA":
        opciones = ["Continuar", "Ajustes", "Menú Principal"]
        rects = obtener_rects_menu(opciones, y_inicial=200)
        dibujar_panel_menu("PAUSADO", opciones, rects, y_inicial=200)

    elif estado_partida == "GAME_OVER":
        opciones = ["Reintentar", "Menú Principal"]
        rects = obtener_rects_menu(opciones, y_inicial=250)
        dibujar_panel_menu("GAME OVER", opciones, rects, y_inicial=250)

    elif estado_partida == "VICTORIA":
        opciones = ["Reintentar", "Menú Principal"]
        rects = obtener_rects_menu(opciones, y_inicial=250)
        dibujar_panel_menu("¡VICTORIA!", opciones, rects, y_inicial=250)

    elif estado_partida == "INICIO":
        overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
        overlay.fill((0, 40, 120, 180)) # Fondo azul semitransparente
        pantalla_juego.blit(overlay, (0, 0))

        # Título
        titulo = "SELECCIONA TU PERSONAJE"
        sombra = fuente_grande.render(titulo, True, (0, 0, 50))
        txt_t = fuente_grande.render(titulo, True, (255, 255, 255))
        rect_t = txt_t.get_rect(center=(ANCHO_PANTALLA//2, 120))
        pantalla_juego.blit(sombra, (rect_t.x + 2, rect_t.y + 2))
        pantalla_juego.blit(txt_t, rect_t)
        
        # Efecto hover
        mx, my = pygame.mouse.get_pos()
        color_azul = (255, 255, 0) if mx < ANCHO_PANTALLA // 2 else (100, 200, 255)
        color_verde = (255, 255, 0) if mx >= ANCHO_PANTALLA // 2 else (100, 255, 100)

        # Personaje Azul (Izquierda)
        txt_azul = fuente_grande.render("AZUL", True, color_azul)
        rect_azul = txt_azul.get_rect(center=(ANCHO_PANTALLA//4, ALTO_PANTALLA//2))
        pantalla_juego.blit(txt_azul, rect_azul)
        
        # Personaje Verde (Derecha)
        txt_verde = fuente_grande.render("VERDE", True, color_verde)
        rect_verde = txt_verde.get_rect(center=(3*ANCHO_PANTALLA//4, ALTO_PANTALLA//2))
        pantalla_juego.blit(txt_verde, rect_verde)

    # --- APLICAR EFECTOS (SHAKE & FOG) A LA PANTALLA REAL ---
    dx = 0
    dy = 0
    if en_peligro:
        tiempo_actual_efecto = pygame.time.get_ticks()
        # Shake solo en los primeros 400ms del golpe
        if tiempo_actual_efecto - tiempo_inicio_peligro < 400:
            dx = random.randint(-10, 10)
            dy = random.randint(-10, 10)

    pantalla.fill((0, 0, 0)) # Fondo negro para que el shake no deje estelas
    pantalla.blit(pantalla_juego, (dx, dy))

    pygame.display.flip()

pygame.quit()
sys.exit()
