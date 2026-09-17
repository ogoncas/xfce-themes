# XFCE Theme Manager

Gerenciador gráfico de temas para XFCE: GTK, ícones, wallpaper, Rofi e Mousepad — com suporte a coleções (perfis) que aplicam tudo de uma vez.

## Recursos

- Lista e aplica temas **GTK**, **de ícones**, **Rofi** e **Mousepad**
- Navega e aplica **wallpapers** por pastas configuráveis, com miniaturas
- Salva **coleções**: combinações de temas aplicadas com um clique
- Busca/filtro em cada lista de temas

## Dependências

- Python 3
- GTK 3 + PyGObject (`python3-gi`)
- `xfconf-query` (XFCE)
- `gsettings` (opcional, para tema do Mousepad)

## Uso

```bash
python3 app.py
```

## Configuração

Salva em `~/.config/xfce-theme-manager/config.json` (pastas de wallpaper e coleções).

## Licença

MIT
