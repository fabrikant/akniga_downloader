# Description #

This is an audiobook downloader for the site akniga.org.

I made it for myself to have books on the go without having to rely on an internet connection.
Im sharing it here with those who also want that freedom.

The downloader adds useful metadata to the downloaded tracks like the book author, 
the book reader, album name, track title, track number and a cover image.

With it you can also download whole book series easily.

--------------------

# Prerequisites #

- Node
- ffmpeg

I was successfully using it with node v16.17.0 and ffmpeg v5.0.1. 
Other versions were not tested.

--------------------

# Guide #

Clone this repository or download it as zip to whatever directory you like.

Go to the root directory of the project. By default it's *akniga-downloader*.

In the root directory create a text file called *books.txt*.

Paste the links of the books you want to download into the *books.txt* file.
Every link has to be on a new line.

Once you've collected the links you will need to find a "resource key".
Simply go on one of the book pages and hit `ctrl + shift + i`.
Browser dev tools will pop up. If you are using Chrome open the "Elements" tab, 
if you are using Firefox open the "Inspector" tab.

Now hit `ctrl + f` and type ".mp3". Dev tools will find the resource URL of the audiobook.
If it doesn't work try playing a track for a second or try another browser.
The resource URL will look something like this:
https://s2.akniga.club/b/645364/SGFoYWhhIVlvdUZvdW5kTWUh,,/author_name_book_name.mp3

Now, from the URL copy the part that looks similar to this: SGFoYWhhIVlvdUZvdW5kTWUh,,
It is the resource key. Paste it as the first line to *books.txt*.

Finally lauch the download process.
If you are on Windows double click on *launch.bat*.
If you are on Linux or Mac double click on *launch.sh*.
If you have Git Bash on Windows *launch.sh* will also work.

Once downloading is complete you will find the books in *audiobooks* folder.

--------------------

# Tips #

The book link looks like this: https://akniga.org/author_name_book_name

You can download all books belonging to a series by pesting a series URL into *books.txt*.
The series URL looks like this: https://akniga.org/series/series_name

In *books.txt* lines that don't start with "https" will be ignored (excluding the first line).
If you prefix a link for example with `#` then it will be skipped.

If you cancel a download process remeber to delete the *temp* folder before starting a new process.
