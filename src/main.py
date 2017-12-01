#!/usr/bin/python
# -*- coding: UTF-8 -*-

# enable debugging in web server environment
import cgitb
from webpageGenerator import percentageOfOccurrenceByReleaseYear
cgitb.enable()

__author__ = "Justin Eyster"
__date__ = "$Jun 2, 2015 2:43:11 PM$"

from datetime import datetime
from bottle import route, run, install, template, request, get, post, static_file, redirect
from databaseQuerierPostgresql import searchResults, totalMovies, getContextLines
from webpageGenerator import generateSearchPage, generateComparisonPage,\
    generateGraphOfTwoKeywords, generateFeedbackPage
from feedbackEmailSender import sendEmail
# The import below says it's unused, but it is used on the web server. Don't remove it.
import cgi

import sys

from config import DEBUG_MODE
import itertools
from operator import itemgetter
import json

print >> sys.stderr, 'spam'

# copied from websiteGenerator.py
def removeBadCharacters(text):
    """
    Removes utf-8 escaped characters that were showing up in results on the webpage.
    :param text: text to remove the newline symbol from, and other utf-8 bullshit
    :return: text that has been cleaned of garbage utf-8 characters
    """
    for i in range(len(text)):
        if len(text) > i and text[i] == "\\":
            if len(text) > i+1 and (text[i+1] == "0" or text[i+1] == "3" or text[i+1] == "2"):
                if len(text) > i+2 and (text[i+2] == "1" or text[i+2] == "0" or text[i+2] == "6"):
                    if len(text) > i+3 and (text[i+3] == "2"or text[i+3] == "2" or text[i+3] == "6"):
                        text = text[0:i] + " " + text[i+4:]
    return u'{}'.format(text).encode('utf-8')

# maps fields within tuple so they are named
def remapResultsHelper(lineOfDialogue):
    return {
        "movieOclcId": lineOfDialogue[0],
        "movieTitle": lineOfDialogue[1],
        "movieLineNumber": lineOfDialogue[2],
        "movieStartTimeStamp": lineOfDialogue[3],
        "movieEndTimeStamp": lineOfDialogue[4],
        "movieLineText": removeBadCharacters(lineOfDialogue[5]),
        "movieReleaseYear": lineOfDialogue[6],
        "dvdReleaseYear": lineOfDialogue[7],
        "runtimeInMinutes": lineOfDialogue[8] if len(lineOfDialogue) > 8 else None,
        "totalNumberOfLines": lineOfDialogue[9] if len(lineOfDialogue) > 8 else None,
        "genre1": lineOfDialogue[10] if len(lineOfDialogue) > 8 else None,
        "genre2": lineOfDialogue[11] if len(lineOfDialogue) > 8 else None,
        "genre3": lineOfDialogue[12] if len(lineOfDialogue) > 8 else None
    }

def remapResults(results):
    # map tuples with list using helper function
    mapped = map(remapResultsHelper, results)

    # separate films by OclcId
    mappedAndGrouped = []
    for key, value in itertools.groupby(mapped, key=itemgetter('movieOclcId')):
        mappedAndGrouped.append(
            {
                'movieOclcId': key,
                'results': []
            }
        )
        for i in value:
            mappedAndGrouped[-1]['results'].append(i)

    # move film-specific attributes up one level
    for film in mappedAndGrouped:
        film['movieTitle'] = film["results"][0]["movieTitle"]
        film['movieReleaseYear'] = film["results"][0]["movieReleaseYear"]
        film['dvdReleaseYear'] = film["results"][0]["dvdReleaseYear"]
        film['runtimeInMinutes'] = film["results"][0]["runtimeInMinutes"]
        film['totalNumberOfLines'] = film["results"][0]["totalNumberOfLines"]
        film['genre1'] = film["results"][0]["genre1"]
        film['genre2'] = film["results"][0]["genre2"]
        film['genre3'] = film["results"][0]["genre3"]
        for lineData in film['results']:
            lineData.pop('movieOclcId')
            lineData.pop('movieTitle')
            lineData.pop('movieReleaseYear')
            lineData.pop('dvdReleaseYear')
            lineData.pop('runtimeInMinutes')
            lineData.pop('totalNumberOfLines')
            lineData.pop('genre1')
            lineData.pop('genre2')
            lineData.pop('genre3')

    return mappedAndGrouped

class App():

    def __init__(self):
        """
        Stores default earliest release year. Right now we're only including movies released after 2000.
        """

        # path to media files set up to point to web server static file location
        self.pathToMediaFiles = "/home1/filmtvse/public_html/static"

        # FUTURE MANAGER OF THIS SOFTWARE LOOK BELOW!
        # TODO: change value below to the year of the first movie in history when expanding to movies released pre-2000
        self.defaultEarliestReleaseYear = 1996

    # def displaySearchPage(self):
    #     """
    #     Displays the search (home) page. Uses an html form (see inputPageTemplate). Uses GET protocol.
    #     :return: a string, the HTML code for the landing page, which includes a search box and metadata parameters.
    #     """
    #     return generateSearchPage(self.defaultEarliestReleaseYear)

    # def searchFromLandingPage(self):
    #     """
    #     Takes the user's search term & metadata parameters from the form on the landing page, then redirects to
    #     the proper URL that will generate the results page.
    #     """
    #     # get search phrase and metadata parameters from the form on the search page.
    #     keywordOrPhrase = request.forms.get('keywordOrPhrase')
    #     # check for whitespace at end of keyword/phrase
    #     if keywordOrPhrase[len(keywordOrPhrase)-1] == " ":
    #         return "<p>Please enter your search term without a space at the end.<a href = '/moviesearch'> Back.</a></p>"
    #     # get rid of question marks and exclamations, they cause an error
    #     keywordOrPhrase = keywordOrPhrase.replace("?","")
    #     keywordOrPhrase = keywordOrPhrase.replace("!","")
    #     # convert spaces to & signs: this ensures that matches are returned for all words/variations of each word
    #     keywordOrPhrase = keywordOrPhrase.replace(" ","&")
    #     # Slashes cause an error when redirecting to the search URL.  For now, we'll interpret them the same as spaces
    #     keywordOrPhrase = keywordOrPhrase.replace("/","&")
    #     genre = request.forms.get('genre')
    #     earliestReleaseYear = request.forms.get('earliestReleaseYear')
    #     latestReleaseYear = request.forms.get('latestReleaseYear')
    #     # if they didn't type anything before clicking search, say so, and give them a back button.
    #     if keywordOrPhrase is None:
    #         return "<p>Please specify a keyword or phrase before clicking 'search.'<a href = '/moviesearch'> Back.</a></p>"
    #     if earliestReleaseYear == "":
    #         earliestReleaseYear = self.defaultEarliestReleaseYear
    #     if latestReleaseYear == "":
    #         latestReleaseYear = datetime.now().year
    #     # forward the user to the first page of results (the URL contains the parameters used to generate results)
    #     redirectUrl = '/moviesearch/'+keywordOrPhrase+'/'+genre+'/'+str(earliestReleaseYear)+'/'+str(latestReleaseYear)+'/'+'1'
    #     redirect(redirectUrl)

    # def displayGraph(self,keywordOrPhrase,genre,earliestReleaseYear,latestReleaseYear):
    #     data = percentageOfOccurrenceByReleaseYear(keywordOrPhrase, genre, earliestReleaseYear, latestReleaseYear)
    #     twoDimensArrayOfVals = []
    #     for item in data:
    #         # create a two dimension array of values to insert into template to be graphed
    #         twoDimensArrayOfVals.append([item[0], round(item[1])])
    #     return {"results": twoDimensArrayOfVals}

    def getSearchResults(self,keywordOrPhrase):
        """
        API call for a text-based search, all filtering is done on the client
        side.
        :param keywordOrPhrase: the keyword or phrase to search.
        :return: JSON containing all search results.
        """
        print >> sys.stderr, 'spam2'
        results = searchResults(keywordOrPhrase)

        return {"results": remapResults(results)}


    # def getContext(self,oclcId,lineNumber):
    #     """
    #     Get the user's previous search term/params so we can create a back button. Return JSON
    #     containing the context requested by the client.
    #     :param oclcId: oclc number of movie to get context from
    #     :param lineNumber: line number clicked by user
    #     :return: html code for the page of context
    #     """
    #     contextLines = getContextLines(oclcId, lineNumber, 40)

    #     results = remapResults(contextLines)[0]
    #     results.pop('runtimeInMinutes')
    #     results.pop('totalNumberOfLines')
    #     results.pop('genre1')
    #     results.pop('genre2')
    #     results.pop('genre3')

    #     return {"context": results}

    # def displayComparisonPage(self):
    #     """
    #     Display the comparison search page to user.
    #     :return: html code for the search page that has two search boxes, to compare two words/phrases
    #     """
    #     return generateComparisonPage(self.defaultEarliestReleaseYear)

    # def graphComparison(self):
    #     """
    #     Get the dual keywords entered on the comparison page.
    #     :return: graph of the two words/phrases that the user entered
    #     """
    #     # get graph/search parameters from search boxes
    #     keywordOrPhrase1 = request.forms.get('keywordOrPhrase1')
    #     keywordOrPhrase2 = request.forms.get('keywordOrPhrase2')
    #     # check for whitespace at end of keywords
    #     if keywordOrPhrase1[len(keywordOrPhrase1)-1] == " " or keywordOrPhrase2[len(keywordOrPhrase2)-1] == " ":
    #         return "<p>Please enter your search terms without a space at the end.<a href = '/moviesearch/compare'> Back.</a></p>"
    #     # get rid of question marks and exclamation marks, they cause an error
    #     keywordOrPhrase1 = keywordOrPhrase1.replace("?","")
    #     keywordOrPhrase2 = keywordOrPhrase2.replace("?","")
    #     keywordOrPhrase1 = keywordOrPhrase1.replace("!","")
    #     keywordOrPhrase2 = keywordOrPhrase2.replace("!","")
    #     # convert spaces to & signs: this ensures that matches are returned for all words/variations of each word
    #     keywordOrPhrase1 = keywordOrPhrase1.replace(" ","&")
    #     keywordOrPhrase2 = keywordOrPhrase2.replace(" ","&")
    #     if len(keywordOrPhrase1) == 0 or len(keywordOrPhrase2) == 0:
    #         return "<p>Please specify two keywords or phrases before clicking 'search.'<a href = '/moviesearch/compare'> Back.</a></p>"
    #     genre = request.forms.get('genre')
    #     earliestReleaseYear = request.forms.get('earliestReleaseYear')
    #     latestReleaseYear = request.forms.get('latestReleaseYear')
    #     if earliestReleaseYear == "":
    #         earliestReleaseYear = self.defaultEarliestReleaseYear
    #     if latestReleaseYear == "":
    #         latestReleaseYear = datetime.now().year

    #     # convert underscores to spaces
    #     # (underscores are sometimes used in the URL in place of spaces, need to convert back)
    #     for i in range(len(keywordOrPhrase1)):
    #         if keywordOrPhrase1[i] == "_":
    #             keywordOrPhrase1 = keywordOrPhrase1[0:i] + " " + keywordOrPhrase1[i+1:]
    #     for i in range(len(keywordOrPhrase2)):
    #         if keywordOrPhrase2[i] == "_":
    #             keywordOrPhrase2 = keywordOrPhrase2[0:i] + " " + keywordOrPhrase2[i+1:]

    #     return generateGraphOfTwoKeywords(keywordOrPhrase1, keywordOrPhrase2, genre, earliestReleaseYear,
    #                                       latestReleaseYear)

    def displayFeedbackPage(self):
        """
        Generate and then display a feedback form to the user.
        :returns: an html string with a feedback form.
        """
        return generateFeedbackPage()

    def sendFeedback(self):
        """
        Get feedback from html form, then send feedback email.
        """
        feedbackText = request.forms.get('feedbackText')
        senderEmailAddress = request.forms.get('senderEmail')
        senderName = request.forms.get('senderName')
        sendEmail(feedbackText, senderEmailAddress, senderName)
        return "<p>Thank you for your feedback!<a href = '/moviesearch'> Back to search page.</a></p>"

    def static(self, path):
        """
        Provides route to static files, such as text files. Only needs to be routed for development server, not web
        server environment. See routing at end of this file.
        :param path: the path to the static file.
        :return: the static file.
        """
        # to save storage on my computer, retrieve text files and images from hard drive
        if path[-4:len(path)] == '.txt' or path[-4:len(path)] == '.png' or path[-4:len(path)] == '.gif':
            return static_file(path, root=self.pathToMediaFiles)
        # other files are found under static directory in working directory
        else:
            return static_file(path, root='static')

    # def handleSitemap(self):
    #     redirect('/sitemap.xml')

    def getResultsTemplate(self):
        with open("templates/searchResultsReactTemplate.html", 'r') as f:
            return f.read()

# initialize App
appInstance = App()
# route the proper URL's to the proper methods in the class
# get('/moviesearch/')(appInstance.displaySearchPage)
# post('/moviesearch/')(appInstance.searchFromLandingPage)
route('/moviesearch/<keywordOrPhrase>')(appInstance.getSearchResults)
# route('/moviesearchgraph/<keywordOrPhrase>/<genre>/<earliestReleaseYear:int>/<latestReleaseYear:int>')\
#     (appInstance.displayGraph)
# route('/moviesearch/context/<oclcId:int>/<lineNumber:int>')\
#     (appInstance.getContext)
# route()
# get('/moviesearch/compare')(appInstance.displayComparisonPage)
# post('/moviesearch/compare')(appInstance.graphComparison)
get('/moviesearch/feedback')(appInstance.displayFeedbackPage)
post('/moviesearch/feedback')(appInstance.sendFeedback)
# route('/moviesearch/sitemap.xml')(appInstance.handleSitemap)
get('/')(appInstance.getResultsTemplate)

# comment out the line below for web server environment (not commented out for local development server)
route('/static/:path#.+#', name='static')(appInstance.static)

# make sure the line below isn't commented out for web server environment (comment out for local development server)
# run(server='cgi')
# comment out the line below for web server environment (not commented out for local development server)
run(host='localhost', port=8080, debug=True)(appInstance)
