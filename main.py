# Константы для фигур
ROCK = 1  # Камень
PAPER = 2  # Бумага
SCISSORS = 3  # Ножницы

# Глобальные переменные для хранения состояния игры
opponent_history = []  # История ходов соперника
our_history = []  # История наших ходов
moves_count = 0  # Счётчик ходов
last_opponent_move = 0  # Последний ход соперника
last_our_move = None  # Наш последний ход


def set_parameters(set_count: int, wins_per_set: int) -> None:
    """
    Инициализация параметров турнира и сброс состояния.
    """
    global opponent_history, our_history, moves_count, last_opponent_move, last_our_move
    opponent_history = []
    our_history = []
    moves_count = 0
    last_opponent_move = 0
    last_our_move = None


def on_game_start() -> None:
    """
    Подготавливает бота к началу новой игры.
    """
    global opponent_history, our_history, moves_count, last_opponent_move, last_our_move
    opponent_history.clear()
    our_history.clear()
    moves_count = 0
    last_opponent_move = 0
    last_our_move = None


def on_game_end() -> None:
    """
    Завершающие действия по окончании игры.
    """
    pass


def counter_move(predicted_move: int) -> int:
    """
    Определяет контрход, побеждающий предсказанный ход соперника.
    Если предсказан:
      - ROCK, возвращает PAPER;
      - PAPER, возвращает SCISSORS;
      - SCISSORS, возвращает ROCK.
    """
    if predicted_move == ROCK:
        return PAPER
    elif predicted_move == PAPER:
        return SCISSORS
    elif predicted_move == SCISSORS:
        return ROCK
    return ROCK


def overall_prediction(history: list) -> int:
    """
    Общий анализ.
    Подсчитывает, сколько раз встречался каждый ход в истории.
    Возвращает ход с максимальной частотой.
    Если история пуста, возвращает None.
    """
    if not history:
        return None
    counts = {ROCK: 0, PAPER: 0, SCISSORS: 0}
    for move in history:
        counts[move] += 1
    predicted = max(counts, key=counts.get)
    return predicted


def deep_sequence_analysis(history: list, max_pattern_length: int = 5) -> int:
    """
    Глубокий анализ последовательностей.

    Анализирует историю ходов соперника, начиная с максимально возможной длины паттерна,
    и постепенно уменьшает длину паттерна. Для каждого паттерна определяется, какой ход
    чаще всего следует за ним. Если найден повторяющийся паттерн, функция возвращает
    предсказанный ход. Если паттерн не найден, возвращает None.
    """
    n = len(history)
    if n < 2:
        return None
    max_len = min(max_pattern_length, n - 1)
    for L in range(max_len, 0, -1):
        pattern = history[-L:]
        counts = {ROCK: 0, PAPER: 0, SCISSORS: 0}
        found = False
        for i in range(n - L):
            if history[i:i + L] == pattern:
                found = True
                if i + L < n:
                    next_move = history[i + L]
                    counts[next_move] += 1
        if found and sum(counts.values()) > 0:
            predicted = max(counts, key=counts.get)
            return predicted
    return None


def choose(previous_opponent_choice: int) -> int:
    """
    Основная функция выбора хода.

    1. Если это первый ход, выбирается ROCK.
    2. Обновляется история ходов соперника.
    3. Применяется глубокий анализ последовательностей по ходам соперника.
    4. Если глубокий анализ не дал результата, применяется общий анализ нашей истории ходов.
    5. Если и это не сработало, по умолчанию выбирается ROCK.
    6. Полученное предсказание преобразуется в контрход – ход, побеждающий предсказанный.
    7. Выбранный ход сохраняется и возвращается.
    """
    global opponent_history, our_history, moves_count, last_opponent_move, last_our_move

    if previous_opponent_choice != 0:
        opponent_history.append(previous_opponent_choice)
        last_opponent_move = previous_opponent_choice

    moves_count += 1

    # Первый ход: базовый выбор
    if moves_count == 1 or not our_history:
        my_move = ROCK
        our_history.append(my_move)
        last_our_move = my_move
        return my_move

    # 1. Пробуем глубокий анализ последовательностей по ходам соперника
    predicted = deep_sequence_analysis(opponent_history, max_pattern_length=5)
    # 2. Если не удалось, анализируем нашу историю ходов через общий анализ
    if predicted is None:
        predicted = overall_prediction(our_history)
    # 3. Если и это не дало результата, по умолчанию выбираем ROCK
    if predicted is None:
        predicted = ROCK

    # Выбираем наш ход как контрход к предсказанному
    my_move = counter_move(predicted)
    our_history.append(my_move)
    last_our_move = my_move

    return my_move


# Пример использования:
if __name__ == "__main__":
    set_parameters(49, 26)
    on_game_start()
    # Примерная симуляция ходов соперника
    opponent_moves = [ROCK, PAPER, SCISSORS, ROCK, PAPER, ROCK, SCISSORS, PAPER, ROCK, SCISSORS]
    for move in opponent_moves:
        my_choice = choose(move)
        print(f"Противник: {move}, Наш ход: {my_choice}")
    on_game_end()
