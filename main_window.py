########################################################################################################################
#                                               Written By Liam Price                                                  #
#                                       Window Cleaning Assistant main_window.py                                       #
#                                              Date Started: 9-07-2020                                                 #
########################################################################################################################

# ██╗░░░░░███████╗███████╗██╗░░██╗░█████╗░███╗░░░███╗██╗░██████╗
# ██║░░░░░██╔════╝██╔════╝██║░░██║██╔══██╗████╗░████║╚█║██╔════╝
# ██║░░░░░█████╗░░█████╗░░███████║███████║██╔████╔██║░╚╝╚█████╗░
# ██║░░░░░██╔══╝░░██╔══╝░░██╔══██║██╔══██║██║╚██╔╝██║░░░░╚═══██╗
# ███████╗███████╗███████╗██║░░██║██║░░██║██║░╚═╝░██║░░░██████╔╝
# ╚══════╝╚══════╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝░░░╚═════╝░

# ░██████╗░█████╗░███████╗████████╗░██╗░░░░░░░██╗░█████╗░██████╗░███████╗
# ██╔════╝██╔══██╗██╔════╝╚══██╔══╝░██║░░██╗░░██║██╔══██╗██╔══██╗██╔════╝
# ╚█████╗░██║░░██║█████╗░░░░░██║░░░░╚██╗████╗██╔╝███████║██████╔╝█████╗░░
# ░╚═══██╗██║░░██║██╔══╝░░░░░██║░░░░░████╔═████║░██╔══██║██╔══██╗██╔══╝░░
# ██████╔╝╚█████╔╝██║░░░░░░░░██║░░░░░╚██╔╝░╚██╔╝░██║░░██║██║░░██║███████╗
# ╚═════╝░░╚════╝░╚═╝░░░░░░░░╚═╝░░░░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝╚═╝░░╚═╝╚══════╝

# Import Modules #
from tkinter import *  # Used to create the user interface on screen
import tkinter as tk  # likewise
from tkinter import ttk  # likewise
from tkcalendar import Calendar  # For creating calender date selection GUI
from tkinter import messagebox as mb  # For creating simple popup windows
from tkinter import simpledialog  # Similar to message box, but this one lets me get a String value input
import paho.mqtt.client as mqtt  # For wireless communication to WatchOS Application
import time, logging  # Self explanatory, keeping track of time
from datetime import date  # For selecting dates inside Tkinter
import json  # This is for storing the database
import glob  # Use this for listing a directory into a list
import os  # Use this for deleting JSON files

# TODO: Add multi processing to optimise program!
# TODO: Swap Linked Jobs and Preferred contact around
# TODO: Add "worker" to entry boxes per clean
# TODO: Add protection against user making multiple jobs or cleans with the same name!

#########################################################################
#                                                                       #
#                        Global Data Structures                         #
#                                                                       #
#########################################################################
job = {}
jobs = {}
history = []
job_names = []

# Global Variable Deceleration #
is_saved = True
clean_schedule_input_val = "1/08/2020"
current_job_id = 'job_num_0'
current_job_name = ""
clean_list = []  # When we display_specific_job this value will store a list off all clean names for reference
is_clean_saved = True
is_new_job = False  # We use this to always be aware if a Job entry is NEW or being UPDATED in the append function. We
# need to know this because if we try to append a clean at the same time as a new job, the cleans wont have a job
# reference which will in turn append all cleans from that last job that was selected which is not good.
total_number_of_jobs = 0

# CLEANS:
total_cleans_global = 0
current_clean_id_global = 0
is_new_clean = False
pre_existing_cleans = False

#########################################################################
#                                                                       #
#                        Main Window Functions                          #
#                                                                       #
#########################################################################


#  Display all jobs to the user according to the values found in the "sort" fields  #
def display_jobs():
    print("Displaying all jobs with sort     values applied")  # Diagnostic purposes
    read_jobs()
    today = date.today()
    today_format = today.strftime("%d/%m/%Y")
    print("Today's date: ", today_format)
    date_sel_button.configure(text=today_format)
    history_lab.config(text='Sort Results:')


# This function is typically called by the 'history_lb_callback' function in order to display all the information for a
# specific job in the GUI. It starts by clearing the Entry boxes and then reading the corresponding JSON file and
# then setting the Entry boxes so the user can manipulate them or just simply view them.
def display_specific_job(id_provided, job_id_specification_val):
    global current_job_id
    global current_job_name
    global total_cleans_global
    global clean_list
    global main_frame
    global pre_existing_cleans
    global clean_sel
    set_entry_normal()
    # Start by clearing all Entry Boxes:
    job_name_input.delete(0, "end")
    job_name_abrv_input.delete(0, "end")
    client_name_input.delete(0, "end")
    other_name_input.delete(0, "end")
    contact_phone_input.delete(0, "end")
    contact_email_input.delete(0, "end")
    linked_jobs_input.delete(0, "end")
    location_input.delete(0, "end")
    general_notes_input.delete(0, "end")
    clean_name_input.delete(0, "end")
    tools_input.delete(0, "end")
    price_input.delete(0, "end")
    clean_schedule_repeat_val.set("")
    clean_description_input.delete(0, "end")
    payment_method_var.set("")
    receipt_var.set("")
    time_eta_input.delete(0, "end")
    time_type_eta_val.set("")

    # The code below is used to reset OptionMenu for cleans
    clean_list = []
    clean_list_empty_temp = [""]

    # Clear the OptionMenu so the user does not get confused
    clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list_empty_temp)
    clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
    clean_sel.grid(row=0, column=3, sticky=W)
    clean_name_sel_val.set(clean_list_empty_temp[0])

    if not id_provided:
        print("ID Not Provided")
        print("Searching for name: " + str(job_id_specification_val) + " Inside all job_id's")
        # This will be used in conjunction with a for loop to find the job id for a job with no id specified. For
        # example a user might select a jobs name, however the program does not know where that name came from so it has
        # to search each job_id and check if the name matches. At the moment there's no need for this feature in the GUI
        # because I have made sure that the job_id is always accessible, but down the track if I add extra features to
        # GUI, this part of the code will be especially helpful.
        found = False
        print("Scanning through " + str(total_number_of_jobs) + " different jobs")
        for unknown_id_num in range(total_number_of_jobs):
            unknown_id = 'job_num_' + str(unknown_id_num)
            print("Scanning " + unknown_id)
            try:
                current_job_name = jobs[unknown_id]['job']['job_name']
                if current_job_name == job_id_specification_val:
                    print("Found corresponding job id! " + unknown_id)
                    found = True
                    break
            except Exception as error:
                print("Reached end of job JSON files with no match? Stopped at job ID: " + unknown_id)

        if found:
            print("matching job  ID was found)")
            search_results.set("Found!")
            temp = unknown_id
            current_job_id = unknown_id  # For global ID so other functions have access
            # For global job_name access so the append_jobs function is capable of knowing what the previous job name
            # was in case the user tries to change the name of a Job
            current_job_name = job_id_specification_val

        elif not found:
            history_lab.config(text='Unknown Error! job_id not resolved!')
            print("Unkown error name not found in any of the job_id's")
            return

    if id_provided:
        print("ID Provided")
        temp = job_id_specification_val
        current_job_id = job_id_specification_val  # For global ID so other functions have access

    job_name_temp = jobs[temp]['job']['job_name']
    new_clean_but.config(text='Add New Clean For "' + job_name_temp + '"')
    run_sel_show_val.set(jobs[temp]['job']['run'])
    job_name_input.insert(END, (jobs[temp]['job']['job_name']))
    job_name_abrv_input.insert(END, jobs[temp]['job']['job_name_abrv'])
    client_name_input.insert(END, jobs[temp]['job']['client_name'])
    other_name_input.insert(END, jobs[temp]['job']['other_name'])
    contact_phone_input.insert(END, jobs[temp]['job']['contact_phone'])
    contact_email_input.insert(END, jobs[temp]['job']['contact_email'])
    linked_jobs_input.insert(END, jobs[temp]['job']['linked_jobs'])
    preferred_contact_var.set(jobs[temp]['job']['preferred_contact'])
    location_input.insert(END, jobs[temp]['job']['location'])
    general_notes_input.insert(END, jobs[temp]['job']['general_notes'])
    # Create a list that is used for the OptionMenu widget so the user can select a clean to view / modify
    clean_list = []
    clean_list_empty_temp = [""]

    # Clear the OptionMenu so the user does not get confused
    clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list_empty_temp)
    clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
    clean_sel.grid(row=0, column=3, sticky=W)

    total_cleans_global = jobs[temp]['job']['number_of_cleans']
    if total_cleans_global == 0:
        print("FOUND 0 CLEANS")
        pre_existing_cleans = False
    print("Found this many cleans in job: " + str(total_cleans_global))

    for i in range(total_cleans_global):
        temp_num = 'clean_' + str(i)
        print("looking for clean: " + temp_num + "in job number " + temp)
        print("Current Clean List is = " + str(clean_list))
        try:
            clean_list.append(jobs[temp][temp_num]['clean_name'])
            clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list)
            clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
            clean_sel.grid(row=0, column=3, sticky=W)
        except:
            print("No more cleans left! Found " + str(i) + " Clean(s)")
            print("Clean List Found = " + str(clean_list))
            # Update OptionMenu List

    set_clean_entry_read_only()
    new_clean_but.config(text='Add New Clean For "' + jobs[temp]['job']['job_name'] + '"')
    delete_job.config(text='Delete Job "' + jobs[temp]['job']['job_name'] + '"')


# This function is very similar to 'display_specific_job' however this function displays only specific 'cleans' for the
# specified job. It also sets the Entry boxes to normal mode and modifies a few other Widgets text variables in order to
# give the user a more 'interactive' experience.
def display_specific_clean(*args):
    global current_job_id
    global current_clean_id_global
    global clean_name_sel_val
    global total_cleans_global
    global is_clean_saved
    # Start by clearing all Entry Boxes:
    print("Displaying Specific Clean")
    set_entry_normal()
    set_clean_entry_normal()
    clean_name_input.delete(0, "end")
    tools_input.delete(0, "end")
    price_input.delete(0, "end")
    clean_schedule_repeat_val.set("")
    clean_description_input.delete(0, "end")
    payment_method_var.set("")
    receipt_var.set("")
    time_eta_input.delete(0, "end")
    time_type_eta_val.set("")

    # Code gets value selected from OptionMenu....
    clean_temp = clean_name_sel_val.get()  # Get the point?
    if clean_temp == "":  # If clean OptionMenu is empty it must be because a new clean has been created, thus exit
        print("Oops! This was only a new clean not a pre existing one...")
        return

    print("We are looking for this 'name' inside any of the clean id's... " + clean_temp)

    for i in range(10):
        range_of_cleans = 'clean_' + str(i)
        print("looking for clean: " + range_of_cleans)
        print("With a name of... " + jobs[current_job_id][range_of_cleans]['clean_name'])
        try:
            if clean_temp == jobs[current_job_id][range_of_cleans]['clean_name']:
                print("Found!")
                current_clean_id_global = range_of_cleans
                is_clean_saved = False
                clean_name_input.insert(END, jobs[current_job_id][range_of_cleans]['clean_name'])
                tools_input.insert(END, jobs[current_job_id][range_of_cleans]['tools'])
                price_input.insert(END, jobs[current_job_id][range_of_cleans]['price'])
                clean_schedule_input_val = jobs[current_job_id][range_of_cleans]['clean_schedule']
                clean_schedule_input.configure(text=clean_schedule_input_val)
                clean_schedule_repeat_val.set(jobs[current_job_id][range_of_cleans]['clean_schedule_repeat'])
                clean_description_input.insert(END, jobs[current_job_id][range_of_cleans]['clean_description'])
                payment_method_var.set(jobs[current_job_id][range_of_cleans]['payment_method'])
                receipt_var.set(jobs[current_job_id][range_of_cleans]['receipt'])
                time_eta_input.insert(END, jobs[current_job_id][range_of_cleans]['time_eta'])
                time_type_eta_val.set(jobs[current_job_id][range_of_cleans]['time_type_eta'])
                return
        except:
            print("Repeat...")
    print("No Clean found by that name!")


# These 2 functions set the all of the Entry boxes to read or write mode. This is so the user can only enter new
# details if they press the New Job button. This method saves the user getting confused about how to use the GUI.
def set_entry_read_only():
    run_sel.config(state='disabled')
    job_name_input.config(state='readonly')
    job_name_abrv_input.config(state='readonly')
    client_name_input.config(state='readonly')
    other_name_input.config(state='readonly')
    contact_phone_input.config(state='readonly')
    contact_email_input.config(state='readonly')
    linked_jobs_input.config(state='readonly')
    preferred_contact_input.config(state='disabled')
    location_input.config(state='readonly')
    general_notes_input.config(state='readonly')


def set_clean_entry_read_only():
    global clean_schedule_repeat_input
    clean_name_input.config(state='readonly')
    tools_input.config(state='readonly')
    price_input.config(state='readonly')
    clean_schedule_input.config(state='disabled')
    clean_schedule_repeat_input.config(state='disabled')
    clean_description_input.config(state='readonly')
    payment_method_input.config(state='disabled')
    receipt_input.config(state='disabled')
    time_eta_input.config(state='readonly')
    time_type_eta_sel.config(state='disabled')


def set_entry_normal():
    global run_sel
    run_sel.config(state='normal')
    job_name_input.config(state='normal')
    job_name_abrv_input.config(state='normal')
    client_name_input.config(state='normal')
    other_name_input.config(state='normal')
    contact_phone_input.config(state='normal')
    contact_email_input.config(state='normal')
    linked_jobs_input.config(state='normal')
    preferred_contact_input.config(state='normal')
    location_input.config(state='normal')
    general_notes_input.config(state='normal')


def set_clean_entry_normal():
    global clean_schedule_repeat_input
    clean_name_input.config(state='normal')
    tools_input.config(state='normal')
    price_input.config(state='normal')
    clean_schedule_input.config(state='normal')
    clean_schedule_repeat_input.config(state='normal')
    clean_description_input.config(state='normal')
    payment_method_input.config(state='normal')
    receipt_input.config(state='normal')
    time_eta_input.config(state='normal')
    time_type_eta_sel.config(state='normal')


# This function runs when the user clicks the new job button, it adds the data found in the 'job' entry's into a
# new JSON file and adds a dictionary inside the corresponding JSON file. Afterwards the function reloads the database
# and GUI.
def new_job_func():
    print("Creating New Job...")
    global is_saved
    global total_cleans_global
    global is_new_job
    global current_job_name
    global pre_existing_cleans
    if is_saved:  # This if statement protects the user from accidentally clearing all the Entry boxes.

        total_cleans_global = 0

        # Start by clearing all Entry Boxes:
        job_name_input.delete(0, "end")
        job_name_abrv_input.delete(0, "end")
        client_name_input.delete(0, "end")
        other_name_input.delete(0, "end")
        contact_phone_input.delete(0, "end")
        contact_email_input.delete(0, "end")
        linked_jobs_input.delete(0, "end")
        location_input.delete(0, "end")
        general_notes_input.delete(0, "end")
        clean_name_input.delete(0, "end")
        tools_input.delete(0, "end")
        price_input.delete(0, "end")
        clean_schedule_repeat_val.set("")
        clean_description_input.delete(0, "end")
        payment_method_var.set("")
        receipt_var.set("")
        time_eta_input.delete(0, "end")
        time_type_eta_val.set("")

        # The code below is used to reset OptionMenu for cleans
        clean_list = []
        clean_list_empty_temp = [""]

        # Clear the OptionMenu so the user does not get confused
        clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list_empty_temp)
        clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
        clean_sel.grid(row=0, column=3, sticky=W)
        clean_name_sel_val.set(clean_list_empty_temp[0])

        new_job_name_val = simpledialog.askstring(title="Add New Job", prompt="Job Name:")
        print("Job Name = " + new_job_name_val)
        current_job_name = new_job_name_val
        set_entry_normal()
        job_name_input.delete(0, "end")
        job_name_input.insert(END, new_job_name_val)
        job_name_input.config(state='readonly')
        new_clean_but.config(text='Add New Clean For "' + new_job_name_val + '"')
        new_job_but.config(text='Please Press "Save" When Finished Creating Job')
        is_saved = False
        is_new_job = True
        pre_existing_cleans = False
    else:
        print("Job is not saved, prompting user...")
        clear_current_job_window = mb.askquestion('Cancel Job', 'Do you really want to cancel new job "' +
                                                  job_name_input.get() + '" ?')
        if clear_current_job_window == 'yes':
            is_saved = True
            cancel_entries()
            new_job_func()


# This function runs when the user clicks the new clean button, it adds the data found in the 'clean' entry's into a
# new dictionary inside the corresponding jobs JSON file. Afterwards the function reloads the database and GUI.
def new_clean_func():
    global current_job_id
    global is_clean_saved
    global clean_name_sel_val
    global is_saved  # is Job info saved?

    global is_new_clean

    if not is_saved:
        print("Job not saved into database!")
        mb.showinfo("Fail", "Please Save Job First!")
        return

    job_name_temp = job_name_input.get()
    empty_list_temp = [""]
    clean_name_sel_val.set(empty_list_temp[0])
    if job_name_temp == "":
        print("No Job selected!")
        mb.showinfo("Fail", "Please Select a Job First!")
        return

    print("Creating New Clean for Job... ")
    new_clean_name_val = simpledialog.askstring(title="Add New Clean", prompt="Clean Name:")
    print("Clean Name = ", new_clean_name_val)
    set_clean_entry_normal()
    clean_name_input.delete(0, "end")
    clean_name_input.insert(END, new_clean_name_val)
    clean_name_input.config(state='readonly')

    # Clear the clean Entries...
    tools_input.delete(0, "end")
    price_input.delete(0, "end")
    clean_schedule_repeat_val.set("")
    clean_description_input.delete(0, "end")
    payment_method_var.set("")
    receipt_var.set("")
    time_eta_input.delete(0, "end")
    time_type_eta_val.set("")

    print("Current Job Info: " + str(jobs[current_job_id]))
    # function to make Clean Entry boxes active

    is_new_clean = True


# This function deletes the desired job from the JSON database and then reloads the global data structures and GUI
def delete_job():
    # These 4 lines get the value form the Tkinter ListBox and remove the brackets so we can use it as a integer
    val = str(history_list_widget.curselection())
    val = val.replace("(", "")
    val = val.replace(")", "")
    val = val.replace(",", "")
    temp = 'job_num_' + val
    # The reason I use a try function here is because if the user has pressed delete without actually selecting a job
    # first, then the exception will show a popup window telling the user that they have not yet selected a job.
    try:
        delete_job_window = mb.askquestion('Delete Job', 'Do you really want to delete the job "' +
                                           jobs[temp]['job']['job_name'] + '" ?')
    except:
        mb.showinfo("Fail", "Please Select a Job First!")
        return
    if delete_job_window == 'yes':
        print("User Pressed Yes To Delete...")
        print("Deleting Job " + jobs[temp]['job']['job_name'])
        os.remove('jobs/' + jobs[temp]['job']['job_name'] + ".json")

        # Clear all Entry Boxes:
        run_sel_show_val.set("")
        job_name_input.delete(0, "end")
        job_name_abrv_input.delete(0, "end")
        client_name_input.delete(0, "end")
        other_name_input.delete(0, "end")
        contact_phone_input.delete(0, "end")
        contact_email_input.delete(0, "end")
        linked_jobs_input.delete(0, "end")
        preferred_contact_var.set("")
        location_input.delete(0, "end")
        general_notes_input.delete(0, "end")

        # Re-Display all jobs in the ListBox and rebuild data structures
        read_jobs()


# This function takes the Job Entry values from GUI and places them into multiple dictionaries and then writes them
# to the JSON file for storage
def append_job():
    global clean_schedule_input_val
    global is_saved
    global current_job_id
    global current_job_name
    global is_new_job
    global is_new_clean  # If is_cleaned_saved: False then increment the total_cleans_global by 1
    global total_cleans_global  # Hence...
    global current_clean_id_global
    global is_clean_saved
    global pre_existing_cleans
    print("Appending Job")
    job = {}

    if total_cleans_global > 0:
        print("There are 1 or more pre existing cleans....")
        pre_existing_cleans = True
        pre_existing_cleans = total_cleans_global

    if is_new_clean:
        print("NEW CLEAN DETECTED, incrementing 'total_cleans_global'")
        total_cleans_global += 1
        print("Total cleans is now: " + str(total_cleans_global))

    job['job'] = {'job_name': job_name_input.get()
        , 'run': run_sel_show_val.get()
        , 'job_name_abrv': job_name_abrv_input.get()
        , 'client_name': client_name_input.get()
        , 'other_name': other_name_input.get()
        , 'contact_phone': contact_phone_input.get()
        , 'contact_email': contact_email_input.get()
        , 'linked_jobs': linked_jobs_input.get()
        , 'preferred_contact': preferred_contact_var.get()
        , 'location': location_input.get()
        , 'general_notes': general_notes_input.get()
        , 'number_of_cleans': total_cleans_global
                  }
    recent_job_name_temp = job_name_input.get()
    if is_new_job:
        print("The current Job is NEW so we wont go any further.")
        is_new_job = False
        with open('jobs/' + recent_job_name_temp + '.json', 'w') as f:
            json.dump(job, f, indent=1)
        is_saved = True
        new_job_but.config(text='New Job')
        read_jobs()
        print("THE GLOBAL JOB ID IS NOW: " + current_job_id)
        display_specific_job(id_provided=False, job_id_specification_val=recent_job_name_temp)
        print("THE GLOBAL JOB ID IS NOW: " + current_job_id)

        # The code below is used to reset OptionMenu for cleans
        clean_list = []
        clean_list_empty_temp = [""]

        # Clear the OptionMenu so the user does not get confused
        clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list_empty_temp)
        clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
        clean_sel.grid(row=0, column=3, sticky=W)

    try:
        if pre_existing_cleans:  # If there are 1 or more Clean(s), add pre existing cleans so we don't delete them.
            print("There are " + str(pre_existing_cleans) + " Clean(s) in JSON file already")
            cleans_range = pre_existing_cleans # SUBTRACT 1 IF THERE R ERRORS
            for i in range(cleans_range):
                clean_id_temp = 'clean_' + str(i)
                print("Appending pre existing Clean ID: " + clean_id_temp + " To Job ID: " + current_job_id)
                job[clean_id_temp] = {'clean_name': jobs[current_job_id][clean_id_temp]['clean_name']
                    , 'tools': jobs[current_job_id][clean_id_temp]['tools']
                    , 'price': jobs[current_job_id][clean_id_temp]['price']
                    , 'clean_schedule': jobs[current_job_id][clean_id_temp]['clean_schedule']
                    , 'clean_schedule_repeat': jobs[current_job_id][clean_id_temp]['clean_schedule_repeat']
                    , 'clean_description': jobs[current_job_id][clean_id_temp]['clean_description']
                    , 'payment_method': jobs[current_job_id][clean_id_temp]['payment_method']
                    , 'receipt': jobs[current_job_id][clean_id_temp]['receipt']
                    , 'time_eta': jobs[current_job_id][clean_id_temp]['time_eta']
                    , 'time_type_eta': jobs[current_job_id][clean_id_temp]['time_type_eta']
                                      }
    except:
        print("Assuming there is a new job that has not yet been appended?")

    if is_new_clean:
        print("New Clean Detected! Appending this clean")
        clean_id_num_temp = total_cleans_global - 1
        print("Appending Current Clean number " + str(clean_id_num_temp))
        job['clean_' + str(clean_id_num_temp)] = {'clean_name': clean_name_input.get()
            , 'tools': tools_input.get()
            , 'price': price_input.get()
            , 'clean_schedule': clean_schedule_input_val
            , 'clean_schedule_repeat': clean_schedule_repeat_val.get()
            , 'clean_description': clean_description_input.get()
            , 'payment_method': payment_method_var.get()
            , 'receipt': receipt_var.get()
            , 'time_eta': time_eta_input.get()
            , 'time_type_eta': time_type_eta_val.get()
                                                  }
        is_clean_saved = True
        is_new_clean = False
    else:
        clean_name_search = clean_name_sel_val.get()
        print("ORIGINAL CLEAN NAME FROM OPTION MENU IS: " + clean_name_search)
        if clean_name_search != "":  # User did not click on a clean therefore clean is empty in GUI, don't append then.
            print("Searching for clean name: " + clean_name_search)
            for unknown_id_num in range(total_cleans_global):
                unknown_clean_id = 'clean_' + str(unknown_id_num)
                try:
                    found = False
                    current_clean_name = jobs[current_job_id][unknown_clean_id]['clean_name']
                    if current_clean_name == clean_name_search:
                        print("Found corresponding clean id! " + unknown_clean_id)
                        current_clean_id_global = unknown_clean_id
                        found = True
                        break
                except:
                    found = False

            if found:
                print("clean id was found, we will continue to append clean")
                print("Appending Current Clean number " + str(current_clean_id_global))
                job[str(current_clean_id_global)] = {'clean_name': clean_name_input.get()
                    , 'tools': tools_input.get()
                    , 'price': price_input.get()
                    , 'clean_schedule': clean_schedule_input_val
                    , 'clean_schedule_repeat': clean_schedule_repeat_val.get()
                    , 'clean_description': clean_description_input.get()
                    , 'payment_method': payment_method_var.get()
                    , 'receipt': receipt_var.get()
                    , 'time_eta': time_eta_input.get()
                    , 'time_type_eta': time_type_eta_val.get()
                                                      }
            elif not found:
                print("Unknown Error has occurred, clean_id was not resolved!")
                return

    # If user changed the name of the Job, also change the name of the file:
    recent_job_name_temp = job_name_input.get()
    print("Current Job Name in memory: " + current_job_name)
    print("Job Name in Entry Box: " + recent_job_name_temp)
    if current_job_name != recent_job_name_temp:
        print("JOB NAME CHANGE DETECTED!")
        os.remove('jobs/' + current_job_name + ".json")
        print("Deleted old version of Job")
        current_job_name = recent_job_name_temp

    with open('jobs/' + recent_job_name_temp + '.json', 'w') as f:
        json.dump(job, f, indent=1)
    is_saved = True
    new_job_but.config(text='New Job')
    read_jobs()
    print("Displaying specific job with updated clean, job_id is: " + current_job_id)
    display_specific_job(id_provided=True, job_id_specification_val=current_job_id)


def get_job_id(search_arguments_temp):
    global current_job_id
    print("Scanning through " + str(total_number_of_jobs) + " different jobs")
    print("Looking for job name: " + search_arguments_temp)
    for unknown_id_num in range(total_number_of_jobs):
        unknown_id = 'job_num_' + str(unknown_id_num)
        print("Scanning " + unknown_id)
        current_job_name = jobs[unknown_id]['job']['job_name']
        if current_job_name == search_arguments_temp:
            current_job_id = unknown_id
            print("Found corresponding job id! " + unknown_id)
            break


# This function reads all of the jobs from each JSON file one by one and stores each one in a dictionary of
# dictionaries. It also creates a list that stores only the names of all the Jobs which will be used for faster search
# times when the user searches for Job names. The function also appends all the Job names into the ListBox in the GUI.
def read_jobs():
    history_lab.config(text='Jobs')
    history_list_widget.delete(0, 'end')
    increment = 0
    global total_number_of_jobs
    print("Reading Jobs")
    try:
        jobs_files = (glob.glob("jobs/*.json"))
    except Exception as error:
        print("Database directory load error! Did the directory change?")
        print("Error code is: " + error)
        return

    try:
        for i in jobs_files:
            f = open(i, 'r+')
            job = json.load(f)
            job_names.append(job['job']['job_name'])  # This stores the names of all jobs for easy existence searching
            history_list_widget.insert(END, job['job']['job_name'])
            dict_val_name = 'job_num_' + str(increment)
            jobs.__setitem__(dict_val_name, job)
            increment += 1
            total_number_of_jobs = increment
            f.close()
    except Exception as error:
        print("Database read error! Did the JSON files get corrupted? Please check for JSON syntax errors")
        print("Error code is: " + error)
        return


# This Function searches the database for a match according to the values entered into the GUI's Search Menu.
def search_database():
    global search_results
    global total_number_of_jobs
    print("Search Function Commencing")
    search_results.set("Searching...")

    search_arguments_sort_temp = search_arguments_var.get()  # Does the user want to search for something specific?
    search_arguments_temp = search_arguments_input_var.get().lower()  # What is the actual variable being searched for?
    if search_arguments_temp == "":
        print("Search Input is empty")
        search_results.set("Please Enter a Value!")
        return

    clear_all_entries()
    history_list_widget.delete(0, 'end')
    found = False

    if search_arguments_sort_temp == "Search In: Job Names":
        print("Searching for job name: " + search_arguments_temp)
        print("Searching In: " + search_arguments_sort_temp)
        # total_number_of_jobs is assigned the total number of jobs found in the JSON storage directory, this happens
        # when the read_jobs function is called, this way we always know how many jobs there are, which means we know
        # EXACTLY how many times to loop through the for loop so we don't waste CPU power. How fancy is that?
        print("Scanning through " + str(total_number_of_jobs) + " different jobs")
        for unknown_id_num in range(total_number_of_jobs):
            unknown_id = 'job_num_' + str(unknown_id_num)
            print("Scanning " + unknown_id)
            try:
                current_job_name = str(jobs[unknown_id]['job']['job_name'])
                if search_arguments_temp in current_job_name.lower():
                    print("Found corresponding job id! " + unknown_id)
                    history_list_widget.insert(END, current_job_name)
                    found = True
            except Exception as error:
                print("Reached end of job JSON files, stopped at job ID: " + unknown_id)

    elif search_arguments_sort_temp == "Search In: Job Location":
        print("Searching for Job Location: " + search_arguments_temp)
        print("Searching In: " + search_arguments_sort_temp)
        # total_number_of_jobs is assigned the total number of jobs found in the JSON storage directory, this happens
        # when the read_jobs function is called, this way we always know how many jobs there are, which means we know
        # EXACTLY how many times to loop through the for loop so we don't waste CPU power. How fancy is that?
        print("Scanning through " + str(total_number_of_jobs) + " different jobs")
        for unknown_id_num in range(total_number_of_jobs):
            unknown_id = 'job_num_' + str(unknown_id_num)
            print("Scanning " + unknown_id)
            try:
                current_job_location = jobs[unknown_id]['job']['location']
                if current_job_location == search_arguments_temp:
                    print("Found corresponding job id! " + unknown_id)
                    history_list_widget.insert(END, jobs[unknown_id]['job']['job_name'])
                    found = True
            except Exception as error:
                print("Reached end of job JSON files, stopped at job ID: " + unknown_id)

    elif search_arguments_sort_temp == "Search In: Client Name":
        print("Searching for Client Name: " + search_arguments_temp)
        print("Searching In: " + search_arguments_sort_temp)
        # total_number_of_jobs is assigned the total number of jobs found in the JSON storage directory, this happens
        # when the read_jobs function is called, this way we always know how many jobs there are, which means we know
        # EXACTLY how many times to loop through the for loop so we don't waste CPU power. How fancy is that?
        print("Scanning through " + str(total_number_of_jobs) + " different jobs")
        for unknown_id_num in range(total_number_of_jobs):
            unknown_id = 'job_num_' + str(unknown_id_num)
            print("Scanning " + unknown_id)
            try:
                current_client_name = jobs[unknown_id]['job']['client_name']
                if current_client_name == search_arguments_temp:
                    print("Found corresponding job id! " + unknown_id)
                    history_list_widget.insert(END, jobs[unknown_id]['job']['job_name'])
                    found = True
            except Exception as error:
                print("Reached end of job JSON files, stopped at job ID: " + unknown_id)

    elif search_arguments_sort_temp == "Search In: Worker Names":
        print("Searching for Worker Name: " + search_arguments_temp)
        print("Searching In: " + search_arguments_sort_temp)
        # total_number_of_jobs is assigned the total number of jobs found in the JSON storage directory, this happens
        # when the read_jobs function is called, this way we always know how many jobs there are, which means we know
        # EXACTLY how many times to loop through the for loop so we don't waste CPU power. How fancy is that?
        print("Scanning through " + str(total_number_of_jobs) + " different jobs")
        for unknown_id_num in range(total_number_of_jobs):
            unknown_id = 'job_num_' + str(unknown_id_num)
            print("Scanning " + unknown_id)
            try:
                current_worker_name = jobs[unknown_id]['job']['other_name']
                if current_worker_name == search_arguments_temp:
                    print("Found corresponding job id! " + unknown_id)
                    history_list_widget.insert(END, jobs[unknown_id]['job']['job_name'])
                    found = True
            except Exception as error:
                print("Reached end of job JSON files, stopped at job ID: " + unknown_id)

    elif search_arguments_sort_temp == "Search In: Everything":
        print("Searching for: " + search_arguments_temp)
        print("Searching In: " + search_arguments_sort_temp)
        # total_number_of_jobs is assigned the total number of jobs found in the JSON storage directory, this happens
        # when the read_jobs function is called, this way we always know how many jobs there are, which means we know
        # EXACTLY how many times to loop through the for loop so we don't waste CPU power. How fancy is that?
        print("Scanning through " + str(total_number_of_jobs) + " different jobs")
        temp = []
        for unknown_id_num in range(total_number_of_jobs):
            unknown_id = 'job_num_' + str(unknown_id_num)
            print("Scanning " + unknown_id)
            current_val = jobs[unknown_id]['job']
            itemsList = current_val.items()
            for item in itemsList:
                print("SCANNING: " + str(item[1]))
                if item[1] == search_arguments_temp:
                    print("Found corresponding job id! " + unknown_id)
                    history_list_widget.insert(END, jobs[unknown_id]['job']['job_name'])
                    temp.append(jobs[unknown_id]['job']['job_name'])
                    found = True

            clean_temp = jobs[unknown_id]['job']['number_of_cleans']
            print("scanning through " + str(clean_temp) + " clean(s)")
            for item in range(clean_temp):
                clean_id = 'clean_' + str(item)
                current_val = jobs[unknown_id][clean_id]
                itemsList = current_val.items()
                for item in itemsList:
                    print("SCANNING: " + str(item[1]))
                    if item[1] == search_arguments_temp:
                        print("Found corresponding job id! " + unknown_id)
                        found = True
                        if not jobs[unknown_id]['job']['job_name'] in temp:
                            history_list_widget.insert(END, jobs[unknown_id]['job']['job_name'])
                            print("Adding job to results")

    if found:
        print("matching job(s) were found)")
        search_results.set("Found!")
        history_lab.config(text='Search Results:')
    elif not found:
        print("No Matches found with criteria")
        search_results.set("No Matches Found!")
        history_lab.config(text='No Matches Found!                              '
                                '(Click This Button To Re-Display All Jobs)')
        return

    display_specific_job(id_provided=True, job_id_specification_val=unknown_id)


#  Function runs when a select date button is clicked  #
def date_sel_window():
    # Function runs when user clicks the "Done" button  #
    def date_submit():
        print(cal.selection_get())
        temp = str(cal.selection_get())
        print("setting button to " + temp)
        date_sel_button.configure(text=temp)

    top = tk.Toplevel(my_window)
    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand1", year=2020, month=7, day=11)
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="Done", command=date_submit).pack()


# This is basically the same as date_sel_window however this function is used only for the clean date selection in
# order to keep things separate and simple.
def clean_date_sel_window():
    global clean_schedule_input_val

    # Function runs when user clicks the "Done" button  #
    def date_submit():
        print(cal.selection_get())
        clean_schedule_input_val = str(cal.selection_get())
        print("setting clean date button to " + clean_schedule_input_val)
        clean_schedule_input.configure(text=clean_schedule_input_val)

    top = tk.Toplevel(my_window)
    cal = Calendar(top,
                   font="Arial 14", selectmode='day',
                   cursor="hand1", year=2020, month=7, day=11)
    cal.pack(fill="both", expand=True)
    ttk.Button(top, text="Done", command=date_submit).pack()


# This function runs as a callback whenever the user clicks on a ListBox field inside the history_list widget. This
# also serves the purpose of selecting jobs when the user toggles the Widget into 'job view.'
def history_lb_callback(event):
    global history_list_widget
    sel = str(history_list_widget.get(ANCHOR))
    print("Selection is " + str(sel))
    print("Value Name is = " + sel)

    # These 4 lines get the value form the Tkinter ListBox and remove the brackets so we can use it as a integer
    val = str(history_list_widget.curselection())
    val = val.replace("(", "")
    val = val.replace(")", "")
    val = val.replace(",", "")
    temp = 'job_num_' + val

    # I decided to use the history_list_widget.curselection() instead so most of the code above is not used, this is
    # Because the order of the list box can change in some scenarios like when using the search menu, therefore the
    # logic above will output a job_id that does not correlate to the actual job_id stored in the dictionary.
    display_specific_job(id_provided=False, job_id_specification_val=sel)


# This function runs as a callback whenever the user clicks on a ListBox field inside the new_leases widget.
def new_leases_lb_callback(event):
    global new_leases_list_widget
    cs = new_leases_list_widget.curselection()
    print("'new_leases' Selection is " + str(cs))


# This function runs as a callback whenever the user clicks on a ListBox field inside the overdue_list widget.
def overdue_lb_callback(event):
    global overdue_list_widget
    cs = overdue_list_widget.curselection()
    print("'overdue' Selection is " + str(cs))


# This function runs as a callback whenever the user clicks on a ListBox field inside the skipped_jobs widget.
def skipped_jobs_lb_callback(event):
    global skipped_jobs_list_widget
    cs = skipped_jobs_list_widget.curselection()
    print("'skipped_jobs' Selection is " + str(cs))


# This function runs when the user clicks 'cancel' so as to clear all the entries so the user doesn't get confused
# confused about whats on the screen.
def cancel_entries():
    global is_clean_saved
    global is_new_job
    global is_saved
    is_saved = True
    is_clean_saved = True
    is_new_job = False
    print("Cancelling Job Entries")
    # Clear all Main / Job Entry Boxes:
    run_sel_show_val.set("")
    job_name_input.delete(0, "end")
    job_name_abrv_input.delete(0, "end")
    client_name_input.delete(0, "end")
    other_name_input.delete(0, "end")
    contact_phone_input.delete(0, "end")
    contact_email_input.delete(0, "end")
    linked_jobs_input.delete(0, "end")
    preferred_contact_var.set("")
    location_input.delete(0, "end")
    general_notes_input.delete(0, "end")
    new_clean_but.config(text='Add New Clean For...')
    new_job_but.config(text='New Job')
    clean_name_input.delete(0, "end")
    tools_input.delete(0, "end")
    price_input.delete(0, "end")
    clean_schedule_repeat_val.set("")
    clean_description_input.delete(0, "end")
    payment_method_var.set("")
    receipt_var.set("")
    time_eta_input.delete(0, "end")
    time_type_eta_val.set("")
    delete_job.config(text='Delete Job')

    # The code below is used to reset OptionMenu for cleans
    clean_list = []
    clean_list_empty_temp = [""]

    # Clear the OptionMenu so the user does not get confused
    clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list_empty_temp)
    clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
    clean_sel.grid(row=0, column=3, sticky=W)
    clean_name_sel_val.set(clean_list_empty_temp[0])
    set_entry_read_only()  # Set Entry boxes to read only
    set_clean_entry_read_only()


# This function toggles between viewing the history of a Job's cleans or viewing a simple list of all jobs applicable
# to the sort values in the top_frame.
def history_job_toggle():
    print("Toggle History / Jobs ListBox")
    read_jobs()


def clear_all_entries():
    print("Clearing ALL Entries")
    new_clean_but.config(text='Add New Clean For')
    delete_job.config(text='Delete Job')
    # Clear all Entry Boxes:
    job_name_input.delete(0, "end")
    job_name_abrv_input.delete(0, "end")
    client_name_input.delete(0, "end")
    other_name_input.delete(0, "end")
    contact_phone_input.delete(0, "end")
    contact_email_input.delete(0, "end")
    linked_jobs_input.delete(0, "end")
    location_input.delete(0, "end")
    general_notes_input.delete(0, "end")
    clean_name_input.delete(0, "end")
    tools_input.delete(0, "end")
    price_input.delete(0, "end")
    clean_schedule_repeat_val.set("")
    clean_description_input.delete(0, "end")
    payment_method_var.set("")
    receipt_var.set("")
    time_eta_input.delete(0, "end")
    time_type_eta_val.set("")
    # The code below is used to reset OptionMenu for cleans
    clean_list = []
    clean_list_empty_temp = [""]
    # Clear the OptionMenu so the user does not get confused
    clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list_empty_temp)
    clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
    clean_sel.grid(row=0, column=3, sticky=W)
    clean_name_sel_val.set(clean_list_empty_temp[0])
    # Clear the clean Entries...
    clean_name_input.delete(0, "end")
    tools_input.delete(0, "end")
    price_input.delete(0, "end")
    clean_schedule_repeat_val.set("")
    clean_description_input.delete(0, "end")
    payment_method_var.set("")
    receipt_var.set("")
    time_eta_input.delete(0, "end")
    time_type_eta_val.set("")


# This function prompts user with a confirmation box, closes the main window, and then opens the login window.
def log_out():
    log_out_window = mb.askquestion('Exit Application', 'Do you really want to log out?')
    if log_out_window == 'yes':
        print("Logging out...")
        my_window.destroy()
        import login_window


#########################################################################
#                                                                       #
#                         MQTT Setup Code                               #
#                                                                       #
#########################################################################
# These variables all get modified from the login_window.py script, only here for reference
online_mode = False
mqtt_ip = ""
mqtt_port = 0
cred_user = ""
cred_pass = ""


def connect_mqtt():
    print("Connecting to MQTT")
    client.username_pw_set(cred_user, cred_pass)
    client.connect(mqtt_ip, mqtt_port)  # establish connection
    time.sleep(1)
    client.loop_start()
    client.subscribe("/WCA/DesktopMain")  # subscribe to mqtt topic
    print("Connect success!")
    main_window_setup()


def on_subscribe(client, userdata, mid, granted_qos):
    time.sleep(1)
    logging.info("sub acknowledge message id=" + str(mid))


def on_disconnect(client, userdata, rc=0):
    logging.info("DisConnected result code " + str(rc))


def on_connect(client, userdata, flags, rc):
    logging.info("Connected flags" + str(flags) + "result code " + str(rc))


def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))
    print("message received  " + msg)
    if msg == "test1":
        print("test1 received from mqtt")
    if msg == "test2":
        print("test2 received from mqtt")


def on_publish(client, userdata, mid):
    logging.info("message published " + str(mid))


logging.basicConfig(level=logging.INFO)  # Error Logging #
QOS = 0  # QoS Level keep at 0
CLEAN_SESSION = True
client = mqtt.Client("WCA-Desktop-1", False)  # create client object
client.on_subscribe = on_subscribe  # assign function to callback
client.on_disconnect = on_disconnect  # assign function to callback
client.on_connect = on_connect  # assign function to callback
client.on_message = on_message  # when a payload is received this function runs


#########################################################################
#                                                                       #
#  Below are the functions specific for each event that is called from  #
#   main_window.py such as when you click a button and it sends a time  #
#                       value to the MQTT broker.                       #
#                                                                       #
#########################################################################


def send_data_time():
    client.publish("/WCA/out", "time")


#########################################################################
#                                                                       #
#                         Tkinter Setup Code                            #
#                                                                       #
#########################################################################
my_window = Tk()

#########################################################################
#                                                                       #
#                           String Variables                            #
#                                                                       #
#########################################################################
num_jobs = StringVar()
total_profit = StringVar()
clean_time_tot = StringVar()
travel_time_tot = StringVar()
total_time = StringVar()
time_sort_val = StringVar()
time_sort_val.set("ETA")  # default value
run_sel_val = StringVar()
run_sel_val.set("Bendigo")
worker_sel_val = StringVar()
worker_sel_val.set("Lynton")
run_sel_show_val = StringVar()
run_sel_show_val.set("")
payment_method_var = StringVar()
payment_method_var.set("")
receipt_var = StringVar()
receipt_var.set("")
clean_name_sel_val = StringVar()
clean_name_sel_val.set("")
time_type_eta_val = StringVar()
time_type_eta_val.set("")
time_frame_sel_val = StringVar()
time_frame_sel_val.set("Day")
preferred_contact_var = StringVar()
preferred_contact_var.set("")
search_arguments_var = StringVar()
search_arguments_var.set("Search In: Everything")
search_arguments_input_var = StringVar()
clean_schedule_repeat_val = StringVar()
clean_schedule_repeat_val.set("")
search_results = StringVar()
search_results.set("Search Results")


#########################################################################
#                                                                       #
#                         Geometry Management                           #
#                                                                       #
#########################################################################

# I wrapped all of the Tkinter code into a function, the reason is so I can import this .py file as a module from the
# login window and vice versa. Although the back and forth part is still experimental at this stage, it gets the job
# done, obviously having to declare so many variables as "global" is a bit annoying but it's the best it's gonna get
# for the time being.
def main_window_setup():
    global clean_sel
    global main_frame
    global general_notes_input
    global location_input
    global preferred_contact_input
    global linked_jobs_input
    global time_type_eta_sel
    global contact_email_input
    global contact_phone_input
    global other_name_input
    global client_name_input
    global job_name_abrv_input
    global job_name_input
    global time_eta_input
    global receipt_input
    global receipt_input
    global payment_method_input
    global payment_method_input
    global clean_description_input
    global clean_schedule_input
    global price_input
    global tools_input
    global clean_name_input
    global clean_schedule_repeat_input
    global time_frame_sel_val
    global history_list_widget
    global new_leases_list_widget
    global overdue_list_widget
    global skipped_jobs_list_widget
    global bg_photo  # This stops the garbage collector from deleting the photo #
    global date_sel_button
    global preferred_contact_var
    global history_lab
    global new_clean_but
    global delete_job
    global history_job_toggle
    global run_sel
    global new_job_but
    global clean_name_sel_val
    global search_results
    my_window.title("WCA Desktop v1.0")
    width = 1100
    height = 828
    my_window.geometry(f'{width}x{height}')
    my_window.iconbitmap('media/WCA-Icon.ico')
    my_window.configure(background='grey')
    my_window.grid_rowconfigure(1, weight=1)
    my_window.grid_columnconfigure(0, weight=1)
    # Background Photo Setup (needs to be done first otherwise it wont be put at the back) #
    bg_photo = PhotoImage(file="media/bgWCA1.PNG")
    bg_photo_label = Label(my_window, image=bg_photo)
    bg_photo_label.place(x=0, y=0)

    # Organise sections of GUI into frames #
    top_frame = Frame(my_window, bg='cyan3')
    main_frame = Frame(my_window, bg="gray20")
    side_panel_frame = Frame(my_window, bg="gray20")
    # Grid all the frames in place #
    top_frame.grid(row=0, sticky="nw")
    main_frame.grid(row=1, sticky="nw")
    side_panel_frame.grid(row=0, rowspan=2, sticky="ne")

    # Top Frame Widget Creation #
    date_sel_lab = Label(top_frame, text="   Time Window   ", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    date_sel_lab.config(font=("Arial", 11))
    time_frame_sel = OptionMenu(top_frame, time_frame_sel_val, "Day", "Week", "Month", "Year")
    time_frame_sel.config(width=12, bg="PeachPuff2", fg="Black")
    date_sel_button = Button(top_frame, text='Choose Date', command=date_sel_window, bg="DeepPink4", fg="Black",
                             height=2,
                             width=15)
    options_sel_lab = Label(top_frame, text="   Other Options   ", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    options_sel_lab.config(font=("Arial", 11))
    worker_sel = OptionMenu(top_frame, worker_sel_val, "Darren", "Brad", "Liam", "Lynton")
    worker_sel.config(width=12, bg="PeachPuff2", fg="Black")
    run_sel = OptionMenu(top_frame, run_sel_val, "Bendigo", "Country", "     All     ", "  Other   ")
    run_sel.config(width=12, bg="PeachPuff2", fg="Black")
    display_jobs_but = Button(top_frame, text="Display All Jobs", bg="DeepPink4", fg="black", command=display_jobs,
                              height=8, width=15)
    num_jobs_lab = Label(top_frame, text="Number Of Jobs", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    num_jobs_lab_var = Label(top_frame, text="      55      ", justify=LEFT, bg="Black", fg="White", relief=RAISED)
    tot_profit_lab = Label(top_frame, text="     Total Profit    ", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    tot_profit_lab_var = Label(top_frame, text="    $400    ", justify=LEFT, bg="Black", fg="White", relief=RAISED)
    tot_clean_time_lab = Label(top_frame, text="Total Clean Time", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    tot_clean_time_lab_var = Label(top_frame, text="    3 Hours    ", justify=LEFT, bg="Black", fg="White",
                                   relief=RAISED)
    tot_travel_time_lab = Label(top_frame, text="Total Travel Time", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    tot_travel_time_lab_var = Label(top_frame, text="     20 min     ", justify=LEFT, bg="Black", fg="White",
                                    relief=RAISED)
    time_sort_sel = OptionMenu(top_frame, time_sort_val, "ETA", "Recorded", "Average Recorded")
    time_sort_sel.config(bg="PeachPuff2", fg="Black")
    tot_time_lab = Label(top_frame, text="              Total Time              ", justify=LEFT, bg="Red", fg="White",
                         relief=RAISED)
    tot_time_lab_var = Label(top_frame, text="    3.4 Hours    ", justify=LEFT, bg="Black", fg="White", relief=RAISED)
    log_out_butn = Button(top_frame, text="Log Out", command=log_out, bg="orange", fg="black")

    # Top Frame Widget Placement #
    date_sel_lab.grid(row=0, column=0, pady=(0, 1), padx=(4, 4))
    time_frame_sel.grid(row=1, column=0, pady=(0, 1))
    date_sel_button.grid(row=2, column=0, pady=(0, 1))
    options_sel_lab.grid(row=0, column=1, pady=(0, 1), padx=(4, 4))
    worker_sel.grid(row=1, column=1)
    run_sel.grid(row=2, column=1)
    display_jobs_but.grid(row=0, column=2, rowspan=3, pady=(10, 15), padx=(0, 10))
    num_jobs_lab.grid(row=0, column=3, sticky=W)
    num_jobs_lab_var.grid(row=0, column=4, sticky=W)
    tot_profit_lab.grid(row=2, column=3, pady=(0, 30))
    tot_profit_lab_var.grid(row=2, column=4, sticky=W, pady=(0, 30))
    tot_clean_time_lab.grid(row=0, column=5, padx=(10, 0))
    tot_clean_time_lab_var.grid(row=0, column=6, sticky=W)
    tot_travel_time_lab.grid(row=2, column=5, pady=(0, 30), sticky=E)
    tot_travel_time_lab_var.grid(row=2, column=6, sticky=W, pady=(0, 30))
    time_sort_sel.grid(row=0, column=7, padx=(10, 0))
    tot_time_lab.grid(row=2, column=7, padx=(10, 0), pady=(0, 30))
    tot_time_lab_var.grid(row=2, column=8, sticky=W, pady=(0, 30))
    log_out_butn.grid(row=0, column=8, sticky=W)

    # Main Frame Widget Creation #
    run_sel = OptionMenu(main_frame, run_sel_show_val, "Run: Bendigo", "Run: Country", "Run: Other")
    run_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
    job_name_input = Entry(main_frame, width=22, justify='center')
    job_name_input.delete(0, "end")
    new_job_but = Button(main_frame, text="New Job", bg="DeepPink4", fg="black", command=new_job_func, height=6,
                         width=13, wraplength=100)
    job_name_abrv_input_label = Label(main_frame, text="Job Abbreviated Name:", justify=LEFT, bg="Red", fg="White",
                                      relief=RAISED)
    job_name_abrv_input = Entry(main_frame, width=40, justify='center', relief='raised')
    job_name_abrv_input.delete(0, "end")
    client_name_input_label = Label(main_frame, text="Client Name:", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    client_name_input = Entry(main_frame, width=40, justify='center', relief='raised')
    client_name_input.delete(0, "end")
    other_name_input_label = Label(main_frame, text="Other Employee Names:", justify=LEFT, bg="Red", fg="White",
                                   relief=RAISED)
    other_name_input = Entry(main_frame, width=40, justify='center', relief='raised')
    other_name_input.delete(0, "end")
    contact_phone_input_label = Label(main_frame, text="Phone Number:", justify=LEFT, bg="Red", fg="White",
                                      relief=RAISED)
    contact_phone_input = Entry(main_frame, width=40, justify='center', relief='raised')
    contact_phone_input.delete(0, "end")
    contact_email_input_label = Label(main_frame, text="Email Address:", justify=LEFT, bg="Red", fg="White",
                                      relief=RAISED)
    contact_email_input = Entry(main_frame, width=40, justify='center', relief='raised')
    contact_email_input.delete(0, "end")
    linked_jobs_input_label = Label(main_frame, text="Linked Jobs:", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    linked_jobs_input = Entry(main_frame, width=40, justify='center', relief='raised')
    linked_jobs_input.delete(0, "end")
    preferred_contact_input_label = Label(main_frame, text="Preffered Contact:", justify=LEFT, bg="Red", fg="White",
                                          relief=RAISED)
    preferred_contact_input = OptionMenu(main_frame, preferred_contact_var, "Phone", "Email", "Other")
    preferred_contact_input.config(width=33, height=1, bg="PeachPuff2", fg="Black")

    location_input_label = Label(main_frame, text="Job Location:", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    location_input = Entry(main_frame, width=40, justify='center', relief='raised')
    location_input.delete(0, "end")
    general_notes_input_label = Label(main_frame, text="General Notes:", justify=LEFT, bg="Red", fg="White",
                                      relief=RAISED)
    general_notes_input = Entry(main_frame, width=40, justify='center', relief='raised')
    general_notes_input.delete(0, "end")
    # Clean Entry side below #
    new_clean_but = Button(main_frame, text="Add New Clean For...", bg="DeepPink4", fg="black", command=new_clean_func,
                           height=6, width=13, wraplength=100)
    clean_list.append("Clean Name")
    clean_sel = OptionMenu(main_frame, clean_name_sel_val, *clean_list)
    clean_sel.config(width=15, height=1, bg="PeachPuff2", fg="Black")
    clean_name_input = Entry(main_frame, relief='raised', width=22, justify='center')
    clean_name_input.delete(0, "end")
    tools_input_label = Label(main_frame, text="Tools Required:", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    tools_input = Entry(main_frame, width=40, justify='center', relief='raised')
    tools_input.delete(0, "end")
    price_input_label = Label(main_frame, text="Price of clean:", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    price_input = Entry(main_frame, width=40, justify='center', relief='raised')
    price_input.delete(0, "end")
    clean_schedule_input_label = Label(main_frame, text="Clean Schedule:", justify=LEFT, bg="Red", fg="White",
                                       relief=RAISED)
    clean_schedule_input = Button(main_frame, text='Choose Starting Date', command=clean_date_sel_window,
                                  bg="DeepPink4",
                                  fg="Black", height=1, width=15, wraplength=100)
    clean_schedule_repeat_input = OptionMenu(main_frame, clean_schedule_repeat_val, "Daily", "Weekly", "Every 2nd Week",
                                             "Every 3 Weeks", "Every Month", "Every 2 Months", "Every 3 Months",
                                             "Every 4 Months", "Every 5 Months", "Every 6 Months", "Every Year")
    clean_schedule_repeat_input.config(width=13, height=1, bg="PeachPuff2", fg="Black")

    clean_description_input_label = Label(main_frame, text="Clean Description:", justify=LEFT, bg="Red", fg="White",
                                          relief=RAISED)
    clean_description_input = Entry(main_frame, width=40, justify='center', relief='raised')
    clean_description_input.delete(0, "end")
    payment_method_input = OptionMenu(main_frame, payment_method_var, "Payment Method: Cash", "Payment Method: Cheque",
                                      "Payment Method: Online", "Payment Method: Other")
    payment_method_input.config(width=33, height=1, bg="PeachPuff2", fg="Black")
    payment_method_input_label = Label(main_frame, text="Payment Method:", justify=LEFT, bg="Red",
                                       fg="White", relief=RAISED)
    receipt_input = OptionMenu(main_frame, receipt_var, "Receipt: Yes", "Receipt: No")
    receipt_input.config(width=33, height=1, bg="PeachPuff2", fg="Black")
    receipt_input_label = Label(main_frame, text="Receipt:", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    time_eta_input_label = Label(main_frame, text="ETA:", justify=LEFT, bg="Red", fg="White", relief=RAISED)
    time_eta_input = Entry(main_frame, width=20, justify='center', relief='raised')
    time_eta_input.delete(0, "end")
    time_type_eta_sel = OptionMenu(main_frame, time_type_eta_val, "Minutes", "Hours", "Days")
    time_type_eta_sel.config(width=12, height=1, bg="PeachPuff2", fg="Black")
    last_time_label = Label(main_frame, text="Last Recorded Clean Time:", justify=LEFT, bg="Red", fg="White",
                            relief=RAISED)
    last_time = Entry(main_frame, width=40, justify='center', relief='raised')
    last_time.delete(0, "end")
    average_time_label = Label(main_frame, text="Average Recorded Clean Time:", justify=LEFT, bg="Red", fg="White",
                               relief=RAISED)
    average_time = Entry(main_frame, width=40, justify='center', relief='raised')
    average_time.delete(0, "end")
    history_lab = Button(main_frame, text="History", justify=CENTER, bg="Red4", fg="White", relief=SUNKEN,
                         command=history_job_toggle, wraplength=216)
    delete_job = Button(main_frame, text="Delete", justify=LEFT, bg="DeepPink4", fg="Black", relief=RAISED,
                        command=delete_job, width=24)
    history_scrollbar = Scrollbar(main_frame)
    history_list_widget = Listbox(main_frame, yscrollcommand=history_scrollbar.set)
    history_list_widget.config(bd=10, cursor="heart", highlightcolor="blue", height=35, width=39)
    history_scrollbar.config(command=history_list_widget.yview)
    history_list_widget.bind("<Double-1>", history_lb_callback)
    cancel_entries_button = Button(main_frame, text='Cancel', command=cancel_entries, bg="DeepPink4", fg="black",
                                   height=2, width=13)
    save_entries_button = Button(main_frame, text='Save', command=append_job, bg="DeepPink4", fg="black", height=2,
                                 width=13)
    search_job = Label(main_frame, text="Search Menu:", justify=LEFT, bg="cyan4", fg="Black", relief=RAISED, width=24)
    search_arguments_menu = OptionMenu(main_frame, search_arguments_var, "Search In: Job Names",
                                       "Search In: Job Location", "Search In: Client Name", "Search In: Worker Names",
                                       "Search In: Everything")
    search_arguments_menu.config(width=22, height=1, bg="PeachPuff2", fg="Black")
    search_arguments_input = Entry(main_frame, width=29, justify='center', relief='raised',
                                   textvariable=search_arguments_input_var)
    search_job_button = Button(main_frame, text='Search', command=search_database, bg="DeepPink4", fg="black", height=2,
                               width=13)
    search_results_label = Label(main_frame, textvariable=search_results, justify=LEFT, bg="cyan4", fg="Black",
                                 relief=RAISED, width=24)

    # Main Frame Widget Placement #
    new_job_but.grid(row=0, column=1, rowspan=2, sticky=E)
    run_sel.grid(row=0, column=1, sticky=W)
    job_name_input.grid(row=1, column=1, ipady=5, pady=5, sticky=W)
    job_name_abrv_input_label.grid(row=2, column=1, sticky=E + W)
    job_name_abrv_input.grid(row=3, column=1, ipady=5, pady=5)
    client_name_input_label.grid(row=4, column=1, sticky=E + W)
    client_name_input.grid(row=5, column=1, ipady=5, pady=5)
    other_name_input_label.grid(row=6, column=1, sticky=E + W)
    other_name_input.grid(row=7, column=1, ipady=5, pady=5)
    contact_phone_input_label.grid(row=8, column=1, sticky=E + W)
    contact_phone_input.grid(row=9, column=1, ipady=5, pady=5)
    contact_email_input_label.grid(row=10, column=1, sticky=E + W)
    contact_email_input.grid(row=11, column=1, ipady=5, pady=5)
    linked_jobs_input_label.grid(row=12, column=1, sticky=E + W)
    linked_jobs_input.grid(row=13, column=1, ipady=5, pady=5)
    preferred_contact_input_label.grid(row=14, column=1, sticky=E + W)
    preferred_contact_input.grid(row=15, column=1)
    location_input_label.grid(row=16, column=1, sticky=E + W)
    location_input.grid(row=17, column=1, ipady=5, pady=5)
    general_notes_input_label.grid(row=18, column=1, sticky=E + W)
    general_notes_input.grid(row=19, column=1, ipady=5, pady=5)
    # Clean input placements below #
    new_clean_but.grid(row=0, column=3, rowspan=2, sticky=E)
    clean_sel.grid(row=0, column=3, sticky=W)
    clean_name_input.grid(row=1, column=3, ipady=5, pady=5, sticky=W)
    tools_input_label.grid(row=2, column=3, sticky=E + W)
    tools_input.grid(row=3, column=3, ipady=5, pady=5)
    price_input_label.grid(row=4, column=3, sticky=E + W)
    price_input.grid(row=5, column=3, ipady=5, pady=5)
    clean_schedule_input_label.grid(row=6, column=3, sticky=E + W)
    clean_schedule_input.grid(row=7, column=3, ipady=5, pady=5, sticky=E)
    clean_schedule_repeat_input.grid(row=7, column=3, pady=5, sticky=W)
    clean_description_input_label.grid(row=8, column=3, sticky=E + W)
    clean_description_input.grid(row=9, column=3, ipady=5, pady=5)
    payment_method_input_label.grid(row=10, column=3, pady=5, sticky=E + W)
    payment_method_input.grid(row=11, column=3, pady=5)
    receipt_input_label.grid(row=12, column=3, pady=5, sticky=E + W)
    receipt_input.grid(row=13, column=3, pady=5)
    time_eta_input_label.grid(row=14, column=3, sticky=E + W)
    time_eta_input.grid(row=15, column=3, ipady=5, pady=5, sticky=W)
    time_type_eta_sel.grid(row=15, column=3, pady=5, sticky=E)
    last_time_label.grid(row=16, column=3, sticky=E + W)
    last_time.grid(row=17, column=3, ipady=5, pady=5)
    average_time_label.grid(row=18, column=3, sticky=E + W)
    average_time.grid(row=19, column=3, ipady=5, pady=5)
    history_lab.grid(row=0, column=4, columnspan=3, sticky=N + S + E + W)
    delete_job.grid(row=19, column=7, columnspan=1, sticky=N + S + E + W)
    history_scrollbar.grid(row=0, rowspan=20, column=6, sticky=N + S)
    history_list_widget.grid(row=1, rowspan=19, column=4, columnspan=2, sticky=N)
    cancel_entries_button.grid(row=19, column=4, sticky=E + W)
    save_entries_button.grid(row=19, column=5, sticky=E + W)
    search_job.grid(row=0, column=7, columnspan=1, sticky=N + S + E + W)
    search_arguments_menu.grid(row=1, column=7, columnspan=1, sticky=N)
    search_arguments_input.grid(row=1, column=7, columnspan=1, sticky=S)
    search_job_button.grid(row=2, column=7, columnspan=1, sticky=N, rowspan=2)
    search_results_label.grid(row=4, column=7, columnspan=1, sticky=N, rowspan=2)

    # Side Panel Frame Widget Creation #
    new_leases_lab = Label(side_panel_frame, text="             New Leases            ", justify=LEFT, bg="Red",
                           fg="White", relief=RAISED)
    new_leases_scrollbar = Scrollbar(side_panel_frame)
    new_leases_list_widget = Listbox(side_panel_frame, yscrollcommand=new_leases_scrollbar.set)
    for line in range(100):
        new_leases_list_widget.insert(END, "This is line number " + str(line))
    new_leases_list_widget.config(bd=10, cursor="heart", highlightcolor="blue", height=11)
    new_leases_scrollbar.config(command=history_list_widget.yview)
    new_leases_list_widget.bind("<Double-1>", new_leases_lb_callback)
    overdue_lab = Label(side_panel_frame, text="             Overdue Jobs          ", justify=LEFT, bg="Red",
                        fg="White", relief=RAISED)
    overdue_scrollbar = Scrollbar(side_panel_frame)
    overdue_list_widget = Listbox(side_panel_frame, yscrollcommand=overdue_scrollbar.set)
    for line in range(100):
        overdue_list_widget.insert(END, "This is line number " + str(line))
    overdue_list_widget.config(bd=10, cursor="heart", highlightcolor="blue", height=13)
    overdue_scrollbar.config(command=overdue_list_widget.yview)
    overdue_list_widget.bind("<Double-1>", overdue_lb_callback)
    skipped_jobs_lab = Label(side_panel_frame, text="             Skipped Jobs           ", justify=LEFT, bg="Red",
                             fg="White", relief=RAISED)
    skipped_jobs_scrollbar = Scrollbar(side_panel_frame)
    skipped_jobs_list_widget = Listbox(side_panel_frame, yscrollcommand=skipped_jobs_scrollbar.set)
    for line in range(100):
        skipped_jobs_list_widget.insert(END, "This is line number " + str(line))
    skipped_jobs_list_widget.config(bd=10, cursor="heart", highlightcolor="blue", height=19)
    skipped_jobs_scrollbar.config(command=skipped_jobs_list_widget.yview)
    skipped_jobs_list_widget.bind("<Double-1>", skipped_jobs_lb_callback)
    # Side Panel Frame Widget Placement #
    new_leases_lab.grid(row=0, column=0, sticky=N)
    new_leases_list_widget.grid(row=1, column=0, sticky=N)
    new_leases_scrollbar.grid(row=1, column=1, sticky=N + S)
    overdue_lab.grid(row=2, column=0, sticky=N)
    overdue_list_widget.grid(row=3, column=0, sticky=N)
    overdue_scrollbar.grid(row=3, column=1, sticky=N + S)
    skipped_jobs_lab.grid(row=4, column=0, sticky=N)
    skipped_jobs_list_widget.grid(row=5, column=0, sticky=N)
    skipped_jobs_scrollbar.grid(row=5, column=1, sticky=N + S)
    set_entry_read_only()
    set_clean_entry_read_only()
    clean_name_sel_val.trace('w', display_specific_clean)  # Trace any changes made to clean selection so we can show
    # the right stuff to user
    my_window.after(500, display_jobs)
    loop_main_window()


# Runs the main loop that updates the GUI, this also gives me the option to run in online or offline mode since the
# school internet is really really GREAT!
def loop_main_window():
    if online_mode:
        print("Starting in Online Mode")
    else:
        print("Starting in Offline Mode")

    my_window.mainloop()

#########################################################################
#                                                                       #
#                             Acknowledgments                           #
#                                                                       #
#########################################################################
#                                                                       #
# I decided to format my Tkinter widgets in the way I have because of   #
# what read in the following StackOverflow post...                      #
# https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using #
#       -frames-and-grid                                                #
# I figured I needed some way or organising my Tkinter widgets because  #
# there is A LOT of widgets in my design.                               #
#########################################################################
