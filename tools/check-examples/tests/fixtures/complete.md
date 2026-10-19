<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
# Complete app layouts

```cpp
class Greeting {
public:
    void begin();
    void update();
    void end();
};
Greeting greeting;
void Greeting::begin() { setColorsOff(); }
void Greeting::update() { HAL::clearDisplay(); HAL::updateDisplay(); }
void Greeting::end() { setColorsOff(); }
```

```cpp
// Counter.h
#pragma once
class Counter {
public:
    void begin();
    void update();
    void end();
};
extern Counter counter;
// Counter.cpp
#include "Counter.h"
Counter counter;
void Counter::begin() { setColorsOff(); }
void Counter::update() { HAL::clearDisplay(); HAL::updateDisplay(); }
void Counter::end() { setColorsOff(); }
```
