import copy
import json
import locale
import os
import re
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk

# === Metadados ===

APP_NAME = "XFCE Theme Manager"
APP_VERSION = "2.0"
APP_ICON_NAME = "preferences-desktop-theme"
DEVELOPER = "Mateus Calixto"
LICENSE_NAME = "MIT"
GITHUB_URL = "https://github.com/ogoncas/xfce-themes"

# === Internacionalização ===

EN = {
    "app_title": APP_NAME,
    "tab_collections": "Collections",
    "tab_gtk": "GTK Theme",
    "tab_icons": "Icons",
    "tab_wallpaper": "Wallpaper",
    "tab_mousepad": "Mousepad",
    "tab_rofi": "Rofi",
    "current_theme": "Current theme:",
    "selected_label": "Selected:",
    "not_available": "Unavailable/Custom",
    "none_selected": "None",
    "filter_placeholder": "Filter items...",
    "refresh": "Refresh",
    "apply_theme": "Apply Theme",
    "apply": "Apply",
    "cancel": "Cancel",
    "save": "Save",
    "add": "Add",
    "remove": "Remove",
    "empty_gtk": "No GTK theme found.",
    "empty_icons": "No icon theme found.",
    "empty_mousepad": "No Mousepad theme found (gtksourceview styles).",
    "empty_rofi": "No .rasi theme found for Rofi.",
    "empty_generic": "No item found.",
    "error_title": "Error",
    "error_apply_title": "Error applying",
    "error_apply_wallpaper_title": "Error applying wallpaper",
    "warning_title": "Warning",
    "err_gtk_apply": "Error applying GTK/XFWM theme: {detail}",
    "err_icon_apply": "Error applying icon theme: {detail}",
    "err_wallpaper_missing_file": "Image file not found: {path}",
    "err_wallpaper_no_props": "No wallpaper property was found.\nCheck if xfdesktop is running.",
    "select_image_prompt": "Select an image in the grid before applying.",
    "select_item_first": "Select an item before applying.",
    "scanning_images": "Scanning images…",
    "no_folder_added": "No folder added.",
    "no_image_found": "No image found.",
    "images_found": "{count} image(s) found.",
    "wallpaper_apply_btn": "Apply Wallpaper",
    "configure_folders_hint": "Manage the scanned folders in Settings.",
    "open_settings": "Open Settings",
    "collections_info": "Save or edit global profiles combining GTK, Icons, Rofi, Mousepad and Wallpaper.",
    "collection_name_placeholder": "New collection name...",
    "save_current": "Save Current",
    "no_collections": "No collection created yet.",
    "collection_apply": "Apply",
    "collection_edit": "Edit",
    "collection_delete": "Delete",
    "collection_name_required": "Enter a name for the collection.",
    "edit_collection_title": "Edit Collection",
    "label_name": "Name:",
    "label_gtk": "GTK:",
    "label_icons": "Icons:",
    "label_wallpaper": "Wallpaper:",
    "label_rofi": "Rofi:",
    "label_mousepad": "Mousepad:",
    "settings_title": "Settings",
    "settings_tooltip": "Settings",
    "tab_general": "General",
    "tab_folders": "Folders",
    "tab_about": "About",
    "language_label": "Language",
    "language_auto": "Automatic (system)",
    "language_pt": "Português (Brasil)",
    "language_en": "English",
    "language_auto_hint": "Currently detected: {lang}",
    "folders_intro": "Add extra folders to scan for each theme type, in addition to the system defaults.",
    "default_folders": "Default",
    "no_custom_folders": "No custom folder added.",
    "choose_folder": "Choose folder",
    "folders_wallpaper": "Wallpaper folders",
    "folders_gtk": "GTK theme folders",
    "folders_icons": "Icon theme folders",
    "folders_rofi": "Rofi theme folders",
    "folders_mousepad": "Mousepad style folders",
    "folders_mousepad_default_note": "System default gtksourceview style directories.",
    "version_label": "Version {version}",
    "about_description": "A graphical manager for GTK, icon, Rofi and Mousepad themes and wallpapers on XFCE.",
    "developer_label": "Developer",
    "license_label": "License",
    "view_on_github": "View on GitHub",
}

PT_BR = {
    "app_title": APP_NAME,
    "tab_collections": "Coleções",
    "tab_gtk": "Tema GTK",
    "tab_icons": "Ícones",
    "tab_wallpaper": "Papel de Parede",
    "tab_mousepad": "Mousepad",
    "tab_rofi": "Rofi",
    "current_theme": "Tema atual:",
    "selected_label": "Selecionado:",
    "not_available": "Indisponível/Personalizado",
    "none_selected": "Nenhum",
    "filter_placeholder": "Filtrar itens...",
    "refresh": "Atualizar",
    "apply_theme": "Aplicar Tema",
    "apply": "Aplicar",
    "cancel": "Cancelar",
    "save": "Salvar",
    "add": "Adicionar",
    "remove": "Remover",
    "empty_gtk": "Nenhum tema GTK encontrado.",
    "empty_icons": "Nenhum tema de ícones encontrado.",
    "empty_mousepad": "Nenhum tema de Mousepad encontrado (estilos gtksourceview).",
    "empty_rofi": "Nenhum tema .rasi encontrado para o Rofi.",
    "empty_generic": "Nenhum item encontrado.",
    "error_title": "Erro",
    "error_apply_title": "Erro ao aplicar",
    "error_apply_wallpaper_title": "Erro ao aplicar papel de parede",
    "warning_title": "Aviso",
    "err_gtk_apply": "Erro ao aplicar tema GTK/XFWM: {detail}",
    "err_icon_apply": "Erro ao aplicar tema de ícones: {detail}",
    "err_wallpaper_missing_file": "Arquivo de imagem não encontrado: {path}",
    "err_wallpaper_no_props": "Nenhuma propriedade de papel de parede foi encontrada.\nVerifique se o xfdesktop está em execução.",
    "select_image_prompt": "Selecione uma imagem na grade antes de aplicar.",
    "select_item_first": "Selecione um item antes de aplicar.",
    "scanning_images": "Escaneando imagens…",
    "no_folder_added": "Nenhuma pasta adicionada.",
    "no_image_found": "Nenhuma imagem encontrada.",
    "images_found": "{count} imagem(ns) encontrada(s).",
    "wallpaper_apply_btn": "Aplicar Wallpaper",
    "configure_folders_hint": "Gerencie as pastas escaneadas nas Configurações.",
    "open_settings": "Abrir Configurações",
    "collections_info": "Salve ou edite perfis globais que englobam GTK, Ícones, Rofi, Mousepad e Wallpaper.",
    "collection_name_placeholder": "Nome da nova coleção...",
    "save_current": "Salvar Atual",
    "no_collections": "Nenhuma coleção criada ainda.",
    "collection_apply": "Aplicar",
    "collection_edit": "Editar",
    "collection_delete": "Excluir",
    "collection_name_required": "Digite um nome para a coleção.",
    "edit_collection_title": "Editar Coleção",
    "label_name": "Nome:",
    "label_gtk": "GTK:",
    "label_icons": "Ícones:",
    "label_wallpaper": "Wallpaper:",
    "label_rofi": "Rofi:",
    "label_mousepad": "Mousepad:",
    "settings_title": "Configurações",
    "settings_tooltip": "Configurações",
    "tab_general": "Geral",
    "tab_folders": "Pastas",
    "tab_about": "Sobre",
    "language_label": "Idioma",
    "language_auto": "Automático (sistema)",
    "language_pt": "Português (Brasil)",
    "language_en": "English",
    "language_auto_hint": "Detectado atualmente: {lang}",
    "folders_intro": "Adicione pastas extras para escanear cada tipo de tema, além dos padrões do sistema.",
    "default_folders": "Padrão",
    "no_custom_folders": "Nenhuma pasta personalizada adicionada.",
    "choose_folder": "Escolher pasta",
    "folders_wallpaper": "Pastas de papel de parede",
    "folders_gtk": "Pastas de temas GTK",
    "folders_icons": "Pastas de temas de ícones",
    "folders_rofi": "Pastas de temas Rofi",
    "folders_mousepad": "Pastas de estilos do Mousepad",
    "folders_mousepad_default_note": "Diretórios padrão do sistema (estilos gtksourceview).",
    "version_label": "Versão {version}",
    "about_description": "Um gerenciador gráfico de temas GTK, ícones, Rofi, Mousepad e papéis de parede no XFCE.",
    "developer_label": "Desenvolvedor",
    "license_label": "Licença",
    "view_on_github": "Ver no GitHub",
}

TRANSLATIONS = {"en": EN, "pt_BR": PT_BR}


def detect_system_language():
    """Retorna 'pt_BR' se o sistema estiver em português; senão, 'en'."""
    candidates = []
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        val = os.environ.get(var)
        if val:
            candidates.append(val.split(":")[0])
    try:
        loc = locale.getlocale()[0]
        if loc:
            candidates.append(loc)
    except (ValueError, TypeError):
        pass

    for c in candidates:
        if c and c.lower().startswith("pt"):
            return "pt_BR"
    return "en"


class I18N:
    def __init__(self):
        self.current = "en"
        self.apply_language(load_config().get("language", "auto"))

    def apply_language(self, lang_setting):
        if lang_setting == "auto" or lang_setting not in TRANSLATIONS:
            self.current = detect_system_language()
        else:
            self.current = lang_setting

    def t(self, key, **kwargs):
        table = TRANSLATIONS.get(self.current, EN)
        text = table.get(key, EN.get(key, key))
        return text.format(**kwargs) if kwargs else text


# === Configuração ===

CONFIG_DIR = os.path.expanduser("~/.config/xfce-theme-manager")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".tiff", ".tif"}

DEFAULT_WALLPAPER_DIRS = [
    d for d in ("/usr/share/backgrounds", os.path.expanduser("~/Pictures"))
    if os.path.isdir(d)
]
DEFAULT_GTK_DIRS = [
    os.path.expanduser("~/.themes"),
    os.path.expanduser("~/.local/share/themes"),
    "/usr/share/themes",
]
DEFAULT_ICON_DIRS = [
    os.path.expanduser("~/.icons"),
    os.path.expanduser("~/.local/share/icons"),
    "/usr/share/icons",
]
DEFAULT_ROFI_DIRS = [
    os.path.expanduser("~/.config/rofi/themes"),
    os.path.expanduser("~/.local/share/rofi/themes"),
    "/usr/share/rofi/themes",
]

CONFIG_KEYS_FOLDERS = {
    "wallpaper_folders": DEFAULT_WALLPAPER_DIRS,
    "gtk_theme_folders": DEFAULT_GTK_DIRS,
    "icon_theme_folders": DEFAULT_ICON_DIRS,
    "rofi_theme_folders": DEFAULT_ROFI_DIRS,
    "mousepad_style_folders": [],
}


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


def get_full_config():
    """Carrega a config e garante que todas as chaves existam."""
    cfg = load_config()
    changed = False
    if "language" not in cfg:
        cfg["language"] = "auto"
        changed = True
    for key in CONFIG_KEYS_FOLDERS:
        if key not in cfg or not isinstance(cfg[key], list):
            cfg[key] = []
            changed = True
    if "collections" not in cfg:
        cfg["collections"] = {}
        changed = True
    if changed:
        save_config(cfg)
    return cfg


def custom_folders(key):
    return list(get_full_config().get(key, []))


def load_wallpaper_folders():
    """Pastas padrão + personalizadas, sem duplicatas."""
    extra = custom_folders("wallpaper_folders")
    return DEFAULT_WALLPAPER_DIRS + [f for f in extra if f not in DEFAULT_WALLPAPER_DIRS]


def load_collections():
    return get_full_config().get("collections", {})


def save_collections(collections):
    cfg = get_full_config()
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


# === Backend ===

def run(cmd, check=True):
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _list_theme_dirs(dirs, marker_subpath):
    """Lista os temas em `dirs` que contêm `marker_subpath`."""
    themes = set()
    for d in dirs:
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if os.path.isdir(os.path.join(d, name, marker_subpath)):
                themes.add(name)
    return sorted(themes)


# ---- GTK ----
def get_gtk_themes():
    dirs = DEFAULT_GTK_DIRS + custom_folders("gtk_theme_folders")
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
        raise RuntimeError(_("err_gtk_apply", detail=(e.stderr or "").strip() or str(e))) from e


# ---- ÍCONES ----
def get_icon_themes():
    dirs = DEFAULT_ICON_DIRS + custom_folders("icon_theme_folders")
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
                    continue
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
        raise RuntimeError(_("err_icon_apply", detail=(e.stderr or "").strip() or str(e))) from e


# ---- WALLPAPER ----
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
        raise RuntimeError(_("err_wallpaper_missing_file", path=path))
    props = get_wallpaper_properties()
    if not props:
        raise RuntimeError(_("err_wallpaper_no_props"))
    for prop in props:
        run(["xfconf-query", "-c", "xfce4-desktop", "-p", prop, "-s", path])
    run(["xfdesktop", "--reload"], check=False)


# ---- ROFI ----
def get_rofi_themes():
    dirs = DEFAULT_ROFI_DIRS + custom_folders("rofi_theme_folders")
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


# ---- MOUSEPAD ----
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

    style_dirs += custom_folders("mousepad_style_folders")

    themes = set()
    for d in style_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".xml"):
                themes.add(os.path.splitext(f)[0])
    return sorted(themes)


def get_current_mousepad_theme():
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


# ---- COLEÇÕES ----
def apply_collection(col_data):
    steps = (
        ("gtk", "label_gtk", set_gtk_theme),
        ("icon", "label_icons", set_icon_theme),
        ("wallpaper", "label_wallpaper", set_wallpaper),
        ("rofi", "label_rofi", set_rofi_theme),
        ("mousepad", "label_mousepad", set_mousepad_theme),
    )
    errors = []
    for key, label_key, setter in steps:
        value = col_data.get(key)
        if not value:
            continue
        try:
            setter(value)
        except Exception as e:
            errors.append(f"{_(label_key)} {e}")

    if errors:
        raise RuntimeError("\n".join(errors))


# === CSS ===

CSS = b"""
headerbar {
    padding: 2px 6px;
}
headerbar .title {
    font-weight: 600;
}
list row {
    padding: 6px 8px;
    border-radius: 6px;
}
list row:selected {
    font-weight: 600;
}
iconview {
    padding: 6px;
}
iconview.view:selected {
    border-radius: 8px;
}
frame {
    border-radius: 8px;
}
button.suggested-action {
    font-weight: 600;
}
label.status-current {
    padding: 2px 0 6px 0;
    opacity: 0.85;
}
label.status-selected {
    padding: 0 0 4px 0;
    font-weight: 600;
}
box.folder-section {
    padding: 6px 2px;
}
"""


def load_css():
    provider = Gtk.CssProvider()
    provider.load_from_data(CSS)
    screen = Gdk.Screen.get_default()
    if screen is not None:
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


# === Utilitários de interface ===

def show_error_dialog(widget, message, title=None):
    """Exibe um diálogo modal de erro."""
    dialog = Gtk.MessageDialog(
        transient_for=widget.get_toplevel(),
        flags=0,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=title or _("error_title"),
    )
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()


def make_icon_button(icon_name, label_text, suggested=False):
    btn = Gtk.Button.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    btn.set_label(f" {label_text}")
    btn.set_always_show_image(True)
    if suggested:
        btn.get_style_context().add_class("suggested-action")
    return btn


# === Lista de temas ===

class ThemeList(Gtk.Box):
    def __init__(self, get_items, get_current, apply_fn, label_fn=None, empty_msg_key=""):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(12)

        self.get_items = get_items
        self.get_current = get_current
        self.apply_fn = apply_fn
        self.label_fn = label_fn or (lambda x: x)
        self.empty_msg_key = empty_msg_key
        self.all_items = []

        self.status = Gtk.Label(xalign=0)
        self.status.get_style_context().add_class("status-current")
        self.pack_start(self.status, False, False, 0)

        self.selected_status = Gtk.Label(xalign=0)
        self.selected_status.get_style_context().add_class("status-selected")
        self.pack_start(self.selected_status, False, False, 0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text(_("filter_placeholder"))
        self.search_entry.connect("search-changed", self.on_search_changed)
        self.pack_start(self.search_entry, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        scroller.set_shadow_type(Gtk.ShadowType.IN)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.connect("row-selected", self.on_row_selected)
        scroller.add(self.listbox)
        self.pack_start(scroller, True, True, 0)

        btn_box = Gtk.Box(spacing=8)

        refresh_btn = make_icon_button("view-refresh-symbolic", _("refresh"))
        refresh_btn.connect("clicked", lambda w: self.reload())

        self.apply_btn = make_icon_button("emblem-default-symbolic", _("apply_theme"), suggested=True)
        self.apply_btn.connect("clicked", self.on_apply)
        self.apply_btn.set_sensitive(False)

        btn_box.pack_start(refresh_btn, False, False, 0)
        btn_box.pack_end(self.apply_btn, False, False, 0)
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
            "<b>{}</b> {}".format(
                GLib.markup_escape_text(_("current_theme")),
                GLib.markup_escape_text(current or _("not_available")),
            )
        )

        if not items:
            row = Gtk.ListBoxRow()
            row.add(Gtk.Label(label=_(self.empty_msg_key) if self.empty_msg_key else _("empty_generic"), xalign=0))
            row.set_selectable(False)
            self.listbox.add(row)
        else:
            for item in items:
                row = Gtk.ListBoxRow()
                row.item_value = item
                lbl = Gtk.Label(label=self.label_fn(item), xalign=0)
                lbl.set_margin_top(4)
                lbl.set_margin_bottom(4)
                lbl.set_margin_start(4)
                row.add(lbl)
                self.listbox.add(row)
                if current and (self.label_fn(item) == current or item == current):
                    self.listbox.select_row(row)
        self.listbox.show_all()
        self.update_selected_status()

    def update_selected_status(self):
        row = self.listbox.get_selected_row()
        if row is not None and hasattr(row, "item_value"):
            self.selected_status.set_markup(
                "<b>{}</b> {}".format(
                    GLib.markup_escape_text(_("selected_label")),
                    GLib.markup_escape_text(self.label_fn(row.item_value)),
                )
            )
            self.apply_btn.set_sensitive(True)
        else:
            self.selected_status.set_markup(
                "<b>{}</b> {}".format(
                    GLib.markup_escape_text(_("selected_label")),
                    GLib.markup_escape_text(_("none_selected")),
                )
            )
            self.apply_btn.set_sensitive(False)

    def on_row_selected(self, listbox, row):
        self.update_selected_status()

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
            show_error_dialog(self, _("select_item_first"), _("error_apply_title"))
            return
        try:
            self.apply_fn(row.item_value)
        except Exception as exc:
            show_error_dialog(self, str(exc), _("error_apply_title"))
        self.reload()


# === Coleções ===

class EditCollectionDialog(Gtk.Dialog):
    def __init__(self, parent, col_name, col_data):
        super().__init__(title=_("edit_collection_title"), transient_for=parent, flags=0)
        self.add_buttons(
            _("cancel"), Gtk.ResponseType.CANCEL,
            _("save"), Gtk.ResponseType.OK,
        )
        self.set_default_size(450, 360)

        box = self.get_content_area()
        box.set_spacing(10)
        box.set_border_width(12)

        grid = Gtk.Grid(row_spacing=10, column_spacing=10)
        box.pack_start(grid, True, True, 0)

        self.entry_name = Gtk.Entry(text=col_name)
        self.entry_name.set_hexpand(True)
        grid.attach(Gtk.Label(label=_("label_name"), xalign=0), 0, 0, 1, 1)
        grid.attach(self.entry_name, 1, 0, 1, 1)

        self.combo_gtk = self._make_combo(get_gtk_themes(), col_data.get("gtk"))
        grid.attach(Gtk.Label(label=_("label_gtk"), xalign=0), 0, 1, 1, 1)
        grid.attach(self.combo_gtk, 1, 1, 1, 1)

        self.combo_icon = self._make_combo(get_icon_themes(), col_data.get("icon"))
        grid.attach(Gtk.Label(label=_("label_icons"), xalign=0), 0, 2, 1, 1)
        grid.attach(self.combo_icon, 1, 2, 1, 1)

        self.entry_wall = Gtk.Entry(text=col_data.get("wallpaper", ""))
        self.entry_wall.set_hexpand(True)
        grid.attach(Gtk.Label(label=_("label_wallpaper"), xalign=0), 0, 3, 1, 1)
        grid.attach(self.entry_wall, 1, 3, 1, 1)

        self.combo_rofi = self._make_combo(get_rofi_themes(), col_data.get("rofi"))
        grid.attach(Gtk.Label(label=_("label_rofi"), xalign=0), 0, 4, 1, 1)
        grid.attach(self.combo_rofi, 1, 4, 1, 1)

        self.combo_mouse = self._make_combo(get_mousepad_themes(), col_data.get("mousepad"))
        grid.attach(Gtk.Label(label=_("label_mousepad"), xalign=0), 0, 5, 1, 1)
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

        info_label = Gtk.Label(label=_("collections_info"), xalign=0)
        info_label.set_line_wrap(True)
        self.pack_start(info_label, False, False, 0)

        form_box = Gtk.Box(spacing=8)
        self.name_entry = Gtk.Entry()
        self.name_entry.set_placeholder_text(_("collection_name_placeholder"))
        self.name_entry.set_hexpand(True)
        self.name_entry.connect("activate", self.on_save_collection)

        save_btn = make_icon_button("list-add-symbolic", _("save_current"), suggested=True)
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

        apply_btn = make_icon_button("emblem-default-symbolic", _("collection_apply"), suggested=True)
        apply_btn.connect("clicked", self.on_apply_collection)

        edit_btn = make_icon_button("document-edit-symbolic", _("collection_edit"))
        edit_btn.connect("clicked", self.on_edit_collection)

        delete_btn = make_icon_button("edit-delete-symbolic", _("collection_delete"))
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
            row.add(Gtk.Label(label=_("no_collections"), xalign=0))
            row.set_selectable(False)
            self.listbox.add(row)
        else:
            for name, data in sorted(self.collections.items()):
                row = Gtk.ListBoxRow()
                row.col_name = name

                details = (
                    f"<b>{GLib.markup_escape_text(name)}</b>\n"
                    f" • {_('label_gtk')} {data.get('gtk', 'N/A')} | {_('label_icons')} {data.get('icon', 'N/A')}\n"
                    f" • {_('label_rofi')} {os.path.basename(data.get('rofi', '') or 'N/A')} | "
                    f"{_('label_wallpaper')} {os.path.basename(data.get('wallpaper', '') or 'N/A')}\n"
                    f" • {_('label_mousepad')} {data.get('mousepad', 'N/A')}"
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
            show_error_dialog(self, _("collection_name_required"), _("warning_title"))
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
            show_error_dialog(self, str(exc), _("warning_title"))

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


# === Wallpaper ===

class WallpaperTab(Gtk.Box):
    THUMB_SIZE = 128

    def __init__(self, open_settings_cb=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.set_border_width(12)
        self.open_settings_cb = open_settings_cb
        self.selected_path = None

        self.preview = Gtk.Image()
        self.preview.set_size_request(-1, 180)
        preview_frame = Gtk.Frame()
        preview_frame.set_shadow_type(Gtk.ShadowType.IN)
        preview_frame.add(self.preview)
        self.pack_start(preview_frame, False, False, 0)

        self.selected_status = Gtk.Label(xalign=0)
        self.selected_status.get_style_context().add_class("status-selected")
        self.pack_start(self.selected_status, False, False, 0)

        hint_row = Gtk.Box(spacing=8)
        hint_label = Gtk.Label(label=_("configure_folders_hint"), xalign=0)
        hint_label.get_style_context().add_class("status-current")
        hint_row.pack_start(hint_label, True, True, 0)
        if self.open_settings_cb:
            open_btn = Gtk.Button.new_with_label(_("open_settings"))
            open_btn.connect("clicked", lambda w: self.open_settings_cb())
            hint_row.pack_start(open_btn, False, False, 0)
        self.pack_start(hint_row, False, False, 0)

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
        grid_scroller.add(self.iconview)
        self.pack_start(grid_scroller, True, True, 0)

        btn_box = Gtk.Box(spacing=8)
        rescan_btn = make_icon_button("view-refresh-symbolic", _("refresh"))
        rescan_btn.connect("clicked", lambda w: self.rescan())

        self.apply_btn = make_icon_button("emblem-default-symbolic", _("wallpaper_apply_btn"), suggested=True)
        self.apply_btn.connect("clicked", self.on_apply)
        self.apply_btn.set_sensitive(False)

        btn_box.pack_start(rescan_btn, False, False, 0)
        btn_box.pack_end(self.apply_btn, False, False, 0)
        self.pack_start(btn_box, False, False, 0)

        self.update_selected_status()
        self.rescan()

    def update_selected_status(self):
        if self.selected_path:
            self.selected_status.set_markup(
                "<b>{}</b> {}".format(
                    GLib.markup_escape_text(_("selected_label")),
                    GLib.markup_escape_text(os.path.basename(self.selected_path)),
                )
            )
            self.apply_btn.set_sensitive(True)
        else:
            self.selected_status.set_markup(
                "<b>{}</b> {}".format(
                    GLib.markup_escape_text(_("selected_label")),
                    GLib.markup_escape_text(_("none_selected")),
                )
            )
            self.apply_btn.set_sensitive(False)

    def rescan(self):
        folders = load_wallpaper_folders()
        self.store.clear()
        self.selected_path = None
        self.preview.clear()
        self.update_selected_status()
        self.count_label.set_text(_("scanning_images"))
        self.spinner.start()
        self.spinner.show()

        while Gtk.events_pending():
            Gtk.main_iteration()

        images = scan_wallpaper_images(folders)
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

        if not folders:
            self.count_label.set_text(_("no_folder_added"))
        elif not images:
            self.count_label.set_text(_("no_image_found"))
        else:
            self.count_label.set_text(_("images_found", count=len(images)))

    def on_icon_selected(self, iconview):
        items = iconview.get_selected_items()
        if not items:
            self.selected_path = None
            self.preview.clear()
            self.update_selected_status()
            return
        tree_iter = self.store.get_iter(items[0])
        path = self.store.get_value(tree_iter, 1)
        self.selected_path = path
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 500, 180, True)
            self.preview.set_from_pixbuf(pixbuf)
        except GLib.Error:
            self.preview.clear()
        self.update_selected_status()

    def on_apply(self, widget):
        self.apply_wallpaper()

    def apply_wallpaper(self):
        if not self.selected_path:
            show_error_dialog(self, _("select_image_prompt"), _("error_apply_wallpaper_title"))
            return
        try:
            set_wallpaper(self.selected_path)
        except Exception as exc:
            show_error_dialog(self, str(exc), _("error_apply_wallpaper_title"))


# === Configurações ===

class FolderListEditor(Gtk.Box):
    """Edita as pastas extras de uma categoria.

    Altera a lista em memória; só é salva ao aplicar as Configurações.
    """

    def __init__(self, folders_ref, default_dirs, default_note=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_style_context().add_class("folder-section")
        self.folders_ref = folders_ref  # lista dentro do config pendente

        info = Gtk.Label(xalign=0)
        if default_dirs:
            info.set_markup(
                "<small>{}: {}</small>".format(
                    GLib.markup_escape_text(_("default_folders")),
                    GLib.markup_escape_text(", ".join(default_dirs)),
                )
            )
        elif default_note:
            info.set_markup("<small>{}</small>".format(GLib.markup_escape_text(default_note)))
        info.set_line_wrap(True)
        self.pack_start(info, False, False, 0)

        row = Gtk.Box(spacing=8)
        scroller = Gtk.ScrolledWindow()
        scroller.set_size_request(-1, 90)
        scroller.set_shadow_type(Gtk.ShadowType.IN)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scroller.add(self.listbox)
        row.pack_start(scroller, True, True, 0)

        btns = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        add_btn = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        add_btn.set_tooltip_text(_("add"))
        add_btn.connect("clicked", self.on_add)
        rem_btn = Gtk.Button.new_from_icon_name("list-remove-symbolic", Gtk.IconSize.BUTTON)
        rem_btn.set_tooltip_text(_("remove"))
        rem_btn.connect("clicked", self.on_remove)
        btns.pack_start(add_btn, False, False, 0)
        btns.pack_start(rem_btn, False, False, 0)
        row.pack_start(btns, False, False, 0)

        self.pack_start(row, False, False, 0)
        self.refresh()

    def refresh(self):
        for c in self.listbox.get_children():
            self.listbox.remove(c)
        if not self.folders_ref:
            r = Gtk.ListBoxRow()
            r.add(Gtk.Label(label=_("no_custom_folders"), xalign=0))
            r.set_selectable(False)
            self.listbox.add(r)
        else:
            for f in self.folders_ref:
                r = Gtk.ListBoxRow()
                r.folder_path = f
                r.add(Gtk.Label(label=f, xalign=0))
                self.listbox.add(r)
        self.listbox.show_all()

    def on_add(self, widget):
        dialog = Gtk.FileChooserDialog(
            title=_("choose_folder"),
            transient_for=self.get_toplevel(),
            action=Gtk.FileChooserAction.SELECT_FOLDER,
        )
        dialog.add_buttons(
            _("cancel"), Gtk.ResponseType.CANCEL,
            _("add"), Gtk.ResponseType.OK,
        )
        response = dialog.run()
        path = dialog.get_filename()
        dialog.destroy()
        if response == Gtk.ResponseType.OK and path and path not in self.folders_ref:
            self.folders_ref.append(path)
            self.refresh()

    def on_remove(self, widget):
        row = self.listbox.get_selected_row()
        if row is None or not hasattr(row, "folder_path"):
            return
        self.folders_ref.remove(row.folder_path)
        self.refresh()


class SettingsWindow(Gtk.Dialog):
    def __init__(self, parent, app):
        super().__init__(title=_("settings_title"), transient_for=parent, flags=0)
        self.set_modal(True)
        self.set_default_size(700, 520)
        self.app = app

        self.pending_config = copy.deepcopy(get_full_config())

        self.add_button(_("cancel"), Gtk.ResponseType.CANCEL)
        apply_btn = self.add_button(_("apply"), Gtk.ResponseType.OK)
        apply_btn.get_style_context().add_class("suggested-action")

        content = self.get_content_area()
        content.set_border_width(0)
        content.set_spacing(0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.set_vexpand(True)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(150)

        sidebar = Gtk.StackSidebar()
        sidebar.set_stack(self.stack)
        hbox.pack_start(sidebar, False, False, 0)
        hbox.pack_start(self.stack, True, True, 0)
        content.pack_start(hbox, True, True, 0)

        self.stack.add_titled(self._build_general_page(), "general", _("tab_general"))
        self.stack.add_titled(self._build_folders_page(), "folders", _("tab_folders"))
        self.stack.add_titled(self._build_about_page(), "about", _("tab_about"))

        self.show_all()

    # -- Geral --
    def _build_general_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_border_width(18)

        lang_label = Gtk.Label(xalign=0)
        lang_label.set_markup(f"<b>{GLib.markup_escape_text(_('language_label'))}</b>")
        box.pack_start(lang_label, False, False, 0)

        current_lang = self.pending_config.get("language", "auto")

        radio_auto = Gtk.RadioButton.new_with_label_from_widget(None, _("language_auto"))
        radio_pt = Gtk.RadioButton.new_with_label_from_widget(radio_auto, _("language_pt"))
        radio_en = Gtk.RadioButton.new_with_label_from_widget(radio_auto, _("language_en"))

        radios = {"auto": radio_auto, "pt_BR": radio_pt, "en": radio_en}
        radios.get(current_lang, radio_auto).set_active(True)

        for key, radio in radios.items():
            radio.connect("toggled", self._on_language_toggled, key)
            box.pack_start(radio, False, False, 0)

        hint = Gtk.Label(xalign=0)
        hint.set_markup(
            "<small>{}</small>".format(
                GLib.markup_escape_text(_("language_auto_hint", lang=_("language_pt") if detect_system_language() == "pt_BR" else _("language_en")))
            )
        )
        box.pack_start(hint, False, False, 0)

        return box

    def _on_language_toggled(self, radio, key):
        if radio.get_active():
            self.pending_config["language"] = key

    # -- Pastas --
    def _build_folders_page(self):
        outer = Gtk.ScrolledWindow()
        outer.set_shadow_type(Gtk.ShadowType.NONE)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_border_width(18)

        intro = Gtk.Label(label=_("folders_intro"), xalign=0)
        intro.set_line_wrap(True)
        box.pack_start(intro, False, False, 0)

        categories = [
            ("folders_wallpaper", "wallpaper_folders", DEFAULT_WALLPAPER_DIRS, None),
            ("folders_gtk", "gtk_theme_folders", DEFAULT_GTK_DIRS, None),
            ("folders_icons", "icon_theme_folders", DEFAULT_ICON_DIRS, None),
            ("folders_rofi", "rofi_theme_folders", DEFAULT_ROFI_DIRS, None),
            ("folders_mousepad", "mousepad_style_folders", [], _("folders_mousepad_default_note")),
        ]

        for title_key, config_key, default_dirs, note in categories:
            expander = Gtk.Expander(label=_(title_key))
            expander.set_expanded(False)
            editor = FolderListEditor(self.pending_config[config_key], default_dirs, note)
            expander.add(editor)
            box.pack_start(expander, False, False, 0)

        outer.add(box)
        return outer

    # -- Sobre --
    def _build_about_page(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_border_width(24)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)

        icon = Gtk.Image.new_from_icon_name(APP_ICON_NAME, Gtk.IconSize.DIALOG)
        icon.set_pixel_size(64)
        box.pack_start(icon, False, False, 4)

        title = Gtk.Label()
        title.set_markup(f"<span size='x-large' weight='bold'>{GLib.markup_escape_text(APP_NAME)}</span>")
        box.pack_start(title, False, False, 0)

        version = Gtk.Label(label=_("version_label", version=APP_VERSION))
        box.pack_start(version, False, False, 0)

        desc = Gtk.Label(label=_("about_description"))
        desc.set_line_wrap(True)
        desc.set_justify(Gtk.Justification.CENTER)
        desc.set_max_width_chars(48)
        box.pack_start(desc, False, False, 8)

        dev = Gtk.Label()
        dev.set_markup(
            "<b>{}</b> {}".format(
                GLib.markup_escape_text(_("developer_label") + ":"),
                GLib.markup_escape_text(DEVELOPER),
            )
        )
        box.pack_start(dev, False, False, 0)

        lic = Gtk.Label()
        lic.set_markup(
            "<b>{}</b> {}".format(
                GLib.markup_escape_text(_("license_label") + ":"),
                GLib.markup_escape_text(LICENSE_NAME),
            )
        )
        box.pack_start(lic, False, False, 0)

        link = Gtk.LinkButton.new_with_label(GITHUB_URL, _("view_on_github"))
        link.set_halign(Gtk.Align.CENTER)
        box.pack_start(link, False, False, 8)

        return box

    def run_and_apply(self):
        response = self.run()
        applied = False
        if response == Gtk.ResponseType.OK:
            save_config(self.pending_config)
            i18n.apply_language(self.pending_config.get("language", "auto"))
            applied = True
        self.destroy()
        if applied:
            self.app.new_window()
        return applied


# === Janela principal ===

class MainWindow(Gtk.Window):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_default_size(760, 620)

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title(_("app_title"))
        settings_btn = Gtk.Button.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON)
        settings_btn.set_tooltip_text(_("settings_tooltip"))
        settings_btn.connect("clicked", self.on_open_settings)
        header.pack_end(settings_btn)
        self.set_titlebar(header)

        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        stack.set_transition_duration(200)

        stack.add_titled(CollectionsTab(), "collections", _("tab_collections"))
        stack.add_titled(
            ThemeList(
                get_gtk_themes, get_current_gtk_theme, set_gtk_theme,
                empty_msg_key="empty_gtk",
            ),
            "gtk", _("tab_gtk"),
        )
        stack.add_titled(
            ThemeList(
                get_icon_themes, get_current_icon_theme, set_icon_theme,
                empty_msg_key="empty_icons",
            ),
            "icons", _("tab_icons"),
        )
        stack.add_titled(WallpaperTab(open_settings_cb=self.on_open_settings), "wallpaper", _("tab_wallpaper"))

        stack.add_titled(
            ThemeList(
                get_mousepad_themes, get_current_mousepad_theme, set_mousepad_theme,
                empty_msg_key="empty_mousepad",
            ),
            "mousepad", _("tab_mousepad"),
        )

        stack.add_titled(
            ThemeList(
                get_rofi_themes, get_current_rofi_theme, set_rofi_theme,
                label_fn=lambda p: os.path.basename(p),
                empty_msg_key="empty_rofi",
            ),
            "rofi", _("tab_rofi"),
        )

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(stack)
        switcher.set_halign(Gtk.Align.CENTER)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_border_width(8)
        box.pack_start(switcher, False, False, 6)
        box.pack_start(stack, True, True, 0)
        self.add(box)

    def on_open_settings(self, widget=None):
        dialog = SettingsWindow(self, self.app)
        dialog.run_and_apply()


# === Aplicação ===

class App:
    """Recria a janela principal para aplicar mudanças de idioma e pastas sem reiniciar."""

    def __init__(self):
        self.window = None
        self._destroy_handler_id = None
        self.new_window()

    def new_window(self):
        old_window = self.window
        old_handler_id = self._destroy_handler_id

        self.window = MainWindow(self)
        self._destroy_handler_id = self.window.connect("destroy", self.on_window_destroy)
        self.window.show_all()

        if old_window is not None:
            if old_handler_id is not None:
                old_window.disconnect(old_handler_id)
            old_window.destroy()

    def on_window_destroy(self, *args):
        Gtk.main_quit()


def main():
    load_css()
    App()
    Gtk.main()


i18n = I18N()
_ = i18n.t


if __name__ == "__main__":
    main()