import requests
from bs4 import BeautifulSoup
import redis
from secrets import password
import datetime

class Scraper:
    def __init__(self, keywords):
        #Get the source from  website
        self.markup = requests.get('https://news.ycombinator.com/').text
        self.keywords = keywords

    def parse(self):
        soup = BeautifulSoup(self.markup, 'html.parser')
        links = soup.findAll("a", {"class": "storylink"})
        self.saved_links = []
        for link in links:
            for keyword in self.keywords:
                if keyword in link.text:
                    self.saved_links.append(link)

    # Need to get the redis server running 
    def store(self):
        r = redis.Redis(host='localhost', port=6379, db=0)  #port = 6379 is the port number by default
        for link in self.saved_links:
            r.set(link.text, str(link))

    def email(self):
        r = redis.Redis(host='localhost', port=6379, db=0)
        links = [str(r.get(k)) for k in r.keys()]
        
        # email
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        fromEmail = 'yourEMAIL@gmail.com' #email to send from
        toEmail = 'yourEmail@gmail.com' #email to send to 

        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Link"
        msg["From"] = fromEmail
        msg["To"] = toEmail

        html = """
            <h4> %s links you might find interesting today:</h4>
            
            %s
        """ % (len(links), '<br/><br/>'.join(links))

        mime = MIMEText(html, 'html')

        msg.attach(mime)

        try:
            mail = smtplib.SMTP('smtp.gmail.com', 587)
            mail.ehlo()
            mail.starttls()
            mail.login(fromEmail, password)
            mail.sendmail(fromEmail, toEmail, msg.as_string())
            mail.quit()
            print('Email sent!')
        except Exception as e:
            print('Something went wrong... %s' % e)

        # flush redis
        r.flushdb()

#Insert your keywords here
s = Scraper(['yourkeyword', 'yourkeyword', 'yourkeyword'])
s.parse()
s.store()
if datetime.datetime.now().hour == 16:
    s.email()
