import paramiko
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk

from tkinter.messagebox import showinfo

recv_messages = ["Message 1", "Message 2", "Message 3"]
sent_messages = ["Sent 1", "Sent 2", "Sent 3"]
x_plot = [0,1,2,3,4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
y_plot = [0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,1,0, 1]

class App(tk.Tk):
  def __init__(self):
    super().__init__()

    # Red Pitaya Logo
    self.logo = tk.PhotoImage(file="redpitaya.png")
    self.logo_label = ttk.Label(self, image=self.logo)
    self.logo_label.pack()

    # Configure window title and size
    self.title('Red Pitaya Galaxy Interface')
    self.geometry('500x500')

    # Setup Notebook For Tabs 1-3
    self.notebook = ttk.Notebook(self)
    self.notebook.pack(fill=tk.BOTH, expand=True)

    # Setup Tab1
    self.tab1 = tk.Frame(self.notebook)
    self.notebook.add(self.tab1, text="Send")

    # Setup Tab2
    self.tab2 = tk.Frame(self.notebook)
    self.notebook.add(self.tab2, text="Receive")

    # Setup Tab3
    self.tab3 = tk.Frame(self.notebook)
    self.notebook.add(self.tab3, text="Settings")

    # ----------
    # ---Tab1---
    # ----------

    # Send Message Textbox Label
    self.label1 = ttk.Label(self.tab1, text='Message to send')
    self.label1.pack()

    # Send Message Textbox
    self.message_entry = tk.Entry(self.tab1)
    self.message_entry.pack()

    # Button that calls button_clicked function that "sends" the message
    self.button1 = ttk.Button(self.tab1, text='Send Message')
    self.button1['command'] = self.button1_clicked
    self.button1.pack()

    # Create list and call refresh_list function that populates it
    self.listbox1 = tk.Listbox(self.tab1)
    self.refresh_list1()
    self.listbox1.pack(pady=25)


    # ----------
    # ---Tab2---
    # ----------

    # Creating Plot
    fig = plt.Figure(figsize=(3, 2), dpi=75)
    ax = fig.add_subplot(111)
    ax.plot(x_plot, y_plot)
    canvas = FigureCanvasTkAgg(fig, master=self.tab2)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=10)

    # Label For Message Log
    self.label2 = ttk.Label(self.tab2, text='Message Log')
    self.label2.pack()

    # Create list and call refresh_list function that populates it
    self.listbox2 = tk.Listbox(self.tab2)
    self.refresh_list2()
    self.listbox2.pack()

    # Create a button to execute C-related files
    self.button_receive = tk.Button(self.tab2, text="Recv Message")
    self.button_receive['command'] = self.button_recv_clicked
    self.button_receive.pack()

    # ----------
    # ---Tab3---
    # ----------

    # Threshold Entry
    self.label_thresh = ttk.Label(self.tab3, text='Thresh')
    self.label_thresh.pack()
    self.thresh_entry = tk.Entry(self.tab3)
    self.thresh_entry.insert(0, '200')
    self.thresh_entry.pack()

    # Sample Entry
    self.label_thresh = ttk.Label(self.tab3, text='Sample Rate')
    self.label_thresh.pack()
    self.samp_entry = tk.Entry(self.tab3)
    self.samp_entry.insert(0, '100')
    self.samp_entry.pack()

    # Downsample Entry
    self.label_downsample = ttk.Label(self.tab3, text='Downsample')
    self.label_downsample.pack()
    self.downsample_entry = tk.Entry(self.tab3)
    self.downsample_entry.insert(0, '8')
    self.downsample_entry.pack()

    # Button that uses Paramiko to execute cmd via ssh
    self.button2 = ttk.Button(self.tab3, text='Send Message')
    self.button2['command'] = self.button2_clicked
    self.button2.pack()


  # In Tab1 Sets Sent Message
  def button1_clicked(self):
    # Retrieve the message
    message = self.message_entry.get()
    # Don't continue if the textbox is empty
    if message == "":
      message = "Textbox is empty, please try again"
    else:
      sent_messages.append(message)
      self.refresh_list1()
      message = message + " has been successfully sent!"
    # Letting the user know what happened
    showinfo(title='Information', message=message)

  # In Tab3 the function that sets the registers and values
  def button2_clicked(self):
    # Send ssh command here
    thresh = int(self.thresh_entry.get())
    samp = int(self.samp_entry.get())
    downsample = int(self.downsample_entry.get())

    # Register Values
    thresh_reg = 0x40300054
    samp_reg = 0x4030005c
    downsample_reg = 0x4030006c

    monitor_bin = "/opt/redpitaya/bin/monitor "

    # Send thresh, samp, downsample
    command_to_send = monitor_bin + str(f"0x{thresh_reg:08x}") + " " + str(thresh)
    print(command_to_send)
    self.send_command(command_to_send)
    command_to_send = monitor_bin + str(f"0x{samp_reg:08x}") + " " + str(samp)
    print(command_to_send)
    self.send_command(command_to_send)
    command_to_send = monitor_bin + str(f"0x{downsample_reg:08x}") + " " + str(downsample)
    print(command_to_send)
    self.send_command(command_to_send)

  # In Tab2 to receive data from C-related files
  def button_recv_clicked(self):
    command_to_send = "./samples"
    print(command_to_send)

    # Call send_command function to send message
    self.send_command(command_to_send)

  # Updates Send Message List
  def refresh_list1(self):
    self.listbox1.delete(0,self.listbox1.size())
    for message in sent_messages:
      self.listbox1.insert(tk.END, message)

  # Updates Recv Message List
  def refresh_list2(self):
    self.listbox2.delete(0,self.listbox2.size())
    for message in recv_messages:
      self.listbox2.insert(tk.END, message)

  # Send Command via SSH with Paramiko
  def send_command(self, message_to_send):
    host = "rp-f0ab99.local"
    username = "root"
    password = "root"

    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, 22, username=username, password=password)
    _stdin, _stdout, _stderr = client.exec_command(message_to_send)
    print(_stdout.read().decode())
    print(_stderr.read().decode())
    client.close()

if __name__ == "__main__":
  app = App()
  app.mainloop()
