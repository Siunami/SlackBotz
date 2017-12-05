# -*- coding: utf-8 -*-
"""
Python Slack Bot class for use with the pythOnBoarding app
"""
import os
import message

from slackclient import SlackClient

import Airtable

# print airtable.get_all()

# To remember which teams have authorized your app and what tokens are
# associated with each team, we can store this information in memory on
# as a global object. When your bot is out of development, it's best to
# save this in a more persistant memory store.
authed_teams = {}


class Bot(object):
    """ Instanciates a Bot object to handle Slack onboarding interactions."""
    def __init__(self):
        super(Bot, self).__init__()
        self.airtable = Airtable.Airtable('appAUfzTdcqhV88YO', 'demo')
        self.name = "pythonboardingbot"
        self.emoji = ":robot_face:"
        # When we instantiate a new bot object, we can access the app
        # credentials we set earlier in our local development environment.
        self.oauth = {"client_id": os.environ.get("CLIENT_ID"),
                      "client_secret": os.environ.get("CLIENT_SECRET"),
                      # Scopes provide and limit permissions to what our app
                      # can access. It's important to use the most restricted
                      # scope that your app will need.
                      "scope": "bot"}
        self.verification = os.environ.get("VERIFICATION_TOKEN")
        ["python"]
        # NOTE: Python-slack requires a client connection to generate
        # an oauth token. We can connect to the client without authenticating
        # by passing an empty string as a token and then reinstantiating the
        # client with a valid OAuth token once we have one.
        self.client = SlackClient(os.environ.get("OAUTH_KEY"))
        # We'll use this dictionary to store the state of each message object.
        # In a production envrionment you'll likely want to store this more
        # persistantly in  a database.
        self.messages = {}

    def auth(self, code):
        """
        Authenticate with OAuth and assign correct scopes.
        Save a dictionary of authed team information in memory on the bot
        object.

        Parameters
        ----------
        code : str
            temporary authorization code sent by Slack to be exchanged for an
            OAuth token

        """
        # After the user has authorized this app for use in their Slack team,
        # Slack returns a temporary authorization code that we'll exchange for
        # an OAuth token using the oauth.access endpoint
        auth_response = self.client.api_call(
                                "oauth.access",
                                client_id=self.oauth["client_id"],
                                client_secret=self.oauth["client_secret"],
                                code=code
                                )
        # To keep track of authorized teams and their associated OAuth tokens,
        # we will save the team ID and bot tokens to the global
        # authed_teams object
        team_id = auth_response["team_id"]
        authed_teams[team_id] = {"bot_token":
                                 auth_response["bot"]["bot_access_token"]}
        # Then we'll reconnect to the Slack Client with the correct team's
        # bot token
        self.client = SlackClient(authed_teams[team_id]["bot_token"])

    def open_dm(self, user_id):
        """
        Open a DM to send a welcome message when a 'team_join' event is
        recieved from Slack.

        Parameters
        ----------
        user_id : str
            id of the Slack user associated with the 'team_join' event

        Returns
        ----------
        dm_id : str
            id of the DM channel opened by this method
        """
        new_dm = self.client.api_call("im.open",
                                      user=user_id)
        print(new_dm)
        dm_id = new_dm["channel"]["id"]
        return dm_id

    def getProfile(self, userid, text, username):
        ## TODO: Currently searching by non-unique name.
        ## Need to use unique value
        member = self.airtable.match('Name', str(text))
        print(member)
        if not member:
            post_message = self.client.api_call(
                              "chat.postMessage",
                              channel=userid,
                              text="Sorry we couldn't find a user with that name. Try /search [skill] to find others",
                              # attachments=attach,
                              icon_emoji=":bust_in_silhouette:",
                              # attachments=text, #messageObj.create_attachments2(text),
                              username = "Profile Bot"
                              # user=userid,
                              # as_user=True
                            )
        else:
            user = member['fields']['Name']
            skills = member['fields']['Skills'].split(',')
            aboutme = member['fields']['AboutMe']
            kudos = member['fields']['kudos']
            numPosts = member['fields']['num-posts']
            badges = member['fields']['badges'].split(',')
            mySkills = ""
            print skills
            for x in range(0,len(skills)):
                if x == len(skills)-1:
                    mySkills = mySkills + skills[x]
                else:
                    mySkills = mySkills + skills[x] + ", "
            print badges
            myBadges = ""
            for badge in badges:
                myBadges = myBadges + badge + ", "

            # texts = "Member: <@" + str(username) + ">\n" + "Skills: " + mySkills + "\n" + "About Me: " + aboutme + "\n" + "Kudos: " + str(kudos) + "\n" + "Post Count: " + str(numPosts) + "\n" + "Badges: " + myBadges
            attach = [{
                        # "fallback": "ReferenceError - UI is not defined: https://honeybadger.io/path/to/event/",
                        "text": "<@" + user + "> " + "Score " + str(kudos),
                        "fields": [
                            {
                                "title": "Skills",
                                "value": mySkills,
                                "short": True
                            },
                            {
                                "title": "Posts",
                                "value": numPosts,
                                "short": True
                            },
                            {
                                "title": "About",
                                "value": aboutme
                                # "short": True
                            },
                            {
                                "title": "Badges",
                                # "value": badges
                                "value": "Shows 5 most recent badges. Click to show more"
                                # "short": True
                            }
                        ],
                        "color": "#F35A00"
                    }]
            post_message = self.client.api_call(
                              "chat.postMessage",
                              channel=userid,
                              # text=texts,
                              attachments=attach,
                              icon_emoji=":bust_in_silhouette:",
                              # attachments=text, #messageObj.create_attachments2(text),
                              username = "Profile Bot"
                              # user=userid,
                              # as_user=True
                            )
        # print("Make profile card")
        # print(userid)


# TODO: getHelp and find both need to find a person based on a given skill
# get_all fields Skills and Name. Any name that is successful is added to list
# anyone in list is potential for member = self.airtable.match('Name', str(text))

    def find(self, userid,textresponse, username):
        people = self.airtable.get_all(fields=['Name','Skills'])
        post_message = self.client.api_call(
                                      "chat.postMessage",
                                      channel="U7YPRCW1K",
                                      text="<@" + str(username) + "> says: " + textresponse,
                                      # attachments=text, #messageObj.create_attachments2(text),
                                      username='Feedback Bot',
                                      icon_emoji=':speech_balloon:'
                                    )

# people = self.airtable.get_all(fields=['Name','Skills'])
# [{u'createdTime': u'2017-12-03T01:09:36.000Z', u'fields': {u'Skills': u'python,skills,java,webdevelopment',
#  u'Name': u'siunami.matt'}, u'id': u'rec1DJ7xxNBUkJodG'}, {u'createdTime': u'2017-12-03T01:40:57.000Z', u'fields': 
#  {u'Skills': u'python, javascript, java', u'Name': u'luce'}, u'id': u'recBGkY4xEP4vfdzl'}, 
#  {u'createdTime': u'2017-12-03T01:41:04.000Z', u'fields': {u'Name': u'Default'}, u'id': u'recJgF2UK061rLLgC'}, 
#  {u'createdTime': u'2017-12-04T09:18:56.000Z', u'fields': {}, u'id': u'recewChBuqCi9Lb2q'}]

    def getHelp(self, userid, text, username):

        print("Get help")
        people = self.airtable.get_all(fields=['Name','Skills'])
        print(people)
        foundPerson = False

        # Start at a random spot in the list.
        # First search for person with all skills tagged in question
        # Then with all skills - 1, etc.
        # On match, send dm to person with question in attachment. Yes/No
        # Yes answer starts a dm with the question asker.


        # while not foundPerson:
        #     individual = people[0]
        #     if not individual['fields']:
        #         fieldKeys = individual['fields'].keys()
        #         for key in fieldKeys:
        #             if key == "Skills":
        #                 skills = individual['fields']['Skills']
        #                 # print individual
        #                 for skill in skills:
        #                     if skill == text:
        #                         foundPerson = True
        #                         mentor = individual
        #                         print(mentor)
        #     people.pop(0)
        #     if len(people) == 0:
        #         foundPerson = True

        # if not not self.airtable.match('user-id', str(userid)):
        #     found_user= self.airtable.match('user-id', str(userid))
        #     fields = {'AboutMe': str(textresponse)}
        #     self.airtable.update(found_user['id'], fields)
        # else:
        post_message = self.client.api_call(
                          "chat.postMessage",
                          channel=userid,
                          text="We will notify you when someone can help you with your question: \n" + text,
                          # attachments=text, #messageObj.create_attachments2(text),
                          username = "Help Bot",
                          icon_emoji=":question:"
                          # user=userid,
                          # as_user=True
                        )
            # new_user = {'user-id': str(userid), 'Name': username, 'AboutMe': textresponse}
            # self.airtable.insert(new_user)


    def updateSkill(self, userid,textresponse):
        skills = textresponse.split(",")
        print(textresponse)
        # messageObj = message.Message()
        # admin = self.open_dm('U7YPRCW1K')
        # print(userid)
        mySkills = ""
        updateSkills = ""
        for x in range(0,len(skills)):
            if x == len(skills) - 1:
                updateSkills = updateSkills + skills[x].strip().lower()
            else:
                updateSkills = updateSkills + skills[x].strip().lower() + ","
            mySkills = mySkills + "+ " + skills[x].strip().lower() + "\n"
        # DONE: Need to grab current skills and only add new skills
        user = self.airtable.match('user-id', str(userid))
        skillList = ""
        newSkills = updateSkills.split(",")
        # TODO: Only get fields skills if it exists.
        # Otherwise error will occur
        # if not currentSkills['fields']:
        currentSkills = user['fields']['Skills'].split(",")
        # DONE only add new skills that are not current skills
        # for nskill in newSkills:
        newSkill = updateSkills.split(",")
        for nskill in newSkill:
            if nskill not in currentSkills:
                currentSkills.append(nskill)

        allSkills = ''
        for x in range(0,len(currentSkills)):
                    #Add to airtable
                    if x == len(currentSkills) - 1:
                        allSkills = allSkills + currentSkills[x].strip().lower()
                    else:
                        allSkills = allSkills + currentSkills[x].strip().lower() + ","
        # temp = str([x.strip() for x in textresponse.split(',')])
        print(allSkills)
        skills = { 'Skills':allSkills }
        self.airtable.update(user['id'], skills)
        print "SKILLS OBJECT: " + str(skills)
        # if not not self.airtable.match('user-id', str(userid)):
        #     found_user= self.airtable.get('user-id', str(userid))
        #     print(found_user)
        #     # fields = {'Skills': }
        #     # self.airtable.update(found_user['id'], fields)
        # else:
        #     new_user = {'user-id': str(userid), 'Name': username, 'Skills': textresponse}
        #     self.airtable.insert(new_user)
        post_message = self.client.api_call(
                                      "chat.postMessage",
                                      channel=userid,
                                      text="You added skills to your profile: \n" + mySkills,
                                      # attachments=text, #messageObj.create_attachments2(text),
                                      username = "Skillz Bot",
                                      icon_emoji = ":muscle:"
                                      # user=userid,
                                      # as_user=True
                                    )

    def removeskill(self, userid,textresponse):
        #TODO very similar to updateskill. Refactor updateskill first
        post_message = self.client.api_call(
                              "chat.postMessage",
                              channel=userid,
                              text="You removed skills to your profile: \n" + mySkills,
                              # attachments=text, #messageObj.create_attachments2(text),
                              username = "Skillz Bot",
                              icon_emoji = ":muscle:"
                              # user=userid,
                              # as_user=True
                            )

    def about(self, userid,textresponse,username):
        print("Got here slash")
        # messageObj = message.Message()
        # admin = self.open_dm('U7YPRCW1K')
        print(userid)
        if not not self.airtable.match('user-id', str(userid)):
            found_user= self.airtable.match('user-id', str(userid))
            fields = {'AboutMe': textresponse}
            self.airtable.update(found_user['id'], fields)
            post_message = self.client.api_call(
                              "chat.postMessage",
                              channel=userid,
                              text="Successfully updated about me.",
                              # attachments=text, #messageObj.create_attachments2(text),
                              username = "Welcome Bot",
                              icon_emoji = ":wave:"
                              # user=userid,
                              # as_user=True
                            )
        else:
            new_user = {'user-id': str(userid), 'Name': username, 'AboutMe': textresponse}
            self.airtable.insert(new_user)
            post_message = self.client.api_call(
                                          "chat.postMessage",
                                          channel="#intros",
                                          text="<@" + username + "> introduced themself. Welcome them to the community! \n" + textresponse,
                                          # attachments=text, #messageObj.create_attachments2(text),
                                          username = "Welcome Bot",
                                          icon_emoji = ":wave:"
                                          # user=userid,
                                          # as_user=True
                                        )

    def slashFeedback(self, userid,textresponse, username):
        print("Got here slash")
        # messageObj = message.Message()
        admin = self.open_dm('U7YPRCW1K')
        post_message = self.client.api_call(
                                      "chat.postMessage",
                                      channel="U7YPRCW1K",
                                      text="<@" + str(username) + "> says: " + textresponse,
                                      # attachments=text, #messageObj.create_attachments2(text),
                                      username='Feedback Bot',
                                      icon_emoji=':speech_balloon:'

                                    )


    def copycat(self, slackevent):
    # def copycat(self, team_id, user_id, slackevent):
        # message_obj = self.messages[team_id][user_id]
        user = self.open_dm(slackevent['event']['user'])
        print(slackevent['event']['user'])
        print("Got here")
        post_message = self.client.api_call(
                                      "chat.postMessage",
                                      channel='#intros',
                                      text='hello from bot! Matthew sent a message: ' + str(slackevent['event']['text']),
                                      user=str(slackevent['event']['user'])
                                    )



    def onboarding_message(self, team_id, user_id):
        """
        Create and send an onboarding welcome message to new users. Save the
        time stamp of this message on the message object for updating in the
        future.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # We've imported a Message class from `message.py` that we can use
        # to create message objects for each onboarding message we send to a
        # user. We can use these objects to keep track of the progress each
        # user on each team has made getting through our onboarding tutorial.

        # First, we'll check to see if there's already messages our bot knows
        # of for the team id we've got.
        if self.messages.get(team_id):
            # Then we'll update the message dictionary with a key for the
            # user id we've recieved and a value of a new message object
            self.messages[team_id].update({user_id: message.Message()})
        else:
            # If there aren't any message for that team, we'll add a dictionary
            # of messages for that team id on our Bot's messages attribute
            # and we'll add the first message object to the dictionary with
            # the user's id as a key for easy access later.
            self.messages[team_id] = {user_id: message.Message()}
        message_obj = self.messages[team_id][user_id]
        # Then we'll set that message object's channel attribute to the DM
        # of the user we'll communicate with
        message_obj.channel = self.open_dm(user_id)
        # We'll use the message object's method to create the attachments that
        # we'll want to add to our Slack message. This method will also save
        # the attachments on the message object which we're accessing in the
        # API call below through the message object's `attachments` attribute.
        message_obj.create_attachments()
        # TODO: On creation of new member, create a profile for them with default values
        # Then in onboarding. Tell them to do /profile and update anything they want anytime

        post_message = self.client.api_call("chat.postMessage",
                                            channel=message_obj.channel,
                                            username=self.name,
                                            icon_emoji=self.emoji,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        timestamp = post_message["ts"]
        # We'll save the timestamp of the message we've just posted on the
        # message object which we'll use to update the message after a user
        # has completed an onboarding task.
        message_obj.timestamp = timestamp

    def update_emoji(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "reaction_added"
        event from Slack. Update timestamp for welcome message.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Add an emoji reaction to this "
                                         "message*~ :thinking_face:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.emoji_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def update_introduce(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "pin_added"
        event from Slack. Update timestamp for welcome message.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Tell us about yourself*~ "
                                         ":wave:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.pin_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def update_pin(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "pin_added"
        event from Slack. Update timestamp for welcome message.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Pin this message*~ "
                                         ":round_pushpin:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.pin_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]

    def update_share(self, team_id, user_id):
        """
        Update onboarding welcome message after recieving a "message" event
        with an "is_share" attachment from Slack. Update timestamp for
        welcome message.

        Parameters
        ----------
        team_id : str
            id of the Slack team associated with the incoming event
        user_id : str
            id of the Slack user associated with the incoming event

        """
        # These updated attachments use markdown and emoji to mark the
        # onboarding task as complete
        completed_attachments = {"text": ":white_check_mark: "
                                         "~*Share this Message*~ "
                                         ":mailbox_with_mail:",
                                 "color": "#439FE0"}
        # Grab the message object we want to update by team id and user id
        message_obj = self.messages[team_id].get(user_id)
        # Update the message's attachments by switching in incomplete
        # attachment with the completed one above.
        message_obj.share_attachment.update(completed_attachments)
        # Update the message in Slack
        post_message = self.client.api_call("chat.update",
                                            channel=message_obj.channel,
                                            ts=message_obj.timestamp,
                                            text=message_obj.text,
                                            attachments=message_obj.attachments
                                            )
        # Update the timestamp saved on the message object
        message_obj.timestamp = post_message["ts"]
