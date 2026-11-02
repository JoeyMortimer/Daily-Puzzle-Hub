"""Embed the newest checked day for a working offline homepage and date fallback."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
index=ROOT/'index.html'
data_files=sorted((ROOT/'data').glob('????-??-??.json'))
if data_files:
    data=json.loads(data_files[-1].read_text(encoding='utf-8'))
    literal=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    # The source template has one marker; rerunning must replace previous content too.
    original=index.read_text(encoding='utf-8')
    import re
    new=re.sub(r'(<script id="embedded-data" type="application/json">).*?(</script>)',lambda m:m.group(1)+literal+m.group(2),original,flags=re.S)
    index.write_text(new,encoding='utf-8')
    print('Embedded',data['date'])
