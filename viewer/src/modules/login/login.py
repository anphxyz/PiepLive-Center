import tkinter as tk
from PIL import Image, ImageTk
from src.utils import helper, tk_helper, store
import re
from src.models.n100_model import N100_model


class Login(object):
    loginPopup = None
    font = ("Arial", 10)

    def __init__(self, parent):
        self.parent = parent
        super(Login, self).__init__()

    def open(self):
         # first destroy
        if None is not self.loginPopup:
            self.loginPopup.destroy()
        # init
        self.loginPopup = tk_helper.makePiepMePopup("Login", w=500, h=400)
        # var
        self.NV117 = tk.StringVar()
        self.PV161 = tk.StringVar()
        #
        loginMainFrame = tk.Frame(self.loginPopup, pady=50)
        loginMainFrame.pack()
        # logo
        fLogo = tk.Frame(loginMainFrame, pady=10)
        fLogo.pack()
        imgLogo = ImageTk.PhotoImage(Image.open(helper._LOGO_PATH))
        lblLogo = tk.Label(fLogo, image=imgLogo, bg="#f2f2f2")
        lblLogo.photo = imgLogo
        lblLogo.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        # PiepMe ID
        self.fPid = tk.Frame(loginMainFrame, pady=15)
        self.fPid.pack()
        ePid = tk.Entry(self.fPid, textvariable=self.NV117,
                        borderwidth=5, relief=tk.FLAT)
        ePid.insert(0, 'GP2Y6B')  # 'PiepMe ID')
        ePid.bind("<FocusIn>", lambda args: ePid.delete('0', 'end'))
        ePid.config(font=self.font)
        self.NV117.trace("w", self.autoUpperNV117)
        ePid.pack(side=tk.LEFT, fill=tk.X)
        #
        btnLogin = tk.Button(self.fPid, text="Login", bd=2, bg="#ff2d55",
                             fg="#fff", relief=tk.RAISED, command=self.onSendNV117)
        btnLogin.configure(width=7, font=self.font)
        btnLogin.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        # Verify TOKEN
        self.fToken = tk.Frame(loginMainFrame, pady=15)
        eToken = tk.Entry(self.fToken, textvariable=self.PV161,
                          borderwidth=5, relief=tk.FLAT)
        eToken.insert(0, 'Token')
        eToken.bind("<FocusIn>", lambda args: eToken.delete('0', 'end'))
        eToken.config(font=self.font)
        eToken.pack(side=tk.LEFT, fill=tk.X)
        #
        btnVerify = tk.Button(self.fToken, text="Verify", bd=2, bg="#ff2d55",
                              fg="#fff", relief=tk.RAISED, command=self.onVerify)
        btnVerify.configure(width=7, font=self.font)
        btnVerify.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
        # nv117 invalid
        self.fInvalid = tk.Frame(loginMainFrame, pady=5)
        lblError = tk.Label(
            self.fInvalid, text="PiepMe ID invalid!", fg="#f00")
        lblError.config(font=self.font)
        lblError.pack(side=tk.LEFT, fill=tk.Y)
        # pv161 invalid
        self.fTokenInvalid = tk.Frame(loginMainFrame, pady=5)
        lblTOkenError = tk.Label(
            self.fTokenInvalid, text="Token invalid!", fg="#f00")
        lblTOkenError.config(font=self.font)
        lblTOkenError.pack(side=tk.LEFT, fill=tk.Y)

    def autoUpperNV117(self, *arg):
        self.NV117.set(self.NV117.get().upper())
        self.character_limit(self.NV117, )

    def character_limit(self, entry, limit=6):
        if len(entry.get()) > limit:
            entry.set(entry.get()[0:limit])

    def onSendNV117(self):
        self.fInvalid.pack_forget()
        regex = re.compile(r"^[A-Z0-9]{6,8}$")
        nv117 = self.NV117.get()
        if regex.match(nv117):
            res = self.getOtpViaNV117(nv117)
            if res['status'] == 'success':
                self.fPid.pack_forget()
                self.fToken.pack(side=tk.LEFT, fill=tk.X)
            else:
                self.fInvalid.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self.fInvalid.pack(side=tk.LEFT, fill=tk.Y)

    def onVerify(self):
        self.fTokenInvalid.pack_forget()
        regex = re.compile(r"^[0-9]{6}$")
        pv161 = self.PV161.get()
        if regex.match(pv161):
            res = self.pieplivecenterLogin(self.NV117.get(), pv161)
            if res['status'] == 'success':
                # save login
               store._new(res['elements'])
            else:
                self.fTokenInvalid.pack(side=tk.LEFT, fill=tk.Y)
        else:
            self.fTokenInvalid.pack(side=tk.LEFT, fill=tk.Y)

    def getOtpViaNV117(self, nv117):
        n100 = N100_model()
        return n100.getOtpViaNV117({
            'NV117': nv117,  # PiepMeID
            'LOGIN': 'ANPH',  # IP hoặc Mac address (của máy)
        })

    def pieplivecenterLogin(self, nv117, pv161):
        n100 = N100_model()
        return n100.pieplivecenterLogin({
            'NV117': nv117,  # PiepMeID
            'PV161': pv161,  # OTP (login)
            'LOGIN': 'ANPH',  # IP hoặc Mac address (của máy)
        })
