import datetime
import requests

# Function to convert month names into their integers
def monthNameToInt ( name ):
    if name == "Jan":
        return 1
    elif name == "Feb":
        return 2
    elif name == "Mar":
        return 3
    elif name == "Apr":
        return 4
    elif name == "May":
        return 5
    elif name == "Jun":
        return 6
    elif name == "Jul":
        return 7
    elif name == "Aug":
        return 8
    elif name == "Sep":
        return 9
    elif name == "Oct":
        return 10
    elif name == "Nov":
        return 11
    elif name == "Dec":
        return 12

# Grab the EIA Henry Hub web page and store it in HHPrice
url = 'https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm'
r = requests.get(url, allow_redirects=True)
HHPrice = open('HenryHubGas.htm')

# Boolean to test whether we are in the data table
inTable = False

# Initialise the output strings with headings
dayOutput = "Date,Price"
monthFirstDateOutput = "Month,Price"
monthAverageOutput = "Month,Price"

# Initialise a date object
date = datetime.datetime(1, 1, 1)

# Variable to store the current daily price
currentPriceString = ""

# Variable to store whether we need to add monthly price data
monthPriceDataNeeded = False

# Variables to store the total prices for the month and the number of days
# for averaging purposes
monthPriceAggregate = 0.00
monthDays = 0

# Iterate through the HTML file to find the start of the table
for line in HHPrice:
    if line.startswith(" <table SUMMARY='Henry Hub Natural Gas"):
        inTable = True

    if inTable:
        # Break apart the HTML formatting to find year, month and day
        if line.startswith(" <td class='B6'>"):
            yearStart = line.rindex(";") + 1
            yearEnd = yearStart + 4
            monthStart = yearEnd + 1
            monthEnd = monthStart + 3
            dayStart = monthEnd + 1
            dayEnd = dayStart + 2
            yearString = line[yearStart: yearEnd]
            monthString = line[monthStart: monthEnd]
            dayString = line[dayStart: dayEnd].strip()

            # Convert the string we've found into ints
            yearInt = int(yearString)
            monthInt = monthNameToInt(monthString)
            dayInt = int(dayString)

            # Create a date object
            newDate = datetime.datetime(yearInt, monthInt, dayInt)

        # Break apart HTML formatting to find start of a price row
        if line.startswith(" <td class='B3'>"):
            priceStart = line.index(">") + 1
            priceEnd = line.rindex("<")
            dailyPriceString = line[priceStart: priceEnd]

            # Check to see if it is a new month
            newMonth = int(newDate.strftime("%m"))
            oldMonth = int(date.strftime("%m"))

            # If we have changed months, we need the monthly price
            if newMonth != oldMonth:
                monthPriceDataNeeded = True
                monthFirstDateOutput += "\n" + newDate.strftime("%b")
                monthFirstDateOutput += " " + newDate.strftime("%Y") + ","

                monthAverageOutput += "\n" + newDate.strftime("%b")
                monthAverageOutput += " " + newDate.strftime("%Y") + ","

                # Average the monthly price and append it to monthAverageOutput
                monthAverage = format(monthPriceAggregate / monthDays, '.2f')
                monthAverageOutput += str(monthAverage)

                # Reset monthPriceAggregate and monthDays for next month
                monthPriceAggregate = 0.00
                monthDays = 0

                # If it is not the first day of the month,
                # The current price will be the month's price
                if newDate.strftime("%d") != "01":
                    monthFirstDateOutput += currentPriceString
                    
                    # We have a monthly price, set flag to false
                    monthPriceDataNeeded = False
                    
                # If it is not a new month, check to see if we are at the
                # first month in the range
                # If we are, we still need monthly price data                
            elif date == datetime.datetime(1, 1, 1):  
                monthPriceDataNeeded = True
                monthFirstDateOutput += "\n" + newDate.strftime("%b")
                monthFirstDateOutput += " " + newDate.strftime("%Y") + ","

            date = newDate 
            
            # Check to see if the dailyPriceString is empty
            # If it is, keep current price as is
            # If not, update current price to match
            if dailyPriceString != "" and dailyPriceString != "NA":
                currentPriceString = dailyPriceString

                # Add price to monthPriceAggregate and increment dats
                monthPriceAggregate += float(dailyPriceString)
                monthDays += 1

            # If we still need a montly price, add it now
            if monthPriceDataNeeded:
                if currentPriceString != "":
                    monthFirstDateOutput += currentPriceString
                    monthPriceDataNeeded = False
                    
            dayOutput += "\n" + date.strftime("%x") + "," + currentPriceString
            
            # Once we have found a price, increment the date by 1 day
            newDate = newDate + datetime.timedelta(1)

# Write output strings to separate files
exportFile = open("Henry_Hub_Gas_Prices_Daily.csv", "w")
exportFile.write(dayOutput)
exportFile.close()

exportFile = open("Henry_Hub_Gas_Prices_Monthly.csv", "w")
exportFile.write(monthFirstDateOutput)
exportFile.close()

exportFile = open("Henry_Hub_Gas_Prices_Monthly_Average.csv", "w")
exportFile.write(monthAverageOutput)
exportFile.close()
            
print ("Daily prices written")
