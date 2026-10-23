"""Convierte los CSV crudos en JSON livianos para la página.
Uso:  python build_data.py
Lee  data/estacion_sn_1046.csv (nivel) y data/estacion_sp_161.csv (pluviómetro)
Escribe data/nivel.json, data/diario.json y data/lluvia.json
"""
import pandas as pd, json

def minutos(s):  # hora local -> minutos desde 1970 (sin zona horaria)
    return (s.astype('datetime64[s]').astype('int64') // 60).tolist()

# ---- Sensor de nivel (cada minuto) -> promedio y máximo cada 10 min
n = pd.read_csv('data/estacion_sn_1046.csv', parse_dates=['fecha'])
n = n[(n.calidad == 'Buena') & (n.nivel >= 0)].sort_values('fecha')  # -999 = lectura inválida
g = n.set_index('fecha').nivel.resample('10min').agg(['mean', 'max']).dropna()
json.dump({'t': minutos(g.index.values), 'avg': g['mean'].round(1).tolist(),
           'max': g['max'].astype(int).tolist()}, open('data/nivel.json', 'w'),
          separators=(',', ':'))

# ---- Resumen diario del sensor de nivel (mín/prom/máx, hora del máx, cobertura, batería, señal)
n['d'] = n.fecha.dt.strftime('%Y-%m-%d')
n['slot'] = n.fecha.dt.floor('10min')
gd = n.groupby('d')
dn = pd.DataFrame({'nmin': gd.nivel.min(), 'navg': gd.nivel.mean().round(1), 'nmax': gd.nivel.max(),
                   'ncov': (n.groupby('d').slot.nunique() / 144 * 100).round(0),
                   'nbat': gd.bateria.mean().round(2), 'nrssi': gd.rssi.mean().round(1),
                   'nreg': gd.size()})
dn['nhm'] = n.loc[gd.nivel.idxmax()].set_index('d').fecha.dt.strftime('%H:%M')
# ---- Pluviómetro: se descartan "Error sistematico"; solo se guardan eventos con lluvia
pa = pd.read_csv('data/estacion_sp_161.csv', parse_dates=['fecha'])
pa['d'] = pa.fecha.dt.strftime('%Y-%m-%d')
pa['slot'] = pa.fecha.dt.floor('10min')
p = pa[pa.calidad == 'Buena'].sort_values('fecha')
gp = pa.groupby('d')
dp = pd.DataFrame({'rcov': (gp.slot.nunique() / 144 * 100).round(0), 'rbat': gp.bateria.mean().round(2),
                   'rssi': gp.rssi.mean().round(1), 'rreg': gp.size()})
dp['rmm'] = p.groupby('d').muestra.sum().round(1)
dp['rmm'] = dp.rmm.where(dp.rcov.notna())
ev = p[p.muestra > 0]
json.dump({'t': minutos(ev.fecha.values), 'mm': ev.muestra.round(1).tolist(),
           'ini': p.fecha.min().strftime('%Y-%m-%d'), 'fin': p.fecha.max().strftime('%Y-%m-%d')},
          open('data/lluvia.json', 'w'), separators=(',', ':'))
dias = pd.date_range(dn.index.min(), dn.index.max()).strftime('%Y-%m-%d')
df = pd.DataFrame(index=dias).join(dn).join(dp).rename(columns={'rssi':'rrssi'})
df['rmm'] = df.rmm.fillna(0).where(df.rcov.notna())
cols = ['nmin','navg','nmax','nhm','ncov','nbat','nrssi','nreg','rmm','rcov','rbat','rrssi','rreg']
out = {'d': list(dias)}
for c in cols:
    out[c] = [None if (isinstance(v, float) and v != v) else (v if c == 'nhm' else (int(v) if float(v).is_integer() else float(v))) for v in df[c].tolist()]
json.dump(out, open('data/diario.json', 'w'), separators=(',', ':'))
print('listo', len(dias), 'días')
