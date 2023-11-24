from picamera.array import PiRGBArray
from picamera import PiCamera
import random
import time
from paho.mqtt import client as mqtt_client
import cv2
import base64
from io import BytesIO
 
client_id = f'raspberry-{random.randint(0, 1000)}'
 
camera = PiCamera()
camera.resolution = (640,400)
rawCapture = PiRGBArray(camera)
 
broker = '10.64.126.227'
port = 1883
requestTopic = f"edge/ocr/{client_id}/request"
responseTopic = f"node/ocr/{client_id}/response"
print(responseTopic)

def capture_convert_display_base64():
    # Inicjalizacja kamery
    camera = PiCamera()
 
    # Przechwyć obraz
    stream = BytesIO()
    camera.capture(stream, format='jpeg')
    stream.seek(0)
 
    # Wczytaj przechwycony obraz
    image = cv2.imdecode(np.frombuffer(stream.getvalue(), dtype=np.uint8), 1)
 
    # Konwersja obrazu na odcienie szarości
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
 
    # Wyświetl obraz
    cv2.imshow("Grayscale Image", gray_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
 
    # Kodowanie obrazu do base64
    _, buffer = cv2.imencode('.png', gray_image)
    base64_image = base64.b64encode(buffer).decode('utf-8')
 
    return base64_image

def frame_to_base64(frame):
    return base64.b64encode(frame)
 
def connect_mqtt():
    def on_connect(
        client, userdata, flags, rc):
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
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
 
    client.subscribe(responseTopic)
    client.on_message = on_message
 
def publish(client):
    file_path = '/home/konrad/Desktop/image1.png'
    #image = camera.capture()
    #gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #img_encoded = cv2.imencode('.png', gray_frame)
    #base64_image = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
 

    #with open(file_path,'rb') as image_file:
        #encoded_string = base64.b64encode(image_file.read())
    camera.capture(rawCapture, format="rgb")
    image = rawCapture.array
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, img_encoded = cv2.imencode('.png', gray)
    base64_image = base64.b64encode(img_encoded.tobytes()).decode('utf-8')

    
    msg = base64_image #capture_convert_display_base64()
    client.publish(requestTopic, msg)
    rawCapture.truncate(0)
    
    
 
 
def run():
    client = connect_mqtt()
    subscribe(client)
    while True:
        time.sleep(5)
        publish(client)
        client.loop()
 
 
if __name__ == '__main__':
    run()
