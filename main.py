ROCK = 1  # Камень
PAPER = 2  # Бумага
SCISSORS = 3  # Ножницы

# Глобальные переменные для хранения состояния игры
opponent_moves = []  # История ходов противника
my_last_move = None  # Наш последний ход
opponent_known_method = False  # Флаг: обнаружена детерминированная закономерность в ходах противника


def set_parameters(set_count: int, wins_per_set_param: int) -> None:
    """
    Вызывается один раз перед началом игры.
    Сбрасываем историю и внутреннее состояние.

    :param set_count: Максимальное количество сетов в игре.
    :param wins_per_set_param: Требуемое количество побед в сете.
    """
    global opponent_moves, my_last_move, opponent_known_method
    opponent_moves = []
    my_last_move = None
    opponent_known_method = False


def on_game_start() -> None:
    """
    Вызывается один раз в начале игры.
    Здесь можно инициализировать состояние.
    """
    global opponent_moves, my_last_move, opponent_known_method
    opponent_moves = []
    my_last_move = None
    opponent_known_method = False


def determine_outcome(my_move: int, opp_move: int) -> str:
    """
    Определяет исход предыдущего хода.
    Если наши и противниковы ходы равны, трактуем это как ничью (которая считается выигрышем для fallback).

    :param my_move: Наш ход.
    :param opp_move: Ход противника.
    :return: "win", "tie" или "lose".
    """
    if my_move == opp_move:
        return "tie"
    # Условия выигрыша: камень побеждает ножницы, ножницы побеждают бумагу, бумага побеждает камень.
    if (my_move == ROCK and opp_move == SCISSORS) or \
            (my_move == SCISSORS and opp_move == PAPER) or \
            (my_move == PAPER and opp_move == ROCK):
        return "win"
    return "lose"


def choose(previous_opponent_choice: int) -> int:
    """
    Выбор хода бота.

    Алгоритм:
    1. Если передан предыдущий ход противника (не 0), добавляем его в историю.
    2. Пытаемся обнаружить детерминированную закономерность в поведении противника:
         - Перебираем состояния с длиной от 3 до 1.
         - Для каждого состояния составляем таблицу переходов и, если для текущего состояния всегда наблюдается один и тот же следующий ход,
           делаем прогноз.
    3. Если предсказание найдено, выбираем ход, который побеждает предсказанный.
    4. Если детерминированного правила нет, используем запасной выбор по Китайской стратегии:
         - Если предыдущий ход закончился выигрышем или ничьёй:
             • После Камня -> Ножницы
             • После Ножниц -> Бумага
             • После Бумаги -> Камень
         - Если проигрыш, то:
             • Если противник, по нашим данным, знает методику (opponent_known_method == True):
                   - После Камня -> Бумага
                   - После Ножниц -> Камень
                   - После Бумаги -> Ножницы
             • Иначе (противник не обнаружил закономерность) – ведём себя как при выигрыше.
    5. Сохраняем наш выбор и возвращаем его.

    :param previous_opponent_choice: Ход противника в предыдущем раунде (0, если это первый ход).
    :return: Код выбранной фигуры (1 - Камень, 2 - Бумага, 3 - Ножницы).
    """
    global opponent_moves, my_last_move, opponent_known_method

    # Если не первый ход, сохраняем ход противника
    if previous_opponent_choice != 0:
        opponent_moves.append(previous_opponent_choice)

    predicted_move = None

    # Пытаемся обнаружить детерминированную закономерность в истории ходов противника
    if opponent_moves:
        for state_length in range(min(3, len(opponent_moves)), 0, -1):
            mapping = {}
            # Перебираем все состояния длиной state_length в истории
            for i in range(len(opponent_moves) - state_length):
                state = tuple(opponent_moves[i:i + state_length])
                next_move = opponent_moves[i + state_length]
                # Если состояние уже встречалось, проверяем, совпадает ли следующий ход
                if state in mapping:
                    if mapping[state] != next_move:
                        mapping[state] = None  # Несогласованность в переходе – правило не детерминировано
                else:
                    mapping[state] = next_move
            last_state = tuple(opponent_moves[-state_length:])
            if last_state in mapping and mapping[last_state] is not None:
                predicted_move = mapping[last_state]
                opponent_known_method = True  # Обнаружено детерминированное поведение
                break

    if predicted_move is not None:
        # Если прогноз сделан, выбираем ход, побеждающий предсказанный:
        # Если противник играет Камень, наш выбор – Бумага;
        # Если противник играет Бумагу, наш выбор – Ножницы;
        # Если противник играет Ножницы, наш выбор – Камень.
        if predicted_move == ROCK:
            chosen = PAPER
        elif predicted_move == PAPER:
            chosen = SCISSORS
        elif predicted_move == SCISSORS:
            chosen = ROCK
        else:
            chosen = ROCK  # запасной вариант
    else:
        # Запасной выбор по Китайской стратегии
        # Если это первый ход, выбираем по умолчанию (например, Камень)
        if my_last_move is None or previous_opponent_choice == 0:
            chosen = ROCK
        else:
            # Определяем исход предыдущего раунда
            outcome = determine_outcome(my_last_move, previous_opponent_choice)
            # Ничья трактуем как выигрыш
            if outcome == "tie":
                outcome = "win"

            if outcome == "win":
                # При выигрыше/ничье:
                # После Камня -> Ножницы, После Ножниц -> Бумага, После Бумаги -> Камень
                if my_last_move == ROCK:
                    chosen = SCISSORS
                elif my_last_move == SCISSORS:
                    chosen = PAPER
                elif my_last_move == PAPER:
                    chosen = ROCK
                else:
                    chosen = ROCK
            else:  # outcome == "lose"
                if opponent_known_method:
                    # Противник, видимо, знает методику – меняем стратегию:
                    # После Камня -> Бумага, После Ножниц -> Камень, После Бумаги -> Ножницы
                    if my_last_move == ROCK:
                        chosen = PAPER
                    elif my_last_move == SCISSORS:
                        chosen = ROCK
                    elif my_last_move == PAPER:
                        chosen = SCISSORS
                    else:
                        chosen = ROCK
                else:
                    # Если противник не проявил детерминированного поведения – действуем как при выигрыше
                    if my_last_move == ROCK:
                        chosen = SCISSORS
                    elif my_last_move == SCISSORS:
                        chosen = PAPER
                    elif my_last_move == PAPER:
                        chosen = ROCK
                    else:
                        chosen = ROCK

    my_last_move = chosen
    return chosen


def on_game_end() -> None:
    """
    Вызывается один раз в конце игры.
    Здесь можно выполнить очистку или логирование.
    """
    pass
