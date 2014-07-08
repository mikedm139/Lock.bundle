lockplex="UPDATE metadata_items SET added_at='2013-11-08 22:47:07' WHERE library_section_id=<THESECTIONNUMBERYOUWANTTOHIDE>; DELETE FROM library_sections WHERE id=<THESECTIONNUMBERYOUWANTTOHIDE>;"

sqlite3 ~/Library/Application\ Support/Plex\ Media\ Server/Plug-in\ Support/Databases/com.plexapp.plugins.library.db "$lockplex"

.exit

exit;