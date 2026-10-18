// SPDX-License-Identifier: CC-BY-SA-4.0
#include "MyApp.h"

MyApp myApp;

void MyApp::begin() {
    setColorsOff();
}

void MyApp::update() {
    auto& d = HAL::displayProxy();
    d.clear();
    d.display();
}

void MyApp::end() {
    setColorsOff();
}
