
#This program extracts HTML element - table with all current results of matches in Polish Ekstraklasa (football league) as a string.
#After extracting this string, the program gathers only necessary data: clubs names and all matches results thanks to RegEx.
#When all of them are gathered, final table of Ekstraklasa is being prepered.
#In order to do that, 6 rules from this webpage (https://en.wikipedia.org/wiki/2021%E2%80%9322_Ekstraklasa) are followed.
#As a final step, two Excel file are created - one with matrix of all match results and another one with final table of Ekstraklasa.
#Also chart with points achieved by given teams is created and shown.



#importing pandas to deal with DataFrame for football club results
#preparing tables for Excel
import pandas as pd
#BeautifulSoup and requests needed for connection with webpage and read html element (table)
from bs4 import BeautifulSoup
import requests
#RegEx needed for extracting necessary data from html element
import re
#matplotlib to prepare a chart with points at the end
import matplotlib.pyplot as plt
#library below used to display today's date in the name of chart with points
from datetime import date

#class created for instances of clubs - with important data like name, results, points and other important data
class Club:
    def __init__(self, name, results, points = 0, subpoints = 0, subgoals = 0, goals = 0, goals_balance = 0,
                victories = 0, victories_guest = 0):
        self.name = name
        self.results = results
        self.points = points
        self.subpoints = subpoints
        self.subgoals = subgoals
        self.goals = goals
        self.goals_balance = goals_balance
        self.victories = victories
        self.victories_guest = victories_guest

def main():
    #url variable is used to store link to webpaage where results table comes from
    url = 'https://pl.fctables.com/polska/ekstraklasa/'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    #attributes of table to find it on webpage
    tabletext = soup.find_all('table', 'table table-striped table-bordered table-hover table-condensed small games-grid')
    #pattern to extract clubs names
    pattern = r'<th class="name" data-toggle="tooltip" title="(.*)"><div class'
    #list of clubs by using pattern
    clubs_list = re.findall(pattern,str(tabletext))
    #pattern for extracting matches results
    pattern2 = r'onclick="game\(.*\)\s?"[\s|>](?:title=")?(.*)<\/div>'
    results_lists = re.findall(pattern2,str(tabletext))
    clubs_number = len(clubs_list)
    #transform results_list into the list of sublists - one sublist is a list with matches results for one football club
    my_list2 = [results_lists[i:i + clubs_number-1] for i in range(0, len(results_lists), clubs_number-1)]

    #create new list with clubs
    #single item is a single Club class object
    clubs = []

    #to create a matrix with all results pandas DataFrame is created
    i = 0
    results_table = pd.DataFrame()
    for club in clubs_list:
        club_element = Club(club,my_list2[i])
        clubs.append(club_element)

        my_list3 = club_element.results[:]
        my_list3.insert(i,"-")
        results_table[club] = my_list3
        results_table.append(my_list3)

        i += 1
    #set index as clubs_list
    results_table.set_axis(clubs_list,axis='index',inplace=True)

    #create DataFrames to store final results
    full_results = pd.DataFrame(columns=['club', 'points', 'subpoints', 'subgoals', 'goals', 'goals_balance', 'victories', 'victories_guest'])
    full_results2 = pd.DataFrame(columns=['club', 'points', 'subpoints', 'subgoals', 'goals', 'goals_balance', 'victories', 'victories_guest'])

    #loop through the results_table to extract goals scored and lost in matches as a guest in order to sum points, goals and victories
    for row in results_table.iterrows():
        points = 0
        goals = 0
        goals_balance = 0
        victories = 0
        victories_guest = 0
        #ReGex used for extracting goals (test) or if match has not taken place yet - info when in will be happening (test2)
        test = re.findall(r"(\d+):(\d+)",string=str(row))
        test2 = re.findall(r"'(.*)'",string=str(row))
        for result in test:
            goals += int(result[1])
            goals_balance += int(result[1]) - int(result[0])

            if int(result[0]) < int(result[1]):
                points += 3
                victories += 1
                victories_guest += 1
            elif int(result[0]) == int(result[1]):
                points += 1
        #updating Club object
        for item in clubs:
            if item.name == str(test2)[2:-2]:
                item.points += points
                item.goals += goals
                item.goals_balance += goals_balance
                item.victories += victories
                item.victories_guest += victories_guest

    #transposing the table with results to sum up matches as a host
    results_table_transposed = results_table.transpose()
    # loop through the results_table to extract goals scored and lost in matches as a host in order to sum points, goals and victories
    for row in results_table_transposed.iterrows():
        points = 0
        goals = 0
        goals_balance = 0
        victories = 0
        victories_guest = 0
        test = re.findall(r"(\d+):(\d+)", string=str(row))
        test2 = re.findall(r"'(.*)'", string=str(row))

        for result in test:
            goals += int(result[0])
            goals_balance += int(result[0]) - int(result[1])

            if int(result[0]) > int(result[1]):
                points += 3
                victories += 1

            elif int(result[0]) == int(result[1]):
                points += 1
        #update Club object
        for item in clubs:
            if item.name == str(test2)[2:-2]:
                item.points += points
                item.goals += goals
                item.goals_balance += goals_balance
                item.victories += victories
                item.victories_guest += victories_guest
                print(f"{item.name} {item.points}")
                #create a set with single element with data regarding specific football team
                single_club_points = {'club': item.name, 'points' : item.points, 'subpoints' : item.subpoints, 'subgoals' : item.subgoals, 'goals' : item.goals,
                                      'goals_balance' : item.goals_balance, 'victories' : item.victories, 'victories_guest': item.victories_guest}
                #append single_club_points to full_results DataFrame
                full_results = full_results.append(single_club_points,True,False,True)
                break
    #check if two or more teams have the same number of points
    #if yes - follow the 2nd and 3rd rules from https://en.wikipedia.org/wiki/2021%E2%80%9322_Ekstraklasa
    for item in clubs:
        issomething = full_results['points'] == item.points
        clubs_same = full_results[issomething]
        index_value = clubs_same[clubs_same['club'] == str(item.name)].index

        clubs_same= clubs_same.drop(index=index_value)
        testor = clubs_same[clubs_same.columns[1]].count()
        i = 0
        if testor > 0:
            print(testor)
            while i < testor:
                rival = clubs_same.iloc[0, i]
                val = results_table.loc[item.name, rival]
                print(val)
                test = re.findall(r"(\d+):(\d+)", string=str(val))
                for result in test:
                    item.subgoals += int(result[1])
                    if result[0] < result[1]:
                        item.subpoints += 3
                    elif result[0] == result[1]:
                        item.subpoints += 1
                val = results_table.loc[rival, item.name]
                test = re.findall(r"(\d+):(\d+)", string=str(val))
                for result in test:
                    item.subgoals += int(result[0])
                    if result[0] > result[1]:
                        item.subpoints += 3
                    elif result[0] == result[1]:
                        item.subpoints += 1
                i += 1
        #add new row to full_results2
        single_club_points2 = {'club': item.name, 'points' : item.points, 'subpoints' : item.subpoints, 'subgoals' : item.subgoals, 'goals' : item.goals,
                                      'goals_balance' : item.goals_balance, 'victories' : item.victories, 'victories_guest': item.victories_guest}
        full_results2 = full_results2.append(single_club_points2, True, False, True)
    #sort rows in full_results2 according to Ekstraklasa table's rules
    full_results2 = full_results2.sort_values(['points', 'subpoints', 'subgoals', 'goals', 'victories', 'victories_guest'], ascending=False)
    #create two Excel files - matrix with all results and current table of Ekstraklsa
    results_table_transposed.to_excel(r"C:\Users\adrog\OneDrive\Desktop\test2.xlsx","Matryca wyników")
    full_results2.to_excel(r"C:\Users\adrog\OneDrive\Desktop\test3.xlsx", "Ekstraklasa tabela",
                           columns=['club', 'points', 'goals','goals_balance', 'subpoints','subgoals', 'victories','victories_guest'],
                           index=False)

    #create and show a plot with points of clubs
    full_results2.plot(x ='club', y='points', kind = 'bar')
    plt.title (f"Polish Ekstraklasa points {date.today().strftime('%d/%m/%Y')}")
    plt.show()

if __name__ == '__main__':
    main()



