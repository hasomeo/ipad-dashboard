import json, urllib.request, datetime, re
from zoneinfo import ZoneInfo

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

codes={0:"Klar",1:"Überwiegend klar",2:"Teilweise bewölkt",3:"Bewölkt",45:"Nebel",48:"Nebel",51:"Nieselregen",53:"Nieselregen",55:"Nieselregen",61:"Regen",63:"Regen",65:"Starker Regen",71:"Schnee",73:"Schnee",75:"Starker Schnee",80:"Regenschauer",81:"Regenschauer",82:"Starke Schauer",95:"Gewitter",96:"Gewitter",99:"Gewitter"}
names=["Heute","Morgen","Übermorgen"]

def city(lat,lon):
    url=("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset&timezone=Europe%%2FBerlin&forecast_days=3")%(lat,lon)
    w=get_json(url)
    days=[]
    for i in range(3):
        days.append({"name":names[i],"max":w["daily"]["temperature_2m_max"][i],"min":w["daily"]["temperature_2m_min"][i],"rain":w["daily"]["precipitation_probability_max"][i] or 0})
    return {"weather":{"current":w["current"]["temperature_2m"],"text":codes.get(w["current"]["weather_code"],"Wetter"),"days":days},"sun":{"sunrise":w["daily"]["sunrise"][0][11:16],"sunset":w["daily"]["sunset"][0][11:16]}}

now=datetime.datetime.now(ZoneInfo("Europe/Berlin"))
data={"updated":now.strftime("%d.%m. %H:%M"),"cities":{"koeln":city(50.9375,6.9603),"frankfurt":city(50.1109,8.6821)}}

with open("data.json","w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,separators=(",",":"))
with open("index.html","r",encoding="utf-8") as f: page=f.read()
payload=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
replacement='<script id="embeddedDashboardData">var DASHBOARD_DATA='+payload+';</script>'
page=re.sub(r'<script id="embeddedDashboardData">.*?</script>',replacement,page,count=1,flags=re.S)
with open("index.html","w",encoding="utf-8") as f: f.write(page)
