import os
from bs4 import BeautifulSoup as bs
import csv

TRANSCRIPTS_DIR = "./Transcripts/"
NO_TRANSCRIPT_DIR = "./Invalid/"
NO_QA_DIR = "./No_QA/"
UNKNOWN_ERROR_DIR = "./Unknown_Error/"
RATED_DIR = "./Rated_Transcripts/"
FQ_ERROR_DIR = "./FQ_Or_Year_Error"
OTHER_DIRS = [NO_TRANSCRIPT_DIR, NO_QA_DIR, RATED_DIR, FQ_ERROR_DIR]
COMPANY_PARTICIPANTS = "Company Participants"
COMPANY_PARTICIPANT_KEYS = ["Company Participants",
                            "Corporate Participants", "Company Representatives"]
ANALYSTS = "Call Participants"
ANALYST_KEYS = ["Conference Call Participants", "Conference Call participants"]
OPERATOR = "Operator"
QUESTION_PARA = "question"
ANSWER_PARA = "answer"
OPERATOR_PARA = "operator"
FISCAL_YEARS = ["2019", "2020", "2021", "2022"]
FISCAL_QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
CONTEXT_WORDS = ["guid", "range", "reaffirm", "reiter", "outlook"]
DIRECTIONAL_WORDS = [
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
    " raisi",
    "maintain",
    "math",
    "accel",
    "early",
    "back half",
    "second half",
    "still",
    "achiev",
    "need",
    "requir",
    "conting" "have to",
    "to hit",
    "pretty",
    "reiter",
    "concern",
    "understand",
    " belie",
    "original",
    "current",
    "difficult",
    " paus",
    " bak",
    "restat",
    "why",
    "anticipat",
    "suggest",
    " beat",
    " hit",
    " conserv",
]


def get_ticker(file_string):
    ticker = (file_string).split("Transcripts/")[1].split(".htm")[0]
    return ticker


def get_fiscal_quarter_and_year(paras):
    try:
        fiscal_quarter_and_year_para = paras[0].text
        contains_fiscal_quarter_and_year = False
        for year in FISCAL_YEARS:
            if year in fiscal_quarter_and_year_para:
                fiscal_year = year
                break
        for quarter in FISCAL_QUARTERS:
            if quarter in fiscal_quarter_and_year_para:
                fiscal_quarter = quarter
                contains_fiscal_quarter_and_year = True
                break
        if not contains_fiscal_quarter_and_year:
            return get_fiscal_quarter_and_year(paras[1:])
        else:
            return (fiscal_quarter, fiscal_year)
    except:
        print("Could not fetch fiscal quarter or year")


def get_speakers(paras, start_key, end_key):
    try:
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
    except:
        print(
            f"BAD TRANSCRIPT ERROR: Could not fetch speakers between {start_key} and {end_key}")


def is_para_type(para, para_type):
    if para_type == OPERATOR_PARA:
        return para.text.strip().capitalize() == OPERATOR
    else:
        para_span = para.find("span", attrs={"class": para_type})
        if not para_span:
            return False
        else:
            return True


def get_next_type_occurrence(paragraphs, paragraph_type):
    for paragraph in paragraphs:
        if (
            is_para_type(paragraph, paragraph_type)
        ):
            next_type_index = paragraphs.index(paragraph)
            break
    if not next_type_index:
        print(f'No Next {paragraph_type} Type Found!')
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


def get_qa_paras(paras):
    # start by finding the question-and-answer section by id
    for para in paras:
        if para.get("id"):
            para_id = para.get("id").lower()
            if "question" in para_id and "answer" in para_id and "session" in para_id:
                start_index = paras.index(para) + 1
                break
     # we redefine the relevant paras as any paras occurring after the question-answer-section begins
    try:
        qa_paras = paras[start_index:]
    except:
        print("BAD TRANSCRIPT ERROR: Could not fetch QA start index")
        qa_paras = []
    return qa_paras


def get_raw_analyst_paras(paras):
    raw_analyst_paras = []
    for para in paras:
        if is_para_type(para, QUESTION_PARA):
            raw_analyst_paras.append(para)
    return raw_analyst_paras

# this and the above should be refactored into a generic method


def get_raw_non_analyst_paras(paras):
    raw_non_analyst_paras = []
    for para in paras:
        if is_para_type(para, OPERATOR_PARA) or is_para_type(para, ANSWER_PARA):
            raw_non_analyst_paras.append(para)
    return raw_non_analyst_paras


def get_next_speaker_para(paras, company_participants):
    for para in paras:
        if (is_para_type(para, QUESTION_PARA) or is_para_type(para, ANSWER_PARA) or is_para_type(para, OPERATOR_PARA) or para.text in company_participants):
            next_speaker_para = para
            break
    if not next_speaker_para:
        print('No next speaker para')
        return
    return next_speaker_para


def get_start_key(paragraphs, key_list):
    try:
        for paragraph in paragraphs:
            for key in key_list:
                if key == paragraph.text.strip():
                    return key
    except:
        print(
            f"BAD TRANSCRIPT ERROR: Could not fetch start key for {key_list}")


def build_questions_list(qa_paras, analyst_paras, company_participants):
    questions = []
    i = 0
    remaining_paras = qa_paras
    while i < len(analyst_paras):
        raw_para = analyst_paras[i]
        # get analyst by getting text from raw para and stripping whitespace
        analyst = raw_para.text.strip()
        # get current index and use this to get remaining para
        current_index = remaining_paras.index(raw_para)
        remaining_paras = remaining_paras[current_index + 1:]
        """
        the question text is everything between the analyst speaker para and the next speaker para
        """
        next_speaker_para = get_next_speaker_para(
            remaining_paras, company_participants)
        next_speaker_index = remaining_paras.index(next_speaker_para)
        question_text = remaining_paras[:next_speaker_index]
        question = (analyst, question_text)
        questions.append(question)
        remaining_paras = remaining_paras[next_speaker_index:]
        i += 1
    return questions


def build_answer(answer_paras, company_participants):
    answer = []
    building_sub_answer = False
    current_sub_answer_paras = []
    for para in answer_paras:
        # if we were not already building a sub_answer, then set the speaker to the para and set building_sub_answer to True
        if (is_para_type(para, OPERATOR_PARA) or is_para_type(para, ANSWER_PARA) or para.text in company_participants) and not building_sub_answer:
            speaker = para
            building_sub_answer = True
        # if we were already building a sub_answer, then a new operator or analyst para indicates that sub_answer is complete
        elif (is_para_type(para, OPERATOR_PARA) or is_para_type(para, ANSWER_PARA) or para.text in company_participants) and building_sub_answer:
            answer.append((speaker, current_sub_answer_paras))
            speaker = para
            current_sub_answer_paras = []
            building_sub_answer = False
        else:
            current_sub_answer_paras.append(para)

    answer.append((speaker, current_sub_answer_paras))
    return answer


def build_answers_list(qa_paras, non_analyst_paras, questions, company_participants):
    remaining_paras = qa_paras
    answers = []
    i = 0
    while i < len(questions):
        current_question_end_index = remaining_paras.index(questions[i][1][-1])
        remaining_paras = remaining_paras[current_question_end_index + 1:]
        if i + 1 < len(questions):
            next_question_start_index = remaining_paras.index(
                questions[i + 1][1][0])
            answer_paras = remaining_paras[:next_question_start_index - 1]
        else:
            answer_paras = remaining_paras
        answer = build_answer(answer_paras, company_participants)
        answers.append(answer)
        i += 1
    return answers


def get_questions(paras, company_participants):
    questions = []
    # get all paragraphs occurring after question-answer section begins
    qa_paras = get_qa_paras(paras)

    raw_analyst_paras = get_raw_analyst_paras(qa_paras)
    questions = build_questions_list(
        qa_paras, raw_analyst_paras, company_participants)
    if len(questions) != len(raw_analyst_paras):
        print(f"BAD TRANSCRIPT ERROR: Number of questions does not equal number of raw analyst paras")
    # set current index to 0, end_index to
    return questions


def get_answers(questions, paras, company_participants):
    answers = []
    # get all paragraphs occurring after question-answer section begins
    qa_paras = get_qa_paras(paras)
    raw_non_analyst_paras = get_raw_non_analyst_paras(qa_paras)
    answers = build_answers_list(
        qa_paras, raw_non_analyst_paras, questions, company_participants)
    return answers


def build_string_from_para_list(paras):
    text_string = ''
    for para in paras:
        text = para.text.strip()
        text_string += text
    return text_string


"""
if question has context and direction, it is a 3
if question has context, it is a 2
if question has direction, it is a 1
"""


def rate_question(text):
    rating = 0
    context = 'No Context in Question'
    direction = 'No Direction in Question'
    for context_word in CONTEXT_WORDS:
        if context_word in text.lower():
            context = context_word
            rating = 2
            break
    for directional_word in DIRECTIONAL_WORDS:
        if directional_word in text.lower():
            direction = directional_word
            rating += 1
            break
    return (rating, context, direction)


# should refactor (along w/ rate_question)
# for the answer, we combine all the text into a single block
def rate_answer(answer):
    rating = 0
    context = 'No Context in Answer'
    direction = 'No Direction in Answer'
    text_string = ''
    for sub_answer in answer:
        text_string += sub_answer[1] + ' '
    for context_word in CONTEXT_WORDS:
        if context_word in text_string.lower():
            context = context_word
            rating = 2
            break
    for directional_word in DIRECTIONAL_WORDS:
        if directional_word in text_string.lower():
            direction = directional_word
            rating += 1
            break
    return (rating, context, direction)


def rate_qa(question_text, answer):
    q_rating, context, skepticism = rate_question(question_text)
    question_rating = (q_rating, context, skepticism)
    a_rating, context, skepticism = rate_answer(answer)
    answer_rating = (a_rating, context, skepticism)
    overall_rating = q_rating * a_rating
    return (overall_rating, question_rating, answer_rating)


def get_exchanges(questions, answers):
    exchanges = []
    i = 0
    while i < len(questions):
        question = questions[i]
        analyst = question[0]
        question_text_paras = question[1]
        question_text = build_string_from_para_list(question_text_paras)
        answer = []
        for sub_answer in answers[i]:
            sub_answer_speaker = sub_answer[0].text.strip()
            sub_answer_text_paras = sub_answer[1]
            sub_answer_text = build_string_from_para_list(
                sub_answer_text_paras)
            sub_answer = (sub_answer_speaker, sub_answer_text)
            answer.append(sub_answer)
        exchange_num = i + 1
        exchange_rating = rate_qa(question_text, answer)
        exchange = (exchange_num, exchange_rating, analyst, question_text,
                    answer)
        exchanges.append(exchange)
        i += 1
    return exchanges


def reset_transcript_locations():
    for dir in OTHER_DIRS:
        for filename in os.listdir(dir):
            old_path = os.path.join(dir, filename)
            new_path = os.path.join(TRANSCRIPTS_DIR)
            os.system(f"mv {old_path} {new_path}")


i = 0

with open("rated_transcripts.csv", mode="w") as ratings_file:
    ratings_writer = csv.writer(
        ratings_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
    )
    ratings_writer.writerow(
        ["ticker", "fiscal_quarter", "fiscal_year",
            "question", "evidence", "rating"]
    )
    for filename in os.listdir(TRANSCRIPTS_DIR):
        html_path = os.path.join(TRANSCRIPTS_DIR, filename)
        no_transcript_path = os.path.join(NO_TRANSCRIPT_DIR, filename)
        no_qa_path = os.path.join(NO_QA_DIR, filename)
        error_path = os.path.join(UNKNOWN_ERROR_DIR, filename)
        rated_path = os.path.join(RATED_DIR, filename)
        ticker = get_ticker(html_path).upper()
        html_file = open(html_path, "r")
        i += 1
        try:
            html_content = html_file.read()
            html_file.close()
            soup = bs(html_content, "html.parser")
            paras = soup.find_all("p")
            questions = []
            if len(paras) == 0:
                print(
                    f"BAD TRANSCRIPT ERROR: {html_path} moved to 'No Transcript' folder")
                os.system(f"mv {html_path} {no_transcript_path}")
                continue
            elif len(paras) > 0:
                fiscal_quarter, fiscal_year = get_fiscal_quarter_and_year(
                    paras)
                print(f"{ticker} {fiscal_quarter} {fiscal_year}\n")
                company_start_key = get_start_key(
                    paras, COMPANY_PARTICIPANT_KEYS)
                analyst_start_key = get_start_key(paras, ANALYST_KEYS)
                company_participants = get_speakers(
                    paras, company_start_key, analyst_start_key
                )
                analysts = get_speakers(paras, analyst_start_key, OPERATOR)
                questions = get_questions(paras, company_participants)
                answers = get_answers(questions, paras, company_participants)
                exchanges = get_exchanges(questions, answers)
                for exchange in exchanges:
                    print(
                        f"QA {exchange[0]} [Rating: {exchange[1][0]}]\n")
                    print(
                        f"Q [Rating: {exchange[1][1][0]}, Context: {exchange[1][1][1]}, Skepticism: {exchange[1][1][2]}]\n")
                    print(f"{exchange[2]}\n")
                    print(f"{exchange[3]}\n")
                    print(
                        f"A [Rating: {exchange[1][2][0]}, Context: {exchange[1][2][1]}, Skepticism: {exchange[1][2][2]}]\n")
                    for answer in exchange[4]:
                        print(f"{answer[0]}\n")
                        print(f"{answer[1]}\n")
            if len(questions) == 0:
                print(
                    f"BAD TRANSCRIPT ERROR: {html_path} moved to 'No QA' folder")
                # os.system(f"mv {html_path} {no_qa_path}")
                continue

        except:
            print(
                f"BAD TRANSCRIPT ERROR: {html_path} moved to 'Unknown Error' folder")
            # os.system(f"mv {html_path} {error_path}")
        finally:
            if i > 2000:
                break

# reset_transcript_locations()
