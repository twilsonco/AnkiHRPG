AnkiHRPG
=======

Anki 2 add-on for use with Habitica. Automatically scores habits when you reach the end of your Anki timebox 
and when you review all cards in a deck.

This add-on uses the Anki database to get its information, so you can do your reviews on any device and they will be included!

For use with Habitica (formerly, Habitica): http://habitica.com

Inspired by: https://github.com/Pherr/Habitica-Anki-Addon

Uses some code from https://github.com/Pherr/Habitica-Anki-Addon but scores you for reaching the end of your
timebox or reviewing all scheduled cards in a deck instead of scoring you for correct answers.

I feel that you should reward yourself for effort, not just performance. This Anki addon gives you points in
your Habitica account for the following:

1. No more cards to review in a deck - Scores 'Anki Deck Complete'
2. Reached a timebox? - Scores 'Anki Timebox Reached'
3. Get flashcards right? - Scores 'Anki Correct Answer' once for every 10 cards you remember.
4. Cards become matures? - Scores 'Anki Matured Cards' once for every 5 cards matured.
5. New cards learned? - Scores 'Anki Learned Cards' once for every 5 cards learned.

*The five habits will be created automatically for you.
**How often the habits are scored can be adjusted by the user.

Set the new habits to positive only for best results.

INSTALLATION
============

The Easy Way:
In Anki, go to Tools >> Add-ons >> Browse & Install
Paste in the following code: 954979168 


Linux:

Install ankihrpg.py to $HOME/Anki/addons/ directory
Start Ank and run Tools >> Setup Habitica
     enter userID and apiKey from Habitica
     optionally modify the rate at which the 5 Habitica habits are scored
     
Habitica userID and apiKey: These are NOT your username and password! See the API section of the settings menu in habitica: https://habitrpg.com/#/options/settings/api

To set up timeboxing for Anki:
Tools >> Preferences >> Timebox time limit

Windows and Mac:

Install ankihrpg.py to [your home directory]/Documents/Anki/addons directory
Start Ank and run Tools >> Setup Habitica Support
* enter userID and apiKey from Habitica
* optionally modify the rate at which the 5 Habitica habits are scored

To set up timeboxing for Anki:
Tools >> Preferences >> Timebox time limit

Set your Anki 2 installation to sync on open/close:
Tools >> Preferences >> Network >> Automatically sync on profile open/close

Set the new habits to positive only for best results.

USE
===

This add-on uses the Anki database to get all its information, so once you've setup the add-on per the instructions above you can do your Anki reviews in Anki 2 on Mac/PC/Linux, in Anki Mobile for iOS, or in AnkiDroid on Android.
Assuming you have proper syncing habits (sync once you're done with reviews, every time!) then each time Anki 2 syncs it will pick up any changes and give increment Habitica habits accordingly.

*For the 'Anki Timebox Reached' habit, the add-on simply sees the amount of time you've spent on reviews, and divides by the timebox duration set above to see how many timeboxes worth of reviews you've done. This isn't ideal, but the Anki database doesn't include information on timebox completion, and this setback alone is nothing compared to being free to do Anki reviews on any device and still get Habitica credit for it! By contrast, now you might get too much credit for timeboxes, but you won't get extra credit for opening a deck that's already complete. So I fixed one problem and introduced another---C'est la vie...

(Previously, this add-on worked by piggybacking Anki 2 events so it would be triggered by things like answering cards and completing decks. Now all information is taken from the Anki database)
