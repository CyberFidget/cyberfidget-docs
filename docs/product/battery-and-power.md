# Battery and Power

Cyber Fidget looks after its rechargeable battery whether you are using the device or letting it rest.

---

## Going to sleep

After about 1 minute with no interaction, Cyber Fidget shows "Going to sleep now..." and enters deep sleep. Press the bottom-right button to wake it.

While it sleeps, the device briefly wakes itself about once an hour to check the battery level, then goes right back to sleep. This takes only a fraction of a second. The screen stays dark and the lights stay off, so you will not notice the check.

---

## When the battery runs very low

If an hourly check finds that the battery is very low, Cyber Fidget shuts down completely instead of returning to normal sleep. No button will wake it in this state. The device stops waking up so it can preserve the last bit of charge.

If the battery runs very low while you are using the device, Cyber Fidget waits until it has stayed low for a few seconds. Brief dips during loud sounds or bright lights do not trigger the shutdown. The screen then shows:

```text
Battery empty
Recharge me!
```

After a moment, the device shuts down in the same protective state.

This protection matters because draining a rechargeable pouch battery too far permanently damages it. The shutdown stops the drain before the battery reaches that zone.

---

## How to start again

Connect USB power to charge the battery. Then slide the power switch off and back on. Cyber Fidget will start normally.

Cycling the power switch always ends the protective shutdown, but charge the battery first. If the battery is still very low, the protection will simply engage again.

---

## Storing your Cyber Fidget

For long-term storage, follow the battery manufacturer's guidance:

- Store it with a decent charge - around half to three-quarters full is
  ideal. Never store it empty, and there is no need to store it at 100%.
- Switch the device off. The power switch fully disconnects the battery.
- Top up the charge roughly every 6 months.

!!! note "How it works"
    This protection is called under-voltage lockout (UVLO). The device reads the cell voltage from the onboard fuel gauge. The working thresholds are about 3.5 V for the asleep check and about 3.3 V while running. These are working values and are still being tuned against the battery's measured discharge curve.

    The brief battery check during sleep uses a negligible amount of energy, well under the battery's own self-discharge.
