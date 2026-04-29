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

    def safe_read_vint(self, default=0):
        """Безопасное чтение VInt с возвратом значения по умолчанию при ошибке"""
        try:
            if self.offset >= len(self.messagePayload):
                return default
            return self.readVInt()
        except Exception:
            return default
    
    def safe_read_long(self, default=(0, 0)):
        """Безопасное чтение Long с возвратом значения по умолчанию при ошибке"""
        try:
            if self.offset + 8 > len(self.messagePayload):
                return default
            return self.readLong()
        except Exception:
            return default
    
    def safe_read_boolean(self, default=False):
        """Безопасное чтение Boolean с возвратом значения по умолчанию при ошибке"""
        try:
            if self.offset >= len(self.messagePayload):
                return default
            return self.readBoolean()
        except Exception:
            return default
    
    def safe_read_string(self, default=""):
        """Безопасное чтение String с возвратом значения по умолчанию при ошибке"""
        try:
            if self.offset >= len(self.messagePayload):
                return default
            return self.readString()
        except Exception:
            return default

    def decode(self):
        fields = {}
        try:
            # Читаем данные о результате битвы с безопасными методами
            fields["GameMode"] = self.safe_read_vint(0)      # Режим игры
            fields["Result"] = self.safe_read_vint(0)        # Результат (0=поражение, 1=победа, 2=ничья)
            fields["Rank"] = self.safe_read_vint(1)          # Место в матче
            fields["BrawlerID"] = self.safe_read_vint(0)     # ID бойца
            fields["Unk1"] = self.safe_read_vint(0)          # Неизвестное поле
            fields["Unk2"] = self.safe_read_vint(0)          # Неизвестное поле
            
            # Читаем количество игроков
            player_count = self.safe_read_vint(0)
            
            fields["Players"] = []
            for i in range(player_count):
                try:
                    player_data = {
                        "AccountID": self.safe_read_long((0, 0)),
                        "Team": self.safe_read_vint(0),
                        "BrawlerID": self.safe_read_vint(0),
                        "HasSkin": self.safe_read_boolean(False),
                        "SkinID": self.safe_read_vint(0) if self.safe_read_boolean(False) else 0,
                        "Name": self.safe_read_string(""),
                        "Trophies": self.safe_read_vint(0),
                        "IsAI": self.safe_read_boolean(False)
                    }
                    fields["Players"].append(player_data)
                except Exception:
                    break
        except Exception as e:
            print(f"[AskForBattleEndMessage] Ошибка при декодировании: {e}")
            # Возвращаем значения по умолчанию при любой ошибке
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
        Обрабатывает окончание битвы и отправляет результат клиенту
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
            from DB.DatabaseHandler import DatabaseHandler
            
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
            
            # Обновляем кубки игрока
            player.Trophies = trophy_data['new_trophies']
            if player.Trophies > player.HighestTrophies:
                player.HighestTrophies = player.Trophies
            
            # Сохраняем данные игрока в базу
            db_instance = DatabaseHandler()
            player_data = player.getDataTemplate(player.ID[0], player.ID[1], player.Token)
            player_data["Trophies"] = player.Trophies
            player_data["HighestTrophies"] = player.HighestTrophies
            player_data["OwnedBrawlers"] = player.OwnedBrawlers
            db_instance.updatePlayerData(player_data, type('', (), {'player': player})())
            
            # Формируем данные игрока для отправки
            player_result = {
                'AccountID': player.ID,
                'TrophyChange': trophy_data['change'],
                'OldTrophies': trophy_data['old_trophies'],
                'NewTrophies': trophy_data['new_trophies'],
                'BrawlerID': brawler_id,
                'BrawlerTrophyChange': trophy_data['change']
            }
            
            # Отправляем BattleEndMessage (ID 24115)
            battle_end_data = {
                'Socket': client,
                'GameMode': game_mode,
                'Result': result_code,
                'Rank': rank,
                'Players': [player_result]
            }
            
            Messaging.sendMessage(24115, battle_end_data)
            print(f"[AskForBattleEndMessage] Отправлено BattleEndMessage (24115)")
            
            # Отправляем AvailableServerCommandMessage с командой обновления (ID 24111)
            command_data = {
                'Socket': client,
                'CommandType': 600,  # EndBattleCommand
                'GameMode': game_mode,
                'Result': result_code,
                'Rank': rank,
                'BrawlerID': brawler_id,
                'TrophyChange': trophy_data['change'],
                'OldTrophies': trophy_data['old_trophies'],
                'NewTrophies': trophy_data['new_trophies']
            }
            
            Messaging.sendMessage(24111, command_data)
            print(f"[AskForBattleEndMessage] Отправлено AvailableServerCommandMessage (24111)")
            
            # Отправляем LobbyInfoMessage для обновления UI лобби (ID 23457)
            Messaging.sendMessage(23457, {'Socket': client})
            print(f"[AskForBattleEndMessage] Отправлено LobbyInfoMessage (23457)")
            
            print(f"[AskForBattleEndMessage] Битва завершена успешно!")
            
        except Exception as e:
            print(f"[AskForBattleEndMessage] Ошибка при обработке: {e}")
            import traceback
            traceback.print_exc()

    def getMessageType(self):
        return 14166  # ID сообщения AskForBattleEnd

    def getMessageVersion(self):
        return self.messageVersion
