import glob
from bs4 import BeautifulSoup as bs

# get list of company participants (employees)


def getCompanyParticipants(htmlAsText):
    companyParticipants = []
    for para in htmlAsText:
        if " - " in para:
            arr = para.split(" - ")
            companyParticipants.append(arr[0])
        elif para == "Analysts":
            break
    return companyParticipants

# get list of call participants (analysts)


def getCallParticipants(htmlAsText):
    callParticipants = []
    for para in htmlAsText:
        if (para == "Conference Call Participants") or (para == "Analysts"):
            startIndex = htmlAsText.index(para)
            break
    i = startIndex + 1
    while i < len(htmlAsText):
        para = htmlAsText[i]
        if para == "Operator" or para in getCompanyParticipants(htmlAsText):
            break
        else:
            arr = para.split(" - ")
            callParticipants.append(arr[0])
            i += 1
    return callParticipants


def getOpeningStatements(htmlAsText):
    i = 0
    for para in htmlAsText:
        if para == "Operator":
            startIndex = htmlAsText.index(para)
        if para == "Question-and-Answer Session":
            endIndex = htmlAsText.index(para)
            break

    openingStatementsBySpeaker = []
    prevPara = [htmlAsText[startIndex]]

    for i in range(startIndex + 1, endIndex):
        para = htmlAsText[i]
        if para in speakers:
            openingStatementsBySpeaker.append(prevPara)
            prevPara = [para]
        else:
            prevPara.append(para)
    openingStatementsBySpeaker.append(prevPara)

    openingStatementsDicts = []
    for section in openingStatementsBySpeaker:
        dict = {
            "SPEAKER": section[0],
            "CONTENT": section[1:]
        }
        openingStatementsDicts.append(dict)
    return openingStatementsDicts


def getQuestionAnswerExchanges(htmlAsText):
    for para in htmlAsText:
        if para == "Question-and-Answer Session":
            startIndex = htmlAsText.index(para) + 1

    exchanges = []
    prevExchange = [htmlAsText[startIndex]]

    for i in range(startIndex + 1, len(htmlAsText)):
        para = htmlAsText[i]
        if para in speakers:
            exchanges.append(prevExchange)
            prevExchange = [para]
        else:
            prevExchange.append(para)
    exchanges.append(prevExchange)

    exchangesDicts = []
    for exchange in exchanges:
        dict = {
            "SPEAKER": exchange[0],
            "CONTENT": exchange[1:]
        }
        exchangesDicts.append(dict)

    for exchange in exchangesDicts:
        if exchange["SPEAKER"] in getCallParticipants(htmlAsText):
            startIndex = exchangesDicts.index(exchange)
            break

    questionAnswerPairs = []
    questionAnswerPair = [exchangesDicts[startIndex]]

    for i in range(startIndex + 1, len(exchangesDicts)):
        exchange = exchangesDicts[i]
        if exchange["SPEAKER"] in getCallParticipants(htmlAsText):
            questionAnswerPairs.append(questionAnswerPair)
            questionAnswerPair = [exchange]
        elif exchange["SPEAKER"] in getCompanyParticipants(htmlAsText):
            questionAnswerPair.append(exchange)
    questionAnswerPairs.append(questionAnswerPair)

    return questionAnswerPairs


loadedHTMLTranscripts = (glob.glob("Transcripts/*.htm*"))
i = 1
for htmlTranscript in loadedHTMLTranscripts:
    try:
        html_file = open(htmlTranscript, 'r')
        html_content = html_file.read()
        html_file.close()

        soup = bs(html_content, 'html.parser')
        print(soup)
        break

        htmlAsText = []

        for paras in soup.find_all("p"):
            para = str(paras.text)
            htmlAsText.append(para)

        speakers = getCallParticipants(
            htmlAsText) + getCompanyParticipants(htmlAsText) + ["Operator"]

    except:
        print("ERROR READING: " + htmlTranscript)

# get Ticker, Quarter
# display in front-end app
# filter exchanges based on occurences of certain word
