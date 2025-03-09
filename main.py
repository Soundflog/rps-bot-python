# Константы для фигур
ROCK = 1  # Камень
PAPER = 2  # Бумага
SCISSORS = 3  # Ножницы

# Глобальные переменные для хранения параметров турнира и состояния игры
max_sets = 0
wins_per_set = 0
opponent_history = []  # История ходов противника
transition = {}  # Марковская цепь: для каждого хода противника хранится статистика последующих ходов
last_opponent_move = 0  # Последний ход противника
move_count = 0  # Счётчик ходов в игре
our_history = []  # История собственных ходов


def set_parameters(set_count: int, wins_per_set_param: int) -> None:
    """
    Вызывается один раз перед началом игры.
    Инициализирует параметры турнира и внутреннее состояние бота.

    :param set_count: Максимальное количество сетов в игре.
    :param wins_per_set_param: Требуемое количество побед в сете.
    """
    global max_sets, wins_per_set, opponent_history, transition, last_opponent_move, move_count, our_history
    max_sets = set_count
    wins_per_set = wins_per_set_param
    opponent_history = []
    transition = {
        ROCK: {ROCK: 0, PAPER: 0, SCISSORS: 0},
        PAPER: {ROCK: 0, PAPER: 0, SCISSORS: 0},
        SCISSORS: {ROCK: 0, PAPER: 0, SCISSORS: 0}
    }
    last_opponent_move = 0
    move_count = 0
    our_history = []


def on_game_start() -> None:
    """
    Вызывается один раз в начале игры.
    Сбрасывает историю ходов и внутренние счётчики.
    """
    global opponent_history, last_opponent_move, move_count, our_history
    opponent_history = []
    last_opponent_move = 0
    move_count = 0
    our_history = []


def counter_move(move: int) -> int:
    """
    Возвращает фигуру, побеждающую данную.

    :param move: Предполагаемый ход противника.
    :return: Ход, который побеждает move.
    """
    if move == ROCK:
        return PAPER  # Бумага побеждает Камень
    elif move == PAPER:
        return SCISSORS  # Ножницы побеждают Бумагу
    elif move == SCISSORS:
        return ROCK  # Камень побеждает Ножницы
    return ROCK  # На всякий случай возвращаем Камень


def overall_prediction(history: list) -> int:
    """
    Определяет наиболее часто встречающийся ход противника за всю игру.
    Если истории нет, возвращает ROCK.

    :param history: Список ходов противника.
    :return: Предполагаемый следующий ход противника.
    """
    freq = {ROCK: 0, PAPER: 0, SCISSORS: 0}
    for move in history:
        freq[move] += 1
    if not history:
        return ROCK
    # Если несколько вариантов равны, выбираем ROCK (так как случайный выбор заменяем на Камень)
    predicted = ROCK
    max_count = freq[ROCK]
    if freq[PAPER] > max_count:
        predicted = PAPER
        max_count = freq[PAPER]
    if freq[SCISSORS] > max_count:
        predicted = SCISSORS
    return predicted


def markov_prediction(last_move: int) -> int:
    """
    Предсказывает следующий ход противника, используя статистику переходов (Марковская цепь).

    :param last_move: Последний ход противника.
    :return: Предполагаемый следующий ход противника.
    """
    if last_move == 0:
        return overall_prediction(opponent_history)
    counts = transition.get(last_move, {ROCK: 0, PAPER: 0, SCISSORS: 0})
    total = counts[ROCK] + counts[PAPER] + counts[SCISSORS]
    if total == 0:
        return overall_prediction(opponent_history)
    predicted = ROCK
    max_count = counts[ROCK]
    if counts[PAPER] > max_count:
        predicted = PAPER
        max_count = counts[PAPER]
    if counts[SCISSORS] > max_count:
        predicted = SCISSORS
    return predicted


def pattern_detection(history: list) -> int:
    """
    Ищет наибольший совпадающий суффикс в истории ходов противника.
    Алгоритм проходит по возможным длинам паттерна от наибольшей до 1 и ищет,
    встречался ли данный суффикс ранее. Если найден хотя бы один случай,
    анализируется, какой ход чаще всего следовал за данным паттерном, и возвращается этот ход.

    :param history: Список ходов противника.
    :return: Предполагаемый следующий ход противника.
    """
    n = len(history)
    # Если истории слишком мало, возвращаем общую статистику
    if n < 2:
        return overall_prediction(history)
    # Ищем самый длинный суффикс, встречавшийся ранее
    for pattern_length in range(n - 1, 0, -1):
        pattern = history[-pattern_length:]
        next_move_counts = {ROCK: 0, PAPER: 0, SCISSORS: 0}
        found = False
        # Ищем паттерн в истории, кроме последнего вхождения
        for i in range(n - pattern_length):
            if history[i:i + pattern_length] == pattern:
                found = True
                if i + pattern_length < n:
                    next_move = history[i + pattern_length]
                    next_move_counts[next_move] += 1
        if found and (next_move_counts[ROCK] + next_move_counts[PAPER] + next_move_counts[SCISSORS] > 0):
            predicted = ROCK
            max_count = next_move_counts[ROCK]
            if next_move_counts[PAPER] > max_count:
                predicted = PAPER
                max_count = next_move_counts[PAPER]
            if next_move_counts[SCISSORS] > max_count:
                predicted = SCISSORS
            return predicted
    return overall_prediction(history)


def choose(previous_opponent_choice: int) -> int:
    """
    Функция выбора хода ботом с запутанной стратегией.

    Алгоритм работы:
      1. Обновление статистики: если ход противника известен,
         обновляются история и статистика переходов.
      2. Счётчик ходов (move_count) используется для переключения между тремя стратегиями:
         - Если move_count % 3 == 0: используется чистый Марковский анализ.
         - Если move_count % 3 == 1: применяется поиск паттернов в истории ходов.
         - Если move_count % 3 == 2: используется комбинированный подход:
             сравниваются результаты Марковского анализа и поиска паттернов;
             если они совпадают, берётся этот результат, иначе применяется общая статистика.
      3. После получения предсказанного хода противника выбирается фигура, которая его побеждает.
      4. Если информации недостаточно для анализа, бот возвращает ROCK.

    :param previous_opponent_choice: Ход противника в предыдущем раунде (0, если это первый ход).
    :return: Код фигуры, которую выбирает бот (1 - Камень, 2 - Бумага, 3 - Ножницы).
    """
    global opponent_history, transition, last_opponent_move, move_count, our_history

    # Обновляем статистику, если ход противника известен
    if previous_opponent_choice != 0:
        if last_opponent_move != 0:
            transition[last_opponent_move][previous_opponent_choice] += 1
        opponent_history.append(previous_opponent_choice)
        last_opponent_move = previous_opponent_choice

    move_count += 1

    # Выбор стратегии в зависимости от счётчика ходов
    if move_count % 3 == 0:
        predicted = markov_prediction(last_opponent_move)
    elif move_count % 3 == 1:
        predicted = pattern_detection(opponent_history)
    else:  # move_count % 3 == 2
        pred_markov = markov_prediction(last_opponent_move)
        pred_pattern = pattern_detection(opponent_history)
        if pred_markov == pred_pattern:
            predicted = pred_markov
        else:
            predicted = overall_prediction(opponent_history)

    # Выбираем ход, побеждающий предсказанный ход противника
    my_choice = counter_move(predicted)
    our_history.append(my_choice)
    return my_choice


def on_game_end() -> None:
    """
    Вызывается один раз в конце игры.
    Здесь можно добавить финальную обработку или логирование статистики.
    """
    pass
