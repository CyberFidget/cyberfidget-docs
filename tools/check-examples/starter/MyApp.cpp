#include "MyApp.h"
#include "globals.h"
#include "HAL.h"
#include "MenuManager.h"

MyApp myApp(HAL::buttonManager());
MyApp* MyApp::instance = nullptr;

MyApp::MyApp(ButtonManager& btnMgr) :
    buttonManager(btnMgr), display(HAL::displayProxy()), audio(HAL::audioManager()) { instance = this; }

// begin() runs once when your app opens from the menu.
// Set things up here: hook up the buttons and start with the lights off.
void MyApp::begin() {
    registerButtonCallbacks();
    setColorsOff();
}

// update() runs about 50 times a second while your app is open.
// Clear the screen, draw what you want, then show it.
// The case hides about 8 pixels at each screen corner, so keep text and
// important pixels out of those corners.
void MyApp::update() {
    display.clear();
    display.setTextAlignment(TEXT_ALIGN_CENTER);
    display.setFont(ArialMT_Plain_16);
    display.drawString(64, 24, "MyApp");
    display.display();
}

// end() runs when your app closes. Let go of the buttons and turn the
// lights off (if your app plays sounds, call audio.stopTone() here too).
void MyApp::end() {
    unregisterButtonCallbacks();
    setColorsOff();
}

// The bottom-left button closes your app and goes back to the menu.
void MyApp::onButtonBackPressed(const ButtonEvent& event) {
    if (event.eventType == ButtonEvent_Released) {
        instance->end();
        MenuManager::instance().returnToMenu();
    }
}

void MyApp::registerButtonCallbacks() {
    buttonManager.registerCallback(button_BottomLeftIndex, onButtonBackPressed);
}

void MyApp::unregisterButtonCallbacks() {
    buttonManager.unregisterCallback(button_BottomLeftIndex);
}
