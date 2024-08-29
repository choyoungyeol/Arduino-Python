#include <dht.h>                  //dht.zip 라이브러리를 설치
#define DHT22_PIN 7             //D7 연결

dht DHT;

float temperature ;
float humidity ;

void setup()
{
  Serial.begin(9600);             //시리얼모니터 출력
  delay(300);
}

void loop()
{
  float chk = DHT.read22(DHT22_PIN); 

  temperature = DHT.temperature;         //온도
  humidity = DHT.humidity;                //상대습도
  
  Serial.print(temperature, 1);              //소숫점 1자리만 출력
  Serial.println(" C");                       //다음 단락

  Serial.print(humidity, 1);                  //소숫점 1자리만 출력
  Serial.println(" %");                       //다음 단락

  delay(1000);                              //1초마다 반복 실행
}
