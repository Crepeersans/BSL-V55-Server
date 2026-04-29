from Heart.Messaging import Messaging
from DB.DatabaseHandler import DatabaseHandler
from Heart.Packets.PiranhaMessage import PiranhaMessage
import json
from Heart.Utils.ClientsManager import ClientsManager

class LoginMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields):
        pass

    def decode(self):
        fields = {}
        fields["AccountID"] = self.readLong()
        fields["PassToken"] = self.readString()
        fields["ClientMajor"] = self.readInt()
        fields["ClientMinor"] = self.readInt()
        fields["ClientBuild"] = self.readInt()
        fields["ResourceSha"] = self.readString()
        fields["Device"] = self.readString()
        fields["PreferredLanguage"] = self.readDataReference()
        fields["PreferredDeviceLanguage"] = self.readString()
        fields["OSVersion"] = self.readString()
        fields["isAndroid"] = self.readBoolean()
        fields["IMEI"] = self.readString()
        fields["AndroidID"] = self.readString()
        fields["isAdvertisingEnabled"] = self.readBoolean()
        fields["AppleIFV"] = self.readString()
        fields["RndKey"] = self.readInt()
        fields["AppStore"] = self.readVInt()
        fields["ClientVersion"] = self.readString()
        fields["TencentOpenId"] = self.readString()
        fields["TencentToken"] = self.readString()
        fields["TencentPlatform"] = self.readVInt()
        fields["DeviceVerifierResponse"] = self.readString()
        fields["AppLicensingSignature"] = self.readString()
        fields["DeviceVerifierResponse"] = self.readString()
        super().decode(fields)
        return fields

    def execute(message, calling_instance, fields):
        if fields["ClientMajor"]==55:
            calling_instance.player.ClientVersion = f'{str(fields["ClientMajor"])}.{str(fields["ClientBuild"])}.{str(fields["ClientMinor"])}'
            fields["Socket"] = calling_instance.client
            db_instance = DatabaseHandler()
            
            # Сохраняем DeviceID и AndroidID в данных игрока
            calling_instance.player.DeviceID = fields.get("IMEI", "") or fields.get("AndroidID", "")
            calling_instance.player.AndroidID = fields.get("AndroidID", "")
            device_id = calling_instance.player.DeviceID
            
            # Проверяем существование игрока с учетом DeviceID
            if db_instance.playerExist(fields["PassToken"], fields["AccountID"], device_id):
                # Игрок существует - загружаем данные
                player_entry = db_instance.getPlayerEntry(fields["AccountID"])
                
                # Если не нашли по AccountID, пробуем найти по DeviceID
                if player_entry is None and device_id:
                    player_entry = db_instance.getAccountByDevice(device_id)
                
                if player_entry:
                    player_data = json.loads(player_entry[2])
                    # Обновляем AccountID на существующий
                    fields["AccountID"] = [player_data["ID"][0], player_data["ID"][1]]
                    calling_instance.player.ID = fields["AccountID"]
                    db_instance.loadAccount(calling_instance.player, fields["AccountID"])
                    
                    # Обновляем токен
                    db_instance.updatePlayerToken(fields["AccountID"], fields["PassToken"])
                    print(f"[LoginMessage] Игрок {fields['AccountID']} успешно загружен (устройство: {device_id})")
                else:
                    # Создаем новый аккаунт
                    account_data = calling_instance.player.getDataTemplate(fields["AccountID"][0], fields["AccountID"][1], fields["PassToken"])
                    account_data["DeviceID"] = device_id
                    account_data["AndroidID"] = calling_instance.player.AndroidID
                    account_data["LastIP"] = calling_instance.client.address[0] if hasattr(calling_instance.client, 'address') else ""
                    
                    db_instance.createAccount(account_data)
                    print(f"[LoginMessage] Создан новый аккаунт для устройства {device_id}")
            else:
                # Создаем новый аккаунт
                account_data = calling_instance.player.getDataTemplate(fields["AccountID"][0], fields["AccountID"][1], fields["PassToken"])
                account_data["DeviceID"] = device_id
                account_data["AndroidID"] = calling_instance.player.AndroidID
                account_data["LastIP"] = calling_instance.client.address[0] if hasattr(calling_instance.client, 'address') else ""
                
                db_instance.createAccount(account_data)
                print(f"[LoginMessage] Создан новый аккаунт для устройства {device_id}")
                
            ClientsManager.AddPlayer(calling_instance.player.ID, calling_instance.client)
            Messaging.sendMessage(20104, fields, calling_instance.player)
            Messaging.sendMessage(24101, fields, calling_instance.player)

    def getMessageType(self):
        return 10101

    def getMessageVersion(self):
        return self.messageVersion