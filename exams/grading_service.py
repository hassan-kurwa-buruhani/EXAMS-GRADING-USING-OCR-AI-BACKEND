# examsapp/services/grading_service.py

import json
import re
from decouple import config
from openai import OpenAI
from exams.models import StudentAnswer, StudentAnswerDocument

client = OpenAI(api_key=config("OPENAI_API_KEY"))

def grade_answer(question_text, max_marks, student_answer):
    """
    Grade a single student's answer using OpenAI and return marks + remarks.
    """
    if not student_answer or not student_answer.strip():
        return 0.0, "No answer provided."

    prompt = f"""
You are an exam grader. Grade the following student answer strictly according to the question and maximum marks.
Return ONLY valid JSON, nothing else, no markdown, no explanations.

Question: {question_text}
Max Marks: {max_marks}

Student Answer: {student_answer}

JSON format example:
{{
  "marks_awarded": 4.5,
  "remarks": "Good explanation, but missing key point about X."
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a strict but fair examiner. Only respond with JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', content, re.DOTALL)

        if not match:
            return 0.0, f"Grading failed: No JSON found in response: {content}"

        data = json.loads(match.group(0))
        marks_awarded = float(data.get("marks_awarded", 0.0))
        remarks = str(data.get("remarks", "")).strip()

        return marks_awarded, remarks

    except Exception as e:
        return 0.0, f"Grading failed: {str(e)}"


def grade_student_answers(student_id, exam_id):
    """
    Grade all answers for a given student & exam, update total marks in StudentAnswerDocument.
    """
    answers = StudentAnswer.objects.filter(student_id=student_id, exam_id=exam_id)

    total_marks = 0.0
    for ans in answers:
        if ans.graded:
            # Still count existing marks in total
            total_marks += ans.marks_awarded or 0.0
            continue  

        marks, remarks = grade_answer(ans.question.question_text, ans.question.marks, ans.answer_text)
        ans.marks_awarded = marks
        ans.remarks = remarks
        ans.graded = True
        ans.save()

        total_marks += marks

    # Update total marks in StudentAnswerDocument
    doc, created = StudentAnswerDocument.objects.get_or_create(
        student_id=student_id,
        exam_id=exam_id,
        defaults={"total_marks": total_marks}
    )
    if not created:
        doc.total_marks = total_marks
        doc.save()

    return total_marks
