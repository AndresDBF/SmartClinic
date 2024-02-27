import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_verification_email(email):
    sender_email = "tu_email@gmail.com"
    sender_password = "tu_contraseña"
    
    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Verificación de Cuenta"
    
    body = "Por favor, haz clic en el siguiente enlace para verificar tu cuenta: https://tudominio.com/verify"
    msg.attach(MIMEText(body, 'plain'))

    # Iniciar la conexión SMTP
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text) 