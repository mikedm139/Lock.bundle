import sqlite3

PREFIX = "/applications/lock"
# I would consider changing the prefix to '/video/lock' since some clients don't display "application" type plugins #

NAME = 'Lock'
ART  = 'art-default.jpg'
ICON = 'icon-default.png'
LOCK_ICON = 'Lock.png'
UNLOCK_ICON = 'Unlock.png'

PMS_SECTIONS = "http://localhost:32400/library/sections"

LOCK_COMMAND = "UPDATE metadata_items SET added_at='%s' WHERE library_section_id=%s; DELETE FROM library_sections WHERE id=%s;"
# % (section['section_created_at'], section['section_id'], section['section_id'])

UNLOCK_COMMAND = "sqlite3 %s \"UPDATE metadata_items SET added_at='%s' WHERE library_section_id=%s; INSERT OR REPLACE INTO library_sections (id,name,section_type,language,agent,scanner,created_at,updated_at,scanned_at,uuid) VALUES (%s,'%s',%s,'%s','%s','%s','%s','%s','%s','%s');\""
# % (DatabasePath(), section['section_created_at'], section['section_id'], 
#    section['section_id'], section['section_name'], section['section_type'], 
#    section['section_language'], section['section_agent'], section['section_scanner'],
#    section['section_created_at'], section['section_updated_at'],
#    section['section_updated_at'], section['section_uuid'])

def Start():
	HTTP.CacheTime = 0
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON)
	ObjectContainer.title = NAME

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
	oc.add(DirectoryObject(key=Callback(Lock, task="lock"), title="Lock", thumb=LOCK_ICON))
	oc.add(InputDirectoryObject(key=Callback(EnterPassword, path="unlock"), title="Unlock", prompt="Enter your password", thumb=UNLOCK_ICON)
	oc.add(InputDirectoryObject(key=Callback(EnterPassword, path="wizard"), title="Change Settings", prompt="Enter your password", thumb=ICON)
	return oc

''' Execute the "lock"/"unlock" command '''
@route(PREFIX + '/lock')
def Lock(task):
	# Open the database
	conn = sqlite3.connect(DatabasePath())
	
	for section in Dict['sections']:
		# Set up the command to pass to sqlite depending on whether we're locking or unlocking
		if task == "lock":
			command = LOCK_COMMAND % (section['section_created_at'], section['section_id'], section['section_id'])
		elif task == "unlock":
			command = UNLOCK_COMMAND % (section['section_created_at'], section['section_id'],
				section['section_id'], section['section_name'], section['section_type'], 
    			section['section_language'], section['section_agent'], section['section_scanner'],
    			section['section_created_at'], section['section_updated_at'],
				section['section_updated_at'], section['section_uuid'])
		
		#execute the given command
		conn.execute(command)

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
	oc.add(InputDirectoryObject(key=Callback(SetPassword), title="Set Password", prompt="Choose your password", thumb=R(ICON))))
	oc.add(InputDirectoryObject(key=Callback(SetPassword, confirm=True) title="Confirm Password", prompt="Confirm your password", thumb=R(ICON))))
	return oc

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
				section_id 			= section_id,
				section_name 		= section.get('title'),
				section_type 		= section.get('type'), # does this need to be converted to some specific int value ?
				section_language 	= section.get('language'),
				section_agent 		= section.get('agent'),
				section_scanner 	= section.get('scanner'),
				section_created_at 	= section.get('created_at'),
				section_updated_at 	= section.get('updated_at'),
				section_uuid 		= section.get('uuid')
			),
			title 	= title,
			sumary	= summary,
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
		
	# Force-save the Dict for good measure (shouldn't be necessary)
	Dict.save()
	
	# return a confirmation to the user
	return ObjectContainer(header=NAME, message="Section \"%s\" has been selected for locking." % section_name)
	
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
