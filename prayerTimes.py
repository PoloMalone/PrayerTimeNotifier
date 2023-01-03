import datetime
import pytz
import requests
import tkinter as tk
from tkinter import messagebox
import json
from timezonefinder import TimezoneFinder
from ttkwidgets.autocomplete import AutocompleteCombobox
from time import sleep
from win10toast import ToastNotifier
import os

#toast notifier
def notif(pray_name):
    n.show_toast("PrayerTimes", pray_name + " comes in " + str(notify_me) +  " minutes", duration = None, threaded=True,
    icon_path = os.getcwd() + "/Prayerbeads.ico")

#initialize
def init():
    prayer_times_dict, refined_time = get_new_times()
    pName, pTime, index = check_each_prayer(prayer_times_dict,refined_time)
    timeleft = get_notification_time(pTime,index)
    sleep_until_notif_time(timeleft,pName,index)

#update the new times from response to labels
def update_prayer_times_today(prayer_times_dict):
    today_prayer_time_FAJR.config(text ="Fajr: " + prayer_times_dict["Fajr"])
    today_prayer_time_SUNRISE.config(text = "Shuruq: " + prayer_times_dict["Sunrise"])
    today_prayer_time_DHUHR.config(text ="Dhuhr: " + prayer_times_dict["Dhuhr"])
    today_prayer_time_ASR.config(text ="Asr: " + prayer_times_dict["Asr"])
    today_prayer_time_MAGHRIB.config(text ="Maghrib: " + prayer_times_dict["Maghrib"])
    today_prayer_time_ISHA.config(text ="Isha: " + prayer_times_dict["Isha"])

#get time now depending on timezone
def time_now_live(time):
    time_now = datetime.datetime.now(timezone)
    time_now_refined = time_now.replace(tzinfo=None)
    time_now_refined = str(time_now_refined).split(" ")
    time_now_refined = time_now_refined[1].split(".")[0]
    time.config(text=" Time Now: " + str(time_now_refined), fg='RED')
    return

#loop until new day
def sleep_until_new_day():
    deadline = "00:00:00"
    deadline_format = datetime.datetime.strptime(deadline, '%H:%M:%S')
    while True:
        time_now = datetime.datetime.now(timezone).replace(tzinfo=None)
        remaining_time_twelve = str((deadline_format - time_now).total_seconds()).split(".")[0]
        remaining_time_twelve = int(remaining_time_twelve)
        rem_time.config(text=" Timeleft before 00:00 - " + convert(remaining_time_twelve))
        time_now_live(label_time_now)
        root.update()
        sleep(0.1)
        stringed_time_now = time_now.strftime('%H:%M:%S')
        if stringed_time_now == deadline:
            break;
    init()
    return  

#loop until notif time
def sleep_until_notif_time(notif_time, pray_name, idx):
    if pray_name == "Sunrise":
        pray_name = "Shuruq"
    while notif_time > datetime.datetime.now(timezone).replace(tzinfo=None):
        time_now = datetime.datetime.now(timezone)
        remaining_time = str((notif_time - time_now.replace(tzinfo=None)).total_seconds()).split(".")[0]
        remaining_time = int(remaining_time)
        rem_time.config(text=" Notify me " + str(notify_me) + " minutes before " + pray_name + " " + convert(remaining_time))
        time_now_live(label_time_now)
        root.update()
        sleep(0.1)
    notif(pray_name)
    if idx == 5:
        sleep_until_new_day()
    else:
        init()
    return

#convert from seconds to Hours, minutes, seconds
def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds)

#get notif time depending on user input
def get_notification_time(prayer_time, index):
    midnight = datetime.datetime.now(timezone).replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
    if index == 0 and datetime.datetime.now(timezone).replace(tzinfo=None) < midnight :
        notification_time = datetime.datetime.combine(
            datetime.datetime.now(timezone).replace(tzinfo=None), prayer_time 
        ) - datetime.timedelta(minutes=notify_me) + datetime.timedelta(days=1)
        return notification_time
    else:
        notification_time = datetime.datetime.combine(
            datetime.datetime.now(timezone).replace(tzinfo=None), prayer_time
        ) - datetime.timedelta(minutes=notify_me)
    
        return notification_time

#http request to get prayer times depending on timezone and location
def get_new_times():
    current_time = datetime.datetime.now(timezone).replace(tzinfo=None) 
    current_date = datetime.datetime.strftime(current_time, '%d-%m-%Y')
    current_day = int(current_date.split("-")[0])
    current_month = int(current_date.split("-")[1])
    current_year = int(current_date.split("-")[2])

    # The URL of the website with the prayer times
    prayer_times_url = f'http://api.aladhan.com/v1/calendar?latitude={latitude}&longitude={longitude}&method={method}&month={current_month}&year={current_year}'
    prayer_times_dict = {}

    current_time_split = str(current_time).split(" ")
    refined_current_time = current_time_split[1].split(".")[0]

    # Send a request to the website to get the prayer times
    response = requests.get(prayer_times_url)

    # Parse the response to get the prayer times
    prayer_times = response.json()

    #insert values to dict
    prayer_times_dict["Fajr"] = (prayer_times["data"][current_day-1]["timings"]["Fajr"].split()[0])
    prayer_times_dict["Sunrise"] = (prayer_times["data"][current_day-1]["timings"]["Sunrise"].split()[0])
    prayer_times_dict["Dhuhr"] = (prayer_times["data"][current_day-1]["timings"]["Dhuhr"].split()[0])
    prayer_times_dict["Asr"] = (prayer_times["data"][current_day-1]["timings"]["Asr"].split()[0])
    prayer_times_dict["Maghrib"] = (prayer_times["data"][current_day-1]["timings"]["Maghrib"].split()[0])
    prayer_times_dict["Isha"] = (prayer_times["data"][current_day-1]["timings"]["Isha"].split()[0])
    
    #update labels
    update_prayer_times_today(prayer_times_dict)
    return prayer_times_dict, refined_current_time

#check what prayer is next
def check_each_prayer(prayer_times_dict, ref_currtime):
    for index, prayer_name in enumerate(prayer_times_dict):
        prayer_time = prayer_times_dict[prayer_name]
        prayer_time = datetime.time.fromisoformat(prayer_time)

        currtime_totime = datetime.datetime.strptime(ref_currtime, '%H:%M:%S').time()
        currtime_todate = datetime.datetime.combine(
            datetime.date.today(), currtime_totime)
        prayertime_todate = datetime.datetime.combine(
            datetime.date.today(), prayer_time)

        diff = prayertime_todate - currtime_todate
  
        if not str(diff).startswith('-') and int(diff.total_seconds()) > (notify_me*60):
            return prayer_name, prayer_time, index
        if index == 5:
            sleep_until_new_day()
            return

#when user clicks "save" update values and call init
def save_inputs():
    global data
    global timezone
    global latitude
    global longitude
    global method
    global notify_me
    method = choose_method.get()
    city = choose_city.get() 
    try:
        notify_me = int(choose_time_to_notif.get())
        time_to_notif_label.config(text="Notify me minutes before prayer: ")
    except ValueError:
        time_to_notif_label.config(text="Input integer please")
        return

    for i in range(len(data)):
        if data[i]['name'] == city:
            latitude = float(data[i]['lat'])
            longitude = float(data[i]['lng'])

    obj = TimezoneFinder()
    timezone_result = obj.timezone_at(lat=latitude, lng=longitude)
    timezone = pytz.timezone(timezone_result) 
    method = methods_dict[method]
    init()
    return

#destroy window when exiting
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()
       
#pack all labels
def pack_labels():
    method_label.pack()
    choose_method.pack()
    location_label.pack()
    choose_city.pack()
    time_to_notif_label.pack()
    choose_time_to_notif.pack()
    save_button.pack()
    today_prayer_time_FAJR.pack()
    today_prayer_time_SUNRISE.pack()
    today_prayer_time_DHUHR.pack()
    today_prayer_time_ASR.pack()
    today_prayer_time_MAGHRIB.pack()
    today_prayer_time_ISHA.pack()
    rem_time.pack()
    label_time_now.pack()
    signature.place(relx = 0.0,
                    rely = 1.0,
                    anchor ='sw')
    version.place(relx = 1.0,
                    rely = 1.0,
                    anchor ='se')


if __name__ == "__main__":
    
    #init values for window
    root = tk.Tk()
    n = ToastNotifier()
    img = tk.PhotoImage(file=os.getcwd() + "/Prayerbeads.png")
    root.geometry("300x400")
    root.title("Prayer Times")
    root.wm_iconphoto(True, img)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    #init values
    timezone = pytz.timezone('Europe/Stockholm') 
    method = "3"
    longitude = "18.063240"
    latitude = "59.334591"
    notify_me = 10
    cities = []

    #different calculating methods to showcase in spinbox
    methods = ['University of Islamic Sciences, Karachi', #1
                'Islamic Society of North America', #2
                'Muslim World League', #3
                'Umm Al-Qura University, Makkah', #4
                'Egyptian General Authority of Survey', #5
                'Institute of Geophysics, University of Tehran', #7
                'Gulf Region', #8
                'Kuwait', #9
                'Qatar', #10
                'Majlis Ugama Islam Singapura, Singapore', #11
                'Union Organization islamic de France', #12
                'Diyanet İşleri Başkanlığı, Turkey', #13
                'Spiritual Administration of Muslims of Russia', #14
                'Moonsighting Committee Worldwide (also requires shafaq paramteer)'] #15

    #different calculating methods with keys and values to use for http request
    methods_dict = {
                'University of Islamic Sciences, Karachi': 1,
                'Islamic Society of North America': 2,
                'Muslim World League': 3, 
                'Umm Al-Qura University, Makkah': 4,
                'Egyptian General Authority of Survey': 5,
                'Institute of Geophysics, University of Tehran': 7,
                'Gulf Region': 8,
                'Kuwait': 9,
                'Qatar': 10, 
                'Majlis Ugama Islam Singapura, Singapore': 11, 
                'Union Organization islamic de France': 12,
                'Diyanet İşleri Başkanlığı, Turkey': 13,
                'Spiritual Administration of Muslims of Russia': 14, 
                'Moonsighting Committee Worldwide (also requires shafaq paramteer)': 15
    }

    #get json data
    data_file =  open('cities.json', encoding="utf8")
    data = json.load(data_file)
    for v in data:
        cities.append(v["name"])
    data_file.close()

    #Labels definitionspip install allcities
    field_method = tk.StringVar(root)
    field_location = tk.StringVar(root)
    field_time_to_notif = tk.StringVar(root)
    field_method.set('Muslim World League')
    field_location.set('Stockholm')
    field_time_to_notif.set('10')
    method_label = tk.Label(root, text ="Calculating method: ")
    choose_method = AutocompleteCombobox(
        root, 
        width=30, 
        font=('Times', 15),
        completevalues=methods,
        textvariable=field_method
        )

    location_label = tk.Label(root, text ="Location(city): ")
    choose_city = AutocompleteCombobox(
        root, 
        width=30, 
        font=('Times', 15),
        completevalues=cities,
        textvariable=field_location
        )
   
    time_to_notif_label = tk.Label(root, text ="Notify me minutes before prayer: ")
    choose_time_to_notif = tk.Entry(
        root, 
        width=5, 
        font=('Times', 15),
        textvariable=field_time_to_notif
        )

    save_button = tk.Button(root,
                            text = "Save", 
                            command = save_inputs)


    today_prayer_time_FAJR = tk.Label(root, text ="")
    today_prayer_time_SUNRISE = tk.Label(root, text = "")
    today_prayer_time_DHUHR = tk.Label(root, text ="")
    today_prayer_time_ASR = tk.Label(root, text ="")
    today_prayer_time_MAGHRIB = tk.Label(root, text ="")
    today_prayer_time_ISHA = tk.Label(root, text ="")

    rem_time = tk.Label(root, text="")
    label_time_now = tk.Label(root, text= "")
  
    signature = tk.Label(root, text="Made by Polo 2023-01-01", font=('Times', 8))
    version = tk.Label(root, text="v 1.2.0.3",font=('Times', 8))

    pack_labels()
    init()
    root.mainloop()

   
