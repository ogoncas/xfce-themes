# XFCE Theme Manager

Gerenciador gráfico de temas para XFCE: GTK, ícones, wallpaper, Rofi e Mousepad — com suporte a coleções (perfis) que aplicam tudo de uma vez.

<img width="1920" height="1200" alt="Captura de tela_2026-09-18_21-08-45" src="https://github.com/user-attachments/assets/15686535-1657-482c-91aa-d0f9f00ea7c8" />

## Recursos

- Lista e aplica temas **GTK**, **de ícones**, **Rofi** e **Mousepad**
- Navega e aplica **wallpapers** com miniaturas e pré-visualização
- Salva **coleções**: combinações de temas que podem ser editadas e aplicadas com um clique
- Busca/filtro em cada lista de temas
- **Pastas extras** para cada tipo de tema, além das padrões do sistema
- Interface em **Português (Brasil)** e **English**, com detecção automática do idioma do sistema

## Dependências

- Python 3
- GTK 3 + PyGObject (`python3-gi`)
- `xfconf-query` (XFCE)
- `xfdesktop` em execução (necessário para aplicar wallpapers)
- `gsettings` (opcional, para o tema do Mousepad)

## Uso

```bash
python3 app.py
```

**Configurações**:

- **Geral:** idioma (automático, Português ou English)
- **Pastas:** pastas extras de wallpaper, GTK, ícones, Rofi e Mousepad
- **Sobre:** versão, desenvolvedor e licença

## Onde os temas são buscados e aplicados

| Tipo | Pastas padrão | Aplicado via |
|------|---------------|--------------|
| GTK | `~/.themes`, `~/.local/share/themes`, `/usr/share/themes` | `xfconf-query` (xsettings e xfwm4) |
| Ícones | `~/.icons`, `~/.local/share/icons`, `/usr/share/icons` | `xfconf-query` (xsettings) |
| Wallpaper | `/usr/share/backgrounds`, `~/Pictures` | `xfconf-query` (xfce4-desktop) |
| Rofi | `~/.config/rofi/themes`, `~/.local/share/rofi/themes`, `/usr/share/rofi/themes` | linha `@theme` em `~/.config/rofi/config.rasi` |
| Mousepad | estilos do gtksourceview em `/usr/share` e `~/.local/share` | `gsettings` e `~/.config/Mousepad/mousepadrc` |

## Configuração

Salva em `~/.config/xfce-theme-manager/config.json`: idioma, pastas extras e coleções.

## Licença

[MIT](LICENSE)
