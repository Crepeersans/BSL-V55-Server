"""
AskForBattleEndMessage - Сообщение от клиента об окончании битвы
Клиент отправляет это сообщение когда матч заканчивается
"""
from Heart.Packets.PiranhaMessage import PiranhaMessage
from Heart.Messaging import Messaging
from Heart.Packets.Server.BattleEndMessage import BattleEndMessage
from DB.DatabaseHandler import DatabaseHandler

class AskForBattleEndMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields):
        pass

    def decode(self):
        fields = {}
        try:
            # Читаем данные о результате битвы
            # Добавляем проверки на конец потока данных
            if self.offset < len(self.messagePayload):
                fields["GameMode"] = self.readVInt()      # Режим игры
            else:
                fields["GameMode"] = 0
                
            if self.offset < len(self.messagePayload):
                fields["Result"] = self.readVInt()        # Результат (0=поражение, 1=победа, 2=ничья)
            else:
                fields["Result"] = 0
                
            if self.offset < len(self.messagePayload):
                fields["Rank"] = self.readVInt()          # Место в матче
            else:
                fields["Rank"] = 1
                
            if self.offset < len(self.messagePayload):
                fields["BrawlerID"] = self.readVInt()     # ID бойца
            else:
                fields["BrawlerID"] = 0
                
            if self.offset < len(self.messagePayload):
                fields["Unk1"] = self.readVInt()          # Неизвестное поле
            else:
                fields["Unk1"] = 0
                
            if self.offset < len(self.messagePayload):
                fields["Unk2"] = self.readVInt()          # Неизвестное поле
            else:
                fields["Unk2"] = 0
            
            # Читаем количество игроков
            if self.offset < len(self.messagePayload):
                player_count = self.readVInt()
            else:
                player_count = 0
                
            fields["Players"] = []
            for i in range(player_count):
                if self.offset >= len(self.messagePayload):
                    break
                player_data = {
                    "AccountID": self.readLong(),
                    "Team": self.readVInt(),
                    "BrawlerID": self.readVInt(),
                    "HasSkin": self.readBoolean(),
                    "SkinID": self.readVInt() if self.readBoolean() else 0,
                    "Name": self.readString(),
                    "Trophies": self.readVInt(),
                    "IsAI": self.readBoolean()
                }
                fields["Players"].append(player_data)
        except Exception as e:
            print(f"[AskForBattleEndMessage] Ошибка при декодировании: {e}")
            # Возвращаем значения по умолчанию при ошибке
            if not fields:
                fields = {
                    "GameMode": 0,
                    "Result": 0,
                    "Rank": 1,
                    "BrawlerID": 0,
                    "Unk1": 0,
                    "Unk2": 0,
                    "Players": []
                }
        
        return fields

    def execute(message, calling_instance, fields):
        """
        Обрабатывает окончание битвы
        """
        client = calling_instance.client
        player = client.player if hasattr(client, 'player') else None
        
        if player is None:
            print("[AskForBattleEndMessage] Ошибка: игрок не найден")
            return
        
        game_mode = fields.get('GameMode', 0)
        result_code = fields.get('Result', 0)
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
        
        print(f"[AskForBattleEndMessage] Режим: {mode}, Результат: {result}, Ранг: {rank}, Боец: {brawler_id}")
        
        try:
            from Heart.Logic.TrophySystem import TrophySystem
            
            # Применяем изменение кубков
            trophy_data = TrophySystem.apply_trophy_change(
                player, 
                mode=mode, 
                rank=rank if mode in ['Solo', 'Duo'] else None,
                result=result,
                brawler_id=brawler_id if mode == '3v3' else None
            )
            
            print(f"[AskForBattleEndMessage] Изменение кубков: {trophy_data['change']}")
            print(f"[AskForBattleEndMessage] Старые кубки: {trophy_data['old_trophies']}, Новые кубки: {trophy_data['new_trophies']}")
            
            # Сохраняем данные игрока в базу
            db_instance = DatabaseHandler()
            player_data = player.getDataTemplate(player.ID[0], player.ID[1], player.Token)
            player_data["Trophies"] = player.Trophies
            player_data["HighestTrophies"] = player.HighestTrophies
            player_data["OwnedBrawlers"] = player.OwnedBrawlers
            db_instance.updatePlayerData(player_data, type('', (), {'player': player})())
            
            # Отправляем ответ клиенту с результатами
            battle_end_fields = {
                'Socket': client,
                'GameMode': game_mode,
                'Result': result_code,
                'Rank': rank,
                'Players': [{
                    'AccountID': player.ID,
                    'TrophyChange': trophy_data['change'],
                    'OldTrophies': trophy_data['old_trophies'],
                    'NewTrophies': trophy_data['new_trophies'],
                    'BrawlerID': brawler_id,
                    'BrawlerTrophyChange': trophy_data.get('change', 0)
                }]
            }
            
            # Отправляем BattleEndMessage
            Messaging.sendMessage(24115, battle_end_fields)
            
            # Отправляем LobbyInfoMessage для обновления UI
            Messaging.sendMessage(23457, {'Socket': client})
            
            print(f"[AskForBattleEndMessage] Битва завершена успешно!")
            
        except Exception as e:
            print(f"[AskForBattleEndMessage] Ошибка при обработке: {e}")
            import traceback
            traceback.print_exc()

    def getMessageType(self):
        return 14166  # ID сообщения AskForBattleEnd

    def getMessageVersion(self):
        return self.messageVersion
