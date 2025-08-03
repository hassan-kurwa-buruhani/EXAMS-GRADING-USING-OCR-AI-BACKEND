import pytesseract
from pdf2image import convert_from_path
from .models import Question
import re


def extract_questions_from_pdf(exam):
    print("PDF path:", exam.exam_paper.path)
    pages = convert_from_path(exam.exam_paper.path)
    print("Total pages converted:", len(pages))

    current_base_number = 1
    suffix_counter = {}

    for page in pages:
        text = pytesseract.image_to_string(page)
        print("OCR TEXT:", text[:1000])
        questions = split_questions(text)
        print("Questions Found:", questions)

        for q_title, q_body in questions:
            if not q_body.strip():
                continue

            question_number = extract_question_number(q_title.strip(), current_base_number, suffix_counter)

            Question.objects.create(
                exam=exam,
                question_number=question_number,
                question_text=q_body.strip()
            )

            if suffix_is_plain_number(question_number):
                current_base_number += 1


def split_questions(text):
    # This pattern ensures we capture titles like "Question One", "Question One a", etc. on their own line.
    pattern = re.compile(r'(?=^Question\s+[A-Z][a-z]+(?:\s+[a-z])?$)', re.IGNORECASE | re.MULTILINE)
    blocks = pattern.split(text)
    questions = []

    for block in blocks:
        lines = block.strip().split('\n')
        if not lines or not lines[0].strip().lower().startswith('question'):
            continue
        question_title = lines[0].strip()
        question_body = '\n'.join(lines[1:]).strip()
        questions.append((question_title, question_body))

    return questions


def extract_question_number(question_title, current_base, suffix_counter):
    match = re.search(r'Question\s+([A-Z][a-z]+)(?:\s+([a-z]))?', question_title, re.IGNORECASE)
    if not match:
        return str(current_base)

    word_number = match.group(1).lower()
    suffix = match.group(2)

    word_to_number = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    base_number = word_to_number.get(word_number, current_base)

    if suffix:
        return f"{base_number}{suffix}"
    else:
        return str(base_number)


def suffix_is_plain_number(question_number):
    return question_number.isdigit()
