# -*- coding: utf-8 -*-
"""
A routing layer for the onboarding bot tutorial built using
[Slack's Events API](https://api.slack.com/events-api) in Python
"""
import json
import bot
from flask import Flask, request, make_response, render_template, jsonify, abort

pyBot = bot.Bot()
slack = pyBot.client

app = Flask(__name__)


def _event_handler(event_type, slack_event):
    """
    A helper function that routes events from Slack to our Bot
    by event type and subtype.

    Parameters
    ----------
    event_type : str
        type of event recieved from Slack
    slack_event : dict
        JSON response from a Slack reaction event

    Returns
    ----------
    obj
        Response object with 200 - ok or 500 - No Event Handler error

    """
    team_id = slack_event["team_id"]

    # Sends the onboarding message
    # if event_type == "message":
    #     # print("got an event")
    #     # print(slack_event['event']['text'])
    #     # pyBot.copycat(slack_event)
    #     user_id = slack_event["event"]["user"]
    #     # Send the onboarding message
    #     pyBot.onboarding_message(team_id, user_id)

    #     # pyBot.copycat(team_id, user_id, slack_event)
    #     return make_response("Recieved message", 200,)
    # ================ Team Join Events =============== #
    # When the user first joins a team, the type of event will be team_join
    if event_type == "team_join":
        user_id = slack_event["event"]["user"]["id"]
        # Send the onboarding message
        pyBot.onboarding_message(team_id, user_id)
        return make_response("Welcome Message Sent", 200,)

    # ============== Share Message Events ============= #
    # If the user has shared the onboarding message, the event type will be
    # message. We'll also need to check that this is a message that has been
    # shared by looking into the attachments for "is_shared".
    elif event_type == "message" and slack_event["event"].get("attachments"):
        user_id = slack_event["event"].get("user")
        if slack_event["event"]["attachments"][0].get("is_share"):
            # Update the onboarding message and check off "Share this Message"
            pyBot.update_share(team_id, user_id)
            return make_response("Welcome message updates with shared message",
                                 200,)

    elif event_type == "message" and slack_event["event"]["text"] == "join":
        # print("got an event")
        print(slack_event['event']['text'])
        # pyBot.copycat(slack_event)
        user_id = slack_event["event"]["user"]
        print("userid: " + user_id)
        # Send the onboarding message
        pyBot.onboarding_message(team_id, user_id)
        # pyBot.update_share(team_id, user_id)

        # pyBot.copycat(team_id, user_id, slack_event)
        return make_response("Recieved message", 200,)

    elif event_type == "message":
        # print("got an event")
        # print(slack_event['event']['text'])
        # pyBot.copycat(slack_event)
        user_id = slack_event["event"]["user"]
        print("userid: " + user_id)
        # Send the onboarding message
        # pyBot.update_share(team_id, user_id)

        # pyBot.copycat(team_id, user_id, slack_event)
        return make_response("Recieved message", 200,)

    # ============= Reaction Added Events ============= #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "reaction_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        pyBot.update_emoji(team_id, user_id)
        return make_response("Welcome message updates with reactji", 200,)

    # =============== Pin Added Events ================ #
    # If the user has added an emoji reaction to the onboarding message
    elif event_type == "pin_added":
        user_id = slack_event["event"]["user"]
        # Update the onboarding message
        pyBot.update_pin(team_id, user_id)
        return make_response("Welcome message updates with pin", 200,)

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/install", methods=["GET"])
def pre_install():
    """This route renders the installation page with 'Add to Slack' button."""
    # Since we've set the client ID and scope on our Bot object, we can change
    # them more easily while we're developing our app.
    client_id = pyBot.oauth["client_id"]
    scope = pyBot.oauth["scope"]
    # Our template is using the Jinja templating language to dynamically pass
    # our client id and scope
    return render_template("install.html", client_id=client_id, scope=scope)


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    """
    This route is called by Slack after the user installs our app. It will
    exchange the temporary authorization code Slack sends for an OAuth token
    which we'll save on the bot object to use later.
    To let the user know what's happened it will also render a thank you page.
    """
    # Let's grab that temporary authorization code Slack's sent us from
    # the request's parameters.
    code_arg = request.args.get('code')
    # The bot's auth method to handles exchanging the code for an OAuth token
    pyBot.auth(code_arg)
    return render_template("thanks.html")


@app.route("/listening", methods=["GET", "POST"])
def hears():
    """
    This route listens for incoming events from Slack and uses the event
    handler helper function to route events to our Bot.
    """
    slack_event = json.loads(request.data)

    # ============= Slack URL Verification ============ #
    # In order to verify the url of our endpoint, Slack will send a challenge
    # token in a request and check for this token in the response our endpoint
    # sends back.
    #       For more info: https://api.slack.com/events/url_verification
    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                             "application/json"
                                                             })

    # ============ Slack Token Verification =========== #
    # We can verify the request is coming from Slack by checking that the
    # verification token in the request matches our app's settings
    if pyBot.verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s \npyBot has: \%s\n\n" % (slack_event["token"], pyBot.verification)
        # By adding "X-Slack-No-Retry" : 1 to our response headers, we turn off
        # Slack's automatic retries during development.
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    # ====== Process Incoming Events from Slack ======= #
    # If the incoming request is an Event we've subcribed to
    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        # Then handle the event by event_type and have your bot respond
        return _event_handler(event_type, slack_event)
    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\ you're looking for.", 404, {"X-Slack-No-Retry": 1})


# The parameters included in a slash command request (with example values):
#   token=gIkuvaNzQIHg97ATvDxqgjtO
#   team_id=T0001
#   team_domain=example
#   channel_id=C2147483705
#   channel_name=test
#   user_id=U2147483697
#   user_name=Steve
#   command=/weather
#   text=94070
#   response_url=https://hooks.slack.com/commands/1234/5678


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    """Parse the command parameters, validate them, and respond.
    Note: This URL must support HTTPS and serve a valid SSL certificate.
    """
    # Parse the parameters you need
    token = request.form.get('token', None)
    #TODO: validate the token
    command = request.form.get('command', None)
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    username = request.form.get('user_name', None)
    
    # Validate the request parameters
    if not token:  # or some other failure condition
        abort(400)

    pyBot.slashFeedback(user, text, username)

    return make_response("Slash command received", 200,)

@app.route("/gethelp", methods=["GET", "POST"])
def help():
    """Parse the command parameters, validate them, and respond.
    Note: This URL must support HTTPS and serve a valid SSL certificate.
    """
    # Parse the parameters you need
    token = request.form.get('token', None)
    #TODO: validate the token
    command = request.form.get('command', None)
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    username = request.form.get('user_name', None)
    
    # Validate the request parameters
    if not token:  # or some other failure condition
        abort(400)

    pyBot.getHelp(user, text, username)

    return make_response("Help command received", 200,)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    """Parse the command parameters, validate them, and respond.
    Note: This URL must support HTTPS and serve a valid SSL certificate.
    """
    # Parse the parameters you need
    token = request.form.get('token', None)
    #TODO: validate the token
    command = request.form.get('command', None)
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    username = request.form.get('user_name', None)
    
    # Validate the request parameters
    if not token:  # or some other failure condition
        abort(400)

    pyBot.getProfile(user, text, username)

    return make_response("Profile command received", 200,)

@app.route("/introduce", methods=["GET", "POST"])
def intro():
    """Parse the command parameters, validate them, and respond.
    Note: This URL must support HTTPS and serve a valid SSL certificate.
    """
    # Parse the parameters you need
    token = request.form.get('token', None)
    #TODO: validate the token
    command = request.form.get('command', None)
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    username = request.form.get('user_name', None)
    # Validate the request parameters
    if not token:  # or some other failure condition
        abort(400)
    # Use one of the following return statements
    # 1. Return plain text
    # return 'Simple plain response to the slash command received'
    # 2. Return a JSON payload
    # See https://api.slack.com/docs/formatting and
    # https://api.slack.com/docs/attachments to send richly formatted messages
    example = jsonify({
        # Uncomment the line below for the response to be visible to everyone
        'response_type': 'in_channel',
        'text': 'More fleshed out response to the slash command',
        'attachments': [
            {
                'fallback': 'Required plain-text summary of the attachment.',
                'color': '#36a64f',
                'pretext': 'Optional text above the attachment block',
                'author_name': 'Bobby Tables',
                'author_link': 'http://flickr.com/bobby/',
                'author_icon': 'http://flickr.com/icons/bobby.jpg',
                'title': 'Slack API Documentation',
                'title_link': 'https://api.slack.com/',
                'text': 'Optional text that appears within the attachment',
                'fields': [
                    {
                        'title': 'Priority',
                        'value': 'High',
                        'short': False
                    }
                ],
                'image_url': 'http://my-website.com/path/to/image.jpg',
                'thumb_url': 'http://example.com/path/to/thumb.png'
            }
        ]
    })

    pyBot.introduce(user, text,username)

    return make_response("Slash command received", 200,)


'''
ImmutableMultiDict([('user_id', u'U7YPRCW1K'), ('response_url', u'https://hooks.slack.com/commands/T7Y4C4BUH/280322015057/TMfBjazG3oRpt7k7OUodsSOJ'), 
('text', u'java'), ('token', u'Zq0U2r2vAJQs0zpClnDXJlm2'), ('trigger_id', u'281912064887.270148147969.c8b62205538f24c8fa9c681f5788e96a'), 
('channel_id', u'D7YLZ48FN'), ('team_id', u'T7Y4C4BUH'), ('command', u'/addskill'), 
('team_domain', u'testytestygroup'), ('user_name', u'siunami.matt'), 
('channel_name', u'directmessage')])
'''
@app.route("/addskill", methods=["GET", "POST"])
def addSkill():
    """Parse the command parameters, validate them, and respond.
    Note: This URL must support HTTPS and serve a valid SSL certificate.
    """
    print(request.form)
    # Parse the parameters you need
    token = request.form.get('token', None)
    #TODO: validate the token
    command = request.form.get('command', None)
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    # Validate the request parameters
    if not token:  # or some other failure condition
        abort(400)

    pyBot.addSkill(user, text)

    return make_response("Slash command received", 200,)


if __name__ == '__main__':
    app.run(debug=True)
