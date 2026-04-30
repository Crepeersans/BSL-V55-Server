import traceback

class Messaging:
    def writeHeader(message, payloadLen):
        message.messageBuffer += message.getMessageType().to_bytes(2, 'big', signed=True)
        message.messageBuffer += payloadLen.to_bytes(3, 'big', signed=True)
        message.messageBuffer += message.messageVersion.to_bytes(2, 'big', signed=True)

    def readHeader(headerBytes):
        headerData = []
        headerData.append(int.from_bytes(headerBytes[:2], 'big', signed=True))
        headerData.append(int.from_bytes(headerBytes[2:5], 'big', signed=True))
        return headerData

    def sendMessage(messageType, fields,  player=None):
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

class MessageManager:
    def receiveMessage(self, messageType, messagePayload):
        from Heart.Logic.LogicLaserMessageFactory import LogicLaserMessageFactory
        
        # ЛОГ ДЛЯ ОТЛАДКИ: Выводим все входящие пакеты
        if messageType in [14166, 14110, 14301, 14303, 10599, 10107, 10110]:
            hex_payload = messagePayload[:50].hex() if len(messagePayload) > 50 else messagePayload.hex()
            print(f"[DEBUG] Пакет ID={messageType}, Длина={len(messagePayload)}, HEX={hex_payload}")
        
        message = LogicLaserMessageFactory.createMessageByType(messageType, messagePayload)
        if message is not None:
            try:
                if message.isServerToClient():
                    message.encode()
                else:
                    message.fields = message.decode()
                    message.execute(self, message.fields)

            except Exception:
                print(f"[ERROR] Ошибка обработки пакета {messageType}:")
                print(traceback.format_exc())
        if messageType > 10100:
            Messaging.sendMessage(23457, {"Socket": self.client}, self.player)