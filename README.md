# HeyPresto!
Video demo: https://youtu.be/M3C2lEREFr4
## Description
HeyPresto is a web app that gives you and your friends a way to all secretly choose and then simultaneously reveal something – whether it's a message, a number or an image.

It's perfect for board or card games played asynchronously online, where you need to make a secret bid, or to choose and simultaneously reveal a card.

## How it works
1. Make a sealed 'box' for you and your friends to submit to.
2. Note the box's unique code and share it with your friends.
3. People's submissions to the box are kept secret until everyone's submitted.
4. Once all the submissions are in, open the box and see what's what!

## Technology

HeyPresto uses the Flask framework to manage its pages, relying on Python code to manage the site's actions, SQL table calls and inserts, and server-side validation.

SQLite was used to manage the app's tables, tracking the 'boxes' created and the content submitted to the boxes.

Python is also used client-side using Jinja2 templating, and JavaScript is used to assist dynamic site effects, check validation on client-side (it's also checked client side, but the JavaScript is used to serve up a better error message experience), create a 'copy-text-to-clipboard' function, and to manage form submission.


## Design process

I originally designed a version of HeyPresto that included user registration and a friend lists (with invites and approvals), so that a sealed box could be made and specific users could be associated with it. But the result was feeling very bogged down in admin processes – users had to wait for their friends to sign up for the site, then send freind requests, then wait for them to be approved, then manage a cumbersome multi-step box making process. It all felt very heavy and bureaucratic for what needed to be a lightweight solution to a simple problem.

So I tore it down and started again – this time with no user registration. When a user made a sealed box, they'd be served up a unique box code, which they could then share with their friends, who could then use that code make a submission to the box. Once all the submissions we're in, the box was ready to be looked at by anyone who had the code.

This new approach has some limitations – it puts a lot more trust in users to manage using the box properly – but ultimately the result felt a lot quicker and more user-friendly.

Since there was no longer and user registration, I also added recaptcha v2 to the paths that let you make a box or check a box, to keep automated bots from making endless boxes and bloating out the app's SQL tables.


# Web app detail

Here's more detail on what each of the files in the web app does.

## Non-HTML files

### app.py
This contains the server side python, organised using the Flask framework, which powers the web app. The Flask routes are used to drive movement between the app's pages, to execute the user's actions, and to serve up the info each page needs. There's also a route to validate the site's recaptcha v2 boxes server-side.

### heypresto.db
The two tables in this database record the 'sealed boxes' created and submitted to by the app's users:

###### boxes
This table holds the overall details of each box, including a unique code, any user-defined name and instructions, and the number of submissions that need to be made to the box before it can open.

###### box_contents
This table holds the specific submissions for each box. When a box is created, each of it's 'slots' is also allocated a random colour (picked from a site-appropriate palatte), and a randomised tilt for its display box and border, giving each box a unique feel.

### script.js
This file holds all the web app's JavaScript, which is primarily used to serve up user-friendly error messages, make changes to web elements (such as expanding content boxes) without needing to reload the page, manage form submission and create a 'copy-text-to-clipboard' function.

### styles.css
This cascading style sheet is used to set the style for the look and feel of the web app, including a couple of instances of animation.

## HTML pages

### layout.html
This page contains the header and footer of the app, including a nav bar (originally adapted from a Bootstrap design but pretty much altered beyond recognition) which is designed to dynamically restack vertically for smaller screen sizes.

### index.html
The front page of the web app, featuring the instructions and portals to make a new box or navigate to an existing one. Google's recaptcha v2 is used (currently with a testing key/secret key) to prevent bots from messing with the web app. There's also a rudamentary function run to check for and remove any very old (6 months - 1 year) 'sealed boxes', and to remove them and any images associated with them.

### make.html
Provides a simple form to make a new 'sealed box', with the user setting a name, some instructions, the type of content the box should take, and he number of submissions the box should take. The input is validated client-side with JavaScript (so user-friendly error messages can be displayed), as well as server-side (to prevent any user shenanigans).

A created box creates a new entry in the SQL 'boxes' table, including a unique 5-character alphabetical code. The slots in the box are also set up int he 'box_contents' table, including the alloation of a random palatte-approprate colour, a random tilt for the slot's content box, and a random tilt for the content box's border, to give each box a bespoke style that fits the web apps look and feel.

### made.html
Users who make a box are pushed to this page, which displays the unique code created for the created box, and provides a button to copy the box code to the users clipboard.

### gobox.html
This is where users land when entering a legitimate box code on the front page. The details of the sealed box are shown, along with each of the submissions – both pending and already made (in which case the submitter's name is shown, but their actual submission is obscured).

A Python function displays how much time has passed since existing submissions were made – to help encourage laggards to get their submissions in quickly.

Users can use a form to submit content to the box, with both client-side (JavaScript) and server-side (Python) validation. Submitted images (if validated as being .jpg, .gif or .png, and no larger than 500kB) are uploaded to a 'static/uploads' folder after being renamed to prevent malicious file names.

Once all the submissions a box needs has been made, the submission button becomes instead an 'open the box' button, which when pressed reveals all the submissions (with some dramatic reveal animation courtesty of some JavaScript).

There's also a simple function to adjust the display size of any text shown in the revealed submission boxes, so that smaller entries (such as single-digit numbers) fill up the content boxes in a more aesthetically pleasing way.
