import math
import os

import pandas as pd
from django.core.management.base import BaseCommand, CommandError

from backend.models import BusinessInvitationCode


class Command(BaseCommand):
    help = 'This command will sync all the business invitation codes'

    def is_nan(self, d):
        try:
            return str(float(d)).lower() == 'nan'
        except: return False
        
    def handle(self, *args, **options):
        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', '..', '..', 'business_code', 'Business Invitation Code.csv'))
        data_frame = pd.read_csv(path, error_bad_lines=False, engine="python")
        
        objects = []
        for _, data in data_frame.iterrows():
            data = dict(data)
            ob = BusinessInvitationCode(
                invitation_code = data["Invitation Code"],
                number_of_interaction = data["Number of Interactions"],
                number_of_responses_per_test = data["Number of responses per Test "],
                employee = True if data["Employee "] == "Y" else False,  
                expiry_date = None if self.is_nan(data["Expiry Date"]) else data["Expiry Date"],  
                external_bot_user = True if data["External Bot user "] == "Y" else False,  
                video_creator = True if data["Video Creator "] == "Y" else False,  
                team_user = True if data["Team user "] == "Y" else False,  
                one_time_user = True if data["One time user"] == "Y" else False,  
                user_type = data["User Type"],
            )
            objects.append(ob)
            
        BusinessInvitationCode.objects.bulk_create(objects)
        print("Business Invitation Codes has been updated.")