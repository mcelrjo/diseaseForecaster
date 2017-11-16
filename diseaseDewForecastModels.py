
import datetime
import forecastio
from geopy.geocoders import Nominatim



class diseasePredictor(object):
    
    def __init__(self, api_key, lat, lon):
        forecast = forecastio.load_forecast(api_key, lat, lon, units = 'si')
        hour = forecast.hourly()
        self.hourly = hour.data
        day = forecast.daily()
        self.daily = day.data
        self.month = int(datetime.datetime.fromtimestamp(int(self.daily[0].d['time'])).strftime('%m'))
        geolocator = Nominatim()
        jointLatLon = str(lat) + ", " + str(lon)
        self.location = geolocator.reverse(jointLatLon)

    def dewPredictor(self):
        '''Derivied in part from Gleason et al. 1994
        '''
        predictorScore = 0
        numHours = 0
        for i in range(len(self.hourly)):
        
            hour = int(datetime.datetime.fromtimestamp(int(self.hourly[i].d['time'])).strftime('%H'))

            if hour > 18 or hour < 9:
                dewDiff = float(self.hourly[i].d['temperature'] - self.hourly[i].d['dewPoint'])
                humidity = (float(self.hourly[i].d['humidity']))*100
                temp = float(self.hourly[i].d['temperature'])
                dewPoint = float(self.hourly[i].d['dewPoint'])
                wind = float(self.hourly[i].d['windSpeed'])*2.23694
                numHours +=1
                if dewDiff <= 3.7:
                    if wind >= 5.6 or humidity < 87:
                        predictorScore += 0.5
                        dewPresence = 'Low'
                        
                    elif wind <= 5.6 and humidity >= 87:
                        predictorScore += 0.8
                        dewPresence = 'High'
                        
                    elif wind <= 5.6 or humidity > 87:
                        predictorScore += 0.5
                        dewPresence = 'Moderate'


                elif dewDiff > 3.7:
                    if wind < 5.6 and humidity >= 87:
                        predictorScore += 1
                        dewPresence = 'Moderate'
                    
                    elif wind < 5.6 or humidity < 87:
                        predictorScore += 0.8
                        dewPresence = 'Mild'
                    
                else:
                    dewPresence = 'Low to not present'

        possible = (predictorScore/numHours)*100
        
        self.dewPrediction = possible
        self.dewPresence = dewPresence
        return possible
        
    def soilTempPredictor(self):
        pass
        
    def dailyForecastData(self):
        humidity = []
        temperatureMax = []
        temperatureMin = []
        dewPoint = []
        precipProbability = []
        cloudCover = []
        dates = []
        self.dewPredictor()
        for i in range(len(self.daily)):
            humidity.append(self.daily[i].d['humidity'])
            temperatureMax.append(self.daily[i].d['temperatureMax'])
            temperatureMin.append(self.daily[i].d['temperatureMin'])
            dewPoint.append(self.daily[i].d['dewPoint'])
            precipProbability.append(self.daily[i].d['precipProbability'])
            cloudCover.append(self.daily[i].d['cloudCover'])
            dates.append(datetime.datetime.fromtimestamp(int(self.daily[i].d['time'])).strftime("%Y-%m-%d"))
            
        self.humidity = humidity
        self.temperatureMax = temperatureMax
        self.temperatureMin = temperatureMin
        self.dewPoint = dewPoint
        self.precipProbability = precipProbability
        self.cloudCover = cloudCover
        self.dates = dates
        
        #The following variables are used in calculations below
        self.hum = (sum(self.humidity)/len(self.humidity))*100
        self.maxT = sum(self.temperatureMax)/len(self.temperatureMax)
        self.minT = sum(self.temperatureMin)/len(self.temperatureMin)
        self.precip = sum(self.precipProbability)/len(self.precipProbability) 
        self.dew = self.dewPrediction
        
    def diseaseForecast(self):
        '''Output a full week forecast for all diseases.  Iterate through each 
        weather factor and run each disease prediction.  Store values for each 
        '''
        miniRingOutput = []
        pythiumBlightOutput = []
        dollarSpotOutput = []
        largePatchOutput = []
        brownPatchOutput = []
        grayLeafSpotOutput = []
        anthracnoseOutput = []
        #springDeadSpotOutput = []
        for i in range(len(self.humidity)):
            self.miniRing(self.temperatureMin[i], self.temperatureMax[i], self.humidity[i], self.precipProbability[i])
            miniRingOutput.append(self.mr)
            self.brownPatch(self.temperatureMin[i], self.precipProbability[i])
            brownPatchOutput.append(self.bp)
            self.pythiumBlight(self.temperatureMax[i], self.temperatureMin[i], self.humidity[i])
            pythiumBlightOutput.append(self.pythium)
            self.dollarSpot(self.temperatureMax[i], self.temperatureMin[i], self.humidity[i], self.precipProbability[i])
            dollarSpotOutput.append(self.ds)
            self.largePatch(self.temperatureMax[i], self.temperatureMin[i], self.humidity[i], self.precipProbability[i])
            largePatchOutput.append(self.rs)
            self.grayLeafSpot(self.temperatureMax[i], self.temperatureMin[i], self.humidity[i], self.precipProbability[i])
            grayLeafSpotOutput.append(self.gls)
            self.anthracnose(self.temperatureMax[i], self.temperatureMin[i], self.humidity[i], self.precipProbability[i])
            anthracnoseOutput.append(self.anthrax)
            #self.springDeadSpot()
            #springDeadSpot.append(self.sds)
        
        self.miniRingOutput = miniRingOutput    
        self.brownPatchOutput = brownPatchOutput
        self.pythiumBlightOutput = pythiumBlightOutput
        self.dollarSpotOutput = dollarSpotOutput
        self.largePatchOutput = largePatchOutput
        self.grayLeafSpotOutput = grayLeafSpotOutput
            
    def pythiumBlight(self, maxT, minT, hum):
        '''pythiumBlight works off of two factors-- maximum daily temperature 
        and average humidity.  Maxiumum temperature is the primary factor and
        humidity is secondary factor
        '''

        if maxT >= 34:
            if hum >=60:
                pythium = 'High'
            elif hum < 60:
                pythium = 'Moderate'
        elif maxT < 34 and minT >= 23:
            if hum >= 60:
                pythium = 'Mild'
            elif hum < 60:
                pythium = 'Low'
        else:
            pythium = 'Not Active'
            
        self.pythium = pythium
        
    def dollarSpot(self, maxT, minT, hum, precip):

        if maxT <= 30 and minT >= 15:
            ds = 'Low'
            if self.dew >=20:
                if hum >=60 and precip > 40:
                    ds = 'High'
                else:
                    ds= 'Moderate'
                
            elif self.dew < 20:
                if hum >=60:
                    ds = 'Mild'
                else:
                    ds = "Low"
        else:
            ds = 'Not active'
        
        self.ds = ds
            
    def largePatch(self, maxT, minT, hum, precip):
        '''Large Patch is a model built for Rhizoctonia solani development on 
        warm-season turfgrass.  A sister model (brownPatch) is for cool-season
        grasses.
        daytime temps over 80F, night time above 55 F.  More active in spring
        and fall on warm-season grasses. High leaf wetness and humidity.
        '''
        
        if maxT <= 26.5 and minT >= 13:
            if hum > 60 and self.dew >= 20 and precip > 0.4:
                rs = 'High'
            elif hum > 60 and self.dew >= 20 and precip < 0.4:
                rs = 'Moderate'
            elif hum > 50 and self.dew <= 20 and precip < 0.4:
                rs = 'Mild'
            else:
                rs = 'Low'
        else:
            rs = "Not Active" 
            
        self.rs = rs
        
    def brownPatch(self, minT, precip):
        '''Model for rhizoctonia solani on cool-season turfgrass.  According to UGA
        temps below 80F with continual wetness for 48h.
        According to GroundsMag article: Temps above 85F, nighttime temps above 60F.  
        High humidity and leaf wetness contribute.  
        Purdue: Nighttime temps above 65F with leaf wetness for >= 10 h.
        '''
        
        if minT > 18:
            if self.dew > 20 and precip >= 40:
                bp = 'High'
            else:
                bp = 'Moderate'
        elif minT > 15:
            if self.dew > 20:
                bp = "Mild"
            else:
                bp = "Low"
        else:
            bp = "Not active"
            
        self.bp = bp
        
    
    def miniRing(self, minT, maxT, hum, precip):
        '''Very little inforamtion regarding weather conditions that are 
        conducive for activity.  Generally presumed that warm days and cool nights 
        along with high humidity and cloud cover are more conducive for growth.
        Persumed that fall is more prevalent than spring.
        '''
        
        if minT <= 18.3 and maxT >= 26.6:
            if hum >= 60 and precip >= 40:
               mr = "High"
            elif hum > 60:
               mr = "Moderate"
            else:
               mr = "Mild"
        elif minT <=21.5 and maxT >= 26:
            mr = "Low"
        else:
            mr = "Not Active"
            
        self.mr = mr
                
        
    def summerPatch(self):
        '''Soil borne fungus on primarily cool-season turf especially Kentucky bluegrass.
        Fungus: Magnaporthe poae.  
        '''
        pass
        
    def grayLeafSpot(self, maxT, minT, hum, precip):
        '''Daytime temps between 80-90 F night time temps between above 65 F.  
        Extended hot, humid, rainy conditions are more favorable.  Most susceptible:
            St. Aug, P. rye, bermudagrass, centipede, bent, some fescues.
            Info from Lee Burpee, UGA 
            http://extension.uga.edu/publications/detail.html?number=B1233#GrayLeafSpot
        '''

        if self.minT >= 16.5:
            if self.hum > 60 and self.maxT <= 33 and self.maxT >=25 and self.precip >= 0.2:
                gls = 'High'
            elif self.hum > 50 and self.maxT <= 33 and self.maxT >=25 and self.precip >= 0.2:
                gls = 'Moderate'
            elif self.hum > 60 and self.maxT <= 33 and self.maxT >=25 and self.precip < 0.2:
                gls = 'Mild'
            else:
                gls = 'Low'
        else:
            gls = "Not Active"
            
        self.gls = gls
        
    def anthracnose(self, maxT, minT, hum, precip):
        '''Night time temperatures > 75 F and leaf wetness > 10 h.  Some info from 
        UGA, Penn State, NC State
        '''

        if self.minT > 24:
            if self.hum > 60 and self.maxT > 32 and self.precip > 40:
                anthrax = 'High'
            elif self.hum > 60 and self.maxT > 32 and self.precip < 40:
                anthrax = 'Moderate'
            elif self.hum > 60 and self.maxT < 32 and self.precip < 40:
                anthrax = 'Mild'
            else:
                anthrax = 'Low'
        else:
            anthrax = "Not Active"
        
        self.anthrax = anthrax
        
        
    def springDeadSpot(self):
        '''Daily avarage soil temp at 65 F is best for growth.  So probably need
        between 55 to 75 F
        if self.maxT 24:
            if self.hum > 60 and self.maxT > 32 and self.precip > 40:
                anthrax = 'High'
            elif self.hum > 60 and self.maxT > 32 and self.precip < 40:
                anthrax = 'Moderate'
            elif self.hum > 60 and self.maxT < 32 and self.precip < 40:
                anthrax = 'Mild'
            else:
                anthrax = 'Low'
        else:
            anthrax = "Not Active"
        
        self.anthrax = anthrax
        
        '''
        pass

api_key = "feae2be941ef3a658195cb8356696650"

lat = 32.6099 # Auburn
lon = -85.4808

#lat = 26.9506 # Tampa
#lon = -82.4572

#lat = 40.7934  # State College
#lon = -77.8600

#lat = 40.4259 #West Lafayette
#lon = -86.9081

#lat = 28.5383 # Orlando
#lon = -81.3792

#lat = 53.39600 #York, UK
#lon = -1.0873

#lat = -33.8688 #Sydney
#lon = 151.2093

#lat = -22.9068 #Rio
#lon = -43.1729

#forecast = forecastio.load_forecast(api_key, lat, lon, units = 'si')

#hour = forecast.hourly()
#hourly = hour.data #This is a hourly data object

#day = forecast.daily()
#daily = day.data  #This is the daily data object

auburn = diseasePredictor(api_key, lat, lon)



auburn.dailyForecastData()
print "--------------Start Report-----------"
print "Predictions for: " + str(auburn.location)
print "------------Weather--------------"
print "Eight day max temps: "+ str(auburn.temperatureMax)
print "Eight day min temps: "+ str(auburn.temperatureMin)
print "Eight day humidity: " + str(auburn.humidity)

print "------------DewPresence-----------------"
auburn.dewPredictor()
print auburn.dewPresence
#print auburn.dewPrediction 

# print "------------MiniRing-------------"
# auburn.miniRing(auburn.minT, auburn.maxT, auburn.hum, auburn.precip)
# print auburn.mr
# print "------------GrayLeafSpot-----------------"
# auburn.grayLeafSpot()
# print auburn.gls
# print "---------Warm-Season LargePatch-------------"
# auburn.largePatch()
# print auburn.rs
# print "--------------DollarSpot-------------------"
# auburn.dollarSpot()
# print auburn.ds 
# print "--------------Anthracnose-----------------"
# auburn.anthracnose()
# print auburn.anthrax
# print "-------------Pythium-----------------"
# auburn.pythiumBlight()
# print auburn.pythium
# print "-----------Cool-Season BrownPatch------------"
# auburn.brownPatch()
# print auburn.bp

#print auburn.daily[0].d['actualTemperature']

print "-----------Week Disease Forecast--------------"
auburn.diseaseForecast()
print auburn.miniRingOutput

print auburn.miniRingOutput    
print auburn.brownPatchOutput
print auburn.pythiumBlightOutput
print auburn.dollarSpotOutput
print auburn.largePatchOutput
print auburn.grayLeafSpotOutput
