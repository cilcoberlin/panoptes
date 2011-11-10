Panoptes
========

Panoptes is a usage-tracking suite for computer labs.  It gathers anonymized
statistics on the usage of your lab, such as the average length of a usage session,
the total number of sessions over a time period or the number of times certain
applications were used over a time period.  It makes this data available for
inspection via a web-based viewer that can display graphs, map overlays and a
list of Google calendar events.

Panoptes consists of a server component that receives usage data and provides the
usage-viewing page and various clients that report usage of a workstation back
to the server.  The server component is a Django application, and the clients
are Python scripts wrapped in platform-appropriate containers.

Server Installation
-------------------

These instructions assume that you are running a Unix-like environment and have
a recent version of git installed.

**Installation**

    git clone git://github.com/cilcoberlin/panoptes.git
    cd panoptes/
    pip install -r pip_requirements.txt
    python setup.py install

**Configuration**

1. Create a new Django project.
2. Add `'panoptes'` to the `INSTALLED_APPS` list in your project's `settings.py` file.
3. Add `AUTH_PROFILE_MODULE = 'panoptes.UserProfile'` to your project's `settings.py` file.
4. Copy the contents of the `panoptes/templates/` directory to your project's `templates/` directory.
5. Copy the contents of the `panoptes/media/` directory to your project's `media/` directory.
6. Include `'panoptes.urls'` in your project's `urls.py` file's `urlpatterns`.
7. Sync the database.

**Standalone Settings**

If Panoptes is the only application that you are running in your project, you can
add the following lines to your project's `settings.py` file, replacing **PANOPTES**
with the URL that you configured for your Panoptes installation.

    LOGIN_URL  = 'PANOPTES/accounts/login'
    LOGOUT_URL = 'PANOPTES/accounts/logout'
    LOGIN_REDIRECT_URL = 'PANOPTES/'

To have Panoptes handle any 404 or 500 errors, you can set the following values
in your project's `urls.py` file configuration.

    handler404 = 'pressgang.core.views.error_404'
    handler500 = 'pressgang.core.views.error_500'

Client Installation
-------------------

For either client, first clone the Panoptes repository or
[download the source archive](https://github.com/cilcoberlin/panoptes/zipball/master).
Next, take note of the absolute URL to your Panoptes installation, as this is
required for installation.  The URL should be something like **http://www.example.com/panoptes/**.

Installing the client on a computer will make that computer able to report usage
to Panoptes.  Since identifcation of reporting computers is done via MAC address,
if you install the client on an imaged computer, any other computers
receiving that image will also be able to report their usage back to Panoptes.

**Mac Client**

To install the client on a Mac machine that you wish to track, open a terminal
window and navigate to the directory containing the downloaded Panoptes repository.
Then run the following lines, replacing **PANOPTES_URL** with the absolute URL to your
Panoptes installation.

     cd client/
     chmod 755 install_mac.sh
     ./install_mac.sh PANOPTES_URL

**Windows Client**

To install the client on a Windows machine that you wish to track, open up a
command prompt (`Run -> cmd`).  Navigate to the directory containing the downloaded
Panoptes repository, then run the following lines, replacing **PANOPTES_URL**
with the absolute URL to your Panoptes installation:

    cd client/
    install_windows.cmd PANOPTES_URL

Configuring Panoptes
--------------------

To configure Panoptes, open a browser and go to the URL of the Django admin site
for your Panoptes project.  Log in to Django as the superuser that you added
when you created your project.  Once logged in, you will need to create a few
items to bring Panoptes to a state where it can track the usage of your lab.  The
model instances that you'll need to create are as follows.

**Locations**

Create a new location describing your lab.  Provide the earliest opening time
and latest closing time, as well as your lab's time zone.  Check the **Default location**
box and save the location.

**Workstations**

For each workstation in your lab, you will need to create a workstation instance.
On the workstation addition screen, provide a name for the workstation, and
use the location you created in the previous step for the **Location** field.
In the **MAC addresses** fieldset, enter the MAC addresses for any network devices
the computer uses.  Once you are done, save the workstation and repeat until you
have created instances for every machine in your lab.

Tracking Applications
---------------------

To allow Panoptes to track application usage, you need to provide two additional
data types, being applications and reported applications.  An application is
the canonical name of the application that you wish to track, and a reported
application is one or more ways in which that application might be reported. Using
these two data types, Panoptes is able to receive multiple reports of the usage
of an application and present them as a single application to a user.  The model
instances that you will need to provide are as follows.

**Applications**

Provide a name for an application that you wish to track and save it. This name
is simply a label that you would like for an application, so if you wished to track
all uses of Firefox and have it appear as "FF Browser" or "Mozilla Firefox", you
would use one of those values for the application's **Name** field.

**Reported Applications**

Once you have added all of the applications that you wish to track, you need to
create a record describing how those applications might be reported by the Panoptes
client.

Knowing what to use for the **Reported name** requires a brief explanation of how
the Panoptes clients report application usage.  On the Mac side, Panoptes will
report each application as the name of the `.app` bundle, stripped of the `.app`
extension.  So, for Firefox on the Mac, which is contained in a `Firefox.app`
bundle, "Firefox" would be reported to the server.  In the same manner, Google
Chrome, contained in a `Google Chrome.app` bundle, would be reported as "Google Chrome".
On the Windows side, Panoptes reports each application as the name of its `.exe`
file stripped of the `.exe` extension.  Firefox, which runs as `firefox.exe`, will
be reported as "firefox", and Microsoft Word, which often runs as `WINWORD.exe`,
will be reported as "WINWORD".  Note that these reported names are case-sensitive,
so you will need to be sure to match the case of the reported application.

Knowing the above information, put an appropriate value in the **Reported name**
field.  Select the application that you would like to associate with it in the
**Application** field, and then associate a location with this reported application,
which allows you to ignore uses of an application from a lab that you're not
concerned about but track them for another, more interesting lab.

Once you have filled out these fields, save the reported application.  Once you are
finished adding each manner in which an application can be reported, Panoptes will
collect data on applications and the duration of their usage.

Restricting Users
-----------------

While the usage sessions recorded by Panoptes do not record any user information,
when a new session is reported by a client, the username of the current user is
reported.  This can be used to create a user-account filter that will only
track sessions from whitelisted users or track any sessions but those from blacklisted
users.  These filters can also be combined, giving you fine-grained control over
which users' sessions are tracked.

To enable these filters, create a new **User account filter** via your project's
admin site.  Select the location where you would like these filters to apply,
then provide a comma- or space-separated list of user names that you would like to
include or exclude.  Sessions from users that fall outside of these filters will
be ignored.

Viewing Google Calendar Events
------------------------------

The usage-viewing component of Panoptes allows you to click on a bar in the
usage graph and view any events from one or more Google calendars of your choosing
that are associated with the date or time represented by the bar.  For example,
if you were viewing usage by day, you could click on a day to view events
on a Google calendar that you use to schedule your lab that occurred on that day.

To associate a Google calendar with a location, create a new **Location calendar**
via your project's admin site.  Select a location for it, provide it with a
display name, a Google calendar ID (which will usually be of the form
`CALENDAR_ID@group.calendar.google.com`) and an optional display order, which will
allow you to control which calendars are shown first on the usage-viewing page.

Once you have associated a Google calendar with a location, you will be able to
view date or time events from that calendar in the Panoptes usage viewer.

Viewing Usage
-------------

Once you have configured Panoptes, go to the URL of your Panoptes installation.
Once you log in, you will be presented with a graph of the recent usage of your lab.
You can experiment with the form fields to the left to change the data being viewed.
