# Qhue

Qhue (pronounced 'Q') is an exceedingly thin Python wrapper for the Philips Hue API.

I wrote it because some of the other (excellent) frameworks out there weren't quite keeping up with developments in the API.  Because Qhue encodes almost none of the underlying models - it's really just a way of constructing URLs and HTTP calls - it should inherit any new API features automatically.  The aim of Qhue is not to create another Python API for the Hue system, so much as to turn the existing API *into* Python, with minimal interference.

## Understanding Qhue

Philips, to their credit, created a beautiful RESTful API for the Hue system.  It may not yet have all the features we'd like, but what does exist is very elegantly designed.  

You can (and should) read [the full documentation here](http://www.developers.meethue.com/philips-hue-api), but a quick summary is that resources like lights, scenes and so forth each have a URL, that might look like this:

    http://[myhub]/api/<username>/lights/1

You can read information about light 1 by doing an HTTP GET of this URL, and modify it by doing an HTTP PUT.

The `qhue` module has a Resource class, which represents something that has a URL. By calling an instance of this class, you'll make an HTTP request to the hub.  It also has a Bridge class, which is a handy starting point, and is itself a Resource.  If that seems a bit abstract, don't worry - all will be made clear below.

## Examples

Note: These examples assume you know the IP address of your bridge.  See [the 'Getting Started' section of the API docs](http://www.developers.meethue.com/documentation/getting-started) if you need help in finding it.  I've assigned mine a static address of 192.168.0.45, so that's what you'll see below.

They also assume you have experimented with the API before, and so have a 'newdeveloper' user account set up on the bridge.  If not, see the section below entitled 'Creating a user'. 

OK.  Now those preliminaries are out of the way...

If you have a Resource, you can check its URL. A Bridge is an example of a Resource, so let's try that:

    # Connect to the bridge with a particular username
    from qhue import Bridge
    b = Bridge("192.168.0.45", 'newdeveloper')

    # This should give you something familiar from the API docs:
    print b.url 

By requesting most other attributes of a Resource object, you will construct a new Resource with the attribute name added to the URL:

    lights = b.lights   # Creates a new Resource with its own URL
    print lights.url    # Should have '/lights' on the end

These Resources are, at this stage, simply *references* to entities on the bridge. To make an actual API call to the bridge, we simply call the Resource as if it were a function:

    # Let's actually call the API and print the results
    print lights()  

Qhue takes the JSON that's returned by the API and turns it back into Python objects, typically a dictionary, so you can access its parts easily:

    # Get the bridge's config info and print the ethernet MAC address
    print b.config()['mac']

Now, ideally, we'd like to be able to construct all of our URLs the same way, but you can't use numbers as attribute names, so we can't write, say, `b.lights.1` to refer to light 1.  Nor can you use variables.  As an alternative, therefore, you can use dictionary key syntax:

    # Get information about light 1
    print b.lights[1]()

    # or, to do the same thing another way:
    print b['lights'][1]()

Alternatively, when you call a resource, you can give it arguments, which will be added to its URL:

    # This is the same as the last examples:
    print b('lights', 1)

So there are several ways to express the same thing, and you can choose the one which fits most elegantly into your code.

To make a change to a value, you also call the resource, but using a keyword argument.  You can change the brightness and hue of a light by setting properties on its *state*, for example:

    b.lights[1].state(bri=128, hue=9000)

and you can mix URL-constructing positional arguments with value-setting keyword arguments, if you like:

    # These are equivalent to the previous example:

    b.lights(1, 'state', bri=128, hue=9000)
    b('lights', 1, 'state', bri=128, hue=9000)

This covers most simple cases.  If you don't have any keyword arguments, the HTTP request will be a GET.  If you do, it will be a PUT.  

Sometimes, though, you need to specify a POST or a DELETE, and you can do so with the special *http_method* argument, which will override the above rule:

    # Delete rule 1
    b('rules', 1, http_method='delete')

And, at present, that's about it.  How's that for approximately 50 lines of code?


## Creating a user

If you haven't used the API before, you'll need to create a user account on the bridge.

    from qhue import Bridge
    b = Bridge("192.168.0.45")  # No username yet
    b(devicetype="test user", username="newdeveloper", http_method="post")

You'll get an error back saying that the link button on the bridge needs to be pressed.  Go and press it, and then run the command again:

    b(devicetype="test user", username="newdeveloper", http_method="post")

This should succeed, and you can now get a new Bridge object as shown in the examples above, passing this username as the second argument.


## Prerequisites

This works under Python 2 and Python 3.  It uses Kenneth Reitz's excellent [requests](http://docs.python-requests.org/en/latest/) module, so you'll need to do:

    pip install requests

or something similar before using Qhue.


## Licence

This little snippet is distributed under the GPL v2. See the LICENSE file. (They spell it that way on the other side of the pond.) It comes with no warranties, express or implied, but just with the hope that it may be useful to someone.


## Contributing

Suggestions, patches, pull requests welcome.  There are many ways this could be improved.  

If you can do so in a general way, without adding too many lines, that would be even better!  Brevity, as Polonius said, is the soul of wit.

[Quentin Stafford-Fraser](http://quentinsf.com)


