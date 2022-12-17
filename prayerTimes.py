import datetime
import pytz
import requests
from tkinter import *
from tkinter import messagebox
from time import sleep


def init():
    value1, value2 = get_new_times()
    pName, pTime, index = check_each_prayer(value1,value2)
    timeleft = get_notification_time(pName,pTime)
    sleep_until_notif_time(timeleft,pName,index)
    root.mainloop()

def prayer_times_today(prayer_times_dict):
    today_prayer_time_FAJR = Label(root, text ="Fajr: " + prayer_times_dict["Fajr"])
    today_prayer_time_DHUHR = Label(root, text ="Dhuhr: " + prayer_times_dict["Dhuhr"])
    today_prayer_time_ASR = Label(root, text ="Asr: " + prayer_times_dict["Asr"])
    today_prayer_time_MAGHRIB = Label(root, text ="Maghrib: " + prayer_times_dict["Maghrib"])
    today_prayer_time_ISHA = Label(root, text ="Isha: " + prayer_times_dict["Isha"])

    labels.append(today_prayer_time_FAJR)
    labels.append(today_prayer_time_DHUHR)
    labels.append(today_prayer_time_ASR)
    labels.append(today_prayer_time_MAGHRIB)
    labels.append(today_prayer_time_ISHA)

    today_prayer_time_FAJR.pack()
    today_prayer_time_DHUHR.pack()
    today_prayer_time_ASR.pack()
    today_prayer_time_MAGHRIB.pack()
    today_prayer_time_ISHA.pack()

def time_now_live(time):
    time_now = datetime.datetime.now(timezone)
    time_now_refined = time_now.replace(tzinfo=None)
    time_now_refined = str(time_now_refined).split(" ")
    time_now_refined = time_now_refined[1].split(".")[0]
    time.config(text=" Time Now: " + str(time_now_refined))
    return


def sleep_until_new_day():
    rem_time_twelve = Label(root, text = " Timeleft bofore 00:00")
    labels.append(rem_time_twelve)
    rem_time_twelve.pack()
    label_time_now = Label(root, text= "Time now: ")
    labels.append(label_time_now)
    label_time_now.pack()
    deadline = "23:59:59"
    deadline_format = datetime.datetime.strptime(deadline, '%H:%M:%S')
    while deadline_format < datetime.datetime.now(timezone).replace(tzinfo=None):
        time_now = datetime.datetime.now(timezone)
        remaining_time_twelve = str((deadline_format - time_now.replace(tzinfo=None)).total_seconds()).split(".")[0]
        remaining_time_twelve = int(remaining_time_twelve)
        rem_time_twelve.config(text=" Timeleft before 00:00 " + convert(remaining_time_twelve))
        print(" Timeleft before 00:00:00 - " + convert(remaining_time_twelve), end="\r")
        sleep(0.5)
        root.update()
    init()
    return  


def sleep_until_notif_time(notif_time, pray_name, idx):
    rem_time = Label(root, text=" Timeleft before notif time ")
    notif_label = Label(root, text="")
    label_time_now = Label(root, text= "Time now: ")
    labels.append(rem_time)
    labels.append(notif_label)
    labels.append(label_time_now)
    label_time_now.pack()
    rem_time.pack()
    while notif_time > datetime.datetime.now(timezone).replace(tzinfo=None):
        time_now = datetime.datetime.now(timezone)
        remaining_time = str((notif_time - time_now.replace(tzinfo=None)).total_seconds()).split(".")[0]
        remaining_time = int(remaining_time)
        rem_time.config(text=" Notify me 10 minutes before " + pray_name + " " + convert(remaining_time))
        print(" Timeleft before " + pray_name+ ": " + convert(remaining_time), end="\r")
        time_now_live(label_time_now)
        sleep(0.5)
        root.update()
    notif_label.pack()
    notif_label.config(text= pray_name + " comes in 10 minutes!!!")
    for label in labels: label.destroy()
    if idx == 4:
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


def get_notification_time(prayer_name, prayer_time):
    # Calculate the time 10 minutes before the prayer
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
    prayer_times_url = f'http://api.aladhan.com/v1/calendar?latitude=56.16156&longitude=15.58661&method=3&month={current_month}&year={current_year}'
    prayer_times_dict = {}

    current_time_split = str(current_time).split(" ")
    refined_current_time = current_time_split[1].split(".")[0]
    print("refined TIME: " + str(refined_current_time))
    print(" ")

    # Send a request to the website to get the prayer times
    response = requests.get(prayer_times_url)


    # Parse the response to get the prayer times
    prayer_times = response.json()

    #print(prayer_times)
    prayer_times_dict["Fajr"] = (prayer_times["data"][current_day-1]["timings"]["Fajr"].split()[0])
    prayer_times_dict["Dhuhr"] = (prayer_times["data"][current_day-1]["timings"]["Dhuhr"].split()[0])
    prayer_times_dict["Asr"] = (prayer_times["data"][current_day-1]["timings"]["Asr"].split()[0])
    prayer_times_dict["Maghrib"] = (prayer_times["data"][current_day-1]["timings"]["Maghrib"].split()[0])
    prayer_times_dict["Isha"] = (prayer_times["data"][current_day-1]["timings"]["Isha"].split()[0])
    
    # The names of the Islamic prayers
    print(prayer_times_dict)
    prayer_times_today(prayer_times_dict)
    return prayer_times_dict, refined_current_time

def check_each_prayer(prayer_times_dict, ref_currtime):
    # Send notifications for all of the prayers
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
        diff_int = int(str(diff).split(":")[1])
        if not str(diff).startswith('-') and diff_int > 10:
            print(prayer_name)
            print(prayer_time)
            print(index)
            return prayer_name, prayer_time, index
        


# The timezone for the location where the prayers are observed

timezone = pytz.timezone('Europe/Stockholm')  
root = Tk()
root.geometry("800x400")
root.title("Prayer Times")
labels = []
init()
