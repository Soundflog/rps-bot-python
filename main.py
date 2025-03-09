# Константы для фигур
ROCK = 1  # Камень
PAPER = 2  # Бумага
SCISSORS = 3  # Ножницы

# Флаг, указывающий, знает ли противник эту методику
OPPONENT_AWARE = False  # Измените на True, если противник осведомлён

# Глобальные переменные для хранения последнего нашего хода
last_my_move = None
# last_opponent_move можно использовать для дополнительного анализа, если потребуется
last_opponent_move = None


def set_parameters(set_count: int, wins_per_set: int) -> None:
    """
    Инициализация параметров игры.
    """
    global last_my_move, last_opponent_move
    last_my_move = None
    last_opponent_move = None


def on_game_start() -> None:
    """
    Подготовка бота к началу игры.
    """
    global last_my_move, last_opponent_move
    last_my_move = None
    last_opponent_move = None


def outcome(my_move: int, opp_move: int) -> str:
    """
    Определяет исход схватки: win, loss или draw.

    :param my_move: наш ход
    :param opp_move: ход противника
    :return: "win", "loss" или "draw"
    """
    if my_move == opp_move:
        return "draw"
    if (my_move == ROCK and opp_move == SCISSORS) or \
            (my_move == SCISSORS and opp_move == PAPER) or \
            (my_move == PAPER and opp_move == ROCK):
        return "win"
    return "loss"


def choose(previous_opponent_choice: int) -> int:
    """
    Определяет следующий ход бота на основе результата предыдущей схватки.

    На первом ходу (previous_opponent_choice == 0) бот выбирает ROCK.

    Если результат предыдущей схватки:
      - win или draw: переходим по схеме (Камень → Ножницы, Ножницы → Бумага, Бумага → Камень)
      - loss:
          - Если противник не знает методику: та же схема, что и при выигрыше
          - Если противник знает методику: обратная схема (Камень → Бумага, Ножницы → Камень, Бумага → Ножницы)

    :param previous_opponent_choice: Ход противника в предыдущей схватке (0, если первого хода еще не было)
    :return: Наш следующий ход (число от 1 до 3)
    """
    global last_my_move, last_opponent_move, OPPONENT_AWARE

    # Первый ход: нет информации о предыдущей схватке
    if previous_opponent_choice == 0 or last_my_move is None:
        last_my_move = ROCK
        last_opponent_move = 0
        return ROCK

    # Определяем исход предыдущей схватки, используя наш последний ход и ход противника
    result = outcome(last_my_move, previous_opponent_choice)

    # Схема перехода при выигрыше (или ничье, трактуем как выигрыш)
    win_mapping = {ROCK: SCISSORS, SCISSORS: PAPER, PAPER: ROCK}

    # Схема перехода при проигрыше, если противник знает методику
    aware_loss_mapping = {ROCK: PAPER, SCISSORS: ROCK, PAPER: SCISSORS}

    if result in ("win", "draw"):
        next_move = win_mapping[last_my_move]
    elif result == "loss":
        if OPPONENT_AWARE:
            next_move = aware_loss_mapping[last_my_move]
        else:
            next_move = win_mapping[last_my_move]
    else:
        # На всякий случай, если результат неопределён, выбираем ROCK
        next_move = ROCK

    last_my_move = next_move
    last_opponent_move = previous_opponent_choice
    return next_move


def on_game_end() -> None:
    """
    Действия по окончании игры.
    """
    pass
