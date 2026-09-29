import json, urllib.request, datetime, re
from zoneinfo import ZoneInfo

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))

# Weather Cologne
w=get("https://api.open-meteo.com/v1/forecast?latitude=50.9375&longitude=6.9603&current=temperature_2m,weather_code&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset&timezone=Europe%2FBerlin&forecast_days=3")
codes={0:"Klar",1:"Überwiegend klar",2:"Leicht bewölkt",3:"Bewölkt",45:"Nebel",48:"Nebel",51:"Nieselregen",53:"Nieselregen",55:"Nieselregen",61:"Regen",63:"Regen",65:"Starker Regen",71:"Schnee",73:"Schnee",75:"Schnee",80:"Schauer",81:"Schauer",82:"Starke Schauer",95:"Gewitter",96:"Gewitter",99:"Gewitter"}
names=["Heute","Morgen","Übermorgen"]
days=[]
for i in range(3):
    days.append({"name":names[i],"max":w["daily"]["temperature_2m_max"][i],"min":w["daily"]["temperature_2m_min"][i],"rain":w["daily"]["precipitation_probability_max"][i] or 0})

# Prayer times Cologne, MWL calculation. If you later have an official Ṣalāh/Aschura data endpoint,
# this is the one block to replace.
today=datetime.datetime.now(ZoneInfo("Europe/Berlin"))
date=today.strftime("%d-%m-%Y")
p=get("https://api.aladhan.com/v1/timingsByCity/"+date+"?city=Cologne&country=Germany&method=3")
t=p["data"]["timings"]
items=[{"name":"Fajr","time":t["Fajr"].split()[0]},
       {"name":"Dhuhr","time":t["Dhuhr"].split()[0]},
       {"name":"Asr","time":t["Asr"].split()[0]},
       {"name":"Maghrib","time":t["Maghrib"].split()[0]},
       {"name":"Isha","time":t["Isha"].split()[0]}]

data={"updated":datetime.datetime.now(ZoneInfo("Europe/Berlin")).strftime("%d.%m. %H:%M"),
      "weather":{"current":w["current"]["temperature_2m"],"text":codes.get(w["current"]["weather_code"],"Wetter"),"days":days},
      "prayers":{"items":items},"sun":{"sunrise":w["daily"]["sunrise"][0][11:16],"sunset":w["daily"]["sunset"][0][11:16]}}
with open("data.json","w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,separators=(",",":"))


# Embed the same data directly into index.html.
# This avoids AJAX/JSON loading problems in very old Safari (iOS 9).
with open("index.html","r",encoding="utf-8") as f:
    html=f.read()
payload=json.dumps(data,ensure_ascii=False,separators=(",",":")).replace("</","<\\/")
replacement='<script id="embeddedDashboardData">var DASHBOARD_DATA='+payload+';</script>'
html=re.sub(r'<script id="embeddedDashboardData">.*?</script>',replacement,html,count=1,flags=re.S)
with open("index.html","w",encoding="utf-8") as f:
    f.write(html)
