import os
import smtplib
from email.message import EmailMessage
import imghdr

class Connect:
    def send_email_pic(self, r_email, img_loc, img_name):
        smtp_port = 587
        smtp_server = "smtp.gmail.com"
        my_email = os.getenv('my_email')
        print(my_email)
        password = os.getenv('email_password')
        receiver_email = r_email
        
        msg = EmailMessage()
        msg['Subject'] = 'T-Digital-Sketch'
        msg['From'] = my_email
        msg['To'] = receiver_email
        msg.set_content('Your sketched picture\nThank you for choosing T-Digital-Sketch')
        try:
            print(img_name)
            with open(img_loc, 'rb') as img_file:
                file_data = img_file.read()
                file_name = img_name
                print(f'FileName: {img_file.name}')
                file_type = imghdr.what(img_file.name)

            msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)
            s = smtplib.SMTP(smtp_server, smtp_port)
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(my_email, password)
            s.sendmail(my_email, receiver_email, msg.as_string())

            
            # with smtplib.SMTP('smtp.gmail.com') as smtp:
            #     print(smtp.user)
            #     smtp.login(user=my_email, password=password)
            #     smtp.send_message(msg)


        except:
            return False

        else:
            pass
