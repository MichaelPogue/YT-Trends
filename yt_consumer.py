import pika
import sys
import time
import os
import ssl
import smtplib
from collections import deque
from time import strftime 
from dotenv import load_dotenv
from email.message import EmailMessage

load_dotenv()
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_SENDER_PASSWORD = os.getenv('EMAIL_SENDER_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')

host = 'localhost'
queue = 'yt_streamstatistics'
data_deque = deque(maxlen = 1)
data_warning = 15000

class ytReceive:
    def decode_message(ch, method, properties, body):
        """  """
        print(f"Received: {body.decode()} at {strftime('%H:%M:%S')}")
        data_deque.append(body.decode())
        initial_data = body.decode()
        initial_split = initial_data.split(",")
        data = initial_split[1][:-1]
        name = initial_split[0]

        if ytReceive.character_detection(data, '.') == True:
            remove_period = data.replace('.', '')
            remove_letter = remove_period.replace('K','')
            data_final = int(remove_letter)*100
            # print(f'--------------> {data_final}')
        elif ytReceive.character_detection(data, '.') == False:
            remove_letter = data.replace('K','')
            data_final = int(remove_letter)*1000
            # print(f'--------------> {data_final}')

        if data_final >= data_warning:
            ytReceive.send_message(name, data_final)
        elif data_final < data_warning:
            pass

        ch.basic_ack(delivery_tag = method.delivery_tag)
        time.sleep(1)

    def send_message(name, data_final):
        subject = f"Project YT-TREND Alert: {name} at {data_final}"
        body = f"""
        Automated Alert Message: 

        The game {name} has {data_final} views. 

        This automated alert message was triggered due to a view score higher than: {data_warning}.
        """

        em = EmailMessage()

        em['From'] = EMAIL_SENDER
        em['To'] = EMAIL_RECEIVER
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com',465, context = context) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_SENDER_PASSWORD)
            smtp.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, em.as_string())

    def character_detection(string, chars):
        for char in string:
            if char in chars:
                return True
        return False

    def receive_message(hn: str, qn: str):
        """  """
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host = hn))
        except Exception as e:
            print("ERROR: connection to RabbitMQ server failed.")
            print(f"Verify the server is running on host={hn}.")
            print(f"The error says: {e}")
            sys.exit(1)
        try:
            channel = connection.channel()
            channel.queue_declare(queue = qn, durable = True)
            channel.basic_qos(prefetch_count=1) 
            channel.basic_consume( queue = qn, on_message_callback = ytReceive.decode_message)
            print("Ready for work. To exit press CTRL+C.")
            channel.start_consuming()
        except Exception as e:
            print("ERROR: Something went wrong.")
            print(f"The error says: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nUser interrupted continuous listening process.")
            sys.exit(0)
        finally:
            print("\nClosing connection. Goodbye.\n")
            connection.close()

def main():
    ytr = ytReceive
    ytr.receive_message(host, queue)


"""  """
if __name__ == "__main__":
    main()