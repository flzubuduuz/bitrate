# Welcome to BitRate!

BitRate is a Python program I made to count the number of occurrences of certain words in Twitch chat during a stream. I was originally made for rating bits (hence the name) in [Northernlion](https://www.twitch.tv/northernlion)'s chat, but it can work with any channel!

Below is a deeper look into how you actually run BitRate. I don't actually recommend using this program because I don't know much about programming, but I hope it serves as a basis for someone with actual coding experience to make this a lot more efficient. (hit me up if you do!)

---


## 1. Log files

In order to use this program, you need to have a ```.log``` file with the correct formatting. Here is a sample of how every line of your log file needs to look like:

```
[2021-04-23 14:03:38]  I'm a user sending a message
[2021-04-23 14:03:48]  POGGERS
[2021-04-23 14:03:49]  POGGERS
[2021-04-23 14:03:50]  LUL
[2021-04-23 14:03:52]  Would you look at that! It's another user!
```

Four things are particularly important:
1. The dates needs to be in ISO format (YY-MM-DD hh:mm:ss)
2. You need to have **two** spaces between the date and the contents of the message.
3. You can't have usernames associated with each message (or else they would be counted as part of the message).
4. You can't have any extra lines that aren't messages in the .log file (cause I didn't account for that edge case the program will just crash lol).

I would recommend using [Twitch Chat Downloader](https://github.com/PetterKraabol/Twitch-Chat-Downloader) and adding the following preset to the ```settings.json``` file in order to get the correct formatting:

```
"bitrate": {
    "comments": {
        "format": "[{timestamp[absolute]}]  {message[body]}",
        "ignore_new_messages": false,
        "timestamp": {
            "absolute": "%Y-%m-%d %H:%M:%S"
        }
    },
    "output": {
        "format": "{id}.log",
        "timestamp": {
            "absolute": "%m.%d"
        }
    }
},
```

If you want the files to have names based on their date (instead of the VOD ID), you can change ```"format": "{id}.log",``` to ```"format": "{timestamp[absolute]}.log",```. If you do this though, downloading multiple VODs from the same day may result in overwrites, so be careful.

---

## 2. Getting started

Once you have your .log files ready to go, place them into the "logs" folder of the program. You can then run the program itself, which will ask you the following:

```
Enter whether you will run on OLD or NEW data: 
```

If you are working with new log files, type NEW. You can then enter a semicolon-delineated list of the log files you are working with, like this:

```
08.10; 08.11; 08.12
```

This will analyze ```08.10.log```, ```08.11.log``` and ```08.12.log```.

I strongly recommend naming the files in chronological order, with the oldest one first.

After inputting the log names, BitRate is going to create a new .csv file in the "data" folder. The name of this file is ```[name of first file]-[name of last file].csv```. Note that you might overwrite the ```.csv``` file if you make a new one with different files, but using the same first and last files.

After the ```.csv``` file has been created, the program will ask you if you want to run DEFAULTS. This is a very useful tool that is covered [later](##-4.-Defaults) on, but for now all you need to know is to enter **Y** if you want to run DEFAULTS, and to enter **N** otherwise.

---

## 3. Commands

Now we can finally start entering commands! In order to run a command, you first need to enter its name. If the command requires any other arguments, you will then be able to input them one by one.

*If at any moment you want to cancel a command and go back to the menu, simply press the interrupt key, which can be done by pressing Ctrl + C (I'm guessing Command + C works on Mac, but I don't know for sure).*


### **3.1.  RATE**

This is the main command of the program. It creates a new column in the .csv, which counts the frequency of a certain word, emote or message in the log files.

It requires the following arguments:

* *name:* the name of the column.
It can be any string you want, as long as it doesn't already exist in the .csv, and it doesn't start with *#* (these are reserved for other things).

* *plusword:* the word you want to count the frequency of. You can add multiple words by adding a semicolon and a space between each one (e.g. one; two; three).

* *minusword*: almost the same as *plusword*, but these words will **subtract** from the frequency instead of adding to it. You can leave it empty if you don't need it.

* *exact*: a boolean (1 if true, 0 if false) for whether or not you want the message to be an exact match of the word you are looking for.

* *cap-sensitive*: a boolean (1 if true, 0 if false) for whether or not you want the lookup to be case-sensitive. If you are counting emotes, this needs to be true (because lul is not an emote but LUL is).

* *interval*: the interval of time (in seconds) for which messages will be counted. For example, by choosing an interval of 20, the column will contain the frequency of messages for the 20 seconds following the timestamp. This accounts for the inherent delay that chat has compared to the stream. **If left empty, defaults to 20.**


### **3.2. TOP**

Gets the timestamps with the highest value for a certain column.

It requires the following arguments:

* *name*: name of the column that you want to check. The column must already exist.

* *number*: the number of values you want to list. It can theoretically be any integer, but things might get weird if you go too high, even for a long stream with lots of activity.


### **3.3. BOTTOM**

Same as *top*, but it picks the lowest values.

This command is only useful if the column you are checking has values for *minusword*; you can still use the command if you don't have any *minusword* values, but it will return a bunch of zeroes with no real utility.

It requires the same arguments as *top*.


### **3.4. BYE**

Lets you close the program without manually closing the tab. It's absolutely unnecessary, but I like it so it stays here.

It requires no other arguments.

---

## 4. Defaults


DEFAULTS is a very useful tool if you tend to run the same commands on every log file. You can store these default commands on a ```.json``` file, and then run them whenever the program detects you are working with a set of log files for the first time.

In order to add a default command (or many!), you will need to write it to the ```defaults.json``` file. This file is a "list of lists", with each inner list being a command.

Now you will see the formatting for each command, followed by an example.

**Note:** the ```default.json``` file, as uploaded to GitHub, has the commands I used for Northernlion's weekly highlights, so if you simply want to use those, you don't need to change the file itself.


### **4.1.  RATE**

```
['rate', name (string), plusword (list of strings), minusword (list of strings), exact (bool), capsens (bool), interval (int)]
```

Examples:

```
['rate', 'pog', ['POGGERS', 'EZClap'], [], 0, 1, 20]
```

```
['rate', 'plustwo', ['+2'], ['-2'], 0, 1, 20]
```

### **4.2. TOP**

```
['first', column (string), number (int), 1]
```

Example:

```
['first', 'plustwo', 10, 1]
```

### **4.3. BOTTOM**

```
['first', column (string), number (int), -1]
```

Example:

```
['first', -1, 'plustwo', 10, -1]
```


**IMPORTANT:** be very careful in the order you put these commands, or you might cause errors! For example, you can't put a *top* command without having a *rate* one before it, because you can't take the highest values from a list that doesn't exist.



That's about it! Thank you for reading, and I hope everything is (at least kind of) clear :)

-flzubuduuz
