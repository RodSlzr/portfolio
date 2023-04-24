#from crime_sentiment 
#import crime_sentiment.app ####maybe not from
import crime_sentiment.dashboard.crime as crime

if __name__ == '__main__':
    #app.run()
    crime.go_crime()
    # app.run_server(debug = False)


# app.run_server(host = "127.0.0.1", port =888, debug=False)