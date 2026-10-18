#ifndef MYAPP_H
#define MYAPP_H

#include "DisplayProxy.h"
#include "ButtonManager.h"

class MyApp {
public:
    MyApp(ButtonManager& btnMgr);
    void begin();
    void update();
    void end();
private:
    ButtonManager& buttonManager;
    DisplayProxy& display;
    static MyApp* instance;
    void registerButtonCallbacks();
    void unregisterButtonCallbacks();
    static void onButtonBackPressed(const ButtonEvent& event);
};

extern MyApp myApp;
#endif
