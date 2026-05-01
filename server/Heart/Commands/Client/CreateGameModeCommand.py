from Heart.Commands.Command import Command

class CreateGameModeCommand(Command):
    def __init__(self, data):
        super().__init__(data)
        self.type = 18  # ID команды создания игры с выбором режима

    def decode(self):
        self.game_mode = self.readVInt()  # Режим игры (3=BrawlBall, 5=Bounty, 8=Heist и т.д.)
        self.map_id = self.readVInt()     # ID карты
        print(f"[CreateGameMode] Запрос режима: GameMode={self.game_mode}, Map={self.map_id}")

    def execute(self, calling_instance, fields):
        client = calling_instance.client
        player = client.player if hasattr(client, 'player') else None
        
        if not player:
            print("[CreateGameMode] Ошибка: игрок не найден")
            return

        # Список поддерживаемых режимов для BSL V55
        # 0=GemGrab, 1=Showdown, 2=BrawlBall, 3=Bounty, 4=Heist, 5=HotZone, 6=Knockout
        valid_modes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 23]
        
        if self.game_mode in valid_modes:
            print(f"[CreateGameMode] Активация режима {self.game_mode}...")
            
            # Здесь должна быть логика создания комнаты под конкретный режим
            # Для теста просто подтверждаем команду и отправляем в матчмейкинг
            
            # В реальной реализации тут нужно:
            # 1. Создать объект матча с выбранным режимом
            # 2. Добавить игрока в очередь матчмейкинга
            # 3. Отправить клиенту подтверждение начала поиска
            
            print(f"[CreateGameMode] Режим {self.game_mode} успешно активирован (требуется полная реализация матчмейкинга)")
        else:
            print(f"[CreateGameMode] Ошибка: Режим {self.game_mode} пока не поддерживается")
