import pyautogui
import time
import os.path
from os import path
import csv

tickers = []
TEMP_IGNORE = ['CTXR']
PERM_IGNORE = ['FMBH', 'FEAC=', 'FEAC+', 'FATBW', 'FAII=', 'EYESW', 'EXPCW', 'EXPCU', 'EVGBC', 'ESSCW', 'ESSCR', 'ESSC', 'ELAT', 'BLNKW', 'CBX', 'CCAC+', 'CCAC=', 'CCIV=', 'CCX+', 'CCX=', 'CLRBZ', 'CLA=', 'CIICU', 'CIICW', 'CIG.C',
               'CHPMW', 'CHPM', 'CHNGU', 'CHCI', 'CHAQ=', 'CHAQ+', 'CHAQ', 'CGRO', 'CFIIU', 'CETXW', 'CELG^', 'CCXX+', 'CCXX=', 'CBO', 'CLBRZ', 'CLA=', 'CPSR', 'CPAAW', 'CRSAW', 'CTA', 'CTEST', 'CTEST.E', 'CTEST.G', 'CTEST.L', 'CTEST.O', 'CTEST.S', 'CTEST.V', 'CTXRW', 'DCUE', 'DEH=', 'DFNS+', 'DFNS=', 'DFPH', 'DFPHW', 'DGNR=', 'DLPNW', 'DMS+', 'DMYD=', 'DMYT+', 'DMYT=', 'DRADP', 'DRIOW', 'DSKEW', 'DTLA', 'DTY', 'EAE', 'ECOLW', 'KTOVW', 'LACQW', 'LATN', 'LATNW', 'LCAHW', 'LCAPU', 'LGC+', 'LGC=', 'LGHLW', 'LGVW', 'LGVW+', 'LGVW=', 'LIVK', 'LMFAW', 'LOAK+', 'LOAK=', 'LSAC', 'LSACW', 'MH', 'MLAC', 'MLACW', 'NBACW', 'NDRAW', 'NESRW', 'NFH+', 'NFINW', 'NGA=', 'NHLDW', 'NMK', 'OAC+', 'OAC=', 'ONTXW', 'OPESW', 'OPP^#', 'ORSN', 'ORSNR', 'ORSNW', 'OSS', 'OXBRW', 'OXY+', 'PACK+', 'PAEWW', 'PANA', 'PANA+', 'PANA=', 'PANA+', 'PANA=', 'PAVMW', 'PAVMZ', 'PCGU', 'PCPL', 'PCPL+', 'PCPL=', 'PIC+', 'PIC=', 'PRIF', 'PRPB=', 'PSAC', 'PSACW', 'PSTH=', 'PTACW', 'RACA', 'RBAC=', 'RMG+', 'RMG=', 'RMPL', 'ROCH', 'ROCHW', 'RPLA+', 'RPLA=', 'SAQN', 'SAQNW', 'SBBA', 'SBE+', 'SBE=', 'SCE', 'SCPE+', 'SCPE=', 'SCVX', 'SCVX+', 'SCVX=', 'SFTW', 'SFTW+', 'SFTW=', 'SGLBW', 'SHIPZ', 'SHLL+', 'SHLL=', 'SIVBP', 'SNGXW', 'SOAC+', 'SOAC=', 'SPAQ+', 'SPAQ=', 'SSPK', 'SSPKW', 'STPK=', 'SWT', 'TALO+', 'TBBK', 'TBKCP', 'TRNE+', 'TRNE=', 'UNB', 'UONE', 'USWSW', 'UTZ+', 'UUUU+', 'UZD', 'VERBW', 'VERT=', 'VERY', 'VIRT', 'VIV', 'VKTXW', 'VRMEW', 'VRT+', 'VST+A', 'VVNT+', 'WPF', 'WPF+', 'WPF=', 'ZAZZT']
IGNORE = TEMP_IGNORE + PERM_IGNORE
csvpath = "./tickers.csv"
REBOOT_LIMIT = 7000

# load all of the tickers into an array
with open(csvpath, 'rt') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in reader:
        tickers.append(row[0])

tickers.pop(0)


def saveTranscript(ticker):
    # allow time for user to naviigate to Chrome window, open new tab
    time.sleep(3)
    pyautogui.hotkey("command", "n")
    time.sleep(2)

    # highlight URL search bar in browser
    pyautogui.hotkey("command", "l")
    time.sleep(1)

    # navigate to individual ticker's transcript page
    pyautogui.typewrite("https://seekingalpha.com/symbol/" +
                        ticker + "/earnings/transcripts")
    time.sleep(1)
    pyautogui.typewrite(["enter"])
    time.sleep(3)

    # find and navigate to most recent earnings call
    pyautogui.hotkey("command", "f")
    time.sleep(.3)
    pyautogui.typewrite("- Earnings Call Transcript")
    time.sleep(.3)
    pyautogui.typewrite(["escape"])
    time.sleep(.3)
    pyautogui.typewrite(["enter"])
    time.sleep(3)

    # save transcript to Transcripts folder
    pyautogui.hotkey("command", "s")
    time.sleep(2)
    pyautogui.typewrite(ticker)
    time.sleep(.3)
    pyautogui.typewrite(["enter"])
    time.sleep(3)

    # close tabs
    pyautogui.hotkey("command", "w")
    time.sleep(.5)
    pyautogui.hotkey("command", "w")
    time.sleep(.5)


def reboot():
    pyautogui.hotkey("command", "q")
    time.sleep(8)
    pyautogui.hotkey("command", "space")
    time.sleep(.5)
    pyautogui.typewrite("google.com")
    time.sleep(.5)
    pyautogui.typewrite(["enter"])
    time.sleep(8)


def getTranscripts(tickers):
    i = 0
    j = 0
    while i < len(tickers):
        ticker = tickers[i]
        if i % 8 == 0 and i > REBOOT_LIMIT:
            reboot()

        if path.exists("./Transcripts/" + ticker + ".html") or path.exists("./Transcripts/" + ticker + ".htm") or path.exists("./Error_Transcripts/" + ticker + ".html") or path.exists("./Error_Transcripts/" + ticker + ".htm"):
            print("ADDED TICKER: " + ticker + ": " + str(i))
            j = 0
            i += 1
        elif ticker in IGNORE:
            print("IGNORED TICKER: " + ticker + ": " + str(i))
            j = 0
            i += 1
        elif j < 2:
            j += 1
            saveTranscript(ticker)
        else:
            print("UNABLE TO ADD TICKER: " + ticker)
            j = 0
            i += 1


getTranscripts(tickers)
