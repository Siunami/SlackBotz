import Airtable

airtable = Airtable.Airtable('appAUfzTdcqhV88YO', 'demo')

# print "RESULTS: " + str(airtable.search('user-id', 'Test'))


# check if user's id is in table
def find_user(id):
    response = airtable.match('user-id', id)
    if not response:
        print "User not found"
        return False
    else:
        print "USER FOUND!!!!!"
        return True


def main():
    dummy = {'user-id': 'Banana'}
    # if slack user's id is already in airtable
    if find_user('Mikeyboy'):
        found_user=airtable.match('user-id', 'Mikeyboy')
        print str(found_user)
        # ^ make this more efficient, don't make it compute above line twice?
    else:
        new_user = {'user-id': 'Mikeyboy', 'Name': 'Jones', 'Notes': 'Likes tunnels'}
        airtable.insert(new_user)


if __name__ == "__main__":
    main()