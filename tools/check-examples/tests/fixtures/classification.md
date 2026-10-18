<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
<!-- check-examples: skip - deliberate pseudocode -->
```cpp
do something;
```

```cpp
int standalone = 1;
```

```
HAL::clearDisplay();
```

```text
HAL::clearDisplay();
```

```
folder/
  child.txt
+----+
| OK |
+----+
```

<!-- check-examples: skip - -->
```ino
int unmarked = 1;
```

<!-- check-examples: skip - separated marker does not apply -->

```cpp
int separate = 1;
```

```cpp
class Example {
public:
    void begin() {}
    void update() {}
    void end() {}
};
Example example;
```

```cpp
// SplitExample.h
class SplitExample {
public:
    void begin();
    void update();
    void end();
};
extern SplitExample splitExample;
// SplitExample.cpp
#include "SplitExample.h"
SplitExample splitExample;
void SplitExample::begin() {}
void SplitExample::update() {}
void SplitExample::end() {}
```

```cpp
class Missing {
public:
    void begin() {}
    void update() {}
    void end() {}
};
```
