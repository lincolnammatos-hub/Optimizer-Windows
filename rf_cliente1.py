import tkinter as tk
import subprocess, os, threading, json, urllib.request, sys
from datetime import datetime

try:
    import winreg, ctypes
except ImportError:
    winreg = ctypes = None

FIREBASE_URL   = "https://almeida-56c0f-default-rtdb.firebaseio.com/keys"
LOCAL_KEY_FILE = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "redflury_key.json")

# ── CORES ──────────────────────────────────────────────────────────────
BG    = "#000000"
BG2   = "#06000f"
BG3   = "#0d0020"
BORD  = "#2a0055"
BORD2 = "#6600cc"
PU    = "#cc44ff"
PU2   = "#8800ff"
PU3   = "#550088"
PU4   = "#1a0035"
WHITE = "#ffffff"
GRAY  = "#660099"

# ── HELPERS ────────────────────────────────────────────────────────────
def is_admin():
    try:
        return ctypes and bool(ctypes.windll.shell32.IsUserAnAdmin())
    except:
        return False

def salvar_key(key, expira):
    try:
        with open(LOCAL_KEY_FILE, "w") as f:
            json.dump({"key": key, "expira": expira}, f)
    except:
        pass

def carregar_key():
    try:
        if os.path.exists(LOCAL_KEY_FILE):
            with open(LOCAL_KEY_FILE) as f:
                d = json.load(f)
            if datetime.now() <= datetime.strptime(d["expira"], "%Y-%m-%d"):
                return True, d["key"]
    except:
        pass
    return False, None

def validar_online(key):
    try:
        key = key.strip().upper()
        req = urllib.request.urlopen(f"{FIREBASE_URL}/{key}.json", timeout=6)
        d   = json.loads(req.read().decode())
        if not d:
            return False, "Key invalida!"
        if datetime.now() > datetime.strptime(d["expira"], "%Y-%m-%d"):
            return False, "Key expirada!"
        salvar_key(key, d["expira"])
        return True, "OK"
    except:
        return False, "Sem conexao com o servidor!"

# ── OTIMIZAÇÕES ────────────────────────────────────────────────────────
def limpar_temp(log):
    log("Limpando arquivos temporarios...")
    total = 0
    for p in [os.environ.get("TEMP",""), os.environ.get("TMP",""),
               r"C:\Windows\Temp", r"C:\Windows\Prefetch"]:
        if not os.path.exists(p): continue
        for f in os.listdir(p):
            try:
                fp = os.path.join(p, f)
                if os.path.isfile(fp): os.remove(fp); total += 1
            except: pass
    log(f"[OK] {total} arquivos removidos!")

def limpar_dns(log):
    log("Limpando cache DNS...")
    subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)
    log("[OK] Cache DNS limpo!")

def otimizar_ram(log):
    log("Otimizando RAM...")
    subprocess.run("rundll32.exe advapi32.dll,ProcessIdleTasks", shell=True, capture_output=True)
    log("[OK] RAM otimizada!")

def desativar_servicos(log):
    log("Desativando servicos...")
    for s in ["SysMain","WSearch","DiagTrack","dmwappushservice"]:
        subprocess.run(f"sc stop {s}", shell=True, capture_output=True)
        subprocess.run(f"sc config {s} start=disabled", shell=True, capture_output=True)
        log(f"  > {s} desativado")
    log("[OK] Servicos desativados!")

def ajustar_desempenho(log):
    log("Ativando alto desempenho...")
    subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
                   shell=True, capture_output=True)
    if winreg:
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(k)
        except: pass
    log("[OK] Desempenho ajustado!")

def limpar_registro(log):
    log("Limpando registro...")
    n = 0
    if winreg:
        for hive, path in [
            (winreg.HKEY_CURRENT_USER,  r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")]:
            try:
                k = winreg.OpenKey(hive, path, 0, winreg.KEY_READ|winreg.KEY_SET_VALUE)
                i, rem = 0, []
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(k, i)
                        exe = val.strip('"').split('"')[0].split()[0]
                        if not os.path.exists(exe): rem.append(name)
                        i += 1
                    except OSError: break
                for nm in rem:
                    try: winreg.DeleteValue(k, nm); n += 1
                    except: pass
                winreg.CloseKey(k)
            except: pass
    log(f"[OK] {n} entradas invalidas removidas!")

# ── WIDGETS AUXILIARES ─────────────────────────────────────────────────
def make_logo(parent, size=44):
    c = tk.Canvas(parent, width=size, height=size, bg=BG2,
                  highlightthickness=0)
    s = size * 0.75
    c.create_text(size//2, size//2+2, text="⚡",
                  font=("Consolas", int(s*0.7), "bold"), fill=PU)
    return c

def sep(parent):
    tk.Frame(parent, bg=PU2, height=2).pack(fill="x")

def header(root, subtitle):
    hdr = tk.Frame(root, bg=BG2, pady=14)
    hdr.pack(fill="x")
    inner = tk.Frame(hdr, bg=BG2)
    inner.pack(padx=22, fill="x")

    logo = make_logo(inner, 50)
    logo.pack(side="left")

    tf = tk.Frame(inner, bg=BG2)
    tf.pack(side="left", padx=12)
    row = tk.Frame(tf, bg=BG2)
    row.pack(anchor="w")
    tk.Label(row, text="RED",   font=("Consolas",20,"bold"), fg=WHITE, bg=BG2).pack(side="left")
    tk.Label(row, text="FLURY", font=("Consolas",20,"bold"), fg=PU,    bg=BG2).pack(side="left", padx=(6,0))
    tk.Label(tf, text=subtitle, font=("Consolas",9), fg=PU2, bg=BG2).pack(anchor="w")

    return inner  # retorna frame para adicionar badge

# ── TELA DE KEY ────────────────────────────────────────────────────────
class TelaKey:
    def __init__(self, root, on_ok):
        self.root, self.on_ok = root, on_ok
        root.title("RED FLURY")
        root.geometry("460x480")
        root.configure(bg=BG)
        root.resizable(False, False)
        self._build()

    def _build(self):
        sep(self.root)
        inner = header(self.root, "// SYSTEM OPTIMIZER v1.0")
        sep(self.root)

        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=38, pady=30)

        lock = tk.Frame(body, bg=BG3, width=74, height=74)
        lock.pack()
        lock.pack_propagate(False)
        tk.Label(lock, text="🔒", font=("Consolas",30), bg=BG3).place(relx=.5,rely=.5,anchor="center")

        tk.Label(body, text="ATIVAÇÃO DO PRODUTO",
                 font=("Consolas",14,"bold"), fg=PU, bg=BG).pack(pady=(18,4))
        tk.Label(body, text="Insira sua key de acesso para continuar",
                 font=("Consolas",9), fg=PU3, bg=BG).pack(pady=(0,20))

        wrap = tk.Frame(body, bg=BG3, highlightbackground=PU2, highlightthickness=1)
        wrap.pack(fill="x")
        self.kv = tk.StringVar()
        e = tk.Entry(wrap, textvariable=self.kv,
                     font=("Consolas",13,"bold"), fg=PU, bg=BG3,
                     insertbackground=PU, relief="flat", justify="center",
                     highlightthickness=0)
        e.pack(fill="x", ipady=11, padx=10)
        e.focus()
        e.bind("<Return>", lambda _: self._ativar())

        tk.Label(body, text="Formato: XXXXX-XXXXX-XXXXX-XXXXX",
                 font=("Consolas",8), fg=PU4, bg=BG).pack(pady=(6,0))

        tk.Button(body, text="🔑   ATIVAR AGORA",
                  font=("Consolas",11,"bold"), fg=WHITE, bg=PU2,
                  activeforeground=WHITE, activebackground=PU3,
                  relief="flat", pady=12, cursor="hand2",
                  command=self._ativar).pack(fill="x", pady=18)

        self.msg = tk.Label(body, text="", font=("Consolas",9), bg=BG)
        self.msg.pack()

    def _ativar(self):
        k = self.kv.get().strip().upper()
        if not k:
            self.msg.config(text="⚠  Digite uma key!", fg="#ffaa00"); return
        self.msg.config(text="⏳  Verificando...", fg=PU)
        self.root.update()
        threading.Thread(target=self._checar, args=(k,), daemon=True).start()

    def _checar(self, k):
        ok, msg = validar_online(k)
        if ok:
            self.msg.config(text="✅  Key valida! Abrindo...", fg=PU)
            self.root.after(900, self.on_ok)
        else:
            self.msg.config(text=f"❌  {msg}", fg="#ff4444")

# ── MENU PRINCIPAL ─────────────────────────────────────────────────────
class MenuApp:
    def __init__(self, root, on_expirado=None):
        self.root = root
        self.on_expirado = on_expirado
        root.title("RED FLURY — System Optimizer")
        root.geometry("760x680")
        root.configure(bg=BG)
        root.resizable(False, False)
        self._build()
        self._verificar_key_periodicamente()

    def _verificar_key_periodicamente(self, intervalo_ms=60_000):
        """Checa a validade da key a cada intervalo_ms (padrao 1 min).
        Se estiver expirada, apaga o cache local e volta para TelaKey."""
        ok, _ = carregar_key()
        if not ok:
            try:
                if os.path.exists(LOCAL_KEY_FILE):
                    os.remove(LOCAL_KEY_FILE)
            except:
                pass
            if self.on_expirado:
                self.root.after(0, self.on_expirado)
            return
        self.root.after(intervalo_ms, self._verificar_key_periodicamente)

    def _build(self):
        sep(self.root)
        inner = header(self.root, "// SYSTEM OPTIMIZER v1.0")

        at = "●  ADMIN" if is_admin() else "●  SEM ADMIN"
        ac = PU if is_admin() else "#ff4444"
        badge = tk.Frame(inner, bg=BG3, padx=12, pady=6)
        badge.pack(side="right")
        tk.Label(badge, text=at, font=("Consolas",10,"bold"), fg=ac, bg=BG3).pack()

        sep(self.root)

        tk.Label(self.root, text="> LOADING...  > OPTIMIZING...  > SYSTEM READY",
                 font=("Consolas",8), fg=GRAY, bg=BG).pack(anchor="w", padx=22, pady=(10,2))

        grid = tk.Frame(self.root, bg=BG)
        grid.pack(padx=22, pady=6, fill="x")

        items = [
    ("📂","Limpar Temporarios",  "%TEMP% / Windows\\Temp",   limpar_temp),
    ("🌍","Limpar Cache DNS",     "ipconfig /flushdns",       limpar_dns),
    ("💾","Otimizar RAM",         "Liberar memoria standby",  otimizar_ram),
    ("⚙","Desativar Servicos",   "Superfetch / Telemetria",  desativar_servicos),
    ("🚀","Ajustar Desempenho",   "Modo alto desempenho",     ajustar_desempenho),
    ("🧹","Limpar Registro",      "Entradas invalidas",       limpar_registro),
]

        for i,(ico,txt,sub,fn) in enumerate(items):
            r,c = divmod(i,2)
            card = tk.Frame(grid, bg=BG2,
                            highlightbackground=BORD, highlightthickness=1,
                            cursor="hand2")
            card.grid(row=r, column=c, padx=6, pady=6, sticky="ew")
            grid.grid_columnconfigure(c, weight=1)

            # linha inferior gradiente simulada
            tk.Frame(card, bg=PU2, height=2).pack(fill="x", side="bottom")

            inner_c = tk.Frame(card, bg=BG2, pady=11, padx=13)
            inner_c.pack(fill="x")

            ico_f = tk.Frame(inner_c, bg=BG3, width=40, height=40,
                             highlightbackground=BORD, highlightthickness=1)
            ico_f.pack(side="left")
            ico_f.pack_propagate(False)
            tk.Label(
            ico_f,
            text=ico,
            font=("Segoe UI Emoji",16),
            fg=PU,
            bg=BG3
            ).place(relx=.5, rely=.5, anchor="center")

            tf2 = tk.Frame(inner_c, bg=BG2)
            tf2.pack(side="left", padx=11)
            tk.Label(tf2, text=txt, font=("Consolas",10,"bold"),
                     fg=PU, bg=BG2).pack(anchor="w")
            tk.Label(tf2, text=sub, font=("Consolas",8),
                     fg=GRAY, bg=BG2).pack(anchor="w")

            for w in [card, inner_c, ico_f, tf2]+list(tf2.winfo_children())+list(inner_c.winfo_children()):
                w.bind("<Button-1>", lambda e,f=fn: self._run(f))

        tk.Button(self.root, text="⚡     OTIMIZACAO COMPLETA     ⚡",
                  font=("Consolas",12,"bold"), fg=WHITE, bg=PU2,
                  activeforeground=WHITE, activebackground=PU3,
                  relief="flat", pady=13, cursor="hand2",
                  command=self._completo).pack(padx=22, pady=8, fill="x")

        tk.Frame(self.root, bg=PU4, height=1).pack(fill="x", padx=22, pady=4)

        tk.Label(self.root, text="// LOG DO SISTEMA",
                 font=("Consolas",9,"bold"), fg=PU3, bg=BG).pack(anchor="w", padx=22)

        lw = tk.Frame(self.root, bg=BG,
                      highlightbackground=BORD2, highlightthickness=1)
        lw.pack(padx=22, pady=5, fill="both", expand=True)

        self.log_box = tk.Text(lw, font=("Consolas",9), fg=PU, bg=BG,
                               relief="flat", state="disabled", wrap="word",
                               insertbackground=PU, selectbackground=BORD)
        sb = tk.Scrollbar(lw, bg=BG3, command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=6)

        self._log("Sistema pronto. Aguardando comando...")
        self._log("Firebase: conectado")

    def _log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"> {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.root.update()

    def _run(self, fn):
        if not is_admin(): self._log("[AVISO] Execute como Administrador!")
        threading.Thread(target=fn, args=(self._log,), daemon=True).start()

    def _completo(self):
        def go():
            self._log("="*40)
            self._log("INICIANDO OTIMIZACAO COMPLETA...")
            self._log("="*40)
            for fn in [limpar_temp,limpar_dns,otimizar_ram,
                       desativar_servicos,ajustar_desempenho,limpar_registro]:
                fn(self._log)
            self._log("="*40)
            self._log("FINALIZADO COM SUCESSO!")
            self._log("="*40)
        threading.Thread(target=go, daemon=True).start()

# ── MAIN ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if ctypes and not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

    root = tk.Tk()

    def voltar_tela_key(motivo="Key expirada! Insira uma nova key."):
        for w in root.winfo_children(): w.destroy()
        root.geometry("460x480")
        tela = TelaKey(root, abrir)
        tela.msg.config(text=f"⚠  {motivo}", fg="#ffaa00")

    def abrir():
        for w in root.winfo_children(): w.destroy()
        root.geometry("760x680")
        MenuApp(root, voltar_tela_key)

    ok, key = carregar_key()

    if ok:
        ok2, _ = validar_online(key)

        if ok2:
            abrir()
        else:
            TelaKey(root, abrir)

    else:
        TelaKey(root, abrir)

    root.mainloop()
