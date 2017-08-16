### Contributing guideline


**How to report a bug?**

Use the issues tab in github.
```
[ ] - Pick an appropriate title
[ ] - Pick appropriate tags
[ ] - When something is not working as expected, always provide the output and settings.
```
---

**How to suggest a new Feature?**

Use the issue tab in github.
```
[ ] - Pick an appropriate title like "Feature request: xyz"
[ ] - Add the "request" label
[ ] - Describe how you expect it to work and maybe provide an example
```
---

**I want to contribute a feature!**

This is a personal project made within 1-2 days. I don't expect it to become a huge thing.

However if you want to contribute a feature, then first create an issue in github.
```
[ ] - Pick a title like "Feature: xyz"
[ ] - Add the "discussion" label
```
There we can discus how it would exactly work and look like.
For the final pull request rebase your feature commits into one.
The commit message should state: "feature #[featureno] - xyz" where [featureno] is the number of the issue.

---

**I want to fix a bug!**

Whenever you want me to accept a pull request please first submit an issue on github:
```
[ ] - Pick a title like "Bug: xyz"
[ ] - Add the "bug" and "contribute" label
```
The commit message must state: "bugfix #[bugno] - xyz" where [bugno] is the number of the issue. 

---

**How do I contact you?**

You may use my mail address. However be aware that I might not respond quickly.

---

**My vision for the project**

I don't really have a big vision. However I want some things to stay as they are:

* Json serialization in that folder structure with data as raw as possible. NO databases or any fancy stuff.
* The tool is to use from a single user on a single user account locally.
* The capability to have a workday counting past 12pm towards the day before 12pm
* The internal use of dd.mm.yyyy and not yyyy.mm.dd
* Any reduction of the flexibility within the settings. Increasing it is welcome.

Ideas for the future:

* A webinterface with daemon mode. So that the application will have it's tray icon and opens the webui on click.
* Exports into various formats non tech normal people use.
