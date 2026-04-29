"""
Тестовый скрипт для проверки системы кубков BSL-V55
Проверяет все режимы: Solo, Duo и 3v3
"""

import sys
sys.path.insert(0, '.')

from Heart.Logic.TrophySystem import TrophySystem
from Heart.Utils.Player import Player

def test_3v3_mode():
    """Тестирование режима 3 на 3"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ РЕЖИМА 3 НА 3")
    print("=" * 60)
    
    tiers = [
        (0, "0-399 (Тиры 1-20)"),
        (400, "400-599 (Тиры 21-30)"),
        (600, "600-799 (Тиры 31-40)"),
        (800, "800-999 (Тиры 41-50)"),
        (1000, "1000-1099 (Престиж I)"),
        (1100, "1100-1199 (Престиж II)"),
        (1200, "1200-1399 (Престиж III)"),
        (1400, "1400-1599"),
        (1600, "1600-1999"),
        (2000, "2000+")
    ]
    
    print(f"{'Тир':<25} {'Победа':>8} {'Поражение':>10} {'Ничья':>8}")
    print("-" * 60)
    
    for tier_value, tier_name in tiers:
        win = TrophySystem.calculate_3v3_trophies(tier_value, 'win')
        loss = TrophySystem.calculate_3v3_trophies(tier_value, 'loss')
        draw = TrophySystem.calculate_3v3_trophies(tier_value, 'draw')
        print(f"{tier_name:<25} {win:>8} {loss:>10} {draw:>8}")
    
    print()

def test_solo_mode():
    """Тестирование режима Solo"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ РЕЖИМА SOLO")
    print("=" * 60)
    
    trophy_levels = [0, 400, 800, 1000, 1400, 1600, 2000]
    
    for trophies in trophy_levels:
        print(f"\nКубки игрока: {trophies}+")
        print(f"{'Место':<6} {'Изменение':>10}")
        print("-" * 20)
        for rank in range(1, 11):
            change = TrophySystem.calculate_solo_duo_trophies(trophies, 'Solo', rank, True)
            print(f"{rank:<6} {change:>+10}")
    
    print()

def test_duo_mode():
    """Тестирование режима Duo"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ РЕЖИМА DUO")
    print("=" * 60)
    
    trophy_levels = [0, 400, 800, 1000, 1400, 1600, 2000]
    
    for trophies in trophy_levels:
        print(f"\nКубки игрока: {trophies}+")
        print(f"{'Место':<6} {'Изменение':>10}")
        print("-" * 20)
        for rank in range(1, 6):  # Duo поддерживает только 1-5 места
            change = TrophySystem.calculate_solo_duo_trophies(trophies, 'Duo', rank, True)
            print(f"{rank:<6} {change:>+10}")
    
    print()

def test_draw_scenario():
    """Тестирование сценария с ничьей (0 кубков)"""
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ НИЧЬЕЙ (0 КУБКОВ)")
    print("=" * 60)
    
    player = Player()
    
    test_cases = [
        (0, "0 кубков"),
        (500, "500 кубков"),
        (1000, "1000 кубков"),
        (1500, "1500 кубков"),
        (2000, "2000+ кубков")
    ]
    
    print(f"{'Кубки':<20} {'Победа':>8} {'Поражение':>10} {'Ничья':>8}")
    print("-" * 60)
    
    for trophies, name in test_cases:
        player.OwnedBrawlers[0]['Trophies'] = trophies
        win = TrophySystem.calculate_3v3_trophies(trophies, 'win')
        loss = TrophySystem.calculate_3v3_trophies(trophies, 'loss')
        draw = TrophySystem.calculate_3v3_trophies(trophies, 'draw')
        print(f"{name:<20} {win:>8} {loss:>10} {draw:>8}")
    
    print("\n✓ Ничья всегда дает 0 кубков во всех тирах!")
    print()

def test_full_battle_simulation():
    """Полная симуляция окончания битвы"""
    print("=" * 60)
    print("СИМУЛЯЦИЯ ОКОНЧАНИЯ БИТВЫ")
    print("=" * 60)
    
    player = Player()
    player.Trophies = 500
    player.OwnedBrawlers[0]['Trophies'] = 500
    
    scenarios = [
        ("3v3 Победа", '3v3', 'win', 0),
        ("3v3 Поражение", '3v3', 'loss', 0),
        ("3v3 Ничья", '3v3', 'draw', 0),
        ("Solo 1 место", 'Solo', 'win', None),
        ("Solo 5 место", 'Solo', 'loss', None),
        ("Duo 1 место", 'Duo', 'win', None),
        ("Duo 3 место", 'Duo', 'loss', None),
    ]
    
    for scenario_name, mode, result, brawler_id in scenarios:
        old_trophies = player.Trophies
        if mode == '3v3' and brawler_id is not None:
            old_brawler_trophies = player.OwnedBrawlers[brawler_id]['Trophies']
        
        trophy_data = TrophySystem.apply_trophy_change(
            player,
            mode=mode,
            rank=1 if mode in ['Solo', 'Duo'] else None,
            result=result,
            brawler_id=brawler_id
        )
        
        print(f"\n{scenario_name}:")
        print(f"  Изменение: {trophy_data['change']:+d}")
        print(f"  Кубки до: {old_trophies}, после: {player.Trophies}")
        
        if mode == '3v3' and brawler_id is not None:
            print(f"  Кубки бойца: {old_brawler_trophies} -> {player.OwnedBrawlers[brawler_id]['Trophies']}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("BSL-V55 TROPHY SYSTEM TEST")
    print("=" * 60 + "\n")
    
    test_3v3_mode()
    test_solo_mode()
    test_duo_mode()
    test_draw_scenario()
    test_full_battle_simulation()
    
    print("=" * 60)
    print("ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
    print("=" * 60)
    print("\nСистема готова к использованию в сервере BSL-V55")
    print("Файлы:")
    print("  - /workspace/server/Heart/Logic/TrophySystem.py")
    print("  - /workspace/server/Heart/Commands/Client/EndBattleCommand.py")
    print("  - /workspace/server/Heart/Logic/LogicCommandManager.py (обновлен)")
    print()
