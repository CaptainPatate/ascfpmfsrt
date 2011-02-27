About ASCFPMFSRT
================

ASCFPMFSRT is an acronym which stand for "A Simple Call For Paper
Manager For Small Researcher Team". It is useful to maintain a
thematic list of CFP in a researcher team.

License
=======

This software is distributed under MIT license. See [LICENSE
file](https://github.com/CaptainPatate/ascfpmfsrt/blob/master/LICENSE)

Installation
============

Currently this software is use [App Engine
framework](http://code.google.com/appengine/). To run ASCFPMFSRT, you
need to create an App Engine Account. The account is free and Google
gave you a free amount of quotas which should be sufficient to run
this software in the most case (see here for more details about [App
Engine Quotas](http://code.google.com/appengine/docs/quotas.html).

1. You need to download the [App Engine
SDK](http://code.google.com/appengine/downloads.html) for your
platform and install it.
1. You need to create an [App Engine
Application](https://appengine.google.com/).
1. Download this software.
1. Use the App Engine SDK to upload this software on your App Engine
instance. For example on unix I use this command:

      [ascfpmfsrt]$ appcfg.py -A my_instance_name update .

And that's it!

Add an user
===========

1. Ask your user to login into your instance of ASCFPMFSRT.
1. Go to your instance [dashboard](https://appengine.google.com)
1. Go to the "Logs" tab and choose to display severity of type INFO
1. Look for line like this: The unauthorized user "te@example.com
(te@example.com) <121840173433018753431>" tried to connect.
1. Go in the Datastore Viewer tab then in the Create sub-tab:
 1. Choose the kind "AuthorizedUser" and go to "next"
 1. Copy the value which is between angle brackets in the log to the
 value input form then save the entity.
 1. The user is now authorized to use the application

Atom feeds
==========
We can access to Atom feeds with these URLs:

* http://youinstance.appspot.com/feed/all
* http://youinstance.appspot.com/feed/submitters
* http://youinstance.appspot.com/feed/submitter/someone@somewhere.com