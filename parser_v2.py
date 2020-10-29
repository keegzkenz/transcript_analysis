import os
from bs4 import BeautifulSoup as bs

TRANSCRIPTS_DIR = '/Users/kylekennedy/Desktop/Transcripts/'
COMPANY_PARTICIPANTS = "Company Participants"
ANALYSTS = "Call Participants"
OPERATOR = 'Operator'
QA_ELEMENT_ID = 'question-answer-session'


def get_ticker(file_string):
    ticker = (file_string).split("Transcripts/")[1].split(".htm")[0]
    return ticker


def get_fiscal_quarter_and_year(para_as_text):
    try:
        fiscal_year_and_quarter = para_as_text.split(") ")[1].split(" Earn")[0]
        if "2020" in fiscal_year_and_quarter:
            fiscal_year = "2020"
        elif "2021" in fiscal_year_and_quarter:
            fiscal_year = "2021"
        fiscal_quarter = fiscal_year_and_quarter.split(" " + fiscal_year)[0]
    except:
        print("Could not fetch fiscal quarter or year")
    return (fiscal_quarter, fiscal_year)


def get_speakers(paras, start_key, end_key):
    speakers = []
    for para in paras:
        start_index = 0
        if start_key in para.text:
            start_index = paras.index(para) + 1
            break
    for para in paras[start_index:]:
        if end_key in para.text:
            end_index = paras.index(para)
            break
    for para in paras[start_index:end_index]:
        if "–" in para.text and "-" in para.text:
            lower = min(para.text.index("–"), para.text.index("-"))
            speaker = para.text[0:lower]
        elif "–" in para.text:
            speaker = para.text.split("–")[0]
        elif "-" in para.text:
            speaker = para.text.split("-")[0]
        speakers.append(speaker.strip())
    return speakers


def get_text_string_from_paras(paras):
    text_string = ''
    for para in paras:
        text_string += (para.text.strip() + "\n")
    return text_string


def build_speaker_tuple(start, end, speaker, paras):
    text = get_text_string_from_paras(
        paras[start:end])
    return (speaker, text)


def print_exchange(exchange):
    print(exchange[0])
    print(f"{exchange[1][0]} (Analyst):\n{exchange[1][1]}")
    print()
    print(
        f"{exchange[2][0]} (Company Participant):\n{exchange[2][1]}")
    print()


def get_exchanges(paras, company_participants, analysts):
    exchanges = []
    exchange_num = 1
    for para in paras:
        if para.get('id') == QA_ELEMENT_ID:
            start_index = paras.index(para) + 1
            break
    paras = paras[start_index:]
    current_index = 0
    end_index = len(paras) - 1
    already_built_a_question = False
    while current_index < end_index:
        current_para = paras[current_index]
        if current_para.find('span', attrs={'class': 'question'}):
            if already_built_a_question:
                answer_end_index = current_index
                answer = build_speaker_tuple(
                    answer_start_index, answer_end_index, company_participant, paras)
                exchange = (exchange_num, question, answer)
                exchanges.append(exchange)
                already_built_a_question = False
                print_exchange(exchange)
                exchange_num += 1
            analyst = current_para.text.strip()
            question_start_index = current_index + 1
        elif current_para.find('span', attrs={'class': 'answer'}):
            # we hit an answer so set is_question to false and handle question
            question_end_index = current_index
            question = build_speaker_tuple(
                question_start_index, question_end_index, analyst, paras)
            already_built_a_question = True
            company_participant = current_para.text.strip()
            answer_start_index = current_index + 1
        elif current_para.text.strip().capitalize() == OPERATOR and already_built_a_question:
            answer = build_speaker_tuple(
                answer_start_index, answer_end_index, company_participant, paras)
            exchange = (exchange_num, question, answer)
            print_exchange(exchange)
            exchanges.append(exchange)
            already_built_a_question = False
        current_index += 1


i = 1
for filename in os.listdir(TRANSCRIPTS_DIR):
    html_transcript = os.path.join(TRANSCRIPTS_DIR, filename)
    ticker = get_ticker(html_transcript)
    html_file = open(html_transcript, 'r')
    i + 1
    try:
        html_content = html_file.read()
        html_file.close()
        soup = bs(html_content, 'html.parser')

        paras = soup.find_all("p")
        if len(paras) > 0:
            fiscal_quarter, fiscal_year = get_fiscal_quarter_and_year(
                paras[0].text)
            print("\n")
            print(f"{ticker} {fiscal_quarter} {fiscal_year}\n\n")
            company_participants = get_speakers(
                paras, COMPANY_PARTICIPANTS, ANALYSTS)
            analysts = get_speakers(paras, ANALYSTS, OPERATOR)
            print(f"{COMPANY_PARTICIPANTS}: {company_participants}\n")
            print(f"{ANALYSTS}: {analysts}\n")
            exchanges = get_exchanges(paras, company_participants, analysts)
        else:
            print(f"{html_transcript} is Missing!")
            break
        for exchange in exchange:
            print(exchange)
    except:
        print("ERROR READING: " + html_transcript)
        break
    finally:
        if i > 5:
            break
