from Heart.Logic.LogicCommandManager import LogicCommandManager
from Heart.Packets.PiranhaMessage import PiranhaMessage


class AvailableServerCommandMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields, player=None):
        command_id = fields.get("CommandType", fields.get("Command", {}).get("ID", 600))
        self.writeVInt(command_id)
        
        command = LogicCommandManager.createCommand(command_id, self.messagePayload)
        if command:
            # Передаем fields напрямую в encode команды
            encoded_data = command.encode(fields)
            self.messagePayload = encoded_data
        
        return self.messagePayload

    def decode(self):
        return {}

    def execute(message, calling_instance, fields):
        pass

    def getMessageType(self):
        return 24111

    def getMessageVersion(self):
        return self.messageVersion