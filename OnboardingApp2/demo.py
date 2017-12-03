import Airtable

airtable = Airtable.Airtable('appAUfzTdcqhV88YO', 'demo')

# print "RESULTS: " + str(airtable.search('user-id', 'Test'))


# check if user's id is in table
def find_user(id):
    response = airtable.match('user-id', id)
    if not response:
        return False
    else:
        return True


def main():
    if not not airtable.match('user-id', 'U7YPRCW1K'):
        found_user=airtable.match('user-id', 'U7YPRCW1K')
        fields = {'AboutMe': "Update intro"}
        airtable.update(found_user['id'], fields)
        # ^ make this more efficient, don't make it compute above line twice?
    else:
        new_user = {'user-id': 'U7YPRCW1K', 'Name': "Matt", 'AboutMe': "My intro"}
        airtable.insert(new_user)


if __name__ == "__main__":
    main()