from typing import List
from .models import Interaction, Response, UserDetail
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
            "Ideal_answer": ""
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
                "Ideal_answer": i.question.ideal_answer
            }
            
            self.output.append(self.obj)
        
    def create_csv(self):
        intrections = Interaction.objects.all() 
        for i in intrections:
            self.prepare_object(i)
            
        dataFrame = pd.DataFrame(self.output)
        dataFrame.to_csv("./data/output.csv")
        
            

def output_csv_ai(file): 
    print(file)
    return True