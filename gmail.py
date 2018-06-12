import imaplib
import smtplib
import email
from PIL import Image
from io import BytesIO
from time import sleep

def colorize(path):
	!python !python image_colorization.py --mode custom --filename path
	image = Image.open(logs/image_pred/pred0.png)
    return image

def PIL_to_bytes(image):
    with BytesIO() as output:
        with image.copy() as img:
            img.save(output, 'jpeg')
        return output.getvalue()

username = 'algoelmer1@gmail.com'
password = 'camion123'

mail = imaplib.IMAP4_SSL('imap.gmail.com')
mail.login(username, password)

while True:
    try:
        mail.select(readonly=False)
    except:
        print('Reconnexion')
        mail.close()
        mail.logout()
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(username, password)
        mail.select(readonly=False)
    
    _, results = mail.search(None, 'UnSeen')
    uids = results[0].decode('utf8').split()
    
    if len(uids) == 0:
        sleep(5)
        continue
    
    for uid in uids:
        _, contenu = mail.fetch(uid, "(RFC822)")
        msg = email.message_from_string(contenu[0][1].decode('utf8'))
        
        payload = msg.get_payload()
        pieces_jointes = list()
        names = list()
        
        for i in range(len(payload)):
            piece_jointe = payload[i]
            piece_jointe_type = piece_jointe.get_content_type()
            try:
                piece_jointe_type = piece_jointe_type.split('/')[0]
            except:
                continue
            if piece_jointe_type == 'image':
                names.append(piece_jointe.get_filename())
                pieces_jointes.append(piece_jointe.get_payload(decode=True))
        
        if len(pieces_jointes) == 0:
            continue
        
        sender = email.utils.parseaddr(msg['From'])[1]
        
        ans = email.message.EmailMessage()
        ans.set_content('Vos images coloriées sont en pièces jointes.')
        subject = msg['Subject']
        if subject != '':
            ans['Subject'] = 'Re: ' + subject
        else:
            ans['Subject'] = 'ELMER-1 : Vos images'
        ans['From'] = 'ELMER-1 <' + username + '>'
        ans['To'] = sender
        
        invalid = 0
        
        for i, piece_jointe in enumerate(pieces_jointes):
            try:
                image = Image.open(BytesIO(piece_jointe))
            except:
                invalid += 1
                continue
            image = colorize(image)
            ans.add_attachment(PIL_to_bytes(image),
                               maintype='image', subtype='jpeg',
                               filename=str(i) + '.jpeg')
        
        if len(pieces_jointes) - invalid == 0:
            continue
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username,password)
        print('Sending message to :', sender)
        server.send_message(ans)
        print('Message sent\n')
        server.quit()