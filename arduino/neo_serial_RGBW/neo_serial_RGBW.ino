
#include<Adafruit_NeoPixel.h>

#define LED 5 // This is a 5v output pin on the ItsyBitsy
#define ANALOG 0
#define NUM_PIXLES 1 // How many NeoPixels in our string of pixels

int pulsePin = 0;
volatile int BPM;
volatile int Signal;
volatile int IBI = 600;
volatile boolean Pulse = false;
volatile boolean QS = false;
volatile int rate[10];                    // array to hold last ten IBI values
volatile unsigned long sampleCounter = 0;          // used to determine pulse timing
volatile unsigned long lastBeatTime = 0;           // used to find IBI
volatile int P =512;                      // used to find peak in pulse wave, seeded
volatile int T = 512;                     // used to find trough in pulse wave, seeded
volatile int thresh = 530;                // used to find instant moment of heart beat, seeded
volatile int amp = 0;                   // used to hold amplitude of pulse waveform, seeded
volatile boolean firstBeat = true;        // used to seed rate array so we startup with reasonable BPM
volatile boolean secondBeat = false;      // used to seed rate array so we startup with reasonable BPM

Adafruit_NeoPixel pixels = Adafruit_NeoPixel(NUM_PIXLES, LED, NEO_GRBW);

void setup() {
  
  pixels.begin();
  pixels.setBrightness(100);

  Serial.begin(9600);
  Serial1.begin(9600); // TX/RX pins on the ItsyBitsy

  interruptSetup();
}

void loop() {
  // We got a message from the Pi
  // Message should be color and brightness information
  if(Serial1.available() >= 8) {
    uint32_t color = buildColor(Serial1.readString());
    for(int i = 0; i < pixels.numPixels(); i++) {
      pixels.setPixelColor(i, color);
    }
    pixels.show(); // Update neopixel
  } else if(Serial.available() >= 8) { // Debug access via USB
  	uint32_t color = buildColor(Serial.readString());
    for(int i = 0; i < pixels.numPixels(); i++) {
      pixels.setPixelColor(i, color);
    }
    pixels.show(); // Update neopixel
  }
  // Give Pi data
  if(QS == true) {
    Serial1.println(BPM);
    Serial.println(BPM);
    QS = false;
  }
}

/**
 * Create the value for the color to display from the color string given to us
 * @param color_str String holding a color value in form RRGGBB (all hex values)
 * @return Color value for neopixels
 */
uint32_t buildColor(String color_str) {
	color_str = color_str.substring(0, 6); // Cut out alpha bits
    uint8_t red = strtoul(color_str.substring(0, 2).c_str(), 2, 16);
    uint8_t green = strtoul(color_str.substring(2, 4).c_str(), 2, 16);
    uint8_t blue = strtoul(color_str.substring(4).c_str(), 2, 16);
    uint8_t white = 0;
    if(red == green && green == blue) {
    	white = red;
    	red = 0;
    	green = 0;
    	blue = 0;
    }
    uint32_t color = pixels.Color(red, green, blue, white);
    return color;
}

/**
 * Set up interrupt for reading heart rate sensor
 * DON'T TOUCH
 */
void interruptSetup() {
  TCCR1A = 0x00;
  TCCR1B = 0x0C;
  OCR1A = 0x3E;
  TIMSK1 = 0x02;
  sei();
}

/**
 * Interrupt for heart rate sensor
 * NO TOUCHY
 */
ISR(TIMER1_COMPA_vect){                         // triggered when Timer2 counts to 124
  cli();                                      // disable interrupts while we do this
  Signal = analogRead(pulsePin);              // read the Pulse Sensor
  sampleCounter += 2;                         // keep track of the time in mS with this variable
  int N = sampleCounter - lastBeatTime;       // monitor the time since the last beat to avoid noise

    //  find the peak and trough of the pulse wave
  if(Signal < thresh && N > (IBI/5)*3){       // avoid dichrotic noise by waiting 3/5 of last IBI
    if (Signal < T){                        // T is the trough
      T = Signal;                         // keep track of lowest point in pulse wave
    }
  }

  if(Signal > thresh && Signal > P){          // thresh condition helps avoid noise
    P = Signal;                             // P is the peak
  }                                        // keep track of highest point in pulse wave

  //  NOW IT'S TIME TO LOOK FOR THE HEART BEAT
  // signal surges up in value every time there is a pulse
  if (N > 250){                                   // avoid high frequency noise
    if ( (Signal > thresh) && (Pulse == false) && (N > (IBI/5)*3) ){
      Pulse = true;                               // set the Pulse flag when we think there is a pulse
      IBI = sampleCounter - lastBeatTime;         // measure time between beats in mS
      lastBeatTime = sampleCounter;               // keep track of time for next pulse

      if(secondBeat){                        // if this is the second beat, if secondBeat == TRUE
        secondBeat = false;                  // clear secondBeat flag
        for(int i=0; i<=9; i++){             // seed the running total to get a realisitic BPM at startup
          rate[i] = IBI;
        }
      }

      if(firstBeat){                         // if it's the first time we found a beat, if firstBeat == TRUE
        firstBeat = false;                   // clear firstBeat flag
        secondBeat = true;                   // set the second beat flag
        sei();                               // enable interrupts again
        return;                              // IBI value is unreliable so discard it
      }


      // keep a running total of the last 10 IBI values
      word runningTotal = 0;                  // clear the runningTotal variable

      for(int i=0; i<=8; i++){                // shift data in the rate array
        rate[i] = rate[i+1];                  // and drop the oldest IBI value
        runningTotal += rate[i];              // add up the 9 oldest IBI values
      }

      rate[9] = IBI;                          // add the latest IBI to the rate array
      runningTotal += rate[9];                // add the latest IBI to runningTotal
      runningTotal /= 10;                     // average the last 10 IBI values
      BPM = 60000/runningTotal;               // how many beats can fit into a minute? that's BPM!
      QS = true;                              // set Quantified Self flag
      // QS FLAG IS NOT CLEARED INSIDE THIS ISR
    }
  }

  if (Signal < thresh && Pulse == true){   // when the values are going down, the beat is over
    Pulse = false;                         // reset the Pulse flag so we can do it again
    amp = P - T;                           // get amplitude of the pulse wave
    thresh = amp/2 + T;                    // set thresh at 50% of the amplitude
    P = thresh;                            // reset these for next time
    T = thresh;
  }

  if (N > 2500){                           // if 2.5 seconds go by without a beat
    thresh = 530;                          // set thresh default
    P = 512;                               // set P default
    T = 512;                               // set T default
    lastBeatTime = sampleCounter;          // bring the lastBeatTime up to date
    firstBeat = true;                      // set these to avoid noise
    secondBeat = false;                    // when we get the heartbeat back
  }

  sei();                                   // enable interrupts when youre done!
}// end isr
