#! /usr/bin/python

# MIT License

# Copyright (c) 2016 Harry Rose - Semaeopus Ltd.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import json
import optparse

# Add an item to the csv row
# Will re-encode to utf8 and wrap quotes around text that contains quotes
def AddCSVItem(str):
	global csvData
	finalStr = str.encode("utf8")
	finalStr = finalStr.replace("\"", "\"\"")
	csvData += "\"{0}\",".format(finalStr)

# Iterate a tasks checklist and generate subtasks
def AddCheckListAsSubTasks(checkListID, parentID):
	if checkListID:
		for checkList in checklistDict[checkListID[0]]:
			status = "Done" if checkList["state"] == "complete" else "To Do"
			resolution = "Done" if status == "Done" else ""
			AddIssue("Sub-Task", "", parentID, status, resolution, checkList["name"], "", "", "", None)

# End the csv row with a simple newline
def EndCSVLine():
	global csvData
	csvData += "\n"

# Take all the information for an issue and convert it into a csv line
def AddIssue(issuetype, IssueID, ParentID, Status, resolution, summary, description, attachments, component, labels):
	AddCSVItem(issuetype)
	AddCSVItem(IssueID)
	AddCSVItem(ParentID)
	AddCSVItem(Status)
	AddCSVItem(resolution)
	AddCSVItem(summary)
	AddCSVItem(description)
	AddCSVItem(component)

	# Handle attachments
	numAttachments = len(attachments) if attachments != None else 0
	if numAttachments > maxAttachments:
		print "\tError! - {0} Attachments found in \"{1}\". Card will be skipped, only {2} will be handled. Update header line and maxAttachments value".format(numAttachments, summary, maxAttachments)
		return 1

	for i in range(numAttachments):
		AddCSVItem(attachments[i]["url"])
	for i in range(numAttachments, maxAttachments):
		AddCSVItem("")

	numLabels = len(labels) if labels != None else 0
	if numLabels > maxLabels:
		print "\tError! - {0} labels found in \"{1}\". Card will be skipped, only {1} will be handled. Update header line and maxLabels value".format(numLabels, summary, maxLabels)
		return 1

	for i in range(numLabels):
		label = labels[i]["name"]
		label = label.replace(" ", "_")
		AddCSVItem(label)
	for i in range(numLabels, maxLabels):
		AddCSVItem("")

	EndCSVLine()

# Set up the parser for options
parser = optparse.OptionParser(version='TrelloJson2JiraCSV v1.0.0')

parser.add_option('-j', '--json'        , dest="jsonPath"   	, action="store"         , help="The path to the trello json file")
parser.add_option('--list_as_component' , dest="listAsComp"    	, action="store_true"    , help="Use the list as a component in Jira rather than setting it as a status", default=False)

(opts, args) = parser.parse_args()

if not opts.jsonPath:
	parser.print_help()
	exit(1)

# Set up variables
jsonPath 		= opts.jsonPath
csvPath 		= jsonPath.replace(".json", ".csv")
listDict 		= {}
checklistDict 	= {}
headerLine 		= "issuetype, Issue ID, Parent ID, Status, Resolution, summary, description, component, attachment, attachment, label, label, label, label, label, label, label, label\n"
csvData 		= ""
maxLabels 		= 8
maxAttachments  = 2

print "Loading " + jsonPath

# Load json data
with open(jsonPath) as data_file:
    data = json.load(data_file)

# Build up our list of list ids to names as trello items only contain ids, we'll use this to map between the two
for list in data["lists"]:
	listDict[list["id"]] = list["name"]

# Same as above to checklists, build up a id to name map
for checkList in data["checklists"]:
	checklistDict[checkList["id"]] = checkList["checkItems"]

# Dump some useful information about the board
print "Trello Board: {0} ({1})".format(data["name"], data["url"])
print "\t{0} lists found".format(len(data["lists"]))
print "\t{0} cards found".format(len(data["cards"]))
print "\t{0} checklists found".format(len(data["checklists"]))
print "\t{0} labels found".format(len(data["labels"]))

# Core loop
for card in data["cards"]:
	# Grab all the core data we'll need from the card
	issueID 	= card["id"]
	cardName 	= card["name"].rstrip()
	shortURL 	= card["shortUrl"].strip()
	cardDesc 	= card["desc"].rstrip()
	labels 		= card["labels"]
	listName 	= listDict[card["idList"]]
	attachments = card["attachments"]
	status 		= "To Do"
	component 	= ""

	# We'll use the list name as the status of component depending on user input
	if opts.listAsComp:
		component = listName
	else:
		status 	  = listName

	# Set resolution up value if we can
	resolution = "Done" if status == "Done" else ""

	# Append URL to description
	if cardDesc:
		cardDesc += "\n\nGenerated from: " + shortURL
	else:
		cardDesc = "Generated from: " + shortURL

	AddIssue("task", issueID, "", status, resolution, cardName, cardDesc, attachments, component, labels)

	AddCheckListAsSubTasks(card["idChecklists"], issueID)

# Write out csv file
with open(csvPath, "w") as csvFile:
	csvFile.write(headerLine)
	csvFile.write(csvData)
	print "\tData written to {0}".format(csvPath)
