import json
import os
import re
import subprocess

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib


# Config persistente
CONFIG_DIR = os.path.expanduser("~/.config/xfce-theme-manager")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".tif"}

DEFAULT_WALLPAPER_FOLDERS = [
    d for d in ("/usr/share/backgrounds", os.path.expanduser("~/Pictures"))
    if os.path.isdir(d)
]


def load_config():
    if os.path.isfile(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return {}


def save_config(cfg):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_wallpaper_folders():
    cfg = load_config()
    folders = cfg.get("wallpaper_folders")
    if folders is None:
        folders = DEFAULT_WALLPAPER_FOLDERS[:]
        save_wallpaper_folders(folders)
    return folders


def save_wallpaper_folders(folders):
    cfg = load_config()
    cfg["wallpaper_folders"] = folders
    save_config(cfg)


def load_collections():
    cfg = load_config()
    return cfg.get("collections", {})


def save_collections(collections):
    cfg = load_config()
    cfg["collections"] = collections
    save_config(cfg)


def scan_wallpaper_images(folders, limit=400):
    results = []
    for folder in folders:
        folder = os.path.expanduser(folder)
        if not os.path.isdir(folder):
            continue
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fname in sorted(files):
                if os.path.splitext(fname)[1].lower() in IMAGE_EXTENSIONS:
                    results.append(os.path.join(root, fname))
                    if len(results) >= limit:
                        return results
    return results


# Backend: detecção e aplicação de temas

def run(cmd, check=True):
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _list_theme_dirs(dirs, marker_subpath, name_filter=None):
    # tema válido = subpasta com marker_subpath presente
    themes = set()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if os.path.isdir(os.path.join(d, name, marker_subpath)):
                if name_filter is None or name_filter(os.path.join(d, name)):
                    themes.add(name)
    return sorted(themes)


# GTK
def get_gtk_themes():
    dirs = [
        os.path.expanduser("~/.themes"),
        os.path.expanduser("~/.local/share/themes"),
        "/usr/share/themes",
    ]
    return _list_theme_dirs(dirs, "gtk-3.0")


def get_current_gtk_theme():
    try:
        return run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName"]).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def set_gtk_theme(name):
    try:
        run(["xfconf-query", "-c", "xsettings", "-p", "/Net/ThemeName", "-s", name])
        run(["xfconf-query", "-c", "xfwm4", "-p", "/general/theme", "-s", name])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao aplicar tema GTK/XFWM: {e.stderr.strip() or e}") from e


# Ícones
def get_icon_themes():
    dirs = [
        os.path.expanduser("~/.icons"),
        os.path.expanduser("~/.local/share/icons"),
        "/usr/share/icons",
    ]
    themes = set()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            index = os.path.join(d, name, "index.theme")
            if not os.path.isfile(index):
                continue
            try:
                with open(index, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                continue
            if "[Icon Theme]" not in content:
                continue
            dirs_match = re.search(r"^Directories=(.*)$", content, re.MULTILINE)
            if dirs_match:
                subdirs = [s for s in dirs_match.group(1).split(",") if s]
                if subdirs and all("cursor" in s.lower() for s in subdirs):
                    continue  # ignora temas só de cursor
            themes.add(name)
    return sorted(themes)


def get_current_icon_theme():
    try:
        return run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName"]).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def set_icon_theme(name):
    try:
        run(["xfconf-query", "-c", "xsettings", "-p", "/Net/IconThemeName", "-s", name])
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao aplicar tema de ícones: {e.stderr.strip() or e}") from e


# Wallpaper
def get_wallpaper_properties():
    try:
        out = run(["xfconf-query", "-c", "xfce4-desktop", "-l"]).stdout
    except (OSError, subprocess.CalledProcessError):
        return []
    return [line.strip() for line in out.splitlines() if line.strip().endswith("last-image")]


def get_current_wallpaper():
    props = get_wallpaper_properties()
    if not props:
        return None
    try:
        return run(["xfconf-query", "-c", "xfce4-desktop", "-p", props[0]]).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def set_wallpaper(path):
    if not os.path.isfile(path):
        raise RuntimeError(f"Arquivo de imagem não encontrado: {path}")
    props = get_wallpaper_properties()
    if not props:
        raise RuntimeError(
            "Nenhuma propriedade de papel de parede foi encontrada.\n"
            "Verifique se o xfdesktop está em execução."
        )
    for prop in props:
        run(["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", path])
    run(["xfdesktop", "--reload"], check=False)


# Rofi
def get_rofi_themes():
    dirs = [
        os.path.expanduser("~/.config/rofi/themes"),
        os.path.expanduser("~/.local/share/rofi/themes"),
        "/usr/share/rofi/themes",
    ]
    themes = []
    for d in dirs:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".rasi"):
                    themes.append(os.path.join(d, f))
    return sorted(set(themes))


def get_current_rofi_theme():
    config_path = os.path.expanduser("~/.config/rofi/config.rasi")
    if not os.path.isfile(config_path):
        return None
    with open(config_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    m = re.search(r'^\s*@theme\s+"?([^"\n]+)"?\s*$', content, re.MULTILINE)
    return m.group(1) if m else None


def set_rofi_theme(theme_path):
    config_path = os.path.expanduser("~/.config/rofi/config.rasi")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    theme_line = f'@theme "{theme_path}"'
    if os.path.isfile(config_path):
        with open(config_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        if re.search(r"^\s*@theme\s+.*$", content, re.MULTILINE):
            content = re.sub(r"^\s*@theme\s+.*$", theme_line, content, flags=re.MULTILINE)
        else:
            content = theme_line + "\n" + content
    else:
        content = "configuration {\n}\n\n" + theme_line + "\n"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(content)


# Mousepad
def get_mousepad_themes():
    base_dirs = ["/usr/share", os.path.expanduser("~/.local/share")]

    style_dirs = []
    for base in base_dirs:
        if not os.path.isdir(base):
            continue
        for d in os.listdir(base):
            if d.startswith("gtksourceview-"):
                styles_path = os.path.join(base, d, "styles")
                if os.path.isdir(styles_path):
                    style_dirs.append(styles_path)

    themes = set()
    for d in style_dirs:
        for f in os.listdir(d):
            if f.endswith(".xml"):
                themes.add(os.path.splitext(f)[0])
    return sorted(themes)


def get_current_mousepad_theme():
    # tenta gsettings primeiro, cai para o arquivo de config
    try:
        res = run(
            ["gsettings", "get", "org.xfce.mousepad.preferences.view", "color-scheme"],
            check=False,
        )
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip().strip("'").strip('"')
    except OSError:
        pass

    rc_path = os.path.expanduser("~/.config/Mousepad/mousepadrc")
    if os.path.isfile(rc_path):
        try:
            with open(rc_path, encoding="utf-8") as f:
                for line in f:
                    if line.lower().startswith("color-scheme="):
                        return line.split("=", 1)[1].strip().strip("'").strip('"')
        except OSError:
            pass
    return None


def set_mousepad_theme(theme_name):
    try:
        run(
            ["gsettings", "set", "org.xfce.mousepad.preferences.view", "color-scheme", theme_name],
            check=False,
        )
    except OSError:
        pass

    rc_path = os.path.expanduser("~/.config/Mousepad/mousepadrc")
    os.makedirs(os.path.dirname(rc_path), exist_ok=True)

    lines = []
    if os.path.isfile(rc_path):
        try:
            with open(rc_path, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError:
            pass

    new_lines = []
    replaced = False
    for line in lines:
        if line.lower().startswith("color-scheme="):
            new_lines.append(f"color-scheme={theme_name}\n")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f"color-scheme={theme_name}\n")

    with open(rc_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


# Coleções
def apply_collection(col_data):
    steps = (
        ("gtk", "GTK", set_gtk_theme),
        ("icon", "Ícones", set_icon_theme),
        ("wallpaper", "Papel de parede", set_wallpaper),
        ("rofi", "Rofi", set_rofi_theme),
        ("mousepad", "Mousepad", set_mousepad_theme),
    )
    errors = []
    for key, label, setter in steps:
        value = col_data.get(key)
        if not value:
            continue
        try:
            setter(value)
        except Exception as e:
            errors.append(f"{label}: {e}")

    if errors:
        raise RuntimeError("\n".join(errors))


# Interface gráfica

def show_error_dialog(widget, message, title="Erro"):
    dialog = Gtk.MessageDialog(
        transient_for=widget.get_toplevel(),
        flags=0,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=title,
    )
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()


class ThemeList(Gtk.Box):
    def __init__(self, get_items, get_current, apply_fn, label_fn=None, empty_msg=""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(12)

        self.get_items = get_items
        self.get_current = get_current
        self.apply_fn = apply_fn
        self.label_fn = label_fn or (lambda x: x)
        self.empty_msg = empty_msg
        self.all_items = []

        self.status = Gtk.Label(xalign=0)
        self.pack_start(self.status, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Filtrar itens...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.pack_start(self.search_entry, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_shadow_type(Gtk.ShadowType.IN)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-activated", self.on_apply)
        scroller.add(self.listbox)
        self.pack_start(scroller, True, True, 0)

        btn_box = Gtk.Box(spacing=8)

        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_btn.set_label(" Atualizar")
        refresh_btn.set_always_show_image(True)
        refresh_btn.connect("clicked", lambda w: self.reload())

        apply_btn = Gtk.Button.new_from_icon_name("emblem-default-symbolic", Gtk.IconSize.BUTTON)
        apply_btn.set_label(" Aplicar Tema")
        apply_btn.set_always_show_image(True)
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply)

        btn_box.pack_start(refresh_btn, False, False, 0)
        btn_box.pack_end(apply_btn, False, False, 0)
        self.pack_start(btn_box, False, False, 0)

        self.reload()

    def reload(self):
        self.all_items = self.get_items()
        query = self.search_entry.get_text().lower()
        if query:
            self.populate_list([i for i in self.all_items if query in self.label_fn(i).lower()])
        else:
            self.populate_list(self.all_items)

    def populate_list(self, items):
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        current = self.get_current()
        self.status.set_markup(
            "<b>Tema Atual:</b> {}".format(GLib.markup_escape_text(current or "Indisponível/Custom"))
        )

        if not items:
            row = Gtk.ListBoxRow()
            row.add(Gtk.Label(label=self.empty_msg or "Nenhum item encontrado.", xalign=0))
            row.set_selectable(False)
            self.listbox.add(row)
        else:
            for item in items:
                row = Gtk.ListBoxRow()
                row.item_value = item
                lbl = Gtk.Label(label=self.label_fn(item), xalign=0)
                lbl.set_margin_top(6)
                lbl.set_margin_bottom(6)
                lbl.set_margin_start(6)
                row.add(lbl)
                self.listbox.add(row)
                if current and (self.label_fn(item) == current or item == current):
                    self.listbox.select_row(row)
        self.listbox.show_all()

    def on_search_changed(self, entry):
        query = entry.get_text().lower()
        if not query:
            filtered = self.all_items
        else:
            filtered = [item for item in self.all_items if query in self.label_fn(item).lower()]
        self.populate_list(filtered)

    def on_apply(self, widget, *args):
        row = self.listbox.get_selected_row()
        if row is None or not hasattr(row, "item_value"):
            return
        try:
            self.apply_fn(row.item_value)
        except Exception as exc:
            show_error_dialog(self, str(exc), "Erro ao aplicar")
        self.reload()


class EditCollectionDialog(Gtk.Dialog):
    def __init__(self, parent, col_name, col_data):
        super().__init__(title="Editar Coleção", transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
        )
        self.set_default_size(450, 360)

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_border_width(12)

        grid = Gtk.Grid(row_spacing=10, column_spacing=10)
        box.pack_start(grid, True, True, 0)

        self.entry_name = Gtk.Entry(text=col_name)
        self.entry_name.set_hexpand(True)
        grid.attach(Gtk.Label(label="Nome:", xalign=0), 0, 0, 1, 1)
        grid.attach(self.entry_name, 1, 0, 1, 1)

        self.combo_gtk = self._make_combo(get_gtk_themes(), col_data.get("gtk"))
        grid.attach(Gtk.Label(label="GTK:", xalign=0), 0, 1, 1, 1)
        grid.attach(self.combo_gtk, 1, 1, 1, 1)

        self.combo_icon = self._make_combo(get_icon_themes(), col_data.get("icon"))
        grid.attach(Gtk.Label(label="Ícones:", xalign=0), 0, 2, 1, 1)
        grid.attach(self.combo_icon, 1, 2, 1, 1)

        self.entry_wall = Gtk.Entry(text=col_data.get("wallpaper", ""))
        self.entry_wall.set_hexpand(True)
        grid.attach(Gtk.Label(label="Wallpaper:", xalign=0), 0, 3, 1, 1)
        grid.attach(self.entry_wall, 1, 3, 1, 1)

        self.combo_rofi = self._make_combo(get_rofi_themes(), col_data.get("rofi"))
        grid.attach(Gtk.Label(label="Rofi:", xalign=0), 0, 4, 1, 1)
        grid.attach(self.combo_rofi, 1, 4, 1, 1)

        self.combo_mouse = self._make_combo(get_mousepad_themes(), col_data.get("mousepad"))
        grid.attach(Gtk.Label(label="Mousepad:", xalign=0), 0, 5, 1, 1)
        grid.attach(self.combo_mouse, 1, 5, 1, 1)

        self.show_all()

    @staticmethod
    def _make_combo(options, active_text):
        combo = Gtk.ComboBoxText()
        combo.append_text("")
        for opt in options:
            combo.append_text(opt)
        if active_text:
            model = combo.get_model()
            for i, row in enumerate(model):
                if row[0] == active_text:
                    combo.set_active(i)
                    break
        return combo

    def get_result(self):
        data = {
            "gtk": self.combo_gtk.get_active_text(),
            "icon": self.combo_icon.get_active_text(),
            "wallpaper": self.entry_wall.get_text().strip(),
            "rofi": self.combo_rofi.get_active_text(),
            "mousepad": self.combo_mouse.get_active_text(),
        }
        return self.entry_name.get_text().strip(), {k: v for k, v in data.items() if v}


class CollectionsTab(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(12)

        self.collections = load_collections()

        info_label = Gtk.Label(
            label="Salve ou edite perfis globais que englobam GTK, Ícones, Rofi, Mousepad e Wallpaper.",
            xalign=0,
        )
        info_label.set_line_wrap(True)
        self.pack_start(info_label, False, False, 0)

        form_box = Gtk.Box(spacing=8)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text("Nome da nova coleção...")
        self.name_entry.set_hexpand(True)
        self.name_entry.connect("activate", self.on_save_collection)

        save_btn = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        save_btn.set_label(" Salvar Atual")
        save_btn.set_always_show_image(True)
        save_btn.get_style_context().add_class("suggested-action")
        save_btn.connect("clicked", self.on_save_collection)

        form_box.pack_start(self.name_entry, True, True, 0)
        form_box.pack_start(save_btn, False, False, 0)
        self.pack_start(form_box, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_shadow_type(Gtk.ShadowType.IN)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scroller.add(self.listbox)
        self.pack_start(scroller, True, True, 0)

        btn_box = Gtk.Box(spacing=8)

        apply_btn = Gtk.Button.new_from_icon_name("emblem-default-symbolic", Gtk.IconSize.BUTTON)
        apply_btn.set_label(" Aplicar")
        apply_btn.set_always_show_image(True)
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply_collection)

        edit_btn = Gtk.Button.new_from_icon_name("document-edit-symbolic", Gtk.IconSize.BUTTON)
        edit_btn.set_label(" Editar")
        edit_btn.set_always_show_image(True)
        edit_btn.connect("clicked", self.on_edit_collection)

        delete_btn = Gtk.Button.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON)
        delete_btn.set_label(" Excluir")
        delete_btn.set_always_show_image(True)
        delete_btn.connect("clicked", self.on_delete_collection)

        btn_box.pack_start(apply_btn, False, False, 0)
        btn_box.pack_start(edit_btn, False, False, 0)
        btn_box.pack_end(delete_btn, False, False, 0)
        self.pack_start(btn_box, False, False, 0)

        self.reload_list()

    def reload_list(self):
        for child in self.listbox.get_children():
            self.listbox.remove(child)

        self.collections = load_collections()
        if not self.collections:
            row = Gtk.ListBoxRow()
            row.add(Gtk.Label(label="Nenhuma coleção criada ainda.", xalign=0))
            row.set_selectable(False)
            self.listbox.add(row)
        else:
            for name, data in sorted(self.collections.items()):
                row = Gtk.ListBoxRow()
                row.col_name = name

                details = (
                    f"<b>{GLib.markup_escape_text(name)}</b>\n"
                    f" • GTK: {data.get('gtk', 'N/A')} | Ícones: {data.get('icon', 'N/A')}\n"
                    f" • Rofi: {os.path.basename(data.get('rofi', '') or 'N/A')} | "
                    f"Wallpaper: {os.path.basename(data.get('wallpaper', '') or 'N/A')}\n"
                    f" • Mousepad: {data.get('mousepad', 'N/A')}"
                )
                lbl = Gtk.Label(xalign=0)
                lbl.set_markup(details)

                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                box.set_border_width(8)
                box.pack_start(lbl, False, False, 0)
                row.add(box)

                self.listbox.add(row)
        self.listbox.show_all()

    def on_save_collection(self, widget):
        name = self.name_entry.get_text().strip()
        if not name:
            show_error_dialog(self, "Digite um nome para a coleção.", "Aviso")
            return

        current_data = {
            "gtk": get_current_gtk_theme(),
            "icon": get_current_icon_theme(),
            "wallpaper": get_current_wallpaper(),
            "rofi": get_current_rofi_theme(),
            "mousepad": get_current_mousepad_theme(),
        }
        current_data = {k: v for k, v in current_data.items() if v}

        self.collections[name] = current_data
        save_collections(self.collections)
        self.name_entry.set_text("")
        self.reload_list()

    def on_apply_collection(self, widget):
        row = self.listbox.get_selected_row()
        if row is None or not hasattr(row, "col_name"):
            return

        col_data = self.collections.get(row.col_name)
        if not col_data:
            return

        try:
            apply_collection(col_data)
        except Exception as exc:
            show_error_dialog(self, str(exc), "Aviso")

    def on_edit_collection(self, widget):
        row = self.listbox.get_selected_row()
        if row is None or not hasattr(row, "col_name"):
            return

        col_name = row.col_name
        col_data = self.collections.get(col_name, {})

        dialog = EditCollectionDialog(self.get_toplevel(), col_name, col_data)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            new_name, new_data = dialog.get_result()

            if new_name and new_name != col_name:
                del self.collections[col_name]
                self.collections[new_name] = new_data
            elif new_name:
                self.collections[col_name] = new_data

            save_collections(self.collections)
            self.reload_list()

        dialog.destroy()

    def on_delete_collection(self, widget):
        row = self.listbox.get_selected_row()
        if row is None or not hasattr(row, "col_name"):
            return

        name = row.col_name
        if name in self.collections:
            del self.collections[name]
            save_collections(self.collections)
            self.reload_list()


class WallpaperTab(Gtk.Box):
    THUMB_SIZE = 128

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(12)

        self.folders = load_wallpaper_folders()
        self.selected_path = None

        self.preview = Gtk.Image()
        self.preview.set_size_request(-1, 180)
        preview_frame = Gtk.Frame()
        preview_frame.set_shadow_type(Gtk.ShadowType.IN)
        preview_frame.add(self.preview)
        self.pack_start(preview_frame, False, False, 0)

        folders_label = Gtk.Label(label="Pastas escaneadas:", xalign=0)
        self.pack_start(folders_label, False, False, 0)

        folders_row = Gtk.Box(spacing=8)

        folders_scroller = Gtk.ScrolledWindow()
        folders_scroller.set_size_request(-1, 80)
        folders_scroller.set_hexpand(True)
        folders_scroller.set_shadow_type(Gtk.ShadowType.IN)
        self.folders_listbox = Gtk.ListBox()
        self.folders_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        folders_scroller.add(self.folders_listbox)
        folders_row.pack_start(folders_scroller, True, True, 0)

        folder_btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        add_folder_btn = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        add_folder_btn.set_label(" Adicionar")
        add_folder_btn.set_always_show_image(True)
        add_folder_btn.connect("clicked", self.on_add_folder)

        remove_folder_btn = Gtk.Button.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON)
        remove_folder_btn.set_label(" Remover")
        remove_folder_btn.set_always_show_image(True)
        remove_folder_btn.connect("clicked", self.on_remove_folder)

        folder_btn_box.pack_start(add_folder_btn, False, False, 0)
        folder_btn_box.pack_start(remove_folder_btn, False, False, 0)
        folders_row.pack_start(folder_btn_box, False, False, 0)

        self.pack_start(folders_row, False, False, 0)

        status_box = Gtk.Box(spacing=8)
        self.count_label = Gtk.Label(xalign=0)
        self.spinner = Gtk.Spinner()
        status_box.pack_start(self.count_label, True, True, 0)
        status_box.pack_start(self.spinner, False, False, 0)
        self.pack_start(status_box, False, False, 0)

        grid_scroller = Gtk.ScrolledWindow()
        grid_scroller.set_vexpand(True)
        grid_scroller.set_shadow_type(Gtk.ShadowType.IN)
        self.store = Gtk.ListStore(GdkPixbuf.Pixbuf, str, str)
        self.iconview = Gtk.IconView(model=self.store)
        self.iconview.set_pixbuf_column(0)
        self.iconview.set_text_column(2)
        self.iconview.set_item_width(self.THUMB_SIZE + 12)
        self.iconview.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.iconview.connect("selection-changed", self.on_icon_selected)
        self.iconview.connect("item-activated", self.on_icon_activated)
        grid_scroller.add(self.iconview)
        self.pack_start(grid_scroller, True, True, 0)

        btn_box = Gtk.Box(spacing=8)
        rescan_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        rescan_btn.set_label(" Atualizar")
        rescan_btn.set_always_show_image(True)
        rescan_btn.connect("clicked", lambda w: self.rescan())

        apply_btn = Gtk.Button.new_from_icon_name("emblem-default-symbolic", Gtk.IconSize.BUTTON)
        apply_btn.set_label(" Aplicar Wallpaper")
        apply_btn.set_always_show_image(True)
        apply_btn.get_style_context().add_class("suggested-action")
        apply_btn.connect("clicked", self.on_apply)

        btn_box.pack_start(rescan_btn, False, False, 0)
        btn_box.pack_end(apply_btn, False, False, 0)
        self.pack_start(btn_box, False, False, 0)

        self.refresh_folder_list()
        self.rescan()

    def refresh_folder_list(self):
        for child in self.folders_listbox.get_children():
            self.folders_listbox.remove(child)
        if not self.folders:
            row = Gtk.ListBoxRow()
            row.add(Gtk.Label(label="Nenhuma pasta adicionada ainda.", xalign=0))
            row.set_selectable(False)
            self.folders_listbox.add(row)
        else:
            for folder in self.folders:
                row = Gtk.ListBoxRow()
                row.folder_path = folder
                row.add(Gtk.Label(label=folder, xalign=0))
                self.folders_listbox.add(row)
        self.folders_listbox.show_all()

    def on_add_folder(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Escolher pasta de papéis de parede",
            transient_for=self.get_toplevel(),
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Adicionar", Gtk.ResponseType.OK,
        )
        response = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.OK and path:
            if path not in self.folders:
                self.folders.append(path)
                save_wallpaper_folders(self.folders)
                self.refresh_folder_list()
                self.rescan()

    def on_remove_folder(self, widget):
        row = self.folders_listbox.get_selected_row()
        if row is None or not hasattr(row, "folder_path"):
            return
        self.folders.remove(row.folder_path)
        save_wallpaper_folders(self.folders)
        self.refresh_folder_list()
        self.rescan()

    def rescan(self):
        self.store.clear()
        self.selected_path = None
        self.preview.clear()
        self.count_label.set_text("Escaneando imagens…")
        self.spinner.start()
        self.spinner.show()

        while Gtk.events_pending():
            Gtk.main_iteration()

        images = scan_wallpaper_images(self.folders)
        for path in images:
            try:
                thumb = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    path, self.THUMB_SIZE, self.THUMB_SIZE, True
                )
            except GLib.Error:
                continue
            self.store.append([thumb, path, os.path.basename(path)])

        self.spinner.stop()
        self.spinner.hide()

        if not self.folders:
            self.count_label.set_text("Nenhuma pasta adicionada.")
        elif not images:
            self.count_label.set_text("Nenhuma imagem encontrada.")
        else:
            self.count_label.set_text(f"{len(images)} imagem(ns) encontrada(s).")

    def on_icon_selected(self, iconview):
        items = iconview.get_selected_items()
        if not items:
            self.selected_path = None
            return
        tree_iter = self.store.get_iter(items[0])
        path = self.store.get_value(tree_iter, 1)
        self.selected_path = path
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 500, 180, True)
            self.preview.set_from_pixbuf(pixbuf)
        except GLib.Error:
            self.preview.clear()

    def on_icon_activated(self, iconview, tree_path):
        tree_iter = self.store.get_iter(tree_path)
        self.selected_path = self.store.get_value(tree_iter, 1)
        self.apply_wallpaper()

    def on_apply(self, widget):
        self.apply_wallpaper()

    def apply_wallpaper(self):
        if not self.selected_path:
            show_error_dialog(self, "Selecione uma imagem na grade antes de aplicar.", "Erro ao aplicar papel de parede")
            return
        try:
            set_wallpaper(self.selected_path)
        except Exception as exc:
            show_error_dialog(self, str(exc), "Erro ao aplicar papel de parede")


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="XFCE Theme Manager")
        self.set_default_size(700, 580)
        self.set_border_width(8)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(200)

        stack.add_titled(CollectionsTab(), "collections", "Coleções")
        stack.add_titled(
            ThemeList(
                get_gtk_themes, get_current_gtk_theme, set_gtk_theme,
                empty_msg="Nenhum tema GTK encontrado.",
            ),
            "gtk", "GTK",
        )
        stack.add_titled(
            ThemeList(
                get_icon_themes, get_current_icon_theme, set_icon_theme,
                empty_msg="Nenhum tema de ícones encontrado.",
            ),
            "icons", "Ícones",
        )
        stack.add_titled(WallpaperTab(), "wallpaper", "Wallpaper")

        stack.add_titled(
            ThemeList(
                get_mousepad_themes, get_current_mousepad_theme, set_mousepad_theme,
                empty_msg="Nenhum tema de Mousepad encontrado (estilos gtksourceview).",
            ),
            "mousepad", "Mousepad",
        )

        stack.add_titled(
            ThemeList(
                get_rofi_themes, get_current_rofi_theme, set_rofi_theme,
                label_fn=lambda p: os.path.basename(p),
                empty_msg="Nenhum tema .rasi encontrado para o Rofi.",
            ),
            "rofi", "Rofi",
        )

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)
        switcher.set_halign(Gtk.Align.CENTER)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.pack_start(switcher, False, False, 6)
        box.pack_start(stack, True, True, 0)
        self.add(box)


def main():
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
