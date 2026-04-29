from Heart.Commands.LogicCommand import LogicCommand
from Heart.Logic.TrophySystem import TrophySystem
# from Heart.Messaging import Messaging
# from Heart.Packets.Server.AvailableServerCommandMessage import AvailableServerCommandMessage

class EndBattleCommand(LogicCommand):
    """
    Команда окончания битвы
    Обрабатывает результаты матча и начисляет/снимает кубки
    """
    def __init__(self, commandData):
        super().__init__(commandData)

    def encode(self, fields):
        LogicCommand.encode(self, fields)
        # Пишем данные о результате битвы
        self.writeVInt(fields.get('GameMode', 0))  # Режим игры
        self.writeVInt(fields.get('Result', 0))    # 0=Поражение, 1=Победа, 2=Ничья
        self.writeVInt(fields.get('Rank', 1))      # Место в матче (1-10)
        self.writeVInt(fields.get('BrawlerID', 0)) # ID бойца (для 3v3)
        self.writeVInt(fields.get('OldTrophies', 0))
        self.writeVInt(fields.get('NewTrophies', 0))
        self.writeVInt(fields.get('TrophyChange', 0))
        return self.messagePayload

    def decode(self, calling_instance):
        fields = {}
        LogicCommand.decode(calling_instance, fields, False)
        
        fields["GameMode"] = calling_instance.readVInt()   # Режим игры
        fields["Result"] = calling_instance.readVInt()     # Результат
        fields["Rank"] = calling_instance.readVInt()       # Ранг в матче
        fields["BrawlerID"] = calling_instance.readVInt()  # ID бойца
        fields["OldTrophies"] = calling_instance.readVInt()
        fields["NewTrophies"] = calling_instance.readVInt()
        fields["TrophyChange"] = calling_instance.readVInt()
        
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields):
        """
        Выполняет команду окончания битвы
        Рассчитывает и применяет изменение кубков
        """
        client = calling_instance.client
        
        # Получаем игрока
        player = client.player if hasattr(client, 'player') else None
        
        if player is None:
            print("[EndBattleCommand] Ошибка: игрок не найден")
            return
        
        # Определяем режим игры
        game_mode = fields.get('GameMode', 0)
        result_code = fields.get('Result', 0)  # 0=Поражение, 1=Победа, 2=Ничья
        rank = fields.get('Rank', 1)
        brawler_id = fields.get('BrawlerID', 0)
        
        # Преобразуем код результата в строку
        if result_code == 1:
            result = 'win'
        elif result_code == 2:
            result = 'draw'
        else:
            result = 'loss'
        
        # Определяем режим для TrophySystem
        # GameMode mapping (примерный, нужно уточнить по серверу)
        # 0 = Gem Grab (3v3), 1 = Showdown (Solo), 2 = Duo Showdown (Duo), и т.д.
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
        
        mode = mode_map.get(game_mode, '3v3')
        
        print(f"[EndBattleCommand] Режим: {mode}, Результат: {result}, Ранг: {rank}, Боец: {brawler_id}")
        
        try:
            # Применяем изменение кубков
            trophy_data = TrophySystem.apply_trophy_change(
                player, 
                mode=mode, 
                rank=rank if mode in ['Solo', 'Duo'] else None,
                result=result,
                brawler_id=brawler_id if mode == '3v3' else None
            )
            
            print(f"[EndBattleCommand] Изменение кубков: {trophy_data['change']}")
            print(f"[EndBattleCommand] Старые кубки: {trophy_data['old_trophies']}, Новые кубки: {trophy_data['new_trophies']}")
            
            # Сохраняем результат для отправки клиенту
            fields['TrophyChange'] = trophy_data['change']
            fields['OldTrophies'] = trophy_data['old_trophies']
            fields['NewTrophies'] = trophy_data['new_trophies']
            
            # Отправляем команду обновления кубков клиенту
            # Это можно сделать через AvailableServerCommandMessage
            
        except Exception as e:
            print(f"[EndBattleCommand] Ошибка при расчете кубков: {e}")
            import traceback
            traceback.print_exc()

    def getCommandType(self):
        return 600  # Новый тип команды для окончания битвы
