unlockplex="UPDATE metadata_items SET added_at='2013-11-08 22:47:07' WHERE library_section_id=<THESECTIONNUMBERYOUWANTTOHIDE>; INSERT OR REPLACE INTO library_sections (id,name,section_type,language,agent,scanner,created_at,updated_at,scanned_at,uuid)
VALUES (<THESECTIONNUMBERYOUWANTTOHIDE>,'<SECTIONNAME>',1,'en','com.plexapp.agents.imdb','Plex Movie Scanner','2013-11-08 22:47:07','2013-11-09 21:53:28','2013-11-09 21:53:28','<UUIDOFYOURSECTION>');"

cd /Applications
./sqlite3 ~/Library/Application\ Support/Plex\ Media\ Server/Plug-in\ Support/Databases/com.plexapp.plugins.library.db "$unlockplex"

.exit

exit;