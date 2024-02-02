#! /usr/bin/python
# -*- coding: utf-8 -*-


import socket, json, os, time
from threading import Thread
import tkinter as tk
import RPi.GPIO as GPIO

class RpcNotification:

    def __init__(self, method, params):
        self.method = method
        self.params = params


class RpcResult:

    def __init__(self, id, result):
        self.id = id
        self.result = result

class RpcSocket:

    def __init__(self, address=("localhost",7000)):
        self.s = socket.socket()
        self.s.connect(address)
        self.buf = ""

    def send(self, method, id=None, params=[]):
        d = dict(jsonrpc="2.0", method=method, params=params)
        if id is not None:
            d["id"] ="1"
        toBeSent = json.dumps(d)+"\n"
        self.s.send(toBeSent.encode())

    def call(self, method, params=[]):
        self.send(method=method, id="1", params=params)

    def notify(self, method, params=[]):
        self.send(method=method, params=params)

    def receive(self):
        l = [self.buf]
        while True:
            p = l[-1]
            #print(p)
            if p == '':
                l.pop()
            #print(p.find('\n'))
            elif p.find(b"\n") > -1:
                ln, sep, tail = p.partition(b'\n')
                l[-1] = ln
                st = b"".join(l)
                self.buf = tail
                break;
            l.append(self.s.recv(10000))
        try:
            d = json.loads(st)
        except ValueError as e:
            print(e)
            print(st)
            return None
        if "params" in d:
            if not d["params"]:
                return None
            #if isinstance(d["params"][0], int):
            #    print('DEBUG: ',d["params"])
            #if isinstance(d["params"][0], float):
            #    print('DEBUG: ',d["params"])
            #elif not  ".v" in (d["params"][0]):
            print(d["params"])
            return RpcNotification(d["method"], d["params"])
        elif "result" in d:
            return RpcResult(d["id"], d["result"])
        else:
            raise ValueError("rpc error: %s" % d)

class getPedals(Thread):
    def __init__(self, sock, labels, volume_slider):
        Thread.__init__(self)
        self.volume_slider = volume_slider
        self.row_selected = 0
        self.labels = labels
        self.effects = ['dide.on_off','univibe_mono.on_off','mbchor.on_off','compressor.on_off','fuzzface.on_off','gx_mbreverb.on_off']
        self.sock = sock
        #self.sock.notify("set", ['amp.out_master', -12.76])
        #self.sock.notify("set", ['noise_gate.threshold', 0.142])
        self.led1 = 23
        self.led2 = 27
        self.led3 = 18
        self.led4 = 4
        
        self.btn1 = 22
        self.btn2 = 17
        self.btn3 = 15
        self.btn4 = 14

        self.encoder_clk = 20
        self.encoder_data = 26
        self.encoder_button = 21

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.led1,GPIO.OUT)
        GPIO.setup(self.led2,GPIO.OUT)
        GPIO.setup(self.led3,GPIO.OUT)
        GPIO.setup(self.led4,GPIO.OUT)
        
        GPIO.setup(self.btn1,GPIO.IN)
        GPIO.setup(self.btn2,GPIO.IN)
        GPIO.setup(self.btn3,GPIO.IN)
        GPIO.setup(self.btn4,GPIO.IN)
        GPIO.setup(self.encoder_clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.encoder_data, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.encoder_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.checkPedals = False
        self.clkLastState = GPIO.input(self.encoder_clk)
        self.btnLastState = GPIO.input(self.encoder_button)

        sock.call("get_parameter", ["amp.out_master"])
        result = sock.receive().result

        self.minVol = result['amp.out_master']['lower_bound']
        self.maxVol = result['amp.out_master']['upper_bound']
        self.volume_step_size=1.0
        self.volume = self.maxVol/2
        self.is_Muted=False

    def run(self):
        while self.checkPedals:
#            if not(self.btnLastState) and GPIO.input(self,encoder_button):
#                if self.is_Muted:
#                    self.lastVolume = self.volume
#                    self.volume = self.minVol
#                else:
#                    self.volume = self.lastVolume
#                self.is_Muted = not(self.is_Muted)
#                self.sock.notify("set", ['amp.out_master', self.volume])
            clkState = GPIO.input(self.encoder_clk)
            dtState = GPIO.input(self.encoder_data)
            if clkState != self.clkLastState:
                if dtState != clkState:
                    self.volume += self.volume_step_size/2
                    if self.volume > self.maxVol:
                        self.volume = self.maxVol
                else:
                    self.volume -= self.volume_step_size/2
                    if self.volume < self.minVol:
                        self.volume = self.minVol
                if clkState == 1:
                    print("Mute State: " + str(self.is_Muted))
                    print("Volume: " + str(int(self.volume)))
                    print("")
                    self.sock.notify("set", ['amp.out_master', self.volume])
                    self.volume_slider.set(self.volume)
            self.clkLastState = clkState


            if GPIO.input(self.btn1) == 1:
                pos = self.row_selected + 0
                self.sock.notify("set", [self.effects[pos], 1])
                GPIO.output(self.led1, GPIO.HIGH)
                self.labels[pos].config(highlightbackground="red", highlightthickness=2)
            if GPIO.input(self.btn1) == 0:
                pos = self.row_selected + 0
                self.sock.notify("set", [self.effects[pos], 0])
                GPIO.output(self.led1, GPIO.LOW)
                self.labels[pos].config(highlightbackground="white", highlightthickness=2)
            if GPIO.input(self.btn2) == 1:
                pos = self.row_selected + 1
                self.sock.notify("set", [self.effects[pos], 1])
                GPIO.output(self.led2, GPIO.HIGH)
                self.labels[pos].config(highlightbackground="red", highlightthickness=2)
            if GPIO.input(self.btn2) == 0:
                pos = self.row_selected + 1
                self.sock.notify("set", [self.effects[pos], 0])
                GPIO.output(self.led2, GPIO.LOW)
                self.labels[pos].config(highlightbackground="white", highlightthickness=2)
            if GPIO.input(self.btn3) == 1:
                pos = self.row_selected + 2
                self.sock.notify("set", [self.effects[pos], 1])
                GPIO.output(self.led3, GPIO.HIGH)
                self.labels[pos].config(highlightbackground="red", highlightthickness=2)
            if GPIO.input(self.btn3) == 0:
                pos = self.row_selected + 2
                self.sock.notify("set", [self.effects[pos], 0])
                GPIO.output(self.led3, GPIO.LOW)
                self.labels[pos].config(highlightbackground="white", highlightthickness=2)
            if GPIO.input(self.btn4) == 1:
                self.row_selected = 3
                GPIO.output(self.led4, GPIO.HIGH)
            if GPIO.input(self.btn4) == 0:
                self.row_selected = 0
                GPIO.output(self.led4, GPIO.LOW)

class getNotifications(Thread):
    def __init__(self, sock, volume_slider):
        print("DEBUG: getNotifications init")
        Thread.__init__(self)
        self.volume_slider = volume_slider
        self.sock = sock

    def run(self):
        while True:
            print("DEBUG: getNotifications run")
            self.sock.call("get_parameter", ["amp.out_master"])
            result = self.sock.receive().result
            self.volume_slider.set(result['amp.out_master']['value']['amp.out_master'])
            if self.sock.receive() == None:
                print("DEBUG: getNotifications no sock")
                break
            print(self.sock.receive().result)

class Guitarix():
    guitarix_pgm = "guitarix -p 7000 -N"
    #guitarix_pgm = "guitarix -p 7000"
    commands = {'banks': 'banks',
                'presets': 'presets',
                'get':'get',
                'set':'set',
                'parameterlist':'parameterlist'}
    #"insert_rack_unit", [fx.id, "", (this.stereo ? 1 : 0)]
    #"remove_rack_unit", [inSender.fx.id, (this.stereo ? 1 : 0)])
    def open_socket(self):
        try:
            self.sock = RpcSocket()
        except socket.error as e:
            if e.errno != 111:
                raise
            return False
        return True

    def __init__(self):
        self.current_params = {}
        time.sleep(3)
        if not self.open_socket():

            os.system(self.guitarix_pgm+"&")
            for i in range(10):
                time.sleep(1)
                if self.open_socket():
                    break
            else:
                raise RuntimeError("Can't connect to Guitarix")
            self

class App():
    def __init__(self,sock, window):
        self.sock = sock
        self.window = window
        self.volume_label = None

    def next_preset(self):
        self.sock.call("setpreset", [self.bankname, "swing"])

    def main(self):
        self.window.mainloop()

    def close_program(self):
        GPIO.cleanup()  # Pulizia dei canali GPIO
        pedal.checkPedals = False
        self.window.destroy()

    def shutdown(self):
        GPIO.cleanup()  # Pulizia dei canali GPIO
        os.system("sudo shutdown now")  # Comando per spegnere la Raspberry Pi

    # Funzione per gestire il valore dello slider
    def update_volume(self, value):
        self.volume_label.config(text="Volume: " + str(value))
        volume = float(value)
        #self.sock.notify("set", ['amp.out_master', -12.76])
        self.sock.notify("set", ['amp.out_master', volume])
        print("NEW VOLUME SLIDE: {0}".format(value))
        print("NEW VOLUME: {0}".format(volume))

    # Funzione per gestire il click su un'immagine
    def image_click(self, event, image_label):
        border_color = image_label.cget("highlightbackground")
        print(image_label)
        if border_color == "red":
            image_label.config(highlightbackground="white", highlightthickness=2)
        else:
            image_label.config(highlightbackground="red", highlightthickness=2)


if __name__=="__main__":
    # Creazione dell'istanza della finestra
    window = tk.Tk()
    
    # Impostazione della finestra come senza bordi e a tutto schermo
    window.attributes("-fullscreen", True)
    window.configure(bg="white")
    #start guitarix with rpc port at 7000
    gx = Guitarix()
    # open a socket at 7000
    sock = RpcSocket()
    app = App(sock, window)
    # receive all available parameters from guitarix
    sock.call("parameterlist", [])
    parameterlist = []
    r = sock.receive().result
    for tp, d in zip(r[::2], r[1::2]):
        if tp == "Enum":
            d = d["IntParameter"]
        elif tp == "FloatEnum":
            d = d["FloatParameter"]
        d = d["Parameter"]
        n = d["id"]
        if "non_preset" in d and n not in ("system.current_preset", "system.current_bank"):
            continue
        parameterlist.append(d["id"])
    parameterlist.sort()
    # print out parameterlist
# for i in parameterlist:
    #    print(i)

    # get current value of a parameter
    #sock.call("get", ['wah.freq'])
    #sock.call("banks", [])

    # set new value for a parameter
    #sock.notify("set", ['wah.freq', 50])
    # and now listen to all parameter changes
    sock.notify("listen",['all'])

    sock.call("get", ['system.current_bank','system.current_preset'])
    result = sock.receive().result
    bankname = result['system.current_bank']
    #banks = 
    actual_preset = result['system.current_preset']
    title_label = tk.Label(window, text=actual_preset, font=("Arial", 24), bg="white")
    title_label.pack(pady=50)
    
    volume_label = tk.Label(window, text="Volume: 50", bg="white")
    volume_label.pack()
    app.volume_label = volume_label
    sock.call("get_parameter", ["amp.out_master"])
    result = sock.receive().result
    volume_slider = tk.Scale(window, from_=result['amp.out_master']['lower_bound'], to=result['amp.out_master']['upper_bound'], resolution=0.5, orient=tk.HORIZONTAL, command=app.update_volume, length=800, width=55)
    volume_slider.set(result['amp.out_master']['value']['amp.out_master'])
    print(result)
    volume_slider.pack()
    # Frame per le righe di effetti
    effects_frame = tk.Frame(window, bg="white")
    effects_frame.pack(pady=20)
    labels = []
    # Prima riga di effetti
    first_row_frame = tk.Frame(effects_frame, bg="white")
    first_row_frame.pack()
    
    effect1_image = tk.PhotoImage(file="Immagini/effetto1.png").subsample(2)
    effect2_image = tk.PhotoImage(file="Immagini/effetto2.png").subsample(2)
    effect3_image = tk.PhotoImage(file="Immagini/effetto3.png").subsample(2)
    effect4_image = tk.PhotoImage(file="Immagini/effetto4.png").subsample(2)
    effect5_image = tk.PhotoImage(file="Immagini/effetto5.png").subsample(2)
    effect6_image = tk.PhotoImage(file="Immagini/effetto6.png").subsample(2)

    effect1_label = tk.Label(first_row_frame, image=effect1_image, bg="white", highlightbackground="white", highlightthickness=2)
    effect1_label.pack(side=tk.LEFT, padx=10)
    effect1_label.bind("<Button-1>", lambda event: app.image_click(event, effect1_label))
    labels.append(effect1_label)
    
    effect2_label = tk.Label(first_row_frame, image=effect2_image, bg="white", highlightbackground="white", highlightthickness=2)
    effect2_label.pack(side=tk.LEFT, padx=10)
    effect2_label.bind("<Button-1>", lambda event: app.image_click(event, effect2_label))
    labels.append(effect2_label)
    
    effect3_label = tk.Label(first_row_frame, image=effect3_image, bg="white", highlightbackground="white", highlightthickness=2)
    effect3_label.pack(side=tk.LEFT, padx=10)
    effect3_label.bind("<Button-1>", lambda event: app.image_click(event, effect3_label))
    labels.append(effect3_label)
    # Seconda riga di effetti
    second_row_frame = tk.Frame(effects_frame, bg="white")
    second_row_frame.pack()
    
    effect4_label = tk.Label(second_row_frame, image=effect4_image, bg="white", highlightbackground="white", highlightthickness=2)
    effect4_label.pack(side=tk.LEFT, padx=10)
    effect4_label.bind("<Button-1>", lambda event: app.image_click(event, effect4_label))
    labels.append(effect4_label)
    
    effect5_label = tk.Label(second_row_frame, image=effect5_image, bg="white", highlightbackground="white", highlightthickness=2)
    effect5_label.pack(side=tk.LEFT, padx=10)
    effect5_label.bind("<Button-1>", lambda event: app.image_click(event, effect5_label))
    labels.append(effect5_label)
    
    effect6_label = tk.Label(second_row_frame, image=effect6_image, bg="white", highlightbackground="white", highlightthickness=2)
    effect6_label.pack(side=tk.LEFT, padx=10)
    effect6_label.bind("<Button-1>", lambda event: app.image_click(event, effect6_label))
    labels.append(effect6_label)
    
    controls_frame = tk.Frame(window, bg="white")
    controls_frame.pack(pady=20)
    shutdown_button = tk.Button(window, text="Spegni", font=("Arial", 16), command=app.shutdown)
    shutdown_button.pack(side=tk.LEFT, padx=10)
    close_button = tk.Button(window, text="Chiudi", font=("Arial", 16), command=app.close_program)
    close_button.pack(side=tk.LEFT, padx=10)


    pedal = getPedals(sock, labels, volume_slider)
    pedal.checkPedals = True
    pedal.daemon = True
    pedal.start()
    worker = getNotifications(sock, volume_slider)
    worker.daemon = True
    worker.start()

    # Avvio del ciclo di esecuzione della finestra
    app.main()
    
