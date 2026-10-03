import gi, os
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class ExYuCalendar(Gtk.Window):
    def __init__(self):
        super().__init__(title="Ex-YU Kalendar")
        self.set_default_size(800, 600)

        # Postavljanje vlastite ikone aplikacije iz mape projekta
        icon_path = os.path.expanduser("~/projects/exyu-gui/icon.png")
        if os.path.exists(icon_path):
            self.set_icon_from_file(icon_path)

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Povijest i Znanost"
        self.set_titlebar(header)

        # Gumb za dodavanje novog podsjetnika
        add_btn = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        add_btn.set_tooltip_text("Dodaj podsjetnik")
        add_btn.connect("clicked", self.on_add_clicked)
        header.pack_start(add_btn)

        self.events = {}
        self.data_path = os.path.expanduser("~/.calendar/calendar")
        self.load_data()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        self.cal = Gtk.Calendar()
        self.cal.connect("day-selected", lambda *a: self.update_list())
        vbox.pack_start(self.cal, True, True, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox = Gtk.ListBox()
        scrolled.add(self.listbox)
        vbox.pack_start(scrolled, True, True, 0)

        self.update_list()

    def load_data(self):
        self.events = {}
        if not os.path.exists(self.data_path): return
        with open(self.data_path, encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    try:
                        y, m, d = map(int, parts[0].split('-'))
                        self.events.setdefault((m, d), []).append(parts[1])
                    except: pass

    def update_list(self):
        for row in self.listbox.get_children():
            self.listbox.remove(row)
        year, month, day = self.cal.get_date()
        events = self.events.get((month + 1, day), [])
        if not events:
            lbl = Gtk.Label(label="Nema događaja za ovaj dan.")
            lbl.set_xalign(0)
            self.listbox.add(lbl)
        else:
            for e in events:
                # Radimo vodoravni red (HBox) u kojem su tekst i gumb za brisanje
                row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                
                lbl = Gtk.Label(label=e)
                lbl.set_xalign(0)
                lbl.set_line_wrap(True)
                row_box.pack_start(lbl, True, True, 0)
                
                # Gumb s ikonom kante za smeće
                del_btn = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
                del_btn.set_tooltip_text("Obriši ovaj događaj")
                del_btn.connect("clicked", self.on_delete_clicked, e)
                row_box.pack_end(del_btn, False, False, 0)
                
                self.listbox.add(row_box)
        self.show_all()

    def on_add_clicked(self, button):
        dialog = Gtk.Dialog(title="Novi podsjetnik", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
        
        box = dialog.get_content_area()
        lbl = Gtk.Label(label="Upišite podsjetnik za odabrani dan:")
        box.pack_start(lbl, True, True, 10)
        
        entry = Gtk.Entry()
        box.pack_start(entry, True, True, 10)
        dialog.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            text = entry.get_text().strip()
            if text:
                year, month, day = self.cal.get_date()
                date_str = f"{year}-{month+1:02d}-{day:02d}"
                
                os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
                with open(self.data_path, "a", encoding="utf-8") as f:
                    f.write(f"{date_str}\t{text}\n")
                
                self.load_data()
                self.update_list()

        dialog.destroy()

    def on_delete_clicked(self, button, event_text):
        year, month, day = self.cal.get_date()
        date_str = f"{year}-{month+1:02d}-{day:02d}"
        
        # Čitamo sve trenutne zapise iz datoteke
        lines = []
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        
        # Zapisujemo natrag sve OSIM onog zapisa koji brišemo
        with open(self.data_path, "w", encoding="utf-8") as f:
            deleted = False
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) == 2 and parts[0] == date_str and parts[1] == event_text and not deleted:
                    # Preskačemo samo jedno podudaranje (brišemo ga)
                    deleted = True
                    continue
                f.write(line)
        
        # Ponovno osvježi sučelje
        self.load_data()
        self.update_list()

win = ExYuCalendar()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
