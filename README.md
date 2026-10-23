# Monitoreo Quebrada Cañaveral · Briceño

Página estática con gráficas de nivel y pluviómetro (por día, por mes, continuidad del monitoreo, mapas de calor y estado de equipos) para publicar con **GitHub Pages**.

## Publicar
1. Sube esta carpeta a un repositorio de GitHub (`index.html`, `build_data.py`, `data/`).
2. Settings → Pages → Source: *Deploy from a branch* → `main` / root.
3. La página queda en `https://TU_USUARIO.github.io/TU_REPO/`.

## Actualizar datos
Pon los CSV nuevos (si los quieres re-procesar) en `data/` (`estacion_sn_1046.csv`, `estacion_sp_161.csv`) y ejecuta:
```
pip install pandas
python build_data.py
```
Haz commit de `data/*.json`. (Los CSV crudos pesan ~24 MB; no hace falta subirlos, agrégalos a `.gitignore`.)

## Ajustes
En `index.html`, bloque `CFG`: título, umbrales de alerta y perfil del cauce.
