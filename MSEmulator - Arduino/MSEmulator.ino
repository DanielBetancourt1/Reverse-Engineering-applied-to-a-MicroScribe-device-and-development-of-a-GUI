
float X;
float Y;
float Z;

const int  RigthP = 2;
const int  LeftP = 3;
int RState = 0;
int LState = 0;

String ReadedRequest;
String readString;
String StrResponse;
byte initPort;
char c;
String temp;
int cont;


const int ledPin =  LED_BUILTIN;// the number of the LED pin

void setup() 
{
  // initialize the button pin as a input:
  pinMode(RigthP, INPUT);
  pinMode(LeftP, INPUT);
  
  pinMode(LED_BUILTIN,OUTPUT); 
  Serial.begin(115600);
  cont = 0;
  randomSeed(analogRead(0));
}

void SingleResponse()
{
  Serial.print(StrResponse);
}

void EchoResponse()
{ 
  Serial.print(ReadedRequest);  
  Serial.print(StrResponse);
}


void Blinkled()
{
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);  
}

void CheckReceived()
{
  if (ReadedRequest.length() >0)
  {
    if (ReadedRequest == "IMMC" || ReadedRequest == "ÅIMMC")   // First Response
    {
      StrResponse = "IMMC";
      SingleResponse();
    }

    if (ReadedRequest == "BEGIN")   // Device ID
    {
      StrResponse = "MSCR";
      SingleResponse();
    }
    
    if (ReadedRequest == "\xc8")    // Product name
    { 
      StrResponse = "MicroScribe3D";
      EchoResponse();
    }

    if (ReadedRequest == "\xc9")    // Product ID
    { 
      StrResponse = "MSCR";
      EchoResponse();
    }

    if (ReadedRequest == "\xCA")    // Model Name
    { 
      StrResponse = "DX";
      EchoResponse();
    }

    if (ReadedRequest == "\xCB")    // Get Serial Number
    { 
      StrResponse = "40937";
      EchoResponse();
    }

    if (ReadedRequest == "\xCC")     // Comment string
    { 
      StrResponse = "Standard+Beta";
      EchoResponse();
    }

    if (ReadedRequest == "\xCD")    // Parameter format
    { 
      StrResponse = "Format DH0.5";
      EchoResponse();
    }

    if (ReadedRequest == "\xCE")    // version
    { 
      StrResponse = "HCI 2.0";
      EchoResponse();
    }

    if (ReadedRequest == "\xc6")    // pulses/ rev values for each encoder.
    { 
      byte initPort[] = {0x03, 0x3F, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
      0x3F, 0xFF, 0x3F, 0xFF, 0x1F, 0xFF, 0x0F, 0xFF, 0x0F, 0xFF, 0x00, 0x00};
      Serial.print(ReadedRequest);
      Serial.write(initPort, sizeof(initPort)); 
    }

    if (ReadedRequest == "\xc0")    // Extra parameters to compute
    { 
      byte initPort[] = {0x24, 0x00, 0x00, 0x3F, 0xF5, 0xFF, 0xF9, 0x3F, 0xE5, 0xC0, 0x02, 0xC0, 
      0x0C, 0x00, 0x00, 0x03, 0xC0, 0x28, 0x10, 0x02, 0x15, 0xFE, 0x6F, 0x01, 0x8F, 0x20, 0x6C, 
      0xFC, 0x92, 0xFF, 0xFD, 0x24, 0x1C, 0x01, 0x40, 0xEB, 0x66};
      Serial.print(ReadedRequest);
      Serial.write(initPort, sizeof(initPort)); 
    }

    if (ReadedRequest == "\xd3")    // Extra Extended Physical Parameters
    { 
      byte initPort[] = {0x02, 0x00, 0x03};
      Serial.print(ReadedRequest);
      Serial.write(initPort, sizeof(initPort)); 
    }

    if (ReadedRequest == "\03")   // Encoder count mode
    { 
      byte initPort[] = {0xCF, 0x83, 0x00, 0x6C, 0x4F, 0x30, 0x5E, 0x35, 0x54, 0x20, 0x02, 0x18,
      0x79, 0x41, 0x60};

      //int Rdm1 = random(1,32000);
      int Rdm1_2 = random(1,384);
      int Rdm2 = random(1,32);
      int Rdm2_2 = random(1,384);
      int Rdm3 = random(1,16);
      int Rdm3_2 = random(1,192);
      int Rdm4 = random(1,8);
      int Rdm4_2 = random(1,96);
      int Rdm5 = random(1,8);
      int Rdm5_2 = random(1,96);

      int Rdm1 = 16;
      String C1_1 = String(Rdm1, HEX);
      char buf[C1_1.length()];
      C1_1.toCharArray(buf, C1_1.length());
      initPort[1] = buf;
      

      
      if (RState == HIGH)
      {
        initPort[2] = 0x01;
      }
      if (LState == HIGH)
      {
        initPort[2] = 0x02;
      }
      if (RState == HIGH && LState == HIGH)
      {
        initPort[2] = 0x03;
      }
      
      Serial.print(ReadedRequest);
      Serial.write(initPort, sizeof(initPort)); 
      
    }

    if (ReadedRequest == "A")
    {
      byte initPort[] = {0xCF, 0x83, 0x00, 0x6C, 0x4F, 0x30, 0x5E, 0x35, 0x54, 0x20, 0x02, 0x18,
      0x79, 0x41, 0x60};

      int Rdm1 = 16000;
      String C1_1 = String(Rdm1, HEX);
      Serial.print(C1_1);
      char buf[C1_1.length()];
      C1_1.toCharArray(buf, C1_1.length());
      initPort[1] = buf;
      //Serial.print(ReadedRequest);
      //Serial.write(initPort, sizeof(initPort)); 
      
    }

   
  }
}

void loop() 
{ 
  RState = digitalRead(RigthP);
  LState = digitalRead(LeftP);
  
  Serial.flush();
  while(!Serial.available()) {} // get stuck if not available
  
  delay(10); //Wait for buffer
  
  for (int i = 0; i = Serial.available(); i++)
  {
    c = Serial.read();  //gets one byte from serial buffer
    ReadedRequest += c;
  }  
  CheckReceived();
  
  //Serial.println(ReadedRequest);
  Serial.flush();
  ReadedRequest ="";
  
} 
