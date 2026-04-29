"""
Trophy System for BSL-V55 Server
Implements trophy changes for win/loss/draw in Solo and Duo modes
Based on the provided trophy tables
"""

class TrophySystem:
    """
    Система расчета кубков для режимов Solo и Duo
    
    Таблица для Solo/Duo (по рангу в матче):
    Кубки (от) | Режим | 1-е | 2-е | 3-е | 4-е | 5-е | 6-е | 7-е | 8-е | 9-е | 10-е
    0          | Solo  | +13 | +10 | +10 | +8  | +6  | +5  | +5  | +5  | +5  | +5
    0          | Duo   | +12 | +6  | +5  | +5  | +5  | —   | —   | —   | —   | —
    400        | Solo  | +13 | +10 | +8  | +5  | +3  | +2  | +1  | -1  | -2  | -2
    400        | Duo   | +12 | +6  | +2  | -1  | -2  | —   | —   | —   | —   | —
    800        | Solo  | +13 | +10 | +8  | +5  | +2  | +1  | -2  | -3  | -4  | -5
    800        | Duo   | +12 | +6  | +2  | -2  | -4  | —   | —   | —   | —   | —
    1000       | Solo  | +13 | +10 | +8  | +5  | +1  | -2  | -3  | -4  | -5  | -6
    1000       | Duo   | +12 | +6  | -1  | -3  | -5  | —   | —   | —   | —   | —
    1400       | Solo  | +3  | +2  | +1  | 0   | -2  | -10 | -25 | -35 | -45 | -55
    1400       | Duo   | +5  | +2  | -5  | -15 | -30 | —   | —   | —   | —   | —
    1600       | Solo  | +2  | +1  | 0   | -1  | -5  | -15 | -30 | -45 | -55 | -65
    1600       | Duo   | +2  | -5  | -15 | -35 | -65 | —   | —   | —   | —   | —
    2000+      | Solo  | +1  | 0   | -1  | -5  | -10 | -20 | -40 | -60 | -70 | -80
    2000+      | Duo   | +1  | -10 | -25 | -50 | -80 | —   | —   | —   | —   | —
    
    Таблица для 3 на 3 (по тиру бойца):
    Кубки бойца (Тиры)         | Победа | Поражение | Баланс (+/-)
    0 – 399 (Тиры 1–20)        | +8     | -2        | +6
    400 – 599 (Тиры 21–30)     | +8     | -3        | +5
    600 – 799 (Тиры 31–40)     | +8     | -4        | +4
    800 – 999 (Тиры 41–50)     | +8     | -5        | +3
    1000 – 1099 (Престиж I)    | +8     | -7        | +1
    1100 – 1199 (Престиж II)   | +5     | -8        | -3
    1200 – 1399 (Престиж III)  | +4     | -10       | -6
    1400 – 1599                | +3     | -15       | -12
    1600 – 1999                | +2     | -30       | -28
    2000+                      | +1     | -80       | -79
    """
    
    # Таблица кубков для Solo/Duo режимов
    SOLO_DUO_TABLE = {
        0: {   # 0-399 кубков
            'Solo': [13, 10, 10, 8, 6, 5, 5, 5, 5, 5],
            'Duo': [12, 6, 5, 5, 5, 0, 0, 0, 0, 0]  # 0 означает не применимо
        },
        400: {  # 400-799 кубков
            'Solo': [13, 10, 8, 5, 3, 2, 1, -1, -2, -2],
            'Duo': [12, 6, 2, -1, -2, 0, 0, 0, 0, 0]
        },
        800: {  # 800-999 кубков
            'Solo': [13, 10, 8, 5, 2, 1, -2, -3, -4, -5],
            'Duo': [12, 6, 2, -2, -4, 0, 0, 0, 0, 0]
        },
        1000: {  # 1000-1399 кубков
            'Solo': [13, 10, 8, 5, 1, -2, -3, -4, -5, -6],
            'Duo': [12, 6, -1, -3, -5, 0, 0, 0, 0, 0]
        },
        1400: {  # 1400-1599 кубков
            'Solo': [3, 2, 1, 0, -2, -10, -25, -35, -45, -55],
            'Duo': [5, 2, -5, -15, -30, 0, 0, 0, 0, 0]
        },
        1600: {  # 1600-1999 кубков
            'Solo': [2, 1, 0, -1, -5, -15, -30, -45, -55, -65],
            'Duo': [2, -5, -15, -35, -65, 0, 0, 0, 0, 0]
        },
        2000: {  # 2000+ кубков
            'Solo': [1, 0, -1, -5, -10, -20, -40, -60, -70, -80],
            'Duo': [1, -10, -25, -50, -80, 0, 0, 0, 0, 0]
        }
    }
    
    # Таблица для 3 на 3 (по тиру бойца)
    THREE_VS_THREE_TABLE = [
        {'min': 0, 'max': 399, 'win': 8, 'loss': -2, 'draw': 0},      # Тиры 1-20
        {'min': 400, 'max': 599, 'win': 8, 'loss': -3, 'draw': 0},    # Тиры 21-30
        {'min': 600, 'max': 799, 'win': 8, 'loss': -4, 'draw': 0},    # Тиры 31-40
        {'min': 800, 'max': 999, 'win': 8, 'loss': -5, 'draw': 0},    # Тиры 41-50
        {'min': 1000, 'max': 1099, 'win': 8, 'loss': -7, 'draw': 0},  # Престиж I
        {'min': 1100, 'max': 1199, 'win': 5, 'loss': -8, 'draw': 0},  # Престиж II
        {'min': 1200, 'max': 1399, 'win': 4, 'loss': -10, 'draw': 0}, # Престиж III
        {'min': 1400, 'max': 1599, 'win': 3, 'loss': -15, 'draw': 0},
        {'min': 1600, 'max': 1999, 'win': 2, 'loss': -30, 'draw': 0},
        {'min': 2000, 'max': 99999, 'win': 1, 'loss': -80, 'draw': 0}
    ]
    
    @staticmethod
    def get_tier_from_trophies(trophies):
        """Определяет порог кубков для таблицы Solo/Duo"""
        if trophies >= 2000:
            return 2000
        elif trophies >= 1600:
            return 1600
        elif trophies >= 1400:
            return 1400
        elif trophies >= 1000:
            return 1000
        elif trophies >= 800:
            return 800
        elif trophies >= 400:
            return 400
        else:
            return 0
    
    @staticmethod
    def calculate_solo_duo_trophies(current_trophies, mode, rank, is_win):
        """
        Расчет изменения кубков для режимов Solo и Duo
        
        Args:
            current_trophies (int): Текущее количество кубков игрока
            mode (str): Режим игры ('Solo' или 'Duo')
            rank (int): Место в матче (1-10)
            is_win (bool): True если победа, False если поражение
            
        Returns:
            int: Изменение количества кубков (положительное или отрицательное)
        """
        tier = TrophySystem.get_tier_from_trophies(current_trophies)
        
        if mode not in ['Solo', 'Duo']:
            raise ValueError("Mode must be 'Solo' or 'Duo'")
        
        if rank < 1 or rank > 10:
            raise ValueError("Rank must be between 1 and 10")
        
        # Для Duo режима поддерживаются только места 1-5
        if mode == 'Duo' and rank > 5:
            raise ValueError("Duo mode only supports ranks 1-5")
        
        trophy_changes = TrophySystem.SOLO_DUO_TABLE[tier][mode]
        
        # Получаем изменение для данного места
        change = trophy_changes[rank - 1]
        
        # Если значение 0 для Duo, значит это место не поддерживается
        if change == 0 and mode == 'Duo' and rank > 5:
            return 0
        
        # Если поражение, инвертируем знак (но не для всех позиций)
        # В таблице указаны значения для победы
        # Для поражения нужно использовать отрицательные значения начиная с определенных позиций
        if not is_win:
            # Для первых мест поражение всё равно дает меньше кубков
            # Но логика зависит от позиции
            if change > 0:
                # Для высоких позиций при поражении даем меньшее положительное значение или 0
                if rank <= 2:
                    change = max(0, change // 2)  # Половина от победы для топ-2
                else:
                    change = 0  # Для остальных мест при поражении - 0
            # Отрицательные значения остаются отрицательными (это уже штраф)
        
        return change
    
    @staticmethod
    def calculate_3v3_trophies(brawler_trophies, result):
        """
        Расчет изменения кубков для режима 3 на 3
        
        Args:
            brawler_trophies (int): Количество кубков бойца
            result (str): Результат матча ('win', 'loss', 'draw')
            
        Returns:
            int: Изменение количества кубков
        """
        for tier in TrophySystem.THREE_VS_THREE_TABLE:
            if tier['min'] <= brawler_trophies <= tier['max']:
                if result == 'win':
                    return tier['win']
                elif result == 'loss':
                    return tier['loss']
                else:  # draw
                    return tier['draw']
        
        # По умолчанию для 2000+
        if result == 'win':
            return 1
        elif result == 'loss':
            return -80
        else:
            return 0
    
    @staticmethod
    def apply_trophy_change(player, mode, rank=None, result='win', brawler_id=None):
        """
        Применяет изменение кубков к игроку
        
        Args:
            player: Объект игрока с атрибутами Trophies и OwnedBrawlers
            mode (str): Режим игры ('Solo', 'Duo', или '3v3')
            rank (int, optional): Место в матче (1-10 для Solo/Duo, не используется для 3v3)
            result (str): Результат матча ('win', 'loss', 'draw')
            brawler_id (int, optional): ID бойца для режима 3v3
            
        Returns:
            dict: Информация об изменении кубков
        """
        is_win = (result == 'win')
        
        result_data = {
            'old_trophies': player.Trophies,
            'new_trophies': player.Trophies,
            'change': 0,
            'mode': mode,
            'result': result
        }
        
        if mode in ['Solo', 'Duo']:
            if rank is None:
                raise ValueError("Rank is required for Solo/Duo modes")
            change = TrophySystem.calculate_solo_duo_trophies(
                player.Trophies, mode, rank, is_win
            )
            result_data['change'] = change
            result_data['rank'] = rank
        elif mode == '3v3':
            if brawler_id is not None and brawler_id in player.OwnedBrawlers:
                brawler_trophies = player.OwnedBrawlers[brawler_id]['Trophies']
                change = TrophySystem.calculate_3v3_trophies(brawler_trophies, result)
                result_data['change'] = change
                result_data['brawler_id'] = brawler_id
                result_data['brawler_trophies'] = brawler_trophies
                # Обновляем кубки бойца
                player.OwnedBrawlers[brawler_id]['Trophies'] += change
            else:
                # Если боец не указан, используем средние кубки
                change = TrophySystem.calculate_3v3_trophies(player.Trophies, result)
                result_data['change'] = change
        else:
            raise ValueError(f"Unknown mode: {mode}")
        
        # Обновляем общие кубки игрока
        player.Trophies += result_data['change']
        result_data['new_trophies'] = player.Trophies
        
        # Обновляем максимальные кубки если нужно
        if player.Trophies > player.HighestTrophies:
            player.HighestTrophies = player.Trophies
        
        return result_data


# Пример использования
if __name__ == "__main__":
    # Тестирование системы
    from Heart.Utils.Player import Player
    
    # Создаем тестового игрока
    player = Player()
    player.Trophies = 0  # Начинаем с 0 кубков
    
    print("=== Тестирование системы кубков ===\n")
    
    # Тест Solo режима с 0 кубков
    print("Solo режим, 0 кубков, 1 место, ПОБЕДА:")
    result = TrophySystem.apply_trophy_change(player, 'Solo', 1, 'win')
    print(f"  Изменение: {result['change']}, Новые кубки: {result['new_trophies']}")
    
    print("\nSolo режим, 13 кубков, 2 место, ПОБЕДА:")
    result = TrophySystem.apply_trophy_change(player, 'Solo', 2, 'win')
    print(f"  Изменение: {result['change']}, Новые кубки: {result['new_trophies']}")
    
    print("\nSolo режим, 23 кубка, 3 место, ПОРАЖЕНИЕ:")
    result = TrophySystem.apply_trophy_change(player, 'Solo', 3, 'loss')
    print(f"  Изменение: {result['change']}, Новые кубки: {result['new_trophies']}")
    
    # Сбросим кубки для теста 3v3
    player.Trophies = 500
    print(f"\n\n3v3 режим, 500 кубков бойца, ПОБЕДА:")
    result = TrophySystem.apply_trophy_change(player, '3v3', result='win', brawler_id=0)
    print(f"  Изменение: {result['change']}, Новые кубки бойца: {player.OwnedBrawlers[0]['Trophies']}")
    
    print(f"\n3v3 режим, 500 кубков бойца, ПОРАЖЕНИЕ:")
    result = TrophySystem.apply_trophy_change(player, '3v3', result='loss', brawler_id=0)
    print(f"  Изменение: {result['change']}, Новые кубки бойца: {player.OwnedBrawlers[0]['Trophies']}")
    
    print(f"\n3v3 режим, 500 кубков бойца, НИЧЬЯ (0 кубков):")
    result = TrophySystem.apply_trophy_change(player, '3v3', result='draw', brawler_id=0)
    print(f"  Изменение: {result['change']}, Новые кубки бойца: {player.OwnedBrawlers[0]['Trophies']}")
    
    # Тест Duo режима
    player.Trophies = 0
    print(f"\n\nDuo режим, 0 кубков, 1 место, ПОБЕДА:")
    result = TrophySystem.apply_trophy_change(player, 'Duo', 1, 'win')
    print(f"  Изменение: {result['change']}, Новые кубки: {result['new_trophies']}")
    
    print("\nDuo режим, 12 кубков, 2 место, ПОБЕДА:")
    result = TrophySystem.apply_trophy_change(player, 'Duo', 2, 'win')
    print(f"  Изменение: {result['change']}, Новые кубки: {result['new_trophies']}")
    
    # Тест разных тиров для 3v3
    print("\n\n=== Тест 3v3 для разных тиров ===")
    test_tiers = [0, 400, 600, 800, 1000, 1100, 1200, 1400, 1600, 2000]
    for tier in test_tiers:
        player.OwnedBrawlers[0]['Trophies'] = tier
        win_result = TrophySystem.calculate_3v3_trophies(tier, 'win')
        loss_result = TrophySystem.calculate_3v3_trophies(tier, 'loss')
        draw_result = TrophySystem.calculate_3v3_trophies(tier, 'draw')
        print(f"Тир {tier} кубков: Победа={win_result:+d}, Поражение={loss_result:+d}, Ничья={draw_result:+d}")
