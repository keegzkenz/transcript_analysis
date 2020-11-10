import os
from bs4 import BeautifulSoup as bs

TRANSCRIPTS_DIR = "./Transcripts/"
ERROR_DIR = "./Error_Transcripts/"
COMPANY_PARTICIPANTS = "Company Participants"
COMPANY_PARTICIPANT_KEYS = ["Company Participants", "Corporate Participants"]
ANALYSTS = "Call Participants"
ANALYST_KEYS = ["Conference Call Participants"]
OPERATOR = "Operator"
QA_ELEMENT_ID = "question-answer-session"
QUESTION_PARA = "question"
ANSWER_PARA = "answer"
OPERATOR_PARA = "operator"
FISCAL_YEARS = ["2019", "2020", "2021", "2022"]
CONTEXT = ["guid", "range", "reaffirm", "reiter", "outlook"]
DIRECTION = [
    "decel",
    " impl",
    "cautio",
    "confiden",
    "chang",
    "reason",
    "why",
    "confirm",
    "comfort",
    " raise",
    "raisi",
    "maintain",
    "math",
    "accel",
]


def get_ticker(file_string):
    ticker = (file_string).split("Transcripts/")[1].split(".htm")[0]
    return ticker


def get_fiscal_quarter_and_year(paras):
    fiscal_quarter_and_year_para = paras[0].text
    contains_fiscal_quarter_and_year = False
    for year in FISCAL_YEARS:
        if year in fiscal_quarter_and_year_para:
            contains_fiscal_quarter_and_year = True
            fiscal_year = year
            break
    if not contains_fiscal_quarter_and_year:
        return get_fiscal_quarter_and_year(paras[1:])
    try:
        fiscal_year_and_quarter = fiscal_quarter_and_year_para.split(") ")[1].split(
            " Earn"
        )[0]
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


def print_exchange(exchange):
    print(exchange[0])
    print(f"{exchange[1][0]} (Analyst):\n{exchange[1][1]}")
    print()
    print(f"{exchange[2][0]} (Company Participant):\n{exchange[2][1]}")
    print()


def print_exchanges(exchanges):
    for exchange in exchanges:
        print_exchange(exchange)


def is_para_type(para, para_type):
    if para_type == OPERATOR_PARA:
        return para.text.strip().capitalize() == OPERATOR
    else:
        return para.find("span", attrs={"class": para_type})


def get_exchanges_bad(paras, company_participants, analysts):
    exchanges = []
    exchange_num = 1

    # start by finding the question-and-answer section by id
    for para in paras:
        if para.get("id") == QA_ELEMENT_ID:
            start_index = paras.index(para) + 1
            break

    # we redefine the relevant paras as any paras occurring after the question-answer-section begins
    paras = paras[start_index:]
    current_index = 0
    end_index = len(paras) - 1
    already_built_a_question = False

    exchange_count = 0

    # starting from the first element and proceeding until the last
    while current_index < end_index:
        current_para = paras[current_index]

        """
        If the para is a question, it means one of three things:
            1. It is the first question (and as a result we do not have a previous answer to build)
            2. It is not the first question, but there was an operator section after the answer finished
            3. It is not the first question, but there was no operator section after the answer finished
        """
        if is_para_type(current_para, QUESTION_PARA):
            analyst = current_para.text.strip()
            question_start_index = current_index + 1

            if already_built_a_question:
                answer_end_index = current_index
                answer = build_speaker_tuple(
                    answer_start_index, answer_end_index, company_participant, paras
                )
                exchange = (exchange_num, question, answer)
                exchanges.append(exchange)
                already_built_a_question = False
                exchange_num += 1
        elif is_para_type(current_para, ANSWER_PARA):
            # we hit an answer so set is_question to false and handle question
            question_end_index = current_index
            question = build_speaker_tuple(
                question_start_index, question_end_index, analyst, paras
            )
            already_built_a_question = True
            company_participant = current_para.text.strip()
            answer_start_index = current_index + 1
        elif is_para_type(current_para, OPERATOR_PARA, already_built_a_question):
            answer = build_speaker_tuple(
                answer_start_index, answer_end_index, company_participant, paras
            )
            exchange = (exchange_num, question, answer)
            exchanges.append(exchange)
            already_built_a_question = False
            exchange_num += 1
        current_index += 1
    return exchanges


def get_next_type_occurrence(paragraphs, paragraph_type, index_min):
    for paragraph in paragraphs:
        if (
            is_para_type(paragraph, paragraph_type)
            and paragraphs.index(paragraph) >= index_min
        ):
            next_type_index = paragraphs.index(paragraph)
            break
    return next_type_index


def build_speaker_tuple(paragraphs):
    speaker = paragraphs[0].text.strip()
    remainder = paragraphs[1:]
    text = ""
    for para in remainder:
        text += para.text.strip() + "\n"
    return (speaker, text)


def get_section_count(paras, para_type):
    count = 0
    for para in paras:
        if is_para_type(para, para_type):
            count += 1
    return count


def get_exchanges(paras, company_participants, analysts):
    exchanges = []
    exchange_num = 1

    # start by finding the question-and-answer section by id
    for para in paras:
        if para.get("id") == QA_ELEMENT_ID:
            start_index = paras.index(para) + 1
            break

    # we redefine the relevant paras as any paras occurring after the question-answer-section begins
    paras = paras[start_index:]
    current_index = 0
    end_index = len(paras) - 1
    already_built_a_question = False

    exchange_count = 0

    # starting from the first element and proceeding until the last
    while len(paras) > 0:
        """
        1. Get the starting index of the next question section
        2. Redefine paras as beginning with the next question
        3. Reset start_index to 0
        """
        try:
            question_start_index = get_next_type_occurrence(paras, QUESTION_PARA, 0)
            paras = paras[question_start_index:]
            question_start_index = 0
            analyst = paras[question_start_index].text.split()
        except:
            print("No further questions")
            break

        try:
            # get the starting index of the next answer section
            answer_start_index = get_next_type_occurrence(
                paras, ANSWER_PARA, question_start_index
            )
        except:
            break

        try:
            # get the starting index of the next operator section
            operator_start_index = get_next_type_occurrence(
                paras, OPERATOR_PARA, question_start_index
            )
        except:
            operator_start_index = answer_start_index
        # the next question is everything b/t question start and earlier of next answer section and next operator section
        question_end_index = min(answer_start_index, operator_start_index)
        question = build_speaker_tuple(paras[question_start_index:question_end_index])
        rating = 0
        for context_word in CONTEXT:
            if context_word in question[1]:
                rating = 1
                for directional_word in DIRECTION:
                    if directional_word in question[1]:
                        rating = 2
        if rating > 0:
            print(f"QUESTION w/ RATING {rating}: {question}")
            print("\n")
        # redefine paras as the remaining text
        paras = paras[question_end_index:]

        # The next answer is everything b/t answer start and earlier of next operator section and next question section
        # next_question_start_index = get_next_type_occurrence(paras, QUESTION_PARA, 0)
        # next_operator_start_index = get_next_type_occurrence(paras, OPERATOR_PARA, 0)
        # answer_end_index = min(next_question_start_index, next_operator_start_index)

        # find the number of sub_answers
        # answer_paras = paras[answer_start_index:answer_end_index]
        # print("ANSWER_PARAS", answer_paras)
        # sub_answer_count =

        # answer = build_speaker_tuple(paras[:answer_end_index])
        # print("ANSWER", answer)

        # build exchange using question, answer, and exchange number
        # increment exchange number
        # exchange = (question, answer, exchange_num)
        # exchanges.append(exchange)
        exchange_num += 1

        # redefine paras as the remaining text
        # paras = paras[answer_end_index:]
    return exchanges


def get_start_key(paragraphs, key_list):
    for paragraph in paragraphs:
        for key in key_list:
            if key == paragraph.text.strip():
                return key


i = 0
for filename in os.listdir(TRANSCRIPTS_DIR):
    html_path = os.path.join(TRANSCRIPTS_DIR, filename)
    error_path = os.path.join(ERROR_DIR, filename)
    ticker = get_ticker(html_path)
    html_file = open(html_path, "r")
    i + 1
    try:
        html_content = html_file.read()
        html_file.close()
        soup = bs(html_content, "html.parser")
        paras = soup.find_all("p")
        if len(paras) > 0:
            fiscal_quarter, fiscal_year = get_fiscal_quarter_and_year(paras)
            print("\n")
            print(f"{ticker} {fiscal_quarter} {fiscal_year}\n\n")
            company_start_key = get_start_key(paras, COMPANY_PARTICIPANT_KEYS)
            analyst_start_key = get_start_key(paras, ANALYST_KEYS)
            company_participants = get_speakers(
                paras, company_start_key, analyst_start_key
            )
            # print(f"{COMPANY_PARTICIPANTS}: {company_participants}\n")
            analysts = get_speakers(paras, ANALYSTS, OPERATOR)
            # print(f"{ANALYSTS}: {analysts}\n")
            exchanges = get_exchanges(paras, company_participants, analysts)
            # print_exchanges(exchanges)
        else:
            print(f"{html_path} is Missing!")
            os.system(f"mv {html_path} {error_path}")
            break
    except:
        print("ERROR READING: " + html_path)
        break
    finally:
        if i > 1:
            break
