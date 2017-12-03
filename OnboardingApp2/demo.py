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

def add_skills(skills_to_add):
    user = airtable.match('user-id', 'Dora')
    temp = str([x.strip() for x in skills_to_add.split(',')])
    print temp
    skills = {'Skills': str([x.strip() for x in skills_to_add.split(',')])}
    airtable.update(user['id'], skills)
    print "SKILLS OBJECT: "+str(skills)
    ### TODO: REMOVE THE APOSTROPHES AND SQUARE BRACKETS []

def get_mentor(skill):
    airtable.search('Skills', skill)
    print True

def main():
    if not not airtable.match('user-id', 'U7YPRCW1K'):
        found_user=airtable.match('user-id', 'U7YPRCW1K')
        fields = {'AboutMe': "Update intro"}
        airtable.update(found_user['id'], fields)
        # ^ make this more efficient, don't make it compute above line twice?
    else:
        new_user = {'user-id': 'U7YPRCW1K', 'Name': "Matt", 'AboutMe': "My intro"}
        airtable.insert(new_user)

    add_skills("python, javascript, being a sad broke college student")

if __name__ == "__main__":
    main()