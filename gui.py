from tkinter import *
from tkinterdnd2 import TkinterDnD
from tkinter import filedialog
from configFiles import getKeyValues, getSectionNames, returnConfigsList, newBankConfig, editBankConfig, removeBankConfig, createConfigFile
from csvConverter import createExcel, convertAndGetLists, readDataFrame, addCsvToList

csvPath=""

def startProgram():
    openMainWindow()

def createFields(masterWindow):
    sections = getSectionNames()
    entries = []
    rowCounter = 1
    Label(masterWindow, text="Bank Name").grid(row=0)
    bankName = Entry(masterWindow)
    bankName.grid(row=0, column=1)
    entries.append(bankName)
    for section in sections:
        Label(masterWindow, text=section).grid(row=rowCounter)
        sectionEntry = Entry(masterWindow)
        sectionEntry.grid(row=rowCounter, column=1)
        entries.append(sectionEntry)
        rowCounter += 1
        continue       
    return(rowCounter, entries)

def populateFields(choosenBank: str, fields: list[Entry]):
    fieldValues = getKeyValues(choosenBank)
    currentField = 0
    for field in fields:
        if(currentField > 0):
            field.insert(END, fieldValues[currentField-1])
        else:
            field.insert(END, choosenBank)
        currentField += 1
        continue
    return

def validateFields(fields: list[Entry]):
    # validationChecks = {"bank_name: , separator": , "skips_rows": , "header": , "encoding": , "start_row": , "date_column": , "amount_column": , "receipt_column": , "partner_column": , "currency_column":  }
    pass

def openCSV(buttonInput: Button):
    global csvPath
    previousPath = csvPath
    csvPath = filedialog.askopenfilename(filetypes=(("CSV Files", "*.csv"),))
    if(not csvPath == ""):
        buttonInput.config(text=csvPath)
        return(csvPath)
    else:
        csvPath = previousPath
        return(previousPath)

def editBank(choosenConfig: str, bankConfigs: list, dropDownList: OptionMenu, feedBackLabel: Label):
    if(choosenConfig.get() in bankConfigs):
        openEditBankWindow(choosenConfig, dropDownList)
    else: 
        feedBackLabel.config(fg="#FF0000", text="You must select a Bank to edit")

def update(choosenConfig, masterWindow, dropDownList):
    # Update the OptionMenu in the main window
    new_banks = returnConfigsList()
    menu = dropDownList["menu"]
    menu.delete(0, "end")
    for bank in new_banks:
        menu.add_command(label=bank, command=lambda value=bank: choosenConfig.set(value))
    choosenConfig.set(new_banks[-1] if new_banks else "Bank")
    masterWindow.destroy()

def createNewButton(master: Frame, csvFilesList: list):
    newButton = Button(text="Input CSV", command=lambda: [addCsvToList(openCSV(newButton), csvFilesList), createNewButton(master, csvFilesList)], master=master)
    newButton.grid(row="1", column="0")
def ok(choosenConfig: StringVar, window: Tk, feedBackLabel: Label, csvFilesList: list):
    choosenBank = choosenConfig
    if(choosenBank == "Bank"):
        feedBackLabel.config(fg="#FF0000", text="You must choose a bank")
    else:
        if(not csvFilesList):
            if(not csvPath == ""):
                try:
                    createExcel(csvPath, *convertAndGetLists(*readDataFrame(csvPath, getKeyValues(choosenBank))))
                    feedBackLabel.config(fg="#008000", text="Success")
                except Exception as e:
                    feedBackLabel.config(fg="#FF0000", text="An Error has occured")
        else:
            for csvFilePath in csvFilesList:
                try:
                    createExcel(csvFilePath, *convertAndGetLists(*readDataFrame(csvFilePath, getKeyValues(choosenBank))))
                    feedBackLabel.config(fg="#008000", text="Success")
                except Exception as e:
                    feedBackLabel.config(fg="#FF0000", text="An Error has occured")
        # window.destroy()

def openMainWindow():
    bankConfigs = returnConfigsList()
    window = Tk()
    choosenConfig = StringVar(window)
    csvFilesList = []
    choosenConfig.set("Bank")
    window.geometry("400x140")
    window.title("Bank Konvertáló")
    inputFunctionsFrame = Frame()
    inputFunctionsFrame.pack()
    buttonInput = Button(text="Input CSV", command=lambda: openCSV(buttonInput), master=inputFunctionsFrame)
    buttonInput.pack(side=LEFT)
    buttonBatchInput = Button(text = "A", command=lambda: batchInput(csvFilesList), master=inputFunctionsFrame)
    buttonBatchInput.pack(side=LEFT)
    dropDownList = OptionMenu(window, choosenConfig, *bankConfigs or ["Bank"])
    dropDownList.pack()
    configFunctionsFrame = Frame(window)
    configFunctionsFrame.pack()
    buttonAddBank = Button(configFunctionsFrame, text="Add New Bank", command=lambda: addNewBank(choosenConfig, dropDownList))
    buttonAddBank.pack(side=LEFT)
    buttonEditBank = Button(configFunctionsFrame, text="Edit Bank", command=lambda: editBank(choosenConfig, returnConfigsList(), dropDownList, feedBackLabel))
    buttonEditBank.pack(side=LEFT)
    buttonOK = Button(text="OK", command=lambda: ok(choosenConfig.get(), window, feedBackLabel, csvFilesList))
    buttonOK.pack()
    feedBackLabel = Label(master=window, text="")
    feedBackLabel.pack()
    window.mainloop()

def addNewBank(choosenConfig, dropDownList):
    addWindow = Tk()
    addWindow.title("New Bank")
    addWindow.geometry("300x300")
    returnedValues = createFields(addWindow)
    rowCounter = returnedValues[0]
    addButton = Button(addWindow, text="Add", command=lambda:[newBankConfig(*[entry.get() for entry in returnedValues[1]]), update(choosenConfig, addWindow, dropDownList)])
    addButton.grid(row=rowCounter, column=1)
    addWindow.mainloop()

def openEditBankWindow(choosenConfig: str, dropDownList):
    bankToEdit = choosenConfig.get()
    editWindow = Tk()
    editWindow.title(f"Edit {bankToEdit}")
    editWindow.geometry("300x300")
    returnedValues = createFields(editWindow)
    populateFields(bankToEdit, returnedValues[1])
    rowCounter = returnedValues[0]
    editButton = Button(text="Save Changes", command=lambda: [editBankConfig(bankToEdit, [newValue.get() for newValue in returnedValues[1]]), update(choosenConfig, editWindow, dropDownList)], master=editWindow)
    editButton.grid(row=rowCounter, column=0)
    buttonRemoveBank = Button(text="Remove Bank", command=lambda: [removeBankConfig(bankToEdit), update(choosenConfig, editWindow, dropDownList)], master=editWindow)
    buttonRemoveBank.grid(row=rowCounter, column=1)
    editWindow.mainloop()

def batchInput(csvFilesList: list):
    batchWindow = Tk()
    batchWindow.title("Batch Selection")
    batchWindow.geometry("400x200")
    buttonsFrame = Frame(master=batchWindow)
    buttonsFrame.pack()
    buttonInput = Button(text="Input CSV", command=lambda: [addCsvToList(openCSV(buttonInput), csvFilesList), createNewButton(buttonsFrame, csvFilesList)], master=buttonsFrame)
    buttonInput.grid(row="0", column="0")
    batchWindow.mainloop()

if __name__ == "__main__":
    createConfigFile()
    startProgram()