# Bonus marks implementations

### Extra Features

- Toggleable darkmode
- Oauth
- Emoji shortcuts
- Latex renderer
- Typing

---
## Toggleable darkmode
> In the header there is a switch to toggle darkmode on and off. This will change the theme of the frontend to a dark theme.

### Oauth
> The Oauth button sign in with google on the login page, enables users to both register and sign in using their google account. Uses a custom oauth_register route which has optional parameters for everything. Users already registered, who use the button are logged in and not re-registered.

### Emoji shortcuts
> The emoji shortcuts allow a user to type something like I :heart: you in messages which will render into a love heart emoji.Supports every emoji listed on http://emoji-cheat-sheet.com/ and works with every message function ie. Message_edit, senddm etc.

### Latex renderer
> Ability to type math equations and latex in messages.For example \(x^2 + 5 = 6x\) will render as an equation.

### Typing
> All functions are typed with the default, and typing Module. Made use of Unions, Optional and TypedDicts for clarity in our typing system