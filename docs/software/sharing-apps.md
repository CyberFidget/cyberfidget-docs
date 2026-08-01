# Sharing from The Archives

The Archives at [cyberfidget.com/explore](https://cyberfidget.com/explore/) is the
shared collection of apps, screensavers, and sprite packs. Every item in it now has
its own web address, so you can send someone straight to the one you mean instead of
telling them what to search for.

---

## Every item has its own address

Open an app, screensaver, or sprite pack and its address appears in your browser's
address bar, in this form:

```
https://cyberfidget.com/explore/?item=<item-id>
```

The `<item-id>` part is the collection's own short name for that item. It is often
recognisably based on the item's title, but it is assigned by the collection rather
than typed by hand, so copy it rather than guessing it. Anyone who opens that address
lands on that item, not on the front of the collection.

Previously the address never changed while you browsed, so there was nothing useful
to copy.

---

## Back and Forward behave normally

Opening an item adds a step to your browser history:

- **Back** closes the item and returns you to the collection.
- **Forward** reopens the item you were looking at.

Closing an item with the close control also returns you to the collection. It never
takes you off the site -- including when you arrived by following someone else's link
directly, where there was no earlier page of ours to go back to.

---

## The Share control

**Share** sits in the item's detail header, next to the close control. What it does
depends on the device:

| If your browser offers | What Share does |
|---|---|
| Its own sharing (usual on phones and tablets) | Opens your device's share sheet, so you can pass the link to any app you already use. |
| No sharing of its own (usual on desktop) | Copies the link and confirms with a brief message: *Copied a share link.* |

Which one you get depends on what the browser itself offers, not on the size of the
screen, so a desktop browser that has its own sharing will use it too.

If you open the share sheet and then dismiss it without choosing anything, nothing
happens and nothing is reported. That is not an error -- you simply changed your mind.

!!! note "The link is clean"
    The shared link is built from the item's identity, not from whatever is currently
    in your address bar. Extra bits that happened to be tacked onto your address are
    left out, so the person you send it to gets the item and nothing else.

---

## What people see when you paste the link

Pasting the link into a chat or a post shows a preview of that specific item, with
its name and description, rather than a generic description of the whole site.

An item that has its own picture shows it in the preview. An item that does not have
one falls back to the general Cyber Fidget picture, and its name and description do
the identifying instead.

---

## Links to items that are no longer there

Authors can take their work out of the collection, and addresses can be mistyped. If
you follow a link to an item that is not in the collection, you get a plain
explanation rather than an empty page:

> This one isn't in the collection. It may have been taken down by its author, or
> the address may be wrong.

A **Back to the collection** control takes you to browsing.

!!! tip "An app you already installed keeps working"
    Removing an item from The Archives only removes the listing. If you already
    installed that app on your Cyber Fidget, it keeps working exactly as before.
    Nothing on the website reaches onto your device to remove or change what is
    installed there.

---

## Command mode works the same way

The Archives also has a text-command skin, where you type commands instead of
clicking cards. Sharing works there too:

- `try <name>` opens the item's player.
- `gui info <name>` opens the item's details.

Both open the item the same way clicking does, so the address bar updates and the
link is ready to share.
