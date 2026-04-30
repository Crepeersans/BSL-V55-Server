from Heart.Messaging import Messaging

from Heart.Packets.PiranhaMessage import PiranhaMessage


class GoHomeMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields):
        pass

    def decode(self):
        fields = {}
        self.readBoolean()
        return fields

    def execute(message, calling_instance, fields):
        """
        Обработка GoHomeMessage - запуск таймера ожидания завершения боя
        """
        print("=== GoHomeMessage: Начало боя ===")
        client = calling_instance.client
        
        # Запускаем таймер на случай если клиент не сможет завершить бой корректно
        Messaging.start_battle_end_timer(client, delay=30.0)  # 30 секунд на бой
        print("[GoHomeMessage] Таймер боя запущен (30 сек)")
        
        fields["Socket"] = calling_instance.client
        Messaging.sendMessage(24101, fields, calling_instance.player)

    def getMessageType(self):
        return 17750

    def getMessageVersion(self):
        return self.messageVersion