import sqlite3

PREFIX = "/applications/lock"
# I would consider changing the prefix to '/video/lock' since some clients don't display "application" type plugins #

NAME = 'Lock'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
LOCK_ICON = 'Lock.png'
UNLOCK_ICON = 'Unlock.png'

PMS_SECTIONS = "http://localhost:32400/library/sections"

LOCK_COMMAND_1 = "UPDATE metadata_items SET added_at=?, metadata_type=20 WHERE library_section_id=?;"
# section['section_created_at'], section['section_id'] NB: metadata_type 20 = undefined and prevents items from showing up in Search
LOCK_COMMAND_2 = "DELETE FROM library_sections WHERE id=?;"
# section['section_id'])

UNLOCK_COMMAND_1 = "UPDATE metadata_items SET added_at=?, metadata_type=? WHERE library_section_id=?;"
# section['section_created_at'], section['section_type'], section['section_id']
UNLOCK_COMMAND_3 = "INSERT OR REPLACE INTO library_sections (id,name,section_type,language,agent,scanner,created_at,updated_at,scanned_at,uuid) VALUES (?,?,?,?,?,?,?,?,?,?);"
#    section['section_id'], section['section_name'], section['section_type'], 
#    section['section_language'], section['section_agent'], section['section_scanner'],
#    section['section_created_at'], section['section_updated_at'],
#    section['section_updated_at'], section['section_uuid'])

def Start():
	HTTP.CacheTime = 0
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	ObjectContainer.title1 = NAME

@handler(PREFIX, NAME, ICON, ART)
def MainMenu():
	# Check if the first run wizard has already been run
	if 'first_run_complete' not in Dict:
		# if not, run the Wizard
		return FirstRunWizard()
	else:
		# if it has already been run, continue to normal operations
		pass
	
	oc = ObjectContainer(no_cache=True)
	oc.add(DirectoryObject(key=Callback(Lock, task="lock"), title="Lock", thumb=R(LOCK_ICON)))
	oc.add(InputDirectoryObject(key=Callback(EnterPassword, path="unlock"), title="Unlock", prompt="Enter your password", thumb=R(UNLOCK_ICON)))
	oc.add(InputDirectoryObject(key=Callback(EnterPassword, path="wizard"), title="Change Settings", prompt="Enter your password", thumb=R(ICON)))
	return oc

''' Execute the "lock"/"unlock" command '''
@route(PREFIX + '/lock')
def Lock(task):
	# Open the database
	conn = sqlite3.connect(DatabasePath())
	
	for section_id in Dict['Sections']:
		s = Dict['Sections'][section_id]
		# Set up the command to pass to sqlite depending on whether we're locking or unlocking
		if task == "lock":
			conn.execute(LOCK_COMMAND_1, [s['section_created_at'], s['section_id']])
			conn.execute(LOCK_COMMAND_3, s['section_id'])
		elif task == "unlock":
			
			conn.execute(UNLOCK_COMMAND_1, [s['section_created_at'],s['section_type'],s['section_id']])
			conn.execute(UNLOCK_COMMAND_2, [s['section_id'],s['section_name'],s['section_type'],s['section_language'],
				s['section_agent'],s['section_scanner'],s['section_created_at'],s['section_updated_at'],s['section_updated_at'],s['section_uuid']])

	# Save our changes
	conn.commit()
	
	# And close the database connection
	conn.close()
	
	return ObjectContainer(header = 'Lock', message = 'Private section has been %sed' % task)
	
''' Prompt user for password before executing "unlock" '''
@route(PREFIX + '/unlock')
def EnterPassword(query, path):
	# compare given password to stored password
	if query == Dict['password']:
		if path == "unlock":
			return Lock(task="unlock")
		elif path == "wizard":
			return FirstRunWizard()
	else:
		return ObjectContainer(header=NAME, message="Incorrect Password")

''' Provide an easy way for users to set up the channel upon first use '''	
@route(PREFIX + '/wizard')
def FirstRunWizard():
	oc = ObjectContainer(title2="Setup")
	oc.add(DirectoryObject(key=Callback(SectionSelector), title="Select section(s) to lock"))
	oc.add(InputDirectoryObject(key=Callback(SetPassword), title="Set Password", prompt="Choose your password", thumb=R(ICON)))
	oc.add(InputDirectoryObject(key=Callback(SetPassword, confirm=True), title="Confirm Password", prompt="Confirm your password", thumb=R(ICON)))
	oc.add(DirectoryObject(key=Callback(FinishWizard), title="Exit Setup"))
	return oc

''' Set the first_run_complete flag and return to the main menu '''
@route(PREFIX + '/endwizard')
def FinishWizard():
	Dict['first_run_complete'] = True
	return MainMenu()

''' Query PMS to present user with list of sections '''
@route(PREFIX + '/sections')
def SectionSelector():
	
	oc = ObjectContainer(title2="Sections", no_cache=True)
	
	# check to see if sections are already tracked in the Dict
	if 'Sections' not in Dict:
		# if not, add a blank "Sections" key to the Dict
		Dict['Sections'] = {}
	else:
		pass
	
	# grab the section list from PMS
	pms_data = XML.ElementFromURL(PMS_SECTIONS)
	
	# parse it for the individual sections
	for section in pms_data.xpath('//Directory'):
		section_id = section.get('key')
		
		# Convert the string 'type' into the integers used in the DB
		section_type = section.get('type')
		if section_type == 'movie'	: type_int = 1
		elif section_type == 'show'	: type_int = 2
		elif section_type == 'artist'	: type_int = 8
		elif section_type == 'photo'	: type_int = 13
		
		# Convert the UNIX timestamp into the date format used in the DB
		created_timestamp = float(section.get('createdAt'))
		created_at = Datetime.FromTimestamp(created_timestamp).isoformat(' ')
		updated_timestamp = float(section.get('updatedAt'))
		updated_at = Datetime.FromTimestamp(updated_timestamp).isoformat(' ')
		
		# Present different title & summary depending on if the section is selected
		if section_id in Dict['Sections']:
			title 	= "[*] %s" % section.get('title')
			summary = "This section is selected for locking"
		else:
			title 	= "[ ] %s" % section.get('title')
			summary = "Select this section for locking"
		oc.add(DirectoryObject(
			key=Callback(
				SelectThiSection, 
				section_id 		= section_id,
				section_name 		= section.get('title'),
				section_type 		= type_int,
				section_language 	= section.get('language'),
				section_agent 		= section.get('agent'),
				section_scanner 	= section.get('scanner'),
				section_created_at 	= created_at,
				section_updated_at 	= updated_at,
				section_uuid 		= section.get('uuid')
			),
			title 	= title,
			summary	= summary,
			thumb 	= section.get('thumb')
			)
		)
	
	if len(Dict['Sections']) > 0:
		oc.add(DirectoryObject(key=Callback(ClearSelections), title="Clear Selected Section(s)", summary="Remove the selected section(s) and start over"))
	return oc

''' Save the selected section details to the Dict '''
@route(PREFIX + '/select')
def SelectThiSection(section_id, section_name, section_type, section_language, section_agent, section_scanner, section_created_at, section_updated_at, section_uuid):
	# Assign the given values to the Dict for storage
	Dict['Sections'][section_id] = {
		'section_id'		: section_id,
		'section_name'		: section_name,
		'section_type'		: section_type,
		'section_language'	: section_language,
		'section_agent'		: section_agent,
		'section_scanner'	: section_scanner,
		'section_created_at': section_created_at,
		'section_updated_at': section_updated_at,
		'section_uuid'		: section_uuid
		}
	
	# return a confirmation to the user
	return ObjectContainer(header=NAME, message="Section \"%s\" has been selected for locking." % section_name)

''' Remove all selected sections from the Dict '''
@route(PREFIX + '/clear')
def ClearSelections():
	Dict['Sections'] = {}
	return ObjectContainer(header=NAME, message="Stored section data has been purged")
	
''' Take the given password and save it in the Dict '''
@route(PREFIX + '/setpassword', confirm=bool)
def SetPassword(query, confirm=False):
	if not confirm:
		# Store the given password.
		Dict['password'] = query
		return ObjectContainer(header=NAME, message="Please confirm your password now.")
	else:
		if 'password' in Dict:
			# Compare the given password to the stored password 
			if query == Dict['password']:
				return ObjectContainer(header=NAME, message="Password confirmed.")
			else:
				return ObjectContainer(header=NAME, message="Passwords do not match. Please try again.")
		else:
			return ObjectContainer(header=NAME, message="Please enter a password before trying to confirm it.")

''' A method to return the path to the database independent of platform '''
@route(PREFIX + '/dbpath')
def DatabasePath():
	return Core.storage.join_path(Core.app_support_path, Core.config.plugin_support_dir_name, 'Databases', 'com.plexapp.plugins.library.db')
