import random
import time
from paho.mqtt import client as mqtt_client

from PIL import Image
import pytesseract
import base64
import io

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

broker = '10.64.126.227'
port = 1883
responseTopic = "node/ocr/<uuid>/response"
requestTopic = "edge/ocr/+/request"

print()

client_id = f'ComputingServer-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        topic_fragments = msg.topic.split('/')
        uuid = topic_fragments[2]
        global responseTopic 
        responseTopic = f"node/ocr/{uuid}/response"

        ##############################

        base64_string = msg.payload.decode()


        # Decode the Base64 string
        decoded_bytes = base64.b64decode(base64_string)

        # Create a BytesIO stream from the decoded bytes
        image_stream = io.BytesIO(decoded_bytes)

        # Open the image using the Python Imaging Library (PIL)
        image = Image.open(image_stream)

        # Display or save the image as needed
        image.show()  # This displays the image
        # image.save("OCR_tests/output.png")  # This saves the image to a file


        # img = Image.open('C:/Users/Konrad/Desktop/OCR_tests/tekst.jpg')
        # img.load()
        recognized_text = pytesseract.image_to_string(image, lang="pol") 
        print(recognized_text)

        ##############################



        # print(f"Received: {msg.payload.decode()}")

        publish(client, recognized_text)
    



    client.subscribe(requestTopic)
    client.on_message = on_message

def publish(client, recognized_text):
    msg = recognized_text
    result = client.publish(responseTopic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{msg}` to topic `{responseTopic}`")
    else:
        print(f"Failed to send message to topic {responseTopic}")

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

    #publish(client)
    #client.loop_stop()


if __name__ == '__main__':
    run()