"""
BattleEndMessage - Сообщение окончания битвы для BSL-V55 Server
СПОСОБ 3: Отправка результатов битвы через BattleEndMessage (ID 24115)
Отправляется сервером клиенту после окончания матча с результатами
"""
from Heart.Packets.PiranhaMessage import PiranhaMessage
from Heart.Logic.TrophySystem import TrophySystem
from Heart.Messaging import Messaging
from Heart.Packets.Server.AvailableServerCommandMessage import AvailableServerCommandMessage


class BattleEndMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields):
        """
        Кодирует данные о результате битвы
        fields должен содержать:
        - GameMode: режим игры (0=Gem Grab, 7=Solo, 8=Duo, и т.д.)
        - Result: результат (0=Поражение, 1=Победа, 2=Ничья)
        - Rank: место в матче (1-10 для Solo/Duo)
        - BrawlerID: ID бойца (для 3v3)
        - Players: список игроков с их результатами
        """
        print("=== СПОСОБ 3: BattleEndMessage (24115) ===")
        # Пишем основную информацию о матче
        self.writeVInt(fields.get('GameMode', 0))
        self.writeVInt(fields.get('Result', 0))
        self.writeVInt(fields.get('Rank', 1))
        
        # Количество игроков в матче
        players = fields.get('Players', [])
        self.writeVInt(len(players))
        
        # Данные по каждому игроку
        for player_data in players:
            self.writeLong(player_data.get('AccountID', [0, 0]))  # HighID, LowID
            self.writeVInt(player_data.get('TrophyChange', 0))     # Изменение кубков
            self.writeVInt(player_data.get('OldTrophies', 0))      # Старые кубки
            self.writeVInt(player_data.get('NewTrophies', 0))      # Новые кубки
            self.writeVInt(player_data.get('BrawlerID', 0))        # ID бойца
            self.writeVInt(player_data.get('BrawlerTrophyChange', 0))  # Изменение кубков бойца
            
        return self.messagePayload

    def decode(self):
        fields = {}
        fields['GameMode'] = self.readVInt()
        fields['Result'] = self.readVInt()
        fields['Rank'] = self.readVInt()
        
        player_count = self.readVInt()
        fields['Players'] = []
        
        for i in range(player_count):
            player_data = {
                'AccountID': self.readLong(),
                'TrophyChange': self.readVInt(),
                'OldTrophies': self.readVInt(),
                'NewTrophies': self.readVInt(),
                'BrawlerID': self.readVInt(),
                'BrawlerTrophyChange': self.readVInt()
            }
            fields['Players'].append(player_data)
        
        return fields

    @staticmethod
    def send_battle_result(client, game_mode, result, rank, players_data):
        """
        Статический метод для отправки результатов битвы
        СПОСОБ 3
        
        Args:
            client: клиентское соединение
            game_mode: режим игры (int)
            result: результат (0=поражение, 1=победа, 2=ничья)
            rank: место в матче (int, 1-10)
            players_data: список словарей с данными игроков
        """
        print("=== СПОСОБ 3: send_battle_result ===")
        player = client.player if hasattr(client, 'player') else None
        
        if player is None:
            print("[СПОСОБ 3] Ошибка: игрок не найден")
            return
        
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
        
        # Преобразуем код результата в строку
        if result == 1:
            result_str = 'win'
        elif result == 2:
            result_str = 'draw'
        else:
            result_str = 'loss'
        
        print(f"[СПОСОБ 3] Режим: {mode}, Результат: {result_str}, Ранг: {rank}")
        
        # Обрабатываем каждого игрока
        processed_players = []
        
        for p_data in players_data:
            account_id = p_data.get('AccountID', [0, 0])
            brawler_id = p_data.get('BrawlerID', 0)
            
            # Находим игрока по AccountID (в реальном сервере нужно искать в базе)
            if account_id == player.AccountID:
                # Применяем изменение кубков
                try:
                    trophy_data = TrophySystem.apply_trophy_change(
                        player,
                        mode=mode,
                        rank=rank if mode in ['Solo', 'Duo'] else None,
                        result=result_str,
                        brawler_id=brawler_id if mode == '3v3' else None
                    )
                    
                    processed_player = {
                        'AccountID': account_id,
                        'TrophyChange': trophy_data['change'],
                        'OldTrophies': trophy_data['old_trophies'],
                        'NewTrophies': trophy_data['new_trophies'],
                        'BrawlerID': brawler_id,
                        'BrawlerTrophyChange': trophy_data.get('change', 0)
                    }
                    
                    print(f"[СПОСОБ 3] Игрок {account_id}: {trophy_data['change']} кубков ({trophy_data['old_trophies']} -> {trophy_data['new_trophies']})")
                    
                    processed_players.append(processed_player)
                    
                except Exception as e:
                    print(f"[СПОСОБ 3] Ошибка при расчете кубков: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                # Для других игроков (в команде или вражеской)
                processed_player = {
                    'AccountID': account_id,
                    'TrophyChange': 0,
                    'OldTrophies': 0,
                    'NewTrophies': 0,
                    'BrawlerID': brawler_id,
                    'BrawlerTrophyChange': 0
                }
                processed_players.append(processed_player)
        
        # Создаем и отправляем сообщение
        fields = {
            'GameMode': game_mode,
            'Result': result,
            'Rank': rank,
            'Players': processed_players
        }
        
        # Отправляем BattleEndMessage клиенту
        Messaging.sendMessage(24115, {  # ID сообщения (нужно подобрать правильный)
            'Socket': client,
            'GameMode': game_mode,
            'Result': result,
            'Rank': rank,
            'Players': processed_players
        })
        print(f"[СПОСОБ 3] Отправлено BattleEndMessage (24115)")
        
        # Также отправляем команду обновления кубков через AvailableServerCommandMessage
        # Это нужно для обновления UI
        command_fields = {
            'Command': {
                'ID': 600,  # EndBattleCommand
                'GameMode': game_mode,
                'Result': result,
                'Rank': rank,
                'BrawlerID': processed_players[0]['BrawlerID'] if processed_players else 0,
                'OldTrophies': processed_players[0]['OldTrophies'] if processed_players else 0,
                'NewTrophies': processed_players[0]['NewTrophies'] if processed_players else 0,
                'TrophyChange': processed_players[0]['TrophyChange'] if processed_players else 0
            }
        }
        
        Messaging.sendMessage(24111, {  # AvailableServerCommandMessage
            'Socket': client,
            'Command': command_fields['Command']
        })
        print(f"[СПОСОБ 3] Отправлено AvailableServerCommandMessage (24111)")

    def execute(message, calling_instance, fields):
        # Это сообщение только для отправки сервером, выполнение не требуется
        pass

    def getMessageType(self):
        return 24115  # Нужный ID сообщения (подобрать по протоколу)

    def getMessageVersion(self):
        return self.messageVersion
