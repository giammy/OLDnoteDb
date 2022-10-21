#!/usr/bin/env python3
import os
import sys
import requests
import json
import random
import time
import argparse
import datetime

#
# a command line interface to REST API of notes
# to get help use: ./client.py --help
#
# some usage examples:
# ./client.py --createEntity '{"__ENT__":"PC", "OWNER":"name1", "LOCATION":"office1"}'
# ./client.py --listEntities STAFFMEMBER   
# ./client.py --searchEntity '{"__ENT__":"PC", "OWNER":"name1"}'     
# ./client.py --searchEntity '{"__ENT__":"STAFFMEMBER", "GROUPNAME":"Group2"}'
# ./client.py --getEntity 6 

# theUrl = "http://127.0.0.1:8000/note"
# theUrl = "http://192.168.1.80/note"
theUrlBase = "http://127.0.0.1:8000"
theUrlToken = theUrlBase + "/token/" # the url to get the JWT token
theUrl = theUrlBase + "/note"


theUsername = ""
thePassword = ""
theAuthorizationToken = None


#
# the following 2 functions create an example entity called STAFFMEMBER, 
# they are invoked by the option --createManyStaffMembers NUM
# to fill the database for testing purposes
#
def createStaffMember(username, email, secondaryEmail, name, surname, groupName, leaderOfGroup, qualification, organization, totalHoursPerYear, totalContractualHoursPerYear, parttimePercent, isTimeSheetEnabled, created, validFrom, validTo, note, officePhone, officeLocation, internalNote, lastChangeAuthor, lastChangeDate):
    rid = createNote(rid=0, type="STAFFMEMBER", data="null") # if data="", the note is created with return code 400
    createNote(rid=rid, type="USERNAME", data=username)
    createNote(rid=rid, type="EMAIL", data=email)
    createNote(rid=rid, type="SECONDARYEMAIL", data=secondaryEmail)
    createNote(rid=rid, type="NAME", data=name)
    createNote(rid=rid, type="SURNAME", data=surname)
    createNote(rid=rid, type="GROUPNAME", data=groupName)
    createNote(rid=rid, type="LEADEROFGROUP", data=leaderOfGroup)
    createNote(rid=rid, type="QUALIFICATION", data=qualification)
    createNote(rid=rid, type="ORGANIZATION", data=organization)
    createNote(rid=rid, type="TOTALHOURSPERYEAR", data=totalHoursPerYear)
    createNote(rid=rid, type="TOTALCONTRACTUALHOURSPERYEAR", data=totalContractualHoursPerYear)
    createNote(rid=rid, type="PARTTIMEPERCENT", data=parttimePercent)
    createNote(rid=rid, type="ISTIMESHEETENABLED", data=isTimeSheetEnabled)
    createNote(rid=rid, type="CREATED", data=created)
    createNote(rid=rid, type="VALIDFROM", data=validFrom)
    createNote(rid=rid, type="VALIDTO", data=validTo)
    createNote(rid=rid, type="NOTE", data=note)
    createNote(rid=rid, type="OFFICEPHONE", data=officePhone)
    createNote(rid=rid, type="OFFICELOCATION", data=officeLocation)
    createNote(rid=rid, type="INTERNALNOTE", data=internalNote)
    createNote(rid=rid, type="LASTCHANGEAUTHOR", data=lastChangeAuthor)
    createNote(rid=rid, type="LASTCHANGEDATE", data=lastChangeDate)
    return rid

def createManyStaffMembers(num, numberOfGroups):
    startTime = time.time()
    for i in range(0, num):
        createStaffMember(username="username%d" % (i), email="email%d@email.it" % (i), secondaryEmail="email%d@email.it" % (i), name="name%d" % (i), surname="surname%d" % (i), groupName="Group%d"%(random.randint(1, numberOfGroups)), leaderOfGroup="leaderOfGroup%d" % (i), qualification="qualification%d" % (i), organization="organization%d" % (i), totalHoursPerYear="totalHoursPerYear%d" % (i), totalContractualHoursPerYear="totalContractualHoursPerYear%d" % (i), parttimePercent="parttimePercent%d" % (i), isTimeSheetEnabled="isTimeSheetEnabled%d" % (i), created="created%d" % (i), validFrom="validFrom%d" % (i), validTo="validTo%d" % (i), note="note%d" % (i), officePhone="officePhone%d" % (i), officeLocation="officeLocation%d" % (i), internalNote="internalNote%d" % (i), lastChangeAuthor="lastChangeAuthor%d" % (i), lastChangeDate="lastChangeDate%d" % (i))
    print("Created %d staff members in %s seconds" % (num, time.time() - startTime))

#
# general functions
#

def getCurrentDate():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+0000")

def printNote(note):
    print(note)
    # print("%i,%i,%i,%s,%s\n" % (note['id'],note['rid'],note['lid'],note['type'],note['data']))

#
# get JWT token
# MITICO! tutta la funzione
#
def getJWTToken(username, password):
    global theUrlToken
    resp = requests.post(url=theUrlToken,
                         # headers={"Content-Type": "application/json"}, 
                         data={'username': username, 'password': password})
    # print(theUrlToken)
    # if resp.status_code != 200:
    #     # print("Error: %s" % (resp.text))
    #     return resp.text
    # return resp.text
    return json.loads(resp.text)

def auxGetHeaders():
    global theAuthorizationToken
    if theAuthorizationToken is None:
        theAuthorizationToken = getJWTToken(theUsername, thePassword)
        # print("token-refresh: %s" % (theAuthorizationToken['refresh']))
        # print("token-access: %s" % (theAuthorizationToken['access']))

    if 'access' in theAuthorizationToken.keys():
        return {'Authorization': 'Bearer ' + theAuthorizationToken['access']}

    print("Error: %s" % (theAuthorizationToken))
    sys.exit()

def auxGetAndReturnList(url):
    resp = requests.get(url=url, headers=auxGetHeaders())
    if (resp.status_code == 200):
        #print(resp.content)
        #print(resp.json())
        return resp.json()
    else:
        return []

def getAllNotes():
    return auxGetAndReturnList(theUrl)

def getNote(id):
    return auxGetAndReturnList(theUrl + "/?id=%s" % (id))

def getNotesWithType(tagName):
    return auxGetAndReturnList(theUrl + "/?type=%s" % (tagName))

def getAttributesOfNote(id):
    return auxGetAndReturnList(theUrl + "/?rid=%d" % (id))

def getEntities(whichType):
    return auxGetAndReturnList(theUrl + "/?type=%s&rid=0" % (whichType))

# create a new note with a POST request
def createNote(rid, type, data):
    resp = requests.post(url=theUrl,
                         headers=auxGetHeaders(), 
                         json={"rid": rid, "lid": 0, "type": type, "data": data})
    # print(resp.status_code)
    if (resp.status_code == 200 or resp.status_code == 201 or resp.status_code == 202 or resp.status_code == 203):
        return resp.json()['id']
    else:
        return -1

# TODO
def isEntityAttributeDuplicate(rid, type, data):
    pass

def addAttributeToEntity(entityId, type, data):
    return createNote(rid=entityId, type=type, data=data)

def createEntity(jsonInfo):
    entityType = jsonInfo['__ENT__']
    rid = createNote(rid=0, type=entityType, data="__ENT__")
    for key in jsonInfo:
        if (key != '__ENT__'):
            createNote(rid=rid, type=key, data=jsonInfo[key])

def checkType(thisType, noteList):
    if len(noteList)<1:
        return False
    return noteList[0]['type'] == thisType

def searchEntity(jsonInfo):
    entityType = jsonInfo['__ENT__']
    del jsonInfo['__ENT__']
    firstKey = list(jsonInfo.keys())[0]
    firstValue = jsonInfo[firstKey]
    noteList = auxGetAndReturnList(theUrl + "/?type=%s&data=%s" % (firstKey, firstValue))
    idList = list(map(lambda x: x['rid'], noteList))
    resList = list(filter(lambda x: checkType(entityType, getNote(x)), idList))
    return resList

#
# Available operations
#         

def infoDb():
    note = getNotesWithType("__SYSTEM__")
    if len(note) == 0:
        return []
    else:  
        note = getAttributesOfNote(note[0]['id']) 
        return note

def initDb():
    if len(infoDb()) > 0:
        return False
    rid = createNote(rid=0, type="__SYSTEM__", data="__ENT__")
    if rid>0:
        createNote(rid=rid, type="CREATED", data=getCurrentDate())
        return True
    else:
        return False

def deleteNote(id):
    resp = requests.delete(url=theUrl + "/" + str(id), headers=auxGetHeaders())
    return(resp)

def resetDb():
    noteList = getAllNotes()
    for note in noteList:
        deleteNote(note['id'])

def countNotes():
    noteList = getAllNotes()
    return len(noteList)

def countEntities():
    noteList = getAttributesOfNote(0) 
    typeList = list(map(lambda x: x['type'], noteList))
    counted = {i:typeList.count(i) for i in typeList}
    return counted 

def printNotes():
    noteList = getAllNotes()
    for note in noteList:
        printNote(note)

def listEntities(whichType):
    noteList = getEntities(whichType)
    idList = list(map(lambda x: x['id'], noteList))
    return idList

def getEntity(id):
    noteList = getAttributesOfNote(id)
    return noteList

# MITICO!
def deleteEntity(id):
    noteList = getAttributesOfNote(id)
    for note in noteList:
        deleteNote(note['id'])
    deleteNote(id)

#
# users management
#

def userAddToGroup(username, groupName):
    print("Adding user %s to group %s" % (username, groupName))
    jsonText = '{"__ENT__":"__AUTHSETUSERGROUP__", "USERNAME":"%s", "GROUP":"%s"}' % (username, groupName)
    # print(jsonText)
    jsonInfo = json.loads(jsonText)
    createEntity(jsonInfo)

def auxUserAndGroupsList():
    idList = listEntities("__AUTHSETUSERGROUP__")
    userGroupNodeList = list(map(lambda x: getEntity(x), idList))
    userGroupList = list(map(lambda x: list(map(lambda y: y['data'], x)), userGroupNodeList))
    return(userGroupList)

def userList():
    print("Listing users")
    userList = list(map(lambda x: x[0], auxUserAndGroupsList()))
    print(userList)
    return None

def userGroupList():
    print("Listing active user groups")
    groupList = list(map(lambda x: x[1], auxUserAndGroupsList()))
    print(groupList)
    return None

def userRemoveFromGroup(username, groupName):
    print("Removing user %s from group %s" % (username, groupName))
    idList = listEntities("__AUTHSETUSERGROUP__")
    userGroupNodeList = list(map(lambda x: getEntity(x), idList))
    userGroupList = list(map(lambda x: list(map(lambda y: y['data'], x)), userGroupNodeList))
    for i in range(len(userGroupList)):
        if userGroupList[i][0] == username and userGroupList[i][1] == groupName:
            deleteEntity(idList[i])
            return True
    return False

#
# default authorization groups management
#

def getIdOfAuthGroupList():
    return(listEntities("AUTHGROUPLIST"))

def groupList():
    print("Listing default authorization groups (AUTHGROUPLIST):")
    ids = getIdOfAuthGroupList()
    if len(ids) == 1:
        entity = getEntity(ids[0])
        #print(entity)
        for attr in entity:
            print(attr['data'])
    else:
        print("Error: no AUTHGROUPLIST found")
    return None

def groupAdd(groupName):
    print("Adding one default group: %s" % (groupName))
    ids = getIdOfAuthGroupList()

    if len(ids) > 1:
        print("More than 1 AUTHGROUPLIST: remove the extra ones")
        return None

    if len(ids) < 1:
        print("No AUTHGROUPLIST: creating one")
        id = createNote(rid=0, type="AUTHGROUPLIST", data="__ENT__")
    else:
        id = ids[0]

    # add attribute to entity
    addAttributeToEntity(id, "GROUPNAME", groupName)
    return None
    
# MITICO! tutta la funzione
def groupRemove(groupName):
    print("Removing one default group: %s" % (groupName))
    ids = getIdOfAuthGroupList()

    if len(ids) > 1:
        print("More than 1 AUTHGROUPLIST: remove the extra ones")
        return None

    if len(ids) < 1:
        print("No AUTHGROUPLIST: nothing to remove")
        return None

    id = ids[0]
    entity = getEntity(id)
    #print(entity)
    for attr in entity:
        if attr['type'] == "GROUPNAME" and attr['data'] == groupName:
            deleteNote(attr['id'])
            return None
    print("Group %s not found" % (groupName))
    return None
#
# main
#

def main():
    global theUrl
    global theUsername
    global thePassword
    global theAuthorizationToken

    parser = argparse.ArgumentParser()

    # general db operations
    parser.add_argument('--infoDb', help='Show some info on the database', action='store_true')
    parser.add_argument('--initDb', help='Initialize the database', action='store_true')
    parser.add_argument('--resetDb', help='Reset the database. WARNING: ALL DATA WILL BE DELETED', action='store_true')

    # notes operations
    parser.add_argument('--countNotes', help='Count all the notes present in the database', action='store_true')  
    parser.add_argument('--printNotes', help='Print all the notes present in the database', action='store_true')

    # entities operations
    parser.add_argument('--countEntities', help='Count all the entities present in the database', action='store_true')
    parser.add_argument('--listEntities', help='List all the entities of given type', metavar='TYPE') 
    parser.add_argument('--createEntity', help='Create a new entity from the given JSON', 
                        metavar='{"__ENT__":"PC", "OWNER":"name1", "LOCATION":"office1"}')
    parser.add_argument('--searchEntity', help='Search an entity from the given JSON (search on 1 property only)', 
                        metavar='{"__ENT__":"PC", "OWNER":"name1"}')
    parser.add_argument('--getEntity', help='Get an entity', type=int, metavar='ID')
    parser.add_argument('--deleteEntity', help='Delete an entity', type=int, metavar='ID')

    # testing flag
    parser.add_argument('--createManyStaffMembers', help='Create may staff members', type=int, metavar='NUM')

    # user management
    parser.add_argument('--userAddToGroup', help='Add a user to a group', metavar='username groupname', nargs='*', type=str)
    parser.add_argument('--userRemoveFromGroup', help='Remove a user from a group', metavar='username groupname', nargs='*', type=str)
    parser.add_argument('--userList', help='List users', action='store_true')
    parser.add_argument('--userGroupList', help='List active groups', action='store_true')

    # groups management
    parser.add_argument('--groupAdd', help='Add a new default authorization group', metavar='GROUPNAME')
    parser.add_argument('--groupRemove', help='Remove a new default authorization group', metavar='GROUPNAME')
    parser.add_argument('--groupList', help='List default authorization groups', action='store_true') 

    # configuration for accessing the database
    parser.add_argument('--host', help='Set the host', metavar='URL of the host') 
    parser.add_argument('--username', help='username for connection', type=str, metavar='username')
    parser.add_argument('--password', help='password for connection', type=str, metavar='password') 

    args = parser.parse_args()

    # check if a username and password are provided by environment variables
    theUrl = os.environ.get("NOTEDB_URL", theUrl)
    theUsername = os.getenv("NOTEDB_USERNAME", theUsername)
    thePassword = os.getenv("NOTEDB_PASSWORD", thePassword)

    # if the flag is present, we need to set hostname, username, password
    if args.__dict__['host'] != None:        
        theUrl = args.__dict__['host']
    if args.__dict__['username'] != None:        
        theUsername = args.__dict__['username']
    if args.__dict__['password'] != None:        
        thePassword = args.__dict__['password']

    # 
    # get the authorization token and store it for the following calls
    auxGetHeaders() 
    print("User %s connected on remote API host: %s" % (theUsername, theUrl))

    for k, arg in args.__dict__.items():
        match k:

            # general db operations
            case 'infoDb':
                if arg:
                    print("Show info about the database:")
                    res = infoDb()
                    if len(res) > 0:
                        print(res)
                    else:
                        print("Database not initialized.")  
                continue
            case 'initDb':
                if arg:
                    print("Initializing the database")
                    if initDb():
                        print("Database initialized")
                    else:
                        print("Database not initialized")
                continue
            case 'resetDb':
                if arg:
                    print("Resetting the database")
                    resetDb()
                continue

            # notes operations
            case 'countNotes':
                if arg:
                    print("Counting the notes in the database: %d" % (countNotes()))
                continue
            case 'printNotes':
                if arg:
                    print("Printing the notes in the database:")
                    printNotes()
                continue

            # entities operations
            case 'countEntities':
                if arg:
                    print("Counting the entities in the database: %s" % (countEntities()))
                continue
            case 'listEntities':
                if arg != None:
                    print("List the entities in the database: %s" % (listEntities(arg)))
                continue
            case 'createEntity':
                if arg != None:
                    print("Creating entity: %s" % (arg))
                    convertedArg = json.loads(arg)
                    createEntity(convertedArg)
                continue
            case 'searchEntity':
                if arg != None:
                    print("Searching entity: %s" % (arg))
                    convertedArg = json.loads(arg)
                    res = searchEntity(convertedArg)
                    print(res)
                continue
            case 'getEntity':
                if arg != None:
                    print("Getting entity: %s" % (arg))
                    res = getEntity(arg)
                    print(res)
                continue
            case 'deleteEntity':
                if arg != None:
                    print("Deleting entity: %s" % (arg))
                    res = deleteEntity(arg)
                    print(res)
                continue

            # testing flag
            case 'createManyStaffMembers':
                if arg != None:
                    print("Creating %d staff members" % (arg))
                    createManyStaffMembers(arg, 10)
                continue

            # user management
            case 'userAddToGroup':
                if arg != None:
                    userAddToGroup(arg[0], arg[1])
                continue
            case 'userRemoveFromGroup':
                if arg != None:
                    userRemoveFromGroup(arg[0], arg[1])
                continue
            case 'userList':
                if arg:
                    userList()
                continue
            case 'userGroupList':
                if arg:
                    userGroupList()
                continue

            # groups management
            case 'groupAdd':
                if arg:
                    groupAdd(arg)
                continue
            case 'groupRemove':
                if arg:
                    groupRemove(arg)
                continue
            case 'groupList':
                if arg:
                    groupList()
                continue

            # configuration for accessing the database
            case 'host':
                # just to avoid the "Unmanaged flag" warning
                pass
            case 'username':
                # just to avoid the "Unmanaged flag" warning
                pass            
            case 'password':
                # just to avoid the "Unmanaged flag" warning
                pass
            case _:
                print("Unmanaged flag: %s" % (k))

main()
