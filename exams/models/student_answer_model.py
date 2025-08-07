from django.db import models
from users.models import User, Roles
from .course_exam_model import Exam
from .question_model import Question
from django.core.validators import FileExtensionValidator
from google.cloud import storage
from django.conf import settings
import re
from datetime import timedelta
import requests
from dotenv import load_dotenv
import os

class StudentAnswerDocument(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='answers')
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': Roles.STUDENT})
    invigilator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invigilated_answers', limit_choices_to={'role': Roles.INVIGILATOR})
    
    pdf = models.FileField(
        upload_to='student_answers/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])]
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    ocr_extracted = models.BooleanField(default=False)  # mark if OCR was already done
    notes = models.TextField(blank=True, null=True)  # Optional

    class Meta:
        unique_together = ('exam', 'student')

    
    def upload_to_gcs(self):
        if not self.pdf:
            return "No PDF to upload."

        blob_name = f"student_answers/{self.exam.id}/{self.student.id}.pdf"
        client = storage.Client()
        bucket = client.bucket(settings.GCS_BUCKET_NAME)
        blob = bucket.blob(blob_name)

        # Upload the file to GCS
        blob.upload_from_file(self.pdf, content_type='application/pdf')

        # Generate a signed URL valid for 1 hour
        url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=10),
            method="GET"
        )

        return f"Signed URL: {url}"

    def extract_text_from_pdf(self):
        from google.cloud import vision_v1
        from google.cloud.vision_v1 import types
        import json

        client = vision_v1.ImageAnnotatorClient()

        gcs_source_uri = f"gs://{settings.GCS_BUCKET_NAME}/student_answers/{self.exam.id}/{self.student.id}.pdf"

        mime_type = "application/pdf"
        batch_size = 1

        feature = vision_v1.Feature(type_=vision_v1.Feature.Type.DOCUMENT_TEXT_DETECTION)

        gcs_source = vision_v1.GcsSource(uri=gcs_source_uri)
        input_config = vision_v1.InputConfig(gcs_source=gcs_source, mime_type=mime_type)

        # Output will be saved to GCS too (optional, not needed now)
        # gcs_destination_uri = "gs://your-bucket-name/path/to/output/"
        # output_config = vision_v1.OutputConfig(gcs_destination=gcs_destination, batch_size=batch_size)

        request = vision_v1.AnnotateFileRequest(
            features=[feature],
            input_config=input_config,
        )

        response = client.batch_annotate_files(requests=[request])

        result_text = ""

        for resp in response.responses:
            if resp.error.message:
                return f"Failed: {resp.error.message}"

            for page_response in resp.responses:
                annotation = page_response.full_text_annotation
                result_text += annotation.text + "\n"

        self.notes = result_text
        self.ocr_extracted = True
        self.save()
        return "Success"



    @staticmethod
    def normalize_question_number(title):
        """
        Converts titles like 'Question One a' to '1a', etc.
        """
        match = re.search(r'Question\s+([A-Z][a-z]+)(?:\s+([a-z]))?', title, re.IGNORECASE)
        if not match:
            return None

        word_to_number = {
            "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
        }

        word = match.group(1).lower()
        suffix = match.group(2) or ""

        base = word_to_number.get(word)
        if not base:
            return None

        return f"{base}{suffix}".lower()


    def extract_answers_from_notes(self):
        if not self.notes:
            return "❌ No OCR notes found to extract answers."

        text = self.notes.strip()

        # More robust pattern to split answers between question titles
        pattern = re.compile(
            r'(?i)^Question\s+[A-Z][a-z]+(?:\s+[a-z])?.*$',  # matches each question title line
            re.MULTILINE
        )

        # Find all question titles with their start positions
        matches = list(pattern.finditer(text))
        blocks = []

        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            block = text[start:end].strip()
            blocks.append(block)

        exam_questions = {q.question_number.lower(): q for q in Question.objects.filter(exam=self.exam)}
        seen_keys = set()
        saved = 0

        for block in blocks:
            lines = block.strip().splitlines()
            if not lines:
                continue

            title = lines[0].strip()
            body = "\n".join(lines[1:]).strip()

            key = self.normalize_question_number(title)
            if not key:
                continue

            seen_keys.add(key)
            question = exam_questions.get(key)
            if not question:
                continue

            StudentAnswer.objects.update_or_create(
                exam=self.exam,
                student=self.student,
                question=question,
                defaults={
                    "answer_text": body if body else None,
                    "graded": False
                }
            )
            saved += 1

        # Handle missing questions
        missing_questions = set(exam_questions.keys()) - seen_keys
        for key in missing_questions:
            question = exam_questions[key]
            StudentAnswer.objects.update_or_create(
                exam=self.exam,
                student=self.student,
                question=question,
                defaults={
                    "answer_text": None,
                    "graded": False
                }
            )

        return f"✅ {saved} answers extracted from notes. 🕳️ {len(missing_questions)} missing answers were also recorded as empty."


    def __str__(self):
        return f"Answer by {self.student.username} for {self.exam.title}"







# model for student's single answer
class StudentAnswer(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': Roles.STUDENT})
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    
    answer_text = models.TextField(null=True, blank=True)
    marks_awarded = models.FloatField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    graded = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('exam', 'student', 'question')


    ...
    
    def grade_with_ai(self):
        if not self.answer_text:
            self.remarks = "No answer provided."
            self.marks_awarded = 0
            self.graded = True
            self.save()
            return
        
        prompt = f"""
You are an expert academic grader.

Here is the exam question:
---
{self.question.question_text}
---

Maximum marks: {self.question.marks}

Here is the student's answer:
---
{self.answer_text}
---

Your task:
1. Grade the answer fairly out of {self.question.marks}.
2. Provide short, constructive feedback.
3. Return a JSON like this: 
   {{
     "score": <number>,
     "remarks": "<string>"
   }}
Only return valid JSON. Do not include any explanation.
"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            import json
            raw_reply = response.choices[0].message.content.strip()
            result = json.loads(raw_reply)

            self.marks_awarded = float(result["score"])
            self.remarks = result["remarks"]
            self.graded = True
            self.save()

            return f"✅ Graded with {result['score']} marks."
        except Exception as e:
            self.remarks = f"❌ Error grading with AI: {str(e)}"
            self.marks_awarded = None
            self.graded = False
            self.save()
            return self.remarks


    def __str__(self):
        return f"Answer by {self.student.username} to Q{self.question.question_number}"

