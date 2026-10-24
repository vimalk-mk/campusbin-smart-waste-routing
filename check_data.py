"""Run before you push:  python check_data.py   (checks that the data files are valid)"""
import gzip, json, os, xml.etree.ElementTree as ET
B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
ok = True
for name, op in (("roads.json", open), ("roads.json.gz", gzip.open)):
    p = os.path.join(B, name)
    try:
        c = json.load(op(p, "rt", encoding="utf-8")); print(f"OK   {name}: {len(c['data']['elements'])} map elements, {os.path.getsize(p)//1024} KB")
    except Exception as e:
        ok = False; print(f"FAIL {name}: {e}")
try:
    n = sum(1 for e in ET.parse(os.path.join(B, "campus.kml")).getroot().iter() if e.tag.endswith("Placemark")); print(f"OK   campus.kml: {n} placemarks")
except Exception as e:
    ok = False; print("FAIL campus.kml:", e)
print("ALL GOOD" if ok else "FIX THE FILES MARKED FAIL (upload them from the zip, do not paste)")
