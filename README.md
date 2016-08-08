# Trello2JiraCSV
A simple python script to convert free Trello json exports to a csv format ready for importing with Jira.

## Features
* Cards become Jira Issues
* All description, label and attachment data is carried over
* Checklists of cards are created as subtasks of original issue in Jira
* Resolution will be carried over if using "To Do" "In Progress" and "Done" lists (Could easily be customised)

## Options
* --list_as_component - Useful if list names in Trello are being used as categories, these will be used as components rather than resolution

## Known limitations
Currently supports a maximum of 8 labels and 2 attachments per card.
If you need more simply update the maxLabels/maxAttachments variables and the headerLine variable

## To Do
Add pre pass to work our the maximum amount of attachments and labels and generate the headerline accordingly (See above)

## Notes
This was a quick script to move over our existing workflow to Jira after having lots of trouble with the default Trello importer for Jira, hopefully it's of help to others!

Please feel free to contribute :)
