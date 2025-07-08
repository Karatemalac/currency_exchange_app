from configparser import ConfigParser
from os import path

config = ConfigParser()
configFilePath = path.join(path.dirname(__file__), "configs", "banks.ini")
# def createConfigFile():
#     config["Test"] = {"Test1": "1", "Test2": "2", "Test3": "3"}
#     config["Test"]["Test4"] = "4"
#     config ["Other"] = {}
#     config["Other"]["Other1"] ="O1"
#     with open(path.join(path.dirname(__file__), "configs", "test.ini"), "w") as configfile:
#         config.write(configfile)
# createConfigFile()
# config.read(path.join(path.dirname(__file__), "configs", "test.ini"))
# print(config.sections())
# print(config["Test"]["Test1"])
def createConfigFile():
    if(not path.isfile(configFilePath)):
        # print("Working")
        with open(path.join(configFilePath), "w") as configfile:
            pass

def newBankConfig(bankName, separator, skipRows, header, encoding, startRow, dateColumn, amountColumn, receiptColumn, partnerColumn):
    config.read(configFilePath)
    if(not config.has_section(bankName)):
        config[bankName] = {"Separator": separator, "Skips_Rows": skipRows, "Header": header, "Encoding": encoding, "Start_Row": startRow, "Date_Column": dateColumn, "Amount_Column": amountColumn, "Receipt_Column": receiptColumn, "Partner_Column": partnerColumn}
    with open(path.join(configFilePath), "w") as configfile:
        config.write(configfile)

def returnConfigsList():
    config.read(configFilePath)
    return(config.sections())

def editBankConfig(choosenBank, key, newValue):
    config.read(configFilePath)
    config[choosenBank][key] = newValue
    with open(configFilePath, "w") as configfile:
        config.write(configfile)

def validateKeys(df, configkeys: list, startRow: int) -> list:
    validLists = []
    for x in range(len(configkeys)):
        if(configkeys[x] == None):
            validLists.append(None)
        else:
            column = int(configkeys[x]) - 1
            validColumn = df.iloc[startRow:, column]
            validList = validColumn.values.tolist()
            validLists.append(validList)
    return(validLists)

def getKeys(choosenBank):
    keys = []
    for key in config[choosenBank]:
        keys.append(config[choosenBank][key])
    return(keys)

createConfigFile()

# if(not getKeys(returnConfigsList()[1])[1]):
#     print("WORKING")
# else:
#     print("NOT WORKING")
# editConfig("Test", "separator", "New")
# newBankConfig("Test", ";", 4, 0, "latin1", 1, 2, 7)