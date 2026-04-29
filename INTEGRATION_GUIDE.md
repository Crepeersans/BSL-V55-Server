# Интеграция системы кубков в BSL-V55 Server

## Обзор

Система реализует расчет кубков для всех режимов игры согласно официальным таблицам Brawl Stars:
- **Solo Showdown** (1-10 места)
- **Duo Showdown** (1-5 места)  
- **3 на 3** (Победа/Поражение/Ничья)

## Файлы

### 1. `/workspace/server/Heart/Logic/TrophySystem.py`
Основной модуль с логикой расчета кубков.

**Основные методы:**
- `calculate_3v3_trophies(brawler_trophies, result)` - расчет для 3v3
- `calculate_solo_duo_trophies(current_trophies, mode, rank, is_win)` - расчет для Solo/Duo
- `apply_trophy_change(player, mode, rank, result, brawler_id)` - применение изменений к игроку

### 2. `/workspace/server/Heart/Commands/Client/EndBattleCommand.py`
Команда окончания битвы (ID: 600).

Автоматически определяет режим игры и рассчитывает кубки.

### 3. `/workspace/server/Heart/Logic/LogicCommandManager.py`
Обновлен регистрацией команды EndBattleCommand.

## Таблицы кубков

### 3 на 3 (по тиру бойца)

| Кубки бойца | Победа | Поражение | Ничья |
|------------|--------|-----------|-------|
| 0-399      | +8     | -2        | 0     |
| 400-599    | +8     | -3        | 0     |
| 600-799    | +8     | -4        | 0     |
| 800-999    | +8     | -5        | 0     |
| 1000-1099  | +8     | -7        | 0     |
| 1100-1199  | +5     | -8        | 0     |
| 1200-1399  | +4     | -10       | 0     |
| 1400-1599  | +3     | -15       | 0     |
| 1600-1999  | +2     | -30       | 0     |
| 2000+      | +1     | -80       | 0     |

### Solo/Duo режимы

Подробные таблицы для каждого тира см. в `TrophySystem.py`.

## Использование

### Пример 1: Расчет для 3v3
```python
from Heart.Logic.TrophySystem import TrophySystem

# Победа с 500 кубками бойца
change = TrophySystem.calculate_3v3_trophies(500, 'win')  # +8

# Поражение с 500 кубками бойца
change = TrophySystem.calculate_3v3_trophies(500, 'loss')  # -3

# Ничья с любыми кубками
change = TrophySystem.calculate_3v3_trophies(500, 'draw')  # 0
```

### Пример 2: Применение к игроку
```python
from Heart.Logic.TrophySystem import TrophySystem
from Heart.Utils.Player import Player

player = Player()
player.Trophies = 500
player.OwnedBrawlers[0]['Trophies'] = 500

# 3v3 победа
result = TrophySystem.apply_trophy_change(
    player, 
    mode='3v3', 
    result='win',
    brawler_id=0
)

print(f"Изменение: {result['change']}")  # +8
print(f"Новые кубки: {result['new_trophies']}")  # 508
```

### Пример 3: Solo режим
```python
# Solo, 0 кубков, 1 место, победа
change = TrophySystem.calculate_solo_duo_trophies(0, 'Solo', 1, True)  # +13

# Solo, 1000 кубков, 8 место, поражение
change = TrophySystem.calculate_solo_duo_trophies(1000, 'Solo', 8, False)  # -4
```

## Интеграция в игровой процесс

### Вариант 1: Автоматически через EndBattleCommand
Клиент отправляет команду 600 с параметрами:
- GameMode - ID режима игры
- Result - результат (0=поражение, 1=победа, 2=ничья)
- Rank - место в матче (для Solo/Duo)
- BrawlerID - ID бойца (для 3v3)

Сервер автоматически рассчитает и применит кубки.

### Вариант 2: Ручной вызов в коде сервера
В месте обработки окончания матча:
```python
# После определения результата матча
trophy_data = TrophySystem.apply_trophy_change(
    player=client.player,
    mode='3v3',  # или 'Solo'/'Duo'
    result='win',  # или 'loss'/'draw'
    brawler_id=brawler_id  # для 3v3
)

# Отправить обновление клиенту
Messaging.sendMessage(24104, {
    "Socket": client,
    "TrophyChange": trophy_data['change'],
    "NewTrophies": trophy_data['new_trophies']
})
```

## Mapping режимов игры

В `EndBattleCommand.py` используется следующая карта режимов:
```python
mode_map = {
    0: '3v3',   # Gem Grab
    1: '3v3',   # Smash & Grab
    2: '3v3',   # Heist
    3: '3v3',   # Bounty
    4: '3v3',   # Brawl Ball
    5: '3v3',   # Hot Zone
    6: '3v3',   # Knockout
    7: 'Solo',  # Solo Showdown
    8: 'Duo',   # Duo Showdown
    9: '3v3',   # Wipeout
    10: '3v3',  # Power Play
}
```

При необходимости обновите mapping согласно вашему серверу.

## Тестирование

Запустите тестовый скрипт:
```bash
cd /workspace/server
python3 ../test_trophy_system.py
```

Все тесты должны пройти успешно.

## Важные заметки

1. **Ничья всегда дает 0 кубков** во всех режимах и тирах
2. Для **Duo режима** поддерживаются только места 1-5
3. Система обновляет как **общие кубки игрока**, так и **кубки бойца** (для 3v3)
4. При превышении максимальных кубков обновляется `HighestTrophies`

## Поддержка

При возникновении проблем проверьте:
1. Импорты модулей
2. Наличие игрока в `client.player`
3. Корректность передачи параметров в `apply_trophy_change()`
