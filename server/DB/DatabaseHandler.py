import json
import sqlite3
import traceback
import os

# Получаем абсолютный путь к директории с базой данных относительно этого файла
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Files", "player.sqlite")

class DatabaseHandler():
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        try:
            self.cursor.execute("""CREATE TABLE main (ID int, Token text, Data json)""")
        except sqlite3.OperationalError:
            pass
        except Exception:
            print(traceback.format_exc())

    def createAccount(self, data):
        try:
            # Добавляем DeviceID и IP для отслеживания устройства
            self.cursor.execute("INSERT INTO main (ID, Token, Data) VALUES (?, ?, ?)", (data["ID"][1], data["Token"], json.dumps(data, ensure_ascii=0)))
            self.conn.commit()
        except Exception:
            print(traceback.format_exc())

    def getAll(self):
        self.playersId = []
        try:
            self.cursor.execute("SELECT * from main")
            self.db = self.cursor.fetchall()
            for i in range(len(self.db)):
                self.playersId.append(self.db[i][0])
            return self.playersId
        except Exception:
            print(traceback.format_exc())

    def getPlayer(self, plrId):
        try:
            self.cursor.execute("SELECT * from main where ID=?", (plrId[1],))
            return json.loads(self.cursor.fetchall()[0][2])
        except Exception:
            print(traceback.format_exc())

    def getPlayerEntry(self, plrId):
        try:
            self.cursor.execute("SELECT * from main where ID=?", (plrId[1],))
            return self.cursor.fetchall()[0]
        except IndexError:
            pass
        except Exception:
            print(traceback.format_exc())

    def loadAccount(self, player, plrId):
        try:
            self.cursor.execute("SELECT * from main where ID=?", (plrId[1],))
            playerData = json.loads(self.cursor.fetchall()[0][2])
            player.ID = playerData["ID"]
            player.Name = playerData["Name"]
            #player.AllianceID = playerData["AllianceID"]
            player.Registered = playerData["Registered"]
            player.Thumbnail = playerData["Thumbnail"]
            player.Namecolor = playerData["Namecolor"]
            player.Region = playerData["Region"]
            player.ContentCreator = playerData["ContentCreator"]
            player.Coins = playerData["Coins"]
            player.Gems = playerData["Gems"]
            player.Blings = playerData["Blings"]
            player.Trophies = playerData["Trophies"]
            player.HighestTrophies = playerData["HighestTrophies"]
            player.TrophyRoadTier = playerData["TrophyRoadTier"]
            player.Experience = playerData["Experience"]
            player.Level = playerData["Level"]
            player.Tokens = playerData["Tokens"]
            player.TokensDoubler = playerData["TokensDoubler"]
            player.SelectedBrawlers = playerData["SelectedBrawlers"]
            player.OwnedPins = playerData["OwnedPins"]
            player.OwnedThumbnails = playerData["OwnedThumbnails"]
            player.OwnedBrawlers = playerData["OwnedBrawlers"]
            player.OwnedSkins = playerData["OwnedSkins"]
        except Exception:
            print(traceback.format_exc())

    def updatePlayerData(self, data, calling_instance):
        try:
            self.cursor.execute("UPDATE main SET Data=? WHERE ID=?", (json.dumps(data, ensure_ascii=0), calling_instance.player.ID[1]))
            self.conn.commit()
            self.loadAccount(calling_instance.player, calling_instance.player.ID)
        except Exception:
            print(traceback.format_exc())

    def playerExist(self, loginToken, loginID, deviceID=None):
        try:
            if loginID[1] in self.getAll():
                entry = self.getPlayerEntry(loginID)
                if entry is None:
                    return False
                # Проверяем токен - если не совпадает, значит устройство другое
                if loginToken != entry[1]:
                    print(f"[DatabaseHandler] Токен не совпадает для игрока {loginID}")
                    # Если передан DeviceID, пробуем найти аккаунт по устройству
                    if deviceID:
                        return self.playerExistByDevice(deviceID)
                    return False
                return True
            # Игрок не найден по ID, пробуем найти по DeviceID
            elif deviceID:
                return self.playerExistByDevice(deviceID)
            return False
        except Exception:
            print(traceback.format_exc())
            return False
    
    def playerExistByDevice(self, deviceID):
        """Проверяет существование аккаунта по DeviceID"""
        try:
            self.cursor.execute("SELECT * from main")
            all_players = self.cursor.fetchall()
            for player_data in all_players:
                try:
                    data = json.loads(player_data[2])
                    if data.get("DeviceID") == deviceID or data.get("AndroidID") == deviceID:
                        print(f"[DatabaseHandler] Найден аккаунт по устройству: {deviceID}")
                        return True
                except:
                    continue
            return False
        except Exception:
            print(traceback.format_exc())
            return False
    
    def getAccountByDevice(self, deviceID):
        """Получает данные аккаунта по DeviceID"""
        try:
            self.cursor.execute("SELECT * from main")
            all_players = self.cursor.fetchall()
            for player_data in all_players:
                try:
                    data = json.loads(player_data[2])
                    if data.get("DeviceID") == deviceID or data.get("AndroidID") == deviceID:
                        print(f"[DatabaseHandler] Загрузка аккаунта по устройству: {deviceID}")
                        return player_data
                except:
                    continue
            return None
        except Exception:
            print(traceback.format_exc())
            return None

    def updatePlayerToken(self, plrId, newToken):
        """Обновляет токен игрока при входе с нового устройства"""
        try:
            self.cursor.execute("UPDATE main SET Token=? WHERE ID=?", (newToken, plrId[1]))
            self.conn.commit()
            print(f"[DatabaseHandler] Токен обновлен для игрока {plrId}")
        except Exception:
            print(traceback.format_exc())