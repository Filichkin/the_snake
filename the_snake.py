from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Стартовая позиция:
COORDS_START_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет камня
STONE_COLOR = (139, 69, 19)

# Скорость движения змейки:
SPEED = 8

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
screen.fill(BOARD_BACKGROUND_COLOR)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """GameObject — это базовый класс, от которого наследуются другие игровые
    объекты.
    """

    def __init__(self, position=None, body_color=None):
        """Конструктор класса GameObject - инициализирует базовые атрибуты
        объекта, такие как его позиция и цвет.
        """
        self.position = position
        self.body_color = body_color

    @classmethod
    def draw_rect(cls, board, color, axis):
        """Рисует прямоугольный объект."""
        pygame.draw.rect(board, color, axis)

    @classmethod
    def draw(cls):
        """Это абстрактный метод, который предназначен для переопределения
        в дочерних классах. Этот метод должен определять, как объект будет
        отрисовываться на экране.
        """
        raise NotImplementedError(__class__.__name__ + '.do_something')


class Apple(GameObject):
    """Класс унаследованный от GameObject, описывающий яблоко
    и действия с ним.
    """

    def __init__(self,
                 occupied_positions=[COORDS_START_CENTER],
                 position=None,
                 body_color=APPLE_COLOR):
        """Конструктор класса Apple."""
        super().__init__(position, body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            new_position = (randint(0, GRID_SIZE) * GRID_SIZE,
                            randint(0, GRID_SIZE) * GRID_SIZE)
            if new_position not in occupied_positions:
                self.position = new_position
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_rect(screen,
                       self.body_color,
                       [self.position[0],
                        self.position[1],
                        GRID_SIZE,
                        GRID_SIZE])


class Stone(Apple):
    """Класс унаследованный от Apple, описывающий камень
    и действия с ним.
    """

    def __init__(self,
                 occupied_positions=[COORDS_START_CENTER],
                 position=None,
                 body_color=STONE_COLOR):
        """Конструктор класса Stone."""
        super().__init__(occupied_positions, position, body_color)
        self.randomize_position(occupied_positions)

    def reset_stone(self):
        """Затирает старый камень при съедании яблока."""
        x_last, y_last = self.position
        self.draw_rect(screen,
                       BOARD_BACKGROUND_COLOR,
                       [x_last, y_last, GRID_SIZE, GRID_SIZE])


class Snake(GameObject):
    """Класс унаследованный от GameObject, описывающий змейку
    и действия с ней.
    """

    def __init__(self, position=None, body_color=SNAKE_COLOR):
        super().__init__(position, body_color)
        self.reset()
        self.next_direction = RIGHT

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки (координаты каждой секции),
        добавляя новую голову в начало списка positions и
        удаляя последний элемент, если длина змейки не увеличилась.
        """
        x_head, y_head = self.get_head_position()
        x_point, y_point = self.direction

        new_x = (x_head + x_point * GRID_SIZE) % SCREEN_WIDTH
        new_y = (y_head + y_point * GRID_SIZE) % SCREEN_HEIGHT

        self.positions.insert(0, (new_x, new_y))

    def draw(self):
        """Oтрисовывает змейку на экране, затирая след."""
        x_point, y_point = self.get_head_position()

        for x, y in self.positions:
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        self.draw_rect(screen,
                       self.body_color,
                       [x_point,
                        y_point,
                        GRID_SIZE,
                        GRID_SIZE])

    def hide_tail(self):
        """Затирание последнего элемента"""
        x_last, y_last = self.positions[-1]
        self.positions.pop()
        self.draw_rect(screen,
                       BOARD_BACKGROUND_COLOR,
                       [x_last, y_last, GRID_SIZE, GRID_SIZE])

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние после столкновения
        с собой или с камнем.
        """
        self.length = 1
        self.positions = [COORDS_START_CENTER]
        self.direction = RIGHT


def handle_keys(game_object):
    """Управляет движениями клавиш."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Функция запуска кода."""
    pygame.init()
    snake = Snake()
    stone = Stone(snake.positions)
    apple = Apple(snake.positions)
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()
        if snake.get_head_position() == apple.position:
            stone.reset_stone()
            apple.randomize_position(snake.positions)
            stone.randomize_position(snake.positions)
            snake.length += 1
        else:
            snake.hide_tail()
            apple.draw()
            stone.draw()
        if (snake.positions.count(snake.get_head_position()) > 1
                or snake.get_head_position() == stone.position):
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        snake.update_direction()
        pygame.display.update()


if __name__ == '__main__':
    main()
