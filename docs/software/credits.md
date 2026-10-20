<!-- Cyber Fidget documentation - CC BY-SA 4.0 -->

# Free use, credits and privacy

After this page you know the ways the studio's [code generator](code-generator.md) can run, where to check costs and limits, and where to read the privacy rules.

Nothing on this page applies if you don't use the **Generate** tab. Writing code, drawing art, building and the emulator never use the code generator.

---

## Three ways to run the generator

**Generator settings**, the small link under the **Describe your app...** box, opens **SETTINGS > ACCOUNT > Generation**, where you choose how generation runs.

| Choice | Who pays | Limits | Sign-in |
|---|---|---|---|
| **Free (built-in)** | Cyber Fidget | The studio shows how many free generations you have and when they reset | Not needed |
| **Use your own key** | You, through your own account with a model provider | Your provider's limits and prices | Not needed |
| **Use my credits** | Credits on your account | Your credit balance | Needed; credits are rolling out |

---

## Free (built-in)

The free allowance lets you try the code generator without setting anything up. The studio shows how many free generations you have and when they reset. Check **Generator settings** and the line under the description box for your allowance.

If you reach the allowance or the free service is busy, follow the studio's message or [use your own key](#use-your-own-key).

---

## Use your own key

An API key (Application Programming Interface key) is a secret code from a model provider's developer website. It lets a program, here the studio, use your account with that provider. The provider charges your account for what you use, by its own prices, and sets its own limits.

1. Get a key from one of the providers the studio supports: **Anthropic**, **OpenAI** or **Google**. The settings link to each provider's key page.
2. Open **Generator settings** and choose **Use your own key**.
3. Pick the **Provider**, paste the key into **API Key** and press **Save**. **Verify** checks that the provider accepts it.
4. Pick a **Model**. **Refresh model list** asks the provider which models your key can use. See [Choosing a model](ota-builder.md#choosing-a-model).

The line under the description box then reads **Using your key** and names the provider or model.

**Max output tokens** limits how long one reply can be. A token is a small piece of text, often part of a word; providers count and charge by tokens. A higher limit lets the model write more code in one reply, but each reply can take longer and cost more.

Check your provider's prices, limits and terms before using your key. For privacy details, read the [Privacy policy](https://cyberfidget.com/privacy/) and your provider's policy.

---

## Use my credits

Credits are rolling out to signed-in accounts. If your account has them, **Generator settings** shows a third choice, **Use my credits**, and **SETTINGS > ACCOUNT** shows a **Credits** card with your balance, the typical cost for each model and your history.

- **Choosing a model:** pick one in **Model for credit generations**, or press the model name in the line under the description box. That line reads, for example, the model name and how many credits you have.
- **What a generation costs:** each model shows "about N credits for a typical generation". The real charge is worked out from what that generation used: what Cyber Fidget is billed for it, plus a small markup, rounded up. Each reply in the thread shows the model and the credits it used.
- **What costs nothing:** a generation that fails on Cyber Fidget's side costs 0 credits and is returned automatically. The automatic fix of a failed build costs 0 credits. Free-allowance and own-key generations never use credits.
- **Expiry:** included credits never expire. Credits from a promo code (**Have a promo code?**) expire on the date the card shows, and are spent first.
- **More credits:** the card has **Request more**, with an optional message. A person at Cyber Fidget reviews each request.
- **Buying:** buying credits is rolling out. If your account offers it, **Buy credits** shows each pack and its price, and the refund terms, before you pay. Bought credits never expire.

---

## Check costs and choices

Choose from the models the studio lists. **Generator settings** shows your free allowance, and the **Credits** card shows your balance and model costs. With your own key, the provider decides which models your key can use and what they cost.

---

## Privacy

Read the [Privacy policy](https://cyberfidget.com/privacy/) for how requests and project information are handled, and the [Terms of Use](https://cyberfidget.com/terms/) for the rules for using the generator. If you use your own key, read your provider's terms and privacy policy too.

!!! warning "Keep private information out of your requests"
    Leave passwords, keys and personal details out of your descriptions and project code when using the code generator.

---

## See also

- [Code generator](code-generator.md) - what it does and how to use it alongside your own work
- [App Builder](ota-builder.md) - choosing a model, and what to do when generating doesn't work
