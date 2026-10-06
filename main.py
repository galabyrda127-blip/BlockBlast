import random
import pygame

pygame.init()

# -------------------- НАСТРОЙКИ --------------------

WIDTH, HEIGHT = 620, 820

BOARD_SIZE = 8
CELL_SIZE = 58
GAP = 5

BOARD_X = 78
BOARD_Y = 105

BG = (24, 27, 38)
BOARD_BG = (35, 39, 53)
CELL_BG = (48, 53, 70)

TEXT = (245, 247, 255)
MUTED = (160, 166, 185)

COLORS = [
    (255, 91, 99),
    (255, 184, 77),
    (82, 202, 120),
    (74, 144, 245),
    (177, 100, 255),
    (44, 211, 190),
    (255, 105, 180),
]

PIECE_SIZE = 36
PIECE_GAP = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Blast")

clock = pygame.time.Clock()

font_big = pygame.font.Font(None, 58)
font_title = pygame.font.Font(None, 46)
font_text = pygame.font.Font(None, 30)
font_small = pygame.font.Font(None, 24)


# -------------------- ФИГУРЫ --------------------

SHAPES = [
    [(0, 0)],

    [(0, 0), (1, 0)],
    [(0, 0), (0, 1)],

    [(0, 0), (1, 0), (2, 0)],
    [(0, 0), (0, 1), (0, 2)],

    [(0, 0), (1, 0), (0, 1), (1, 1)],

    [(0, 0), (1, 0), (2, 0), (3, 0)],
    [(0, 0), (0, 1), (0, 2), (0, 3)],

    [(0, 0), (0, 1), (1, 1)],
    [(0, 0), (1, 0), (1, 1)],
    [(0, 0), (1, 0), (0, 1)],
    [(0, 0), (0, 1), (1, 0)],

    [(0, 0), (1, 0), (2, 0), (1, 1)],
    [(1, 0), (0, 1), (1, 1), (2, 1)],

    [(0, 0), (0, 1), (1, 1), (2, 1)],
    [(0, 0), (0, 1), (1, 0), (1, 1)],

    [(0, 0), (0, 1), (0, 2), (1, 2)],
    [(1, 0), (1, 1), (0, 2), (1, 2)],
]


def new_piece():
    return {
        "shape": random.choice(SHAPES),
        "color": random.choice(COLORS)
    }


def new_game():
    board = [
        [None for _ in range(BOARD_SIZE)]
        for _ in range(BOARD_SIZE)
    ]

    pieces = [
        new_piece(),
        new_piece(),
        new_piece()
    ]

    return board, pieces, 0, 0


board, pieces, score, combo = new_game()

# Информация о фигуре, которую сейчас перетаскиваем.
dragging = None

running = True


# -------------------- РИСОВАНИЕ --------------------

def draw_text(text, font, color, center):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=center)
    screen.blit(surface, rect)


def board_pixel(col, row):
    x = BOARD_X + col * (CELL_SIZE + GAP)
    y = BOARD_Y + row * (CELL_SIZE + GAP)

    return x, y


def draw_block(x, y, color, size=CELL_SIZE, radius=10, alpha=255):
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.rect(
        surface,
        (*color, alpha),
        (0, 0, size, size),
        border_radius=radius
    )

    if alpha > 150:
        highlight = tuple(min(255, c + 35) for c in color)

        pygame.draw.line(
            surface,
            (*highlight, alpha),
            (8, 7),
            (size - 9, 7),
            3
        )

        pygame.draw.line(
            surface,
            (*highlight, alpha),
            (7, 10),
            (7, size - 11),
            3
        )

    screen.blit(surface, (x, y))


def shape_size(shape):
    width = max(x for x, _ in shape) + 1
    height = max(y for _, y in shape) + 1

    return width, height


def piece_pixel_size(shape, cell_size=PIECE_SIZE):
    width, height = shape_size(shape)

    total_width = width * cell_size + (width - 1) * PIECE_GAP
    total_height = height * cell_size + (height - 1) * PIECE_GAP

    return total_width, total_height


def draw_piece(
    piece,
    center_x,
    center_y,
    size=PIECE_SIZE,
    alpha=255
):
    shape = piece["shape"]
    color = piece["color"]

    width, height = shape_size(shape)

    total_width = width * size + (width - 1) * PIECE_GAP
    total_height = height * size + (height - 1) * PIECE_GAP

    start_x = center_x - total_width / 2
    start_y = center_y - total_height / 2

    for sx, sy in shape:

        x = int(start_x + sx * (size + PIECE_GAP))
        y = int(start_y + sy * (size + PIECE_GAP))

        draw_block(
            x,
            y,
            color,
            size,
            8,
            alpha
        )


def get_piece_rect(piece, center):
    """Получаем настоящую область фигуры для мыши."""

    width, height = piece_pixel_size(piece["shape"])

    rect = pygame.Rect(
        0,
        0,
        width,
        height
    )

    rect.center = center

    # Немного увеличиваем область захвата,
    # чтобы фигуру было легче брать мышью.
    rect.inflate_ip(18, 18)

    return rect


def draw_board():
    total = BOARD_SIZE * (CELL_SIZE + GAP) - GAP

    pygame.draw.rect(
        screen,
        BOARD_BG,
        pygame.Rect(
            BOARD_X - 12,
            BOARD_Y - 12,
            total + 24,
            total + 24
        ),
        border_radius=18
    )

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            x, y = board_pixel(col, row)

            pygame.draw.rect(
                screen,
                CELL_BG,
                (x, y, CELL_SIZE, CELL_SIZE),
                border_radius=9
            )

            if board[row][col] is not None:

                draw_block(
                    x,
                    y,
                    board[row][col]
                )


# -------------------- ПОЛЕ И ФИГУРЫ --------------------

def get_board_cell(mouse_pos):
    mx, my = mouse_pos

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            x, y = board_pixel(col, row)

            rect = pygame.Rect(
                x,
                y,
                CELL_SIZE,
                CELL_SIZE
            )

            if rect.collidepoint(mx, my):
                return col, row

    return None


def can_place(shape, col, row):
    for sx, sy in shape:

        x = col + sx
        y = row + sy

        if x < 0 or x >= BOARD_SIZE:
            return False

        if y < 0 or y >= BOARD_SIZE:
            return False

        if board[y][x] is not None:
            return False

    return True


def place_piece(piece, col, row):
    for sx, sy in piece["shape"]:

        x = col + sx
        y = row + sy

        board[y][x] = piece["color"]


def clear_lines():
    full_rows = []
    full_cols = []

    for row in range(BOARD_SIZE):

        if all(
            board[row][col] is not None
            for col in range(BOARD_SIZE)
        ):
            full_rows.append(row)

    for col in range(BOARD_SIZE):

        if all(
            board[row][col] is not None
            for row in range(BOARD_SIZE)
        ):
            full_cols.append(col)

    for row in full_rows:

        for col in range(BOARD_SIZE):
            board[row][col] = None

    for col in full_cols:

        for row in range(BOARD_SIZE):
            board[row][col] = None

    return len(full_rows) + len(full_cols)


def has_any_move():
    for piece in pieces:

        if piece is None:
            continue

        for row in range(BOARD_SIZE):

            for col in range(BOARD_SIZE):

                if can_place(
                    piece["shape"],
                    col,
                    row
                ):
                    return True

    return False


# -------------------- ИНТЕРФЕЙС --------------------

def piece_area(index):
    centers = [
        (120, 650),
        (310, 650),
        (500, 650)
    ]

    return centers[index]


def draw_ui(mouse_pos):
    draw_text(
        "BLOCK BLAST",
        font_title,
        TEXT,
        (WIDTH // 2, 45)
    )

    draw_text(
        f"Очки: {score}",
        font_text,
        TEXT,
        (WIDTH // 2, 77)
    )

    draw_text(
        "Перетащи фигуру на поле",
        font_small,
        MUTED,
        (WIDTH // 2, 620)
    )

    for i, piece in enumerate(pieces):

        if piece is None:
            continue

        center = piece_area(i)

        # При наведении фигура слегка подсвечивается.
        hover = (
            dragging is None
            and get_piece_rect(piece, center).collidepoint(mouse_pos)
        )

        if hover:

            width, height = piece_pixel_size(piece["shape"])

            glow = pygame.Rect(
                0,
                0,
                width + 18,
                height + 18
            )

            glow.center = center

            pygame.draw.rect(
                screen,
                (70, 77, 100),
                glow,
                border_radius=12,
                width=3
            )

        if dragging is None or dragging["index"] != i:

            draw_piece(
                piece,
                center[0],
                center[1]
            )

    button = pygame.Rect(
        215,
        755,
        190,
        46
    )

    pygame.draw.rect(
        screen,
        (55, 61, 82),
        button,
        border_radius=12
    )

    draw_text(
        "Новая игра",
        font_text,
        TEXT,
        button.center
    )


def draw_game_over():

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill(
        (10, 12, 18, 175)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    panel = pygame.Rect(
        75,
        275,
        WIDTH - 150,
        230
    )

    pygame.draw.rect(
        screen,
        (37, 42, 58),
        panel,
        border_radius=22
    )

    draw_text(
        "ИГРА ОКОНЧЕНА",
        font_big,
        TEXT,
        (WIDTH // 2, 335)
    )

    draw_text(
        f"Счёт: {score}",
        font_title,
        TEXT,
        (WIDTH // 2, 390)
    )

    draw_text(
        "Нажми «Новая игра»",
        font_text,
        MUTED,
        (WIDTH // 2, 445)
    )


def reset_game():
    global board
    global pieces
    global score
    global combo
    global dragging

    board, pieces, score, combo = new_game()
    dragging = None


# -------------------- РАСЧЁТ ПЕРЕТАСКИВАНИЯ --------------------

def get_drop_cell(mouse_pos):
    """
    Вычисляет клетку, куда попадёт фигура.
    Здесь фигура теперь нормально привязана к курсору.
    """

    if dragging is None:
        return None

    piece = dragging["piece"]

    # Точка, которая должна стать левым верхним углом фигуры.
    top_left_x = (
        mouse_pos[0] - dragging["offset_x"]
    )

    top_left_y = (
        mouse_pos[1] - dragging["offset_y"]
    )

    # Переводим координаты экрана в координаты поля.
    col = round(
        (top_left_x - BOARD_X)
        / (CELL_SIZE + GAP)
    )

    row = round(
        (top_left_y - BOARD_Y)
        / (CELL_SIZE + GAP)
    )

    return col, row


def draw_preview(mouse_pos):
    """Показывает место, куда сейчас можно поставить фигуру."""

    if dragging is None:
        return

    piece = dragging["piece"]

    drop_cell = get_drop_cell(mouse_pos)

    if drop_cell is None:
        return

    col, row = drop_cell

    width, height = shape_size(piece["shape"])

    # Если фигура слишком далеко от поля,
    # просто не показываем подсказку.
    if (
        col >= BOARD_SIZE
        or row >= BOARD_SIZE
        or col + width <= 0
        or row + height <= 0
    ):
        return

    valid = can_place(
        piece["shape"],
        col,
        row
    )

    preview_color = piece["color"]

    if not valid:
        preview_color = (190, 70, 80)

    # Показываем точное место будущей установки.
    for sx, sy in piece["shape"]:

        x = col + sx
        y = row + sy

        if (
            0 <= x < BOARD_SIZE
            and 0 <= y < BOARD_SIZE
        ):

            px, py = board_pixel(
                x,
                y
            )

            draw_block(
                px,
                py,
                preview_color,
                CELL_SIZE,
                9,
                120
            )


# -------------------- СОБЫТИЯ --------------------

while running:

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                # Кнопка новой игры.
                button = pygame.Rect(
                    215,
                    755,
                    190,
                    46
                )

                if button.collidepoint(event.pos):

                    reset_game()
                    continue

                # Ищем фигуру под курсором.
                for i, piece in enumerate(pieces):

                    if piece is None:
                        continue

                    center = piece_area(i)

                    hitbox = get_piece_rect(
                        piece,
                        center
                    )

                    if hitbox.collidepoint(event.pos):

                        width, height = piece_pixel_size(
                            piece["shape"]
                        )

                        top_left_x = (
                            center[0] - width / 2
                        )

                        top_left_y = (
                            center[1] - height / 2
                        )

                        # Сохраняем точку, за которую игрок
                        # схватил фигуру.
                        dragging = {
                            "index": i,
                            "piece": piece,
                            "offset_x": event.pos[0] - top_left_x,
                            "offset_y": event.pos[1] - top_left_y
                        }

                        break

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1 and dragging is not None:

                piece = dragging["piece"]
                drop_cell = get_drop_cell(event.pos)

                if drop_cell is not None:

                    col, row = drop_cell

                    if can_place(
                        piece["shape"],
                        col,
                        row
                    ):

                        place_piece(
                            piece,
                            col,
                            row
                        )

                        index = dragging["index"]

                        pieces[index] = None

                        score += len(
                            piece["shape"]
                        )

                        lines = clear_lines()

                        if lines:

                            combo += 1

                            score += (
                                lines * 10
                                + combo * 5
                            )

                        else:

                            combo = 0

                        # После использования всех трёх фигур
                        # появляются новые.
                        if all(
                            piece is None
                            for piece in pieces
                        ):

                            pieces = [
                                new_piece(),
                                new_piece(),
                                new_piece()
                            ]

                dragging = None

    # -------------------- РИСОВАНИЕ --------------------

    screen.fill(BG)

    draw_board()

    draw_ui(mouse_pos)

    # Подсказка установки показывается под фигурой.
    if dragging is not None:

        draw_preview(mouse_pos)

        # Сама фигура идёт за курсором.
        draw_piece(
            dragging["piece"],
            mouse_pos[0],
            mouse_pos[1] - 55,
            size=32,
            alpha=235
        )

    # Не показываем Game Over во время перетаскивания.
    if dragging is None and not has_any_move():

        draw_game_over()

    pygame.display.flip()

    clock.tick(60)


pygame.quit()