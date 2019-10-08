import paho.mqtt.client as mqtt
Topic = "zgateway0001"
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe( Topic )

def on_message(client, userdata, msg):
    print("topic: "+msg.topic+" Msg: "+str(msg.payload))
    #print( client)
    print("Enter Msg")

client = mqtt.Client(client_id="mac_id1234567891")
client.username_pw_set("admin", "q1w2e3r4")
client.on_connect = on_connect
client.on_message = on_message

HOST = "47.94.155.129"

client.connect(HOST, 61613, 60)
#client.loop_forever()
#user = input("Enter Your Name:")
#client.user_data_set(user)
client.loop_start()

while True:
    Msg = input()
    if Msg:
        client.publish(Topic, Msg)