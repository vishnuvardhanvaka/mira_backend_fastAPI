import smtplib
from email.message import EmailMessage
from email.header import Header
import ssl
from dotenv import load_dotenv
import os
import random
from database import Database


class Mail:
    def __init__(self,count=1):
        load_dotenv()
        self.sender=os.environ.get(f'SENDER_MAIL{count}')
        self.password=os.environ.get(f'SENDER_MAIL_PASSWORD{count}') #check "Allow less secure apps"  issue - https://www.youtube.com/watch?v=6ANKk9NQ3GI
        # print(self.sender,self.password)
        self.em=EmailMessage()
        self.em['From'] = '{} <{}>'.format('Mira', self.sender)

    def sendOTP(self,username,receiver):
        otp=random.randint(100000,999999)
        subject='Welcome to Mira - your trusted companion in journey of parenthood! 🎉'
        # wishmsg=f'''Welcome {username}'''
        welmsg=f'''Welcome to Mira {username}! 👋 

 🎊 We're thrilled 💫 to have you on board, and we appreciate you choosing Mira to support you in taking care of your newborn.
'''     
        about=f'''Mira is designed to make your parenting experience easier and more enjoyable. 

        🌟 Here's what you can expect: ✨

🤖 Chat Bot Assistance: Our intelligent chat bot is here to answer any questions you might have about your newborn. From feeding schedules to sleep patterns, feel free to ask anything!

🛍️ Product Recommendations: Discover the best products for your little one with our personalized recommendation system. We'll help you find the perfect items for your baby's needs.

📚 Knowledge Modules: Explore a wealth of knowledge through our informative modules covering various topics related to baby care. Stay informed and make confident decisions for your baby's well-being.

Thank you for choosing Mira! We're here to support you every step of the way. If you have any questions or need assistance, don't hesitate to reach out to our support team at [miracarez@gmail.com]. 💌

Wishing you and your little one all the joy and happiness on this incredible journey of parenthood. 🍼

Best regards,

The Mira Team _V
        '''
        
        body=f'''
{welmsg}

🔑 YOUR OTP is : {otp} 

{about}

'''
        
        self.em['To']=receiver
        self.em['Subject']=subject
        self.em.set_content(body)

        context=ssl.create_default_context()
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com',587,context=context) as smtp:
                smtp.login(self.sender,self.password)
                smtp.sendmail(self.sender,receiver,self.em.as_string())
            return otp,'ok'
        except Exception as e:
            return None,str(e)
    
    def sendPassword(self,username,receiver,password):
        
        subject='Password 🔐'
        wishmsg=f'''Hello {username}!'''
        welmsg='''Hope you are doing Great !'''     
        
        body=f'''
{wishmsg}

{welmsg}

Here is your Account password: "{password}"'''
        
        self.em['To']=receiver
        self.em['Subject']=subject
        self.em.set_content(body)
        
        context=ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
            smtp.login(self.sender,self.password)
            smtp.sendmail(self.sender,receiver,self.em.as_string())
            
        return 1
















