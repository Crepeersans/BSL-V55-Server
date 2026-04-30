import traceback
import time
from threading import Timer

class Messaging:
    # Храним таймеры для каждого клиента
    battle_end_timers = {}
    
    def writeHeader(message, payloadLen):
        message.messageBuffer += message.getMessageType().to_bytes(2, 'big', signed=True)
        message.messageBuffer += payloadLen.to_bytes(3, 'big', signed=True)
        message.messageBuffer += message.messageVersion.to_bytes(2, 'big', signed=True)

    def readHeader(headerBytes):
        headerData = []
        headerData.append(int.from_bytes(headerBytes[:2], 'big', signed=True))
        headerData.append(int.from_bytes(headerBytes[2:5], 'big', signed=True))
        return headerData

    def sendMessage(messageType, fields, player=None):
        from Heart.Logic.LogicLaserMessageFactory import LogicLaserMessageFactory
        message = LogicLaserMessageFactory.createMessageByType(messageType, b'')
        if player is not None:
            message.encode(fields, player)
        else:
            message.encode(fields)
        Messaging.writeHeader(message, len(message.messagePayload))
        message.messageBuffer += message.messagePayload
        try:
            fields["Socket"].send(message.messageBuffer)
        except Exception:
            print(traceback.format_exc())

    def start_battle_end_timer(client, delay=5.0):
        """
        Запускает таймер для принудительного завершения боя.
        Если клиент не отправил AskForBattleEndMessage за delay секунд,
        сервер сам завершит бой с результатом по умолчанию.
        """
        # Отменяем предыдущий таймер если есть
        if client in Messaging.battle_end_timers:
            Messaging.battle_end_timers[client].cancel()
        
        def force_end_battle():
            print(f"[ТАЙМЕР] Принудительное завершение боя для клиента {client}")
            Messaging.force_complete_battle(client)
        
        timer = Timer(delay, force_end_battle)
        timer.daemon = True
        timer.start()
        Messaging.battle_end_timers[client] = timer
        print(f"[ТАЙМЕР] Запущен таймер завершения боя на {delay} сек")

    def cancel_battle_end_timer(client):
        """Отменяет таймер завершения боя"""
        if client in Messaging.battle_end_timers:
            Messaging.battle_end_timers[client].cancel()
            del Messaging.battle_end_timers[client]
            print("[ТАЙМЕР] Таймер отменен (бой успешно завершен)")

    def force_complete_battle(client):
        """
        Принудительно завершает бой с результатом по умолчанию.
        Используется когда клиент не отправил пакет завершения.
        """
        print("=== ПРИНУДИТЕЛЬНОЕ ЗАВЕРШЕНИЕ БОЯ ===")
        player = client.player if hasattr(client, 'player') else None
        
        if player is None:
            print("[ПРИНУДИТЕЛЬНО] Ошибка: игрок не найден")
            return
        
        # Для 3v3 режима определяем результат случайно (для теста)
        # В реальной игре тут должна быть логика проверки состояния матча
        import random
        result_code = random.choice([1, 0, 2])  # 1=Победа, 0=Поражение, 2=Ничья
        game_mode = 0  # Gem Grab (3v3)
        rank = 1
        brawler_id = list(player.OwnedBrawlers.keys())[0] if player.OwnedBrawlers else 0
        
        result_map = {1: 'win', 0: 'loss', 2: 'draw'}
        result = result_map[result_code]
        
        print(f"[ПРИНУДИТЕЛЬНО] Режим: 3v3, Результат: {result.upper()}")
        
        try:
            from Heart.Logic.TrophySystem import TrophySystem
            from DB.DatabaseHandler import DatabaseHandler
            
            # Применяем изменение кубков
            trophy_data = TrophySystem.apply_trophy_change(
                player,
                mode='3v3',
                rank=None,
                result=result,
                brawler_id=brawler_id
            )
            
            print(f"[ПРИНУДИТЕЛЬНО] Изменение кубков: {trophy_data['change']}")
            print(f"[ПРИНУДИТЕЛЬНО] Старые кубки: {trophy_data['old_trophies']}, Новые кубки: {trophy_data['new_trophies']}")
            
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
            
            # Отправляем BattleEndMessage (ID 24115)
            player_result = {
                'AccountID': player.ID,
                'TrophyChange': trophy_data['change'],
                'OldTrophies': trophy_data['old_trophies'],
                'NewTrophies': trophy_data['new_trophies'],
                'BrawlerID': brawler_id,
                'BrawlerTrophyChange': trophy_data['change']
            }
            
            Messaging.sendMessage(24115, {
                'Socket': client,
                'GameMode': game_mode,
                'Result': result_code,
                'Rank': rank,
                'Players': [player_result]
            })
            print("[ПРИНУДИТЕЛЬНО] Отправлено BattleEndMessage (24115)")
            
            # Отправляем AvailableServerCommandMessage с EndBattleCommand (ID 600)
            Messaging.sendMessage(24111, {
                'Socket': client,
                'CommandType': 600,
                'GameMode': game_mode,
                'Result': result_code,
                'Rank': rank,
                'BrawlerID': brawler_id,
                'TrophyChange': trophy_data['change'],
                'OldTrophies': trophy_data['old_trophies'],
                'NewTrophies': trophy_data['new_trophies']
            })
            print("[ПРИНУДИТЕЛЬНО] Отправлено AvailableServerCommandMessage (24111) с CommandType=600")
            
            # Отправляем LobbyInfoMessage для обновления UI
            Messaging.sendMessage(23457, {'Socket': client})
            print("[ПРИНУДИТЕЛЬНО] Отправлено LobbyInfoMessage (23457)")
            
            print("[ПРИНУДИТЕЛЬНО] Бой завершен успешно!")
            
        except Exception as e:
            print(f"[ПРИНУДИТЕЛЬНО] Ошибка: {e}")
            import traceback
            traceback.print_exc()

class MessageManager:
    def receiveMessage(self, messageType, messagePayload):
        from Heart.Logic.LogicLaserMessageFactory import LogicLaserMessageFactory
        
        # ЛОГ ДЛЯ ОТЛАДКИ: Выводим все входящие пакеты
        if messageType in [14166, 14110, 14301, 14303, 10599, 10107, 10110]:
            hex_payload = messagePayload[:50].hex() if len(messagePayload) > 50 else messagePayload.hex()
            print(f"[DEBUG] Пакет ID={messageType}, Длина={len(messagePayload)}, HEX={hex_payload}")
        
        # АВТОМАТИЧЕСКИЙ ЗАПУСК ТАЙМЕРА ПРИ ПОЛУЧЕНИИ БОЕВЫХ ДЕЙСТВИЙ
        # Если клиент шлет боевые пакеты (2492, 2493 и т.д.) - перезапускаем таймер
        if messageType in range(2400, 2600) and hasattr(self, 'client'):
            # Это боевой пакет - перезапускаем таймер завершения
            Messaging.start_battle_end_timer(self.client, delay=8.0)
            print(f"[БОЙ] Получено боевое действие ID={messageType}, таймер сброшен")
        
        # ХАК: Если клиент прислал 14110 вместо 14166 - считаем это завершением боя
        if messageType == 14110:
            print("[ХАК] Клиент прислал 14110 вместо 14166 - обрабатываем как AskForBattleEndMessage")
            messageType = 14166  # Подменяем ID на правильный
        
        message = LogicLaserMessageFactory.createMessageByType(messageType, messagePayload)
        if message is not None:
            try:
                if message.isServerToClient():
                    message.encode()
                else:
                    message.fields = message.decode()
                    
                    # ЕСЛИ ЭТО AskForBattleEndMessage (14166) - отменяем таймер
                    if messageType == 14166:
                        Messaging.cancel_battle_end_timer(self.client)
                    
                    message.execute(self, message.fields)

            except Exception:
                print(f"[ERROR] Ошибка обработки пакета {messageType}:")
                print(traceback.format_exc())
        if messageType > 10100:
            Messaging.sendMessage(23457, {"Socket": self.client}, self.player)