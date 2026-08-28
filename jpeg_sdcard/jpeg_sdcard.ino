// Alterar para cálculos com integers
// experimentar outro tipos de threshold
// LUT
// tracking de blobs?

// Programa com capacidade de criar a página web e fazer uma deteção ok
// Introdução de HSV
#include "Arduino.h"

#include "esp_camera.h"
#include <esp_heap_caps.h>
#include <math.h>

#include "FS.h"                // File System
#include "SD_MMC.h"            // SD Card for ESP32

#define SD_MMC_CMD 38
#define SD_MMC_CLK 39 
#define SD_MMC_D0  40

int processingDelay = 1000;

int lastMillis = 0;

int counter = 1;

const uint16_t pinLED = 2;

uint8_t ledPower = 75;

#define CAMERA_MODEL_ESP32S3_EYE // Has PSRAM

// #define RESOLUTION FRAMESIZE_QQVGA   // 160x120 -> 19200
// #define FB_COUNT 2
// #define RESOLUTION FRAMESIZE_QVGA    // 320x240 -> 76800
// #define FB_COUNT 1
#define RESOLUTION FRAMESIZE_VGA    // 640x480 -> 76800
#define FB_COUNT 1


int width = 0;
int height = 0;

#include "camera_pins.h"

void setupLedFlash(int pin);

void setResolution(int framesize) {
  switch (framesize) {
    case FRAMESIZE_QQVGA:   // 160x120 -> 19200
      width = 160; height = 120; break;
    case FRAMESIZE_QVGA:    // 320x240 -> 76800
      width = 320; height = 240; break;
    default:
      width = 0; height = 0; // Unknown
      break;
  }
}

void initSDCard() {
  SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);
  if (!SD_MMC.begin("/sdcard", true, true, SDMMC_FREQ_DEFAULT, 5)) {
    Serial.println("SD Card Mount Failed");
    return;
  }
  uint8_t cardType = SD_MMC.cardType();
  if (cardType == CARD_NONE) {
    Serial.println("No SD card attached");
    return;
  }
  Serial.print("SD_MMC Card Type: ");
    if(cardType == CARD_MMC){
        Serial.println("MMC");
    } else if(cardType == CARD_SD){
        Serial.println("SDSC");
    } else if(cardType == CARD_SDHC){
        Serial.println("SDHC");
    } else {
        Serial.println("UNKNOWN");
    }
}

void saveImageToSD(camera_fb_t * fb, int imageCount) {
  String path = "/picture" + String(imageCount) + ".jpg";
  fs::FS &fs = SD_MMC;
  File file = fs.open(path.c_str(), FILE_WRITE);

  if (!file) {
    Serial.println("Failed to open file in writing mode");
  } else {
    file.write(fb->buf, fb->len);
    Serial.printf("Saved: %s\n", path.c_str());

    //rgbLedWrite(RGB_BUILTIN, ledPower, 0, 0);
    //ledPower = (ledPower == 75)? 0 : 75;
  }
  file.close();
}

void resumeCounterFromSD() {
  File root = SD_MMC.open("/");
  int maxCounter = -1;

  while (File file = root.openNextFile()) {
    String name = file.name();
    // Look for files starting with "picture" and ending in ".jpg"
    if (name.startsWith("picture") && name.endsWith(".jpg")) {
      // Extract the number between "picture" and ".jpg"
      int num = name.substring(7, name.length() - 4).toInt();
      if (num > maxCounter) {
        maxCounter = num;
      }
    }
    file.close();
  }
  counter = maxCounter + 1;
  Serial.printf("Resuming from image number: %d\n", counter);
}

void setup() {
  pinMode(pinLED, OUTPUT);
  digitalWrite(pinLED, LOW);

  //pinMode(RGB_BUILTIN, OUTPUT);
  //digitalWrite(RGB_BUILTIN, LOW);
  //neopixelWrite();
  //rgbLedWrite(RGB_BUILTIN, 40, 40, 0);

  Serial.begin(115200);
  Serial.setDebugOutput(true);
  Serial.println();

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 27000000;       // Setting the camera frequncy to 27MHz, the buffer to at least 2 frames ensures maximum performance.
  config.frame_size = RESOLUTION;  // The images are taken in RGB and converted to HSV
  config.pixel_format = PIXFORMAT_RGB565;
  // config.pixel_format = PIXFORMAT_JPEG;
  // config.jpeg_quality = 5;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  // config.grab_mode = CAMERA_GRAB_LATEST;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.fb_count = FB_COUNT;

  // camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }

  sensor_t *s = esp_camera_sensor_get();
  // initial sensors are flipped vertically and colors are a bit saturated
  if (s->id.PID == OV3660_PID) {
    s->set_vflip(s, 1);        // flip it back
    s->set_brightness(s, 1);   // up the brightness just a bit
    s->set_saturation(s, -2);  // lower the saturation
  }

  setResolution(RESOLUTION);

  initSDCard();
  resumeCounterFromSD();

  //for(int i; i < 6; i++) {
  //  rgbLedWrite(RGB_BUILTIN, 0, ledPower, 0);
  //  delay(200);
  //  ledPower = (ledPower == 75)? 0 : 75;
  //}
  //rgbLedWrite(RGB_BUILTIN, 0, 0, 0);
}

void loop() {
  if (millis() - lastMillis > processingDelay) {
    lastMillis = millis();

    camera_fb_t *fb = esp_camera_fb_get();

    if (fb){
      saveImageToSD(fb, counter);
      counter++;
      esp_camera_fb_return(fb);
    }
  }
  delay(10);
}
