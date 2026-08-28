# ==========================================================
# Proyecto: Esquivando Obstaculos en la Ciudad
# Materia: Programacion en Python
# Colegio: Institucion Educativa Sagrado Corazon de Jesus
# Codigo base v1.0
#
# Descripcion: juego base 2D donde un personaje debe esquivar
# autos en un escenario urbano. Este es el punto de partida
# del proyecto: a partir de aca cada grupo agrega las consignas
# (imagenes propias, salto, animacion de fondo, barra de
# energia, contador de kilometros, mensajes de fin de juego, etc.)
# ==========================================================

# ---------- Librerias ----------
import pygame
import sys

# ---------- Constantes ----------
ANCHO_PANTALLA = 1920
ALTO_PANTALLA = 1080
FPS = 60

COLOR_CIELO = (135, 206, 235)
COLOR_CALLE = (70, 70, 70)
COLOR_VEREDA = (150, 150, 150)
COLOR_EDIFICIO_1 = (120, 140, 170)
COLOR_EDIFICIO_2 = (90, 110, 140)
COLOR_PERSONAJE = (30, 90, 220)
COLOR_AUTO = (220, 40, 40)
COLOR_TEXTO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_ALERTA = (255, 60, 60)

VELOCIDAD_AUTO = 6

# ---------- Variables globales ----------
personaje_x = 60
personaje_y = ALTO_PANTALLA - 110
personaje_ancho = 40
personaje_alto = 60

auto_x = ANCHO_PANTALLA
auto_y = ALTO_PANTALLA - 95
auto_ancho = 70
auto_alto = 35

mostrar_reglas = True


# ---------- Funciones ----------

def dibujar_ciudad(pantalla):
    """Dibuja un fondo de ciudad simple: cielo, edificios, vereda y calle.
    Consigna 1 del proyecto: pueden reemplazar esto por una imagen de fondo
    real usando pygame.image.load() en vez de figuras dibujadas."""
    pantalla.fill(COLOR_CIELO)
    pygame.draw.rect(pantalla, COLOR_EDIFICIO_2, (40, 120, 90, 200))
    pygame.draw.rect(pantalla, COLOR_EDIFICIO_1, (160, 80, 110, 240))
    pygame.draw.rect(pantalla, COLOR_EDIFICIO_2, (300, 140, 80, 180))
    pygame.draw.rect(pantalla, COLOR_EDIFICIO_1, (420, 60, 120, 260))
    pygame.draw.rect(pantalla, COLOR_EDIFICIO_2, (580, 110, 90, 210))
    pygame.draw.rect(pantalla, COLOR_EDIFICIO_1, (700, 90, 90, 230))
    pygame.draw.rect(pantalla, COLOR_VEREDA, (0, ALTO_PANTALLA - 60, ANCHO_PANTALLA, 20))
    pygame.draw.rect(pantalla, COLOR_CALLE, (0, ALTO_PANTALLA - 40, ANCHO_PANTALLA, 40))
    for x in range(0, ANCHO_PANTALLA, 60):
        pygame.draw.rect(pantalla, COLOR_TEXTO, (x, ALTO_PANTALLA - 22, 30, 4))


def dibujar_reglas(pantalla, fuente):
    """Muestra el cartel de reglas al inicio del juego."""
    texto1 = fuente.render("Esquivando Obstaculos en la Ciudad", True, COLOR_TEXTO)
    texto2 = fuente.render("Presiona una tecla para comenzar", True, COLOR_TEXTO)
    caja = pygame.Rect(0, 0, ANCHO_PANTALLA, 70)
    pygame.draw.rect(pantalla, COLOR_NEGRO, caja)
    pantalla.blit(texto1, (20, 15))
    pantalla.blit(texto2, (20, 40))


def dibujar_personaje(pantalla):
    """Dibuja el avatar del personaje (por ahora, un cuadrado).
    Consigna 1 del proyecto: reemplazar por una imagen propia con
    pygame.image.load() y pantalla.blit()."""
    rect_personaje = pygame.Rect(personaje_x, personaje_y, personaje_ancho, personaje_alto)
    pygame.draw.rect(pantalla, COLOR_PERSONAJE, rect_personaje)
    return rect_personaje


def dibujar_auto(pantalla):
    """Dibuja el auto que se desplaza hacia el personaje (por ahora, un
    rectangulo rojo). Consigna 1 del proyecto: reemplazar por una imagen
    de auto real."""
    rect_auto = pygame.Rect(auto_x, auto_y, auto_ancho, auto_alto)
    pygame.draw.rect(pantalla, COLOR_AUTO, rect_auto)
    return rect_auto


def mover_auto():
    """Mueve el auto hacia la izquierda. Si sale de la pantalla por el lado
    izquierdo, vuelve a aparecer del lado derecho (consigna 4 del proyecto)."""
    global auto_x
    auto_x -= VELOCIDAD_AUTO
    if auto_x < -auto_ancho:
        auto_x = ANCHO_PANTALLA


# ---------- Bloque de inicializacion ----------
pygame.init()
pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Esquivando Obstaculos en la Ciudad")
reloj = pygame.time.Clock()
fuente = pygame.font.SysFont("arial", 20)
fuente_grande = pygame.font.SysFont("arial", 32, bold=True)

# ---------- Bloque principal ----------
juego_activo = True
while juego_activo:
    reloj.tick(FPS)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            juego_activo = False
        if evento.type == pygame.KEYDOWN and mostrar_reglas:
            mostrar_reglas = False
        # Consigna 3 del proyecto: acá se va a leer la tecla espacio
        # (pygame.K_SPACE) para hacer saltar al personaje.

    dibujar_ciudad(pantalla)

    if mostrar_reglas:
        dibujar_reglas(pantalla, fuente)
    else:
        mover_auto()
        rect_personaje = dibujar_personaje(pantalla)
        rect_auto = dibujar_auto(pantalla)

        # Deteccion simple de colision. Consigna 7 del proyecto:
        # reemplazar este aviso por el texto "JUEGO TERMINADO" pausando
        # el juego.
        if rect_personaje.colliderect(rect_auto):
            texto_choque = fuente_grande.render("CHOQUE!", True, COLOR_ALERTA)
            pantalla.blit(texto_choque, (ANCHO_PANTALLA // 2 - 60, 90))

        # Consigna 5 del proyecto: acá va la barra de energia (60 segundos).
        # Consigna 6 del proyecto: acá va el contador de kilometros restantes.

    pygame.display.flip()

pygame.quit()
sys.exit()
