########################################################################################################################
#                                                  Written By Liam Price                                               #
#       This module runs in order to prompt user with a login screen and an option to use the software offline.        #
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
from tkinter import *
from tkinter.messagebox import showinfo
import json  # Used to load and dump login cred info for the MQTT client (handled in main_window.py)

############################################
#                                          #
#   Global Variables and data structures   #
#                                          #
############################################
pass_attempt = 0
online_mode = False
path_to_profiles = 'misc_data/login_creds.json'


#########################################################################
#                                                                       #
#                        Main Window Functions                          #
#                                                                       #
#########################################################################
def login():
    global pass_attempt
    print("Attempting Login")  # Diagnostic purposes
    print(password_input.get())
    if password_input.get() == "class":
        print("Password Correct")
        password_feedback.set("  Enter Password  ")
        if online_mode:  # Online Mode #
            # Close login window #
            login_window.destroy()
            initiate_mqtt()
        if not online_mode:  # Offline Mode #
            print("Logging in with offline mode")
            # Close login window #
            login_window.destroy()
            import main_window as main
            main.online_mode = False  # Tell main_window that we are in online mode
            main.main_window_setup()
    else:
        print("Wrong Password")
        password_input.delete(0, "end")
        password_feedback.set("Wrong Password")
        pass_attempt += 1
        if pass_attempt == 5:
            showinfo("Access Denied", "Password entered incorrectly 5 times! Application will now close.")
            login_window.destroy()


def initiate_mqtt():
    print("Initiating MQTT")
    mqtt_ip = str(ip_input_val.get())
    mqtt_port = int(port_input_val.get())
    cred_user = mqtt_user_input_val.get()
    cred_pass = mqtt_pass_input_val.get()
    try:
        import main_window as main
        main.online_mode = True  # Tell main_window that we are in online mode
        main.mqtt_ip = mqtt_ip
        main.mqtt_port = mqtt_port
        main.cred_user = cred_user
        main.cred_pass = cred_pass
        main.connect_mqtt()
    except Exception as reason:
        online_mode_val.set("Connection Failed!")
        print("Connection Failed")
        print(reason)


def on_network_type_change(*args):
    global online_mode
    c_val = str(online_mode_val.get())
    if c_val == "Online Mode":
        online_mode = True
        print("Online Mode Activated")
        replace_custom_widgets()
    elif c_val == "Offline Mode":
        online_mode = False
        print("Offline Mode Activated")
        remove_custom_widgets()


def on_custom_connection_change(*args):
    connection_id = str(connection_type_sel_val.get())
    if connection_id == "Public":
        read_custom_connection('public')

    if connection_id == "Internal":
        read_custom_connection('internal')

    if connection_id == "Custom":
        read_custom_connection('custom')


def remove_custom_widgets():  # Call this function when offline mode enabled so as to not confuse user #
    save_butt.grid_remove()  # Remove save button
    customization_lab.grid_remove()
    connect_type_sel.grid_remove()
    ip_input.grid_remove()
    port_input.grid_remove()
    user_input.grid_remove()
    pass_input.grid_remove()
    bottom_frame.grid_remove()


def replace_custom_widgets():  # Inverse of remove_custom_widgets #
    print("Replacing custom widgets")
    bottom_frame.grid()
    customization_lab.grid(row=0, column=0)
    connect_type_sel.grid(row=2, column=0)
    ip_input.grid(row=3, column=0)
    port_input.grid(row=4, column=0)
    user_input.grid(row=5, column=0)
    pass_input.grid(row=6, column=0)
    save_butt.grid(row=7, column=0)
    connection_type_sel_val.set("Public")  # Return to default values #


# function will read given profile from json file and display it in entry widgets.
def read_custom_connection(profile):
    print("Reading connection profile")

    # read json file into a dictionary
    with open(path_to_profiles) as f:
        file = json.load(f)

        if not file:
            # file is empty, create it...
            new_dict = {
                'public': {
                    'ip': '201.127.10.44',
                    'port': '443',
                    'user': 'admin',
                    'password': 'srBf46^jkA'
                },
                'internal': {
                    'ip': '192.168.1.1',
                    'port': '1883',
                    'user': 'random_username',
                    'password': 'srBf46^jkA'
                },
                'custom': {
                    'ip': '10.44.20.1',
                    'port': '132',
                    'user': 'admin',
                    'password': 'srBf46^jkA'
                }
            }
            out_file = open(path_to_profiles, "w")
            json.dump(new_dict, out_file, indent=1)
            file = new_dict

        profile_dict = file[profile]
        ip = profile_dict['ip']
        port = profile_dict['port']
        user = profile_dict['user']
        password = profile_dict['password']

    ip_input_val.set(ip)
    port_input_val.set(port)
    mqtt_user_input_val.set(user)
    mqtt_pass_input_val.set(password)


def save_profile():
    print("Saving connection vars to txt file")
    connection_type = str(connection_type_sel_val.get())
    connection_list = [ip_input_val.get(), port_input_val.get(), mqtt_user_input_val.get(), mqtt_pass_input_val.get()]
    print(connection_list)

    # read json file into a dictionary
    with open(path_to_profiles) as f:
        file = json.load(f)
    if connection_type == 'Public':
        profile_ref = 'public'
    elif connection_type == 'Internal':
        profile_ref = 'internal'
    else:
        profile_ref = 'custom'

    file[profile_ref]['ip'] = connection_list[0]
    file[profile_ref]['port'] = connection_list[1]
    file[profile_ref]['user'] = connection_list[2]
    file[profile_ref]['password'] = connection_list[3]

    out_file = open(path_to_profiles, "w")
    json.dump(file, out_file, indent=1)


# Function that runs when the "enter" key is hit #
def key_pressed(event):
    if event.keysym == "Return":
        print("return hit")
        login()

#########################################################################
#                                                                       #
#                         Tkinter Setup Code                            #
#                                                                       #
#########################################################################
login_window = Tk()
login_window.title("WCA Login")
screen_width = login_window.winfo_screenwidth()
screen_height = login_window.winfo_screenheight()
width = 800
height = 600
login_window.geometry(f'{width}x{height}')
login_window.iconbitmap('media/WCA-Icon.ico')
login_window.configure(background='grey')
# Background Photo Setup (needs to be done first otherwise it wont be put at the back) #
bg_photo = PhotoImage(file="media/login_pic_annotated.png")
bg_photo_label = Label(login_window, image=bg_photo)
bg_photo_label.place(x=0, y=0)

#########################################################################
#                                                                       #
#                           String Variables                            #
#                                                                       #
#########################################################################

online_mode_val = StringVar()
online_mode_val.set("Offline Mode")
online_mode_val.trace('w', on_network_type_change)
connection_type_sel_val = StringVar()
connection_type_sel_val.set("Public")
connection_type_sel_val.trace('w', on_custom_connection_change)
ip_input_val = StringVar()
port_input_val = StringVar()
mqtt_user_input_val = StringVar()
mqtt_pass_input_val = StringVar()
password_feedback = StringVar()

#########################################################################
#                                                                       #
#                         Geometry Management                           #
#                                                                       #
#########################################################################

# Organise sections of GUI into frames #
top_frame = Frame(login_window)
bottom_frame = Frame(login_window, bg='gray')
# Grid all the frames in place #
top_frame.grid(row=0, sticky="n")
bottom_frame.grid(row=3, sticky="s")

# Main Frame Widget Creation #
enter_pass_lab = Label(login_window, textvariable=password_feedback, justify=LEFT, bg="Red", fg="White", relief=RAISED)
password_input = Entry(login_window, width=20, justify='center', show="*")
login_butt = Button(login_window, text="Login", bg="white", fg="black", height=2, width=15, command=login)
connection_sel = OptionMenu(login_window, online_mode_val, "Online Mode", "Offline Mode")
connection_sel.config(bg="white")
customization_lab = Label(bottom_frame, justify='center', text="Customize Connection")
connect_type_sel = OptionMenu(bottom_frame, connection_type_sel_val, "Public", "Internal", "Custom")
connect_type_sel.config(bg="white")
ip_input = Entry(bottom_frame, width=20, justify='center', textvariable=ip_input_val)
port_input = Entry(bottom_frame, width=20, justify='center', textvariable=port_input_val)
user_input = Entry(bottom_frame, width=20, justify='center', textvariable=mqtt_user_input_val)
pass_input = Entry(bottom_frame, width=20, justify='center', textvariable=mqtt_pass_input_val)
save_butt = Button(login_window, text="Save", bg="white", fg="black", height=2, width=15, command=save_profile)

# Main Frame Widget Placement #
enter_pass_lab.place(relx=0.43, rely=0.45, anchor=CENTER)
password_input.place(relx=0.57, rely=0.45, anchor=CENTER)
login_butt.place(relx=0.5, rely=0.5, anchor=CENTER)
connection_sel.place(relx=0.5, rely=.3, anchor=CENTER)
customization_lab.grid(row=0, column=0)
connect_type_sel.grid(row=2, column=0)
ip_input.grid(row=3, column=0)
port_input.grid(row=4, column=0)
user_input.grid(row=5, column=0)
pass_input.grid(row=6, column=0)

# Side Panel Frame Widget Creation #


# Side Panel Frame Widget Placement #

# Set any Entry Variables Here #
password_feedback.set("  Enter Password  ")

# Default to offline mode #
remove_custom_widgets()

# Assign key-bind to login window #
login_window.bind("<Key>", key_pressed)

# Runs the main loop that updates the GUI #
login_window.mainloop()

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
