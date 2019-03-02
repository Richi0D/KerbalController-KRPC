//analog pins
const byte pRX = A5;       //rotation x-axis
const byte pRY = A4;       //rotation y-axis
const byte pRZ = A6;       //rotation z-axis
pinMode(pRX, INPUT);
pinMode(pRY, INPUT);
pinMode(pRZ, INPUT);

//define the structure of a control packet
struct ControlPacket {  //the following controls can be sent to python (defined by the plugin)
  int Pitch;            //  0 ; 0 -> 1023
  int Roll;             //  1 ; 0 -> 1023
  int Yaw;              //  2 ; 0 -> 1023
};

//Create an instance of a control packet
ControlPacket CPacket;
// length of the structure
int len_struct = sizeof(CPacket);

void setup() {
  Serial.begin(115200);   //Serial connection
}

void loop() {
      CPacket.Yaw = analogRead(pRX);
      CPacket.Pitch = analogRead(pRY);
      CPacket.Roll = analogRead(pRZ)
      sendControlpacket();  //send control packet
}
// send the structure from CPacket
void sendControlpacket() {
  Serial.write('<');                                //startmarker
  Serial.write((uint8_t *)&CPacket, len_struct);    //send struct
  Serial.write('>');                                //endMarker
  return;
}
