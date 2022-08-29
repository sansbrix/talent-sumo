from typing import List
from .models import *
import io
from django.http import response
import random
import pandas as pd


def create_user_invite_code():
    fixed_digits = 6
    code = random.randrange(111111, 999999, fixed_digits)
    while UserDetail.objects.filter(invite_code=code).count() != 0:
        code = random.randrange(111111, 999999, fixed_digits)
    else:
        return code


class CreateCSVForInputAI(object):
    def __init__(self) -> None:
        self.obj = {
            "Interaction_ID": "",
            "Candidate_ID": "",
            "Test_ID": "",
            "Track": "",
            "Interaction_Mode": "",
            "Description": "",
            "Question_ID": "",
            "Question": "",
            "Answer_Format": "",
            "Base_Scoring": "",
            "Content_Scoring": "",
            "Response": "",
            "Ideal_answer": "",
        }

        self.output = []

    def prepare_object(self, obj: Interaction) -> List[dict]:
        for i in Response.objects.filter(interaction=obj):
            self.obj = {
                "Interaction_ID": obj.id,
                "Candidate_ID": obj.candidate.id,
                "Test_ID": obj.test.id,
                "Track": obj.test.track,
                "Interaction_Mode": obj.test.interaction_mode,
                "Description": obj.test.job_describtion,
                "Question_ID": i.question.id,
                "Question": i.question.question,
                "Answer_Format": i.question.answer_format,
                "Base_Scoring": "yes" if i.question.rated else "no",
                "Content_Scoring": "yes" if i.question.content_rated else "no",
                "Response": i.response,
                "Ideal_answer": i.question.ideal_answer,
            }

            self.output.append(self.obj)

    def create_csv(self):
        intrections = Interaction.objects.all()
        for i in intrections:
            self.prepare_object(i)

        dataFrame = pd.DataFrame(self.output)
        dataFrame.to_csv("./data/output.csv")


def output_csv_ai(file):
    try:
        FILE_PATH = file
        df = pd.read_csv(
            FILE_PATH, delim_whitespace=True, error_bad_lines=False, engine="python"
        )
        first_row = df.columns
        file = pd.read_csv(FILE_PATH, skiprows=1)
        file.columns = file.columns.str.strip()
        file.columns = file.columns.str.replace("_", " ")
        file = file.drop(file.columns[42:], axis=1)
        for item, data in file.iterrows():
            response = dict(data)
            score = Score.objects.create(
                interaction_id=response["Interaction id"],
                manager_quotient_percentile=response["Manager Quotient Percentile"],
                leadership_quotient_percentile=response[
                    "Leadership Quotient Percentile"
                ],
                learner_quotient_percentile=response["Learner Quotient percentile"],
                people_quotient=response["People Quotient"],
                resume_score=response["Resume Score"],
                video_estimated_gesture_score=response["Estimated Gesture score"],
                interaction_percentile=response["Interaction percentile"],
                question_id=response["Question No."],
            )
            audio = AudioScore.objects.create(
                score=score,
                audio_sales_quotient=response["Sales Quotient"],
                audio_manager_quotient=response["Manager Quotient"],
                audio_leadership_quotient=response["Leadership Quotient"],
                audio_learner_quotient=response["Learner Quotient"],
                audio_sales_quotient_percentile=response["Sales Quotient Percentile"],
                audio_people_qutient_percentile=response["People Quotient Percentile"],
                audio_pace=response["Pace"],
                audio_power_word_density=response["Power word density"],
                audio_word_cloud=response["Word Cloud"],
                audio_volume=response["Volume"],
                audio_pitch=response["Pitch"],
                audio_aggregate_content_score=response["Aggregate content score"],
                audio_raw_interaction_score=response["Raw interaction score"],
                audio_interaction_score=response["Interaction score"],
                audio_energy=response["Energy"],
            )
            AudioScorePerQuestion.objects.create(
                audio_score=audio,
                grammer_score=response["Grammer score"],
                audio_transcript=response["Transcript"],
                audio_confidence=response["Confidence"],
                audio_fluency=response["Fluency"],
                audio_content_score=response["Content score"],
                audio_per_question_content_score=response["per question content score"],
                audio_silence_number=response["silence number"],
                audio_silence_length=response["silence length"],
                audio_filler_words_score=response["filler words score"],
                audio_sentiment_score=response["sentiment score"],
            )
            TextScorePerQuestion.objects.create(
                score=score,
                question_grammer_score=response["Grammer Score Per Question"],
            )
            ScorePerQuestion.objects.create(
                score=score,
                mcq_value=response["MCQ Value"],
                video_likeability=response["Likeability"],
                video_charm=response["Charm"],
            )
        return True
    except:
        return False
