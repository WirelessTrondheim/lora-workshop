<head>
</head>

<style>
    body {
        margin: auto;
        width: 70%;
        padding: 10px;
        font: sans-serif;
    }
    p {
        margin: 0 0 20px;
    }
</style>


# Hands-on LoRa workshop

**Date:** Monday, 23. May 2016 12-14, at [DIGS](http://www.digs.no/)

**Organizers:** embedded.trd, Wireless Trondheim and [CTT (Carbon Track and Trace)](http://www.carbontrackandtrace.com/)

The purpose of this 2-hour workshop is to get hands-on experience
with using the LoRa network in Trondheim. LoRa is a new
radio standard for connecting things to the internet. Its
features are long range and low battery. So it is useful to
power the internet of things.

You need to bring your laptop.

We bring the hardware:

* 6x [Nucleo-L152RE](https://developer.mbed.org/platforms/ST-Nucleo-L152RE/)
* 6x [Semtech SX1276MB1xAS](https://developer.mbed.org/components/SX1276MB1xAS/)
* 2x [Seed Grove Shield V2](https://developer.mbed.org/components/Seeed-Grove-Shield-V2/)

# 1. Acquire knowledge about LoRa

Skim the attached [technical overview of LoRa and LoRaWAN](pdfs/LoRaWAN101.pdf)

If you are sufficiently adventurous you can also skim the
[LoRaWAN specification](pdfs/LoRaWAN Specification 1R0.pdf).

![foo](images/network.png)

# 2. Create an account at the ARM embed platform

**NOTE: I had to whitelist the webpage in my ad-blocker to avoid visual bugs.**

To produce binaries for hardware, we use the
[ARM embed platform](https://developer.mbed.org/).

It is a convenient web-based platform. First you write your C code in the browser and
it is compiled on ARM's servers. Next the binary is downloaded to
your local storage medium. Last you transfer it to a device.

Add the
[microcontroller "platform"](https://developer.mbed.org/platforms/ST-Nucleo-L152RE/)
to your mbed compiler.

After you have created an account, go to the compiler and create a new program.
Select the Nucleo-L152RE platform.

# 3. Produce the binary

First create a new program. Choose "Empty Program" in the templates dropdown.

Second rightclick on your program and click "import library". Search for
"mbed". Import the one where author is
["mbed\_official".](http://mbed.org/users/mbed_official/code/mbed/).

Third, create a New File "main.cpp". Fill it with this content:

	#include "mbed.h"
	
	int main() {
	
	    while(1) {
	        printf("hello world \n");
	        wait(0.5); // 500 ms
	    }
	}

Last, hit the Compile button.

If the compilation is successful, a binary should be downloaded to your local storage.

# 4. Transfer the binary to the microcontroller

This is also known as _flashing_ the device. Attach the microcontroller to your laptop
via USB cable. It should appear as a storage device and will probably be mounted
onto your filesystem automatically.

Transfer the binary by moving it:

	mv downloads/lora-workshop-test_NUCLEO_L152RE.bin /media/d/NODE_L152RE/

This will actually flash the device.

The USB port also exposes a serial port. Its purpose is communication between the
microcontroller and your laptop. Inspect the serial output with (Linux):

	minicom -D /dev/ttyACM0 -b 9600

It should print out "hello world" each second.

# 5. Hello LoRa!

Now we are gonna attach the Seed Grove Shield V2 and Semtech SX1276MB1xAS onto
the Nucleo. Like this:

![](images/prototype.jpg)

Also attach the radio antenna to ANT_\HF.

To compile a lora application we need to import two libraries:

* [Semtech/LMiC](https://developer.mbed.org/teams/Semtech/code/LMiC/)
* [Semtech/SX1276Lib](https://developer.mbed.org/teams/Semtech/code/SX1276Lib/)

[IBM LoRaWAN in C (LMiC)](http://www.research.ibm.com/labs/zurich/ics/lrsc/lmic.html)
is IBM's implementation of the LoRaWAN protocol. Its API can be found in the 
[user guide](pdfs/LMiC-v1.5.pdf).

Semtech/SX1276Lib is a driver for the SX1276 RF transceiver.

After importing those two libraries, you could try to compile. You will discover some compile errors:

    Error: Undefined symbol hal\_failed() (referred from lmic.cpp.NUCLEO\_L152RE.o).
    Error: Undefined symbol hal\_checkTimer(unsigned) (referred from oslmic.cpp.NUCLEO_L152RE.o).
    Error: Undefined symbol hal\_enableIRQs() (referred from oslmic.cpp.NUCLEO_L152RE.o).
    Error: Undefined symbol hal\_disableIRQs() (referred from oslmic.cpp.NUCLEO_L152RE.o).
    Error: Undefined symbol hal\_init() (referred from oslmic.cpp.NUCLEO_L152RE.o).
    Error: Undefined symbol hal\_sleep() (referred from oslmic.cpp.NUCLEO_L152RE.o).
    Error: Undefined symbol hal\_ticks() (referred from oslmic.cpp.NUCLEO_L152RE.o).
    Error: Undefined symbol hal\_waitUntil(unsigned) (referred from radio.cpp.NUCLEO_L152RE.o).

The LMiC library is separated into a large portion of portable code and a small platform-specific part.
By implementing the functions of this hardware abstraction layer with the specified semantics, the
library can be easily ported to new hardware platforms.

For the Nucleo-L152RE, create a file "hal.cpp" with the following contents:

## hal.cpp

	#include "mbed.h"
	#include "lmic.h"
	#include "mbed_debug.h"
	 
	#if !USE_SMTC_RADIO_DRIVER
	 
	extern void radio_irq_handler( u1_t dio );
	 
	static DigitalOut nss( D10 );
	static SPI spi( D11, D12, D13 ); // ( mosi, miso, sclk )
	 
	static DigitalInOut rst( A0 );
	static DigitalOut rxtx( A4 );
	 
	static InterruptIn dio0( D2 );
	static InterruptIn dio1( D3 );
	static InterruptIn dio2( D4 ); 
	 
	static void dio0Irq( void ) {
	    radio_irq_handler( 0 );
	}
	 
	static void dio1Irq( void ) {
	    radio_irq_handler( 1 );
	}
	 
	static void dio2Irq( void ) {
	    radio_irq_handler( 2 );
	}
	 
	#endif
	 
	static u1_t irqlevel = 0;
	static u4_t ticks = 0;
	 
	static Timer timer;
	static Ticker ticker;
	 
	static void reset_timer( void ) {
	    ticks += timer.read_us( ) >> 6;
	    timer.reset( );
	}
	 
	void hal_init( void ) {
	     __disable_irq( );
	     irqlevel = 0;
	 
	#if !USE_SMTC_RADIO_DRIVER
	    // configure input lines
	    dio0.mode( PullDown );
	    dio0.rise( dio0Irq );
	    dio0.enable_irq( );
	    dio1.mode( PullDown );   
	    dio1.rise( dio1Irq );
	    dio1.enable_irq( );
	    dio2.mode( PullDown );
	    dio2.rise( dio2Irq );
	    dio2.enable_irq( );
	    // configure reset line
	    rst.input( );
	    // configure spi
	    spi.frequency( 8000000 );
	    spi.format( 8, 0 );
	    nss = 1;
	#endif
	    // configure timer
	    timer.start( );
	    ticker.attach_us( reset_timer, 10000000 ); // reset timer every 10sec
	     __enable_irq( );
	}
	 
	#if !USE_SMTC_RADIO_DRIVER
	 
	void hal_pin_rxtx( u1_t val ) {
	    rxtx = !val;
	}
	 
	void hal_pin_nss( u1_t val ) {
	    nss = val;
	}
	 
	void hal_pin_rst( u1_t val ) {
	    if( val == 0 || val == 1 )
	    { // drive pin
	        rst.output( );
	        rst = val;
	    } 
	    else
	    { // keep pin floating
	        rst.input( );
	    }
	}
	 
	u1_t hal_spi( u1_t out ) {
	    return spi.write( out );
	}
	 
	#endif
	 
	void hal_disableIRQs( void ) {
	    __disable_irq( );
	    irqlevel++;
	}
	 
	void hal_enableIRQs( void ) {
	    if( --irqlevel == 0 )
	    {
	        __enable_irq( );
	    }
	}
	 
	void hal_sleep( void ) {
	    // NOP
	}
	 
	u4_t hal_ticks( void ) {
	    hal_disableIRQs( );
	    int t = ticks + ( timer.read_us( ) >> 6 );
	    hal_enableIRQs( );
	    return t;
	}
	 
	static u2_t deltaticks( u4_t time ) {
	    u4_t t = hal_ticks( );
	    s4_t d = time - t;
	    if( d <= 0 ) {
	        return 0;    // in the past
	    }
	    if( ( d >> 16 ) != 0 ) {
	        return 0xFFFF; // far ahead
	    }
	    return ( u2_t )d;
	}
	 
	void hal_waitUntil( u4_t time ) {
	    while( deltaticks( time ) != 0 ); // busy wait until timestamp is reached
	}
	 
	u1_t hal_checkTimer( u4_t time ) {
	    return ( deltaticks( time ) < 2 );
	}
	 
	void hal_failed( void ) {
	    while( 1 );
	}

## main.cpp

Now let's improve main.cpp. It looks confusing at first if you are unfamiliar with LMiC. Here it is:

	#include "mbed.h"
	#include "lmic.h"
	 
	#define LORAWAN_NET_ID (uint32_t) 0x00000000
	// TODO: enter device address below, for TTN just set ???
	#define LORAWAN_DEV_ADDR (uint32_t) 0x5A480000
	#define LORAWAN_ADR_ON 1
	#define LORAWAN_CONFIRMED_MSG_ON 1
	#define LORAWAN_APP_PORT 3//15
	 
	static uint8_t NwkSKey[] = {
	    // TODO: enter network, or use TTN default
	    // e.g. for 2B7E151628AED2A6ABF7158809CF4F3C =>
	    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6, 
	    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
	};
	 
	static uint8_t ArtSKey[] = {
	    // TODO: enter application key, or use TTN default
	    // e.g. for 2B7E151628AED2A6ABF7158809CF4F3C =>
	    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6, 
	    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
	};
	 
	osjob_t initjob;
	osjob_t sendFrameJob;
	u1_t n = 0;
	 
	void os_getArtEui (uint8_t *buf) {} // ignore
	void os_getDevEui (uint8_t *buf) {} // ignore
	void os_getDevKey (uint8_t *buf) {} // ignore
	 
	void onSendFrame (osjob_t* j) {
	    const char* message = "Hello LoRa"; // ASCII only
	    int frameLength = strlen(message); // keep it < 32
	    for (int i = 0; i < frameLength; i++) {
	        LMIC.frame[i] = message[i];
	    }
	    int result = LMIC_setTxData2(LORAWAN_APP_PORT, LMIC.frame, 
	        frameLength, LORAWAN_CONFIRMED_MSG_ON); // calls onEvent()
	}
	 
	void onInit (osjob_t* j) {
	    LMIC_reset();
	    LMIC_setAdrMode(LORAWAN_ADR_ON);
	    LMIC_setDrTxpow(DR_SF12, 14);
	    LMIC_setSession(LORAWAN_NET_ID, LORAWAN_DEV_ADDR, NwkSKey, ArtSKey);
	    onSendFrame(NULL);
	}
	 
	void onEvent (ev_t ev) { // called by lmic.cpp, see also oslmic.h
	    //debug_event(ev);
	    if (ev == EV_TXCOMPLETE) {
	        os_setCallback(&sendFrameJob, onSendFrame);
	    }
	}
	 
	int main (void) {
	    printf("main\r\n");
	    os_init();
	    os_setCallback(&initjob, onInit);
	    os_runloop(); // blocking
	}

The network key and application keys are good. They are used by The Things Network.

One change you need to do is set the LORAWAN\_DEV\_ADDR. This is the device address of the node
that is communicating with the network. Its purpose is similar to MAC addresses in Ethernet.

Hit the compile button and flash the Nucleo.

# 6. Did our data arrive?

Inspect the HTTP API and look for your data. 
