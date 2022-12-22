import datetime
import pytz
import requests
from tkinter import *
from tkinter import messagebox
import json
import time
from timezonefinder import TimezoneFinder
from time import sleep
from ttkwidgets.autocomplete import AutocompleteCombobox
from tkinter import *
from win10toast import ToastNotifier


def init():
    value1, value2 = get_new_times()
    pName, pTime, index = check_each_prayer(value1,value2)
    timeleft = get_notification_time(pName,pTime,index)
    sleep_until_notif_time(timeleft,pName,index)
    root.mainloop()

def prayer_times_today(prayer_times_dict):

    today_prayer_time_FAJR = Label(root, text ="Fajr: " + prayer_times_dict["Fajr"])
    today_prayer_time_SUNRISE = Label(root, text = "Shuruq: " + prayer_times_dict["Sunrise"])
    today_prayer_time_DHUHR = Label(root, text ="Dhuhr: " + prayer_times_dict["Dhuhr"])
    today_prayer_time_ASR = Label(root, text ="Asr: " + prayer_times_dict["Asr"])
    today_prayer_time_MAGHRIB = Label(root, text ="Maghrib: " + prayer_times_dict["Maghrib"])
    today_prayer_time_ISHA = Label(root, text ="Isha: " + prayer_times_dict["Isha"])

    labels.append(today_prayer_time_FAJR)
    labels.append(today_prayer_time_SUNRISE)
    labels.append(today_prayer_time_DHUHR)
    labels.append(today_prayer_time_ASR)
    labels.append(today_prayer_time_MAGHRIB)
    labels.append(today_prayer_time_ISHA)
    
    today_prayer_time_FAJR.pack()
    today_prayer_time_SUNRISE.pack()
    today_prayer_time_DHUHR.pack()
    today_prayer_time_ASR.pack()
    today_prayer_time_MAGHRIB.pack()
    today_prayer_time_ISHA.pack()

def time_now_live(time):
    time_now = datetime.datetime.now(timezone)
    time_now_refined = time_now.replace(tzinfo=None)
    time_now_refined = str(time_now_refined).split(" ")
    time_now_refined = time_now_refined[1].split(".")[0]
    time.config(text=" Time Now: " + str(time_now_refined), fg='#00FF00')
    return


def sleep_until_new_day():
    rem_time_twelve = Label(root, text = " Timeleft bofore 00:00")
    labels.append(rem_time_twelve)
    rem_time_twelve.pack()
    label_time_now = Label(root, text= "Time now: ")
    labels.append(label_time_now)
    label_time_now.pack()
    deadline = "00:00:00"
    deadline_format = datetime.datetime.strptime(deadline, '%H:%M:%S')
    while True:
        time_now = datetime.datetime.now(timezone).replace(tzinfo=None)
        remaining_time_twelve = str((deadline_format - time_now).total_seconds()).split(".")[0]
        remaining_time_twelve = int(remaining_time_twelve)
        rem_time_twelve.config(text=" Timeleft before 00:00 - " + convert(remaining_time_twelve))
        time_now_live(label_time_now)
        root.update()
        stringed_time_now = time_now.strftime('%H:%M:%S')
        if stringed_time_now == deadline:
            for label in labels: label.destroy()
            break;
    init()
    return  


def sleep_until_notif_time(notif_time, pray_name, idx):
    rem_time = Label(root, text=" Timeleft before notif time ")
    label_time_now = Label(root, text= "Time now: ")
    labels.append(rem_time)
    labels.append(label_time_now)
    rem_time.pack()
    label_time_now.pack()
    if pray_name == "Sunrise":
        pray_name = "Shuruq"
    while notif_time > datetime.datetime.now(timezone).replace(tzinfo=None):
        time_now = datetime.datetime.now(timezone)
        remaining_time = str((notif_time - time_now.replace(tzinfo=None)).total_seconds()).split(".")[0]
        remaining_time = int(remaining_time)
        rem_time.config(text=" Notify me " + str(notify_me) + " minutes before " + pray_name + " " + convert(remaining_time))
        time_now_live(label_time_now)
        root.update()
    n.show_toast("PrayerTimes", pray_name + " comes in 10 minutes", duration = 10,
    icon_path ="E:/Prayerbeads.ico")
    for label in labels: label.destroy()
    if idx == 5:
        sleep_until_new_day()
    else:
        init()
    return

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
     
    return "%d:%02d:%02d" % (hour, minutes, seconds)


def get_notification_time(prayer_name, prayer_time, index):
    # Calculate the minutes before the prayer
    if index == 0:
        notification_time = datetime.datetime.combine(
            datetime.date.today(), prayer_time 
        ) - datetime.timedelta(minutes=notify_me) + datetime.timedelta(days=1)
        return notification_time
    else:
        notification_time = datetime.datetime.combine(
            datetime.date.today(), prayer_time
        ) - datetime.timedelta(minutes=10)
        print("Prayer: " + str(prayer_name))
        print(" ")
        print("Notif time: "+ str(notification_time))
        print(" ")
        # Get the current time in the specified timezone
        time_now = datetime.datetime.now(timezone).replace(tzinfo=None)
        print("Timenow: " + str(time_now))
        print(" ")
    
        return notification_time




def get_new_times():
    current_time = datetime.datetime.now(timezone).replace(tzinfo=None) 
    print("CURRENT DATE: "+ str(current_time))
    print(" ")
    current_date = datetime.datetime.strftime(current_time, '%d-%m-%Y')
    print("refined DATE: " + str(current_date))
    print(" ")

    current_day = int(current_date.split("-")[0])
    current_month = int(current_date.split("-")[1])
    current_year = int(current_date.split("-")[2])

    # The URL of the website with the prayer times
    prayer_times_url = f'http://api.aladhan.com/v1/calendar?latitude={latitude}&longitude={longitude}&method={method}&month={current_month}&year={current_year}'
    prayer_times_dict = {}

    current_time_split = str(current_time).split(" ")
    refined_current_time = current_time_split[1].split(".")[0]
    print("refined TIME: " + str(refined_current_time))
    print(" ")

    # Send a request to the website to get the prayer times
    response = requests.get(prayer_times_url)


    # Parse the response to get the prayer times
    prayer_times = response.json()

    prayer_times_dict["Fajr"] = (prayer_times["data"][current_day-1]["timings"]["Fajr"].split()[0])
    prayer_times_dict["Sunrise"] = (prayer_times["data"][current_day-1]["timings"]["Sunrise"].split()[0])
    prayer_times_dict["Dhuhr"] = (prayer_times["data"][current_day-1]["timings"]["Dhuhr"].split()[0])
    prayer_times_dict["Asr"] = (prayer_times["data"][current_day-1]["timings"]["Asr"].split()[0])
    prayer_times_dict["Maghrib"] = (prayer_times["data"][current_day-1]["timings"]["Maghrib"].split()[0])
    prayer_times_dict["Isha"] = (prayer_times["data"][current_day-1]["timings"]["Isha"].split()[0])
    
    # The names of the Islamic prayers
    print(prayer_times_dict)
    print(refined_current_time)
    prayer_times_today(prayer_times_dict)
    return prayer_times_dict, refined_current_time

def check_each_prayer(prayer_times_dict, ref_currtime):
  
    for index, prayer_name in enumerate(prayer_times_dict):
        
        # Get the prayer time from the response
        prayer_time = prayer_times_dict[prayer_name]
        print(prayer_name)

        prayer_time = datetime.time.fromisoformat(prayer_time)
        print(prayer_time)

        currtime_totime = datetime.datetime.strptime(ref_currtime, '%H:%M:%S').time()
        currtime_todate = datetime.datetime.combine(
            datetime.date.today(), currtime_totime
        )
        print(currtime_todate)
        prayertime_todate = datetime.datetime.combine(
            datetime.date.today(), prayer_time
        )
        print(prayertime_todate)
        diff = prayertime_todate - currtime_todate
        print("DIFFF: " + str(diff))

        if not str(diff).startswith('-'):
            print(prayer_name)
            print(prayer_time)
            print(index)
            return prayer_name, prayer_time, index
        if index == 5:
            sleep_until_new_day()
            return

      

def save_inputs():
    global timezone
    global latitude
    global longitude
    global method
    global notify_me
    method = choose_method.get()
    city = choose_city.get() 
    notify_me = int(choose_time_to_notif.get())
    with open('cities.json') as f:    
        data = json.load(f)
        for i in range(len(data)):
            if data[i]['name'] == city:
                latitude = float(data[i]['lat'])
                longitude = float(data[i]['lng'])
    obj = TimezoneFinder()
    timezone_result = obj.timezone_at(lat=latitude, lng=longitude)
    timezone = pytz.timezone(timezone_result) 
    method = methods_dict[method]
    for label in labels: label.destroy()
    init()
    return


if __name__ == "__main__":
    n = ToastNotifier()
    img = PhotoImage(file="E:/Prayerbeads.png")
    root.wm_iconphoto(True, img)
    timezone = pytz.timezone('Europe/Stockholm') 
    method = "3"
    longitude = "18.063240"
    latitude = "59.334591"
    notify_me = 10

    root = Tk()
    root.geometry("300x400")
    root.title("Prayer Times")
    labels = []
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

    cities = []

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


    with open('cities.json') as data_file:    
        data = json.load(data_file)
        for v in data:
            cities.append(v["name"])


    field_method = StringVar(root)
    field_location = StringVar(root)
    field_time_to_notif = StringVar(root)
    field_method.set('Muslim World League')
    field_location.set('Stockholm')
    field_time_to_notif.set('10')
    method_label = Label(root, text ="Calculating method: ")
    choose_method = AutocompleteCombobox(
        root, 
        width=30, 
        font=('Times', 15),
        completevalues=methods,
        textvariable=field_method
        )
    method_label.pack()
    choose_method.pack()
    location_label = Label(root, text ="Location: ")
    choose_city = AutocompleteCombobox(
        root, 
        width=30, 
        font=('Times', 15),
        completevalues=cities,
        textvariable=field_location
        )
    location_label.pack()
    choose_city.pack()

    time_to_notif_label = Label(root, text ="Notify me minutes bofore prayer: ")
    choose_time_to_notif = Entry(
        root, 
        width=5, 
        font=('Times', 15),
        textvariable=field_time_to_notif
        )
    time_to_notif_label.pack()
    choose_time_to_notif.pack()


    save_button = Button(root,
                            text = "Save", 
                            command = save_inputs)


    save_button.pack()

    init()
