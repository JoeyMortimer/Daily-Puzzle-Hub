#!/usr/bin/env python3
"""Phase 2 refinement installer — run from Daily-Puzzle-Hub repository root."""
from pathlib import Path
import base64, zlib, re, json

ROOT=Path(__file__).resolve().parent
JS_PAYLOAD='eNqtWv1u28gR/z9PsVHSkExI6sOyk9imBCf29QIkcRAnd7iqKrQmVxJriuSRlCXFJnAPUaD/tM/R/9s3uSfpzOySIiX5zmkDBBa5H7MzszO/+WCaT9nph+/Zx7Pv3rw/O2Wv334+u2An70/Zq/OTj6fs9M3Fh7cnP7Ef9tivv/yNcTeb84DF8y9fAsHcYC5Sk4VRxpJ5IFKbPW0+cKMwzZgXTz8k0SQRacocFooFe8dj3Th68GA8D93Mj0Jc8hoJ6BPTM24eMOaP9Yceu71lnp1mPJunDx1HuxaJP/aFp+HEQ8/mYboQicESkc2TkA2GR7BTnsmdYtpkvudM+rbvrWfTeRwHQMg5SRK+sv2UfnXPJimMvnqwx36QiURfOr1sFYtozJYOsJFmiR9OtCdPljY8zXTDsGcgEKwqBw4lLyAFHA5bvvixtsFnORf7YRz5YbZeULBnByKcZFNYtN8vxjYpu0mUpm7gzy7/t/0/z4UIU409ebK5bZtcGviu0FvmnlEXgGfuVKRwPt5coeNEuFm6oWBu06jRVw+KGXndNFKcXVNVQTJ2aM2gNTQZTwR3QOX6ctAZWksYe9Y2nsLbHr618a269dKfTESaOQPblkcP7TRKMl1fmivD6SE1fWVY9Ls0DCAndxd80AtjoxP2+IYWxUZuuSIA+0fpGRhpkqWMg9zRAtbEQCE34fBgPgvpvT3M7ZFZ0DkPBQN7yqaCBTxB1phSI+wBO0+LcxTjRs7wtLRC4lOyYnHAXbBFxmG5WonqKB5RKfl//r6e21vPoYpyxf2lmPhhSIQKAdYkqmKsN4MwxAjpKa+awyJKvEBoRtUYFs4FOQ1YwDUH17q91TTDzqLPcSyS1zwVurE2hOZfBifWn4Y3+/njpp3BcfrC2HCegu51tBBBSre6GBbu6k6dnnZy9ub8s2b7IXiyB8DiTsFNpXHVb3b0Ce5AQoXUQ8oWfjYFYRcoPCh89CbD4zKOc49v5Jm5PLt4BcHbfU071FItZ/qJyc5M9sZk5yxK2GdDEknZ2A8BMQORAZvMT+mMLp6xQ4si9DZ0CHrddigaRYeih9KhlHQ0SOikL0wfDH30I4zAuT5efl1cdUMLNH6QoTKg9JYrzlOQx9hiOOPhJKpzDJaUOuDq8FPjqi4DThtPnuCPOqjndPuDQdtsD81Bx+zC3665NxxKOQaJ6Q5Rko9kp0nVPN1cahVpDRKrPRy48Ae5e6f1Nc5mURTCHXGAtFADtRc4XRNk5oe+lc696Gr+rcQ5KMXZI3EOzIN7ilOxu7pQd3EPwYmHXlrnfArhBbxkDbbcBuSZCYMm7HieTnXyAxpFHf76yz8AgOSq/Ndf/qluXG1OY7jshM+29hcTG6a13iFdqkoLEGia9u3Bes0Q3lrDIpoUMpCiHLW+urrEasaq7FwgIjPQBgFkVmVunEQzBXMb+i5Zy6sXTGS3NK0iZ03RQApNBH/WeFa3D5wzNuPbZphBbEcG21XuYCO5Joc4IwMOSoYhAC4pzKqhAaQl9pgfEp0Om0QQWuCtTq4elGrbUGMSr5DAzu02z3SrbdwdCmZwV4FI6joSyzjZCgfcFj/POeaCFBqOfsd4MWRmkBLOQ08Ak8KrW2Lk8ZWWMrlMQkKxqWZ9yMqWDY/9BG9yysF0SpzGlTXblbxFsYMz4MoQRvXm4NmfrafNYXN9QhTX6FPYh5DHs0gRjuIa2d+0uHQ+iwGCN2LrFRjclYizuwzuyri9fXh1R2JVi4LhfHaJAocbtteWrF4Bp/Cvr+FpAKOeQGY8rWpCiGJtdiVEXOwoovKrKAoED9fBRJ72m4uqUXXjkE7lkPbvHZJWIuxGUnv0IN+uQ15hRjIx6RbKckTeY12NmlYpKqbRInTegcnbEEJ0rCDeimvIDWwwO30CBQhcRMuskVnv9tMPfujgqlpNANVL+hpT/HKqkvCvd08F98CfHKLS1z6e/XB28pZ9+v6MfffmhzP24/nH0wvtUJHqa/guyzvQ7fszqPVO6LVfIRmAW6WO5LZI/ElEWe3oU5lPHHv+NRR/HDhsgPYs3GCB+TR6x4i3W1PyQho9mYIcN3GRXApDInX1qVGONoF2b2TYfwVV6AoVlOJHx6mQV6YOQHVbsEsEeInW+rUBpYLPrYBfisBpnMe4CUCNCjw2BjeUx07szM8CYeSNHplZVa41MQsV3Sj5VWpfizHjQQDjpKecNYF29bpzaSOwmtZJ+ei0xzek7nz30ZfzLIM7UZzhakmnSrs/OpbLGJaqTkO+NGp0QrHMGszjGSf9OI1CdDDNvDJhcVKt06ANeFXKrMCcQXWYVFaMqTJKWgWTUkP0lhfs0nVLtnqjQ61mHnSqG0l4a/ROguKCEqIkPKVhLa+roNe6j9yJSMXXCS539L73PdXZqHKumCivD3iTttgbbaHJW+55IinaHzonNPnqfB7gR2by8q4h8D3fhUAV9Kn0XAh+an0ChKEqvQoMUZHpVMsGeCRPr4acaz/1LwPh+MdhNRqq8qAI7rjVgDwt8DP0XqKHtdloCxmSeTihahqNTRHv4w1B1Yb6Vre/AQUVMNgAIaTXWLujD7jZ6mufzj8QEoLtwsBBX3t1/unT+Ts1Nvr4+f0fsTLKR3npoTvoWkpKtuZU81NLPWvILkqhVuXSShSUUQy6H57hcbG6QRBl2u0pp5ItA7Sq4yaMHsfFDlnDWlDsuo3e55DaCCyChAO5xsKes8yfCZOS8mguA1aRGy+mEDhZCvEembCPmzHIQMawjUlV1pTHpChyeFw1qr622zHJ2aokwElL21TTG9QLIFIawBcSqnRKrXRKRAZEhW95uAIDWVCgVuvnVmC8tDgA/2iM5X1FITnxXIM0FQbuho8Psie0Ez++osF2V3utlr4A1in84Eu9aJOR0+KT0yvn8HXQGZr0uzc0DON+EFT2CRF/auys98ecHMcZaI/E2DtwPc3UHrme2B938cnrikuPnsZdb3zZorGxOx7Lp47gQs623Beei0/iQLTcl0TFFQfeWI55XXdPUX7BL2ms7bnipVZpIeNNB3yVyqZjmQMV+c/1FioOkrbpts2kY7qdoXNtUotSTzpW0qbepNux3HbZl7wLu0hLljq8AXXeCoC2MUl8D9OqQyhZ23kT/nYgnh7RsMzSYcalGZdmLrl7NUkiKJBgQml14P9BPSnFDwmqkM/8GyOUuuvfgqgLgB+JT0AXKvN5wBNq666xinBoN/6QllD8uooyATkEz4RSSnqYiFhAmQr5Ath3brbHiXFUX4l9lZ3L1iq0Uv+LOHR54OrtVusPlNjRQoPtGkSlFtZTg4d7gWjVM74Cx5TG74+gtOGbQOjvHP1/4GdVF3nZIf8aBMVy7jVPvNqXpQlUxN7t7c5vS3VshNVF4UXfcHYAp+xP1L5gVfIpGPuAlYOzq7TcOKGao6mDyv3PtpPJ4gvX7e1NvkmqxNpddDajyhahzU2k1eZTdprwBXv/0yeLXI65fuKS117IpiN223yod9lpRB8C01UIWIC+A/6MTkcfBau3ozbW4hrVYc7oDtSAmvbdGfv3v1TZplqU1DTKES1GRxsJNn4bKPLq29vB0DArvcPNvkG1/E0zpwbOio2MT2R9W0T3ane9ltmuN5QYVUNlzEKrCYLV7kPkGovOy0twjEfewbgz5jKbRFEXxo48uIrbknHUs8Nt/ClCfz1HwBkIwXQfZT3xAjyCRsC1EmpiO72tvrZsa697MweGUQ1ldHHPUHHPtDtu7wSZHPvJTHjFZxA8FftLaDD8GuyHQxpNhXk2hWGAFBkGtGqSkE3TohWMRruemqfCc/AT8wVkHMZmN2MwNJnnp1dFO1GRw06LU3biB7pr2fvGUwB1U0+Kx8r6S/RzzFD4S8gZKMvgLzwhny5boiMoa3kJ+Yt4TmN73lhwWtf19sU+PeHeFzLfkEYAIp9xd3pHyYWyOrL3jfPDu7p9uARuF3/Wt4s76qnfUb1pHSWOvm2OBtmj6+51tEMSGhII+i3SB0mFdKsanMdxFKxwQGo1xVI7loljrMdOj0b1uDBgUzOKR6ZhKQ7+GECwgrQAfSaJrqhYJw7zYsRa+B4oo/F8vxzBE10eQ6xB36oNI/VivNkr+qzEU6nx4upv0HxsQFl9RJ8G8JMA7FDp3dJcDR0pgNxwRLZUSI5oiKC4RI6XwK27wqcVPCVOY+95IVwpDnEjATffKsHJGceQoOD/lUDnMxNgEN2P8EY6j+luWMnS0d1nhfGuIPksXqr3jWyAl5CsU56SrJAyorTws9GJhsmHckP//iI+EnzcHT9fX+EjF1JvcbB5g217H7VAWUCGOUlJWNJ91oFHnLB46E7BSBsz3/MCsA0vghKDh5l1CfEUr3k9pVhod/e63Q68RrAKY5DT6LbV60L4k2kGFtRqFegqFYp4iucVifDOTFji3FbiHvLMvxaW+gCH7YfrCbv2xeJVBGK1WIsdtFrsBRzJlrMghF3TLIsPm83FYmEv9uwomTQ7rVarCftAnxHGC382qfcvL6LgGrCzCLhVDKVvbeie8iueRQ05GZEZLGYrsCvIuIvYR00K8twyljy+kQZdGZAtgGPkqWhiSIS/Kz4/lj5ECnec7ou+hs089X2d4AVzfPouB3L4IXEsexL1j3QwJTm2IRjSN/oyOJBkhIVEawqXGeCFwrnsc1hkcpUVGFs8yF1CWyuShPzBfwFSbTVS'
CSS_PAYLOAD='eNqVll1vmzAUhu/7KyxVm5oKEj4TClKlaq20SVVVrR8XvTPYEK9gI9sk7aL+99kECJB0bRUJYYyP3/Oe55jMTsHl7U9w+/D0dH0Fflw/XN2B7+Dm4v7X4xW4u/99cXN5Bx5dcDo7mqJyaS4JlSZn6w0ioszha5jm+CWCOcmoSSQuRJhgKjGPMliGtlW+RDFMnjPOKorCFeQnplnCEvNJFDOOMA/t8gUIlhMEtrM5obidNDlEpBJhoMKUECFCszomsNWqqIA8I9SUrAzP1DBlSpkgf3FoO2qo45hLTLKlDO2pHyUsZ7xRQOjz5K2XD62KGPMupYwTFKm7BA9T0qmGlFEcrQmSy9Bx1T7NFvX9UPVimPwxDrCTwkbIse95drzYql5vYwS+1agqOcs4FmLzBZPqrDuXnKFB9fidSoz2BEtv0/PS7QKF1nsmtkvPp5CKtZKEsEg2zSpfabeAFtC8zSuaDfHRFxMRjhNJGA3VLlVBa4K88iBcTei5Dt2LCkQB87ynvuOicXjhD3MoKonRpBfBzLFUG4ihvlbJn0pIkr6aiQqphDRq+ssTrPbf0uE6OzrcHR0axq6ax0mAHGSPKqnSij5kcVchFa6FynE87NljqD4ofD/vKRHmiggS5xiMsmo0NjvBIPFhMuTbSR10NkLChHVNR4YeNnLLwZort/Wltj3Y4acRUiT5HUjjPUBcScnoV5pm0euZoD1Y3juxxvTvodUrir2n8nwLZ+tDnLPkOZL4RZo14K0H+3j2w1q7sFAmS1Pj0fBWEHpiW9Y3w5mrtyYRFKXqJ5Wo8ia0R0AxQepW4zhX8ytce211TuszFlaS9axoC5+maf8pKWCGQ20t5EqNclWlcSIZ4NoVg2cxPLEM/ZvazgQoWwzJ1SlRQq5e1OOJcWB1zFQli08t76upTUpgntROgBmYT8Bw2Hahs+tB1/U8Fx3oQbbCPM3ZOlwShDAdGK/nlJ2bvXC1ZNc1fM/wPGPq+5PO1b0vhPeJRu862w0ctNfZPTS8Dg1al9QU2ikkxni4Xo1Hv6lGpVZFDtIkxf/7wMx7B9rOShRjmFoHZQCxykbwb4VpUe05WQsZgOvOvLejmKHXKYL8GQz+gxij57uv5icb+O3oH2RyMuw='

def decode(p):
    return zlib.decompress(base64.b64decode(p)).decode('utf-8')

def only(text, needle, label):
    n=text.count(needle)
    if n!=1:raise SystemExit(f'Expected exactly one {label}, found {n}; no changes written')

def main():
    paths={name:ROOT/name for name in ('app.js','style.css','index.html')}
    for name,p in paths.items():
        if not p.is_file():raise SystemExit(f'Missing {name}; run in repository root')
    js=paths['app.js'].read_text(encoding='utf-8')
    css=paths['style.css'].read_text(encoding='utf-8')
    html=paths['index.html'].read_text(encoding='utf-8')
    if 'DPH REFINED CLUES AND BOARD DISPLAY V3' in js:
        print('Already installed; nothing changed')
        return
    only(js,'function cardHTML(g)','cardHTML marker')
    only(js,'clueLevels.clear();','date change marker')
    anchor="const cb=event.target.closest('[data-clue]');"
    only(js,anchor,'clue click marker')
    js=js.replace('function cardHTML(g)',decode(JS_PAYLOAD)+'\nfunction cardHTML(g)',1)
    js=js.replace('clueLevels.clear();','clueLevels.clear();dphProgress.clear();',1)
    handler="const pb=event.target.closest('[data-dph-progress]');if(pb){const id=pb.dataset.dphProgress;if(pb.dataset.progressAction==='reset')dphProgress.delete(id);else dphProgress.set(id,(dphProgress.get(id)||0)+1);render();return;}"
    js=js.replace(anchor,handler+anchor,1)
    css+='\n'+decode(CSS_PAYLOAD)+'\n'
    for file in ('app.js','style.css'):
        patt=r'((?:src|href)=["\'])([^"\']*'+re.escape(file)+r')(?:\?[^"\']*)?(["\'])'
        html,n=re.subn(patt,lambda m:m.group(1)+m.group(2)+'?v=phase2-clue-board-v3'+m.group(3),html)
        if n!=1:raise SystemExit(f'Expected one asset reference to {file}; found {n}. No changes written.')
    writes={paths['app.js']:js,paths['style.css']:css,paths['index.html']:html}
    update=ROOT/'scripts'/'update.py'
    if update.exists():
        src=update.read_text(encoding='utf-8')
        if 'def dph_extract_pinpoint_clues(' not in src:
            only(src,'def update_linkedin(day,out):','LinkedIn updater function')
            helper='''\ndef dph_extract_pinpoint_clues(text):
    """Extract exactly five numbered clues from a dated Pinpoint page."""
    if not text or 'Today' not in text:return None
    pattern=r'\\bClue\\s*#\\s*([1-5])\\b.*?\\bHide\\b\\s*(.+?)(?=\\b[1-5]\\s+Reveal\\s+Clue\\s*#|\\bGive me a hint\\b|\\bToday.s Pinpoint Answer\\b|$)'
    matches=re.findall(pattern,text,flags=re.I|re.S)
    values={}
    for num,value in matches:
        candidate=' '.join(value.split()).strip(' .')
        if 2<=len(candidate)<=60 and num not in values:values[num]=candidate
    return [values[str(n)] for n in range(1,6)] if len(values)==5 else None

'''
            src=src.replace('def update_linkedin(day,out):',helper+'def update_linkedin(day,out):',1)
            anchor="out['games'][game]={'status':'verified','number':f'#{n}','hint':[],'answer':result,'source':url}"
            only(src,anchor,'verified LinkedIn assignment')
            src=src.replace(anchor,anchor+"\n            if game=='pinpoint':\n                clues=dph_extract_pinpoint_clues(txt)\n                if clues:out['games'][game]['clues']=clues",1)
            writes[update]=src
    board=ROOT/'scripts'/'phase2_boards.py'
    if board.exists():
        s=board.read_text(encoding='utf-8')
        writes[board]=s.replace('for x in clues[:4]','for x in clues[:5]')
    pin=['Body','Greeting','Address','Signature','P.S. (after the main text)']
    cross=['Something a broken pipe or tap may have.','What a bird eats with.','An animal whose name also means to tolerate.','A type of wild pig.','To fly upward, high and majestically.']
    curated=ROOT/'data'/'boards'/'2026-11-02.json'
    if curated.exists():
        obj=json.loads(curated.read_text(encoding='utf-8'))
        obj.setdefault('clues',{})['pinpoint']=pin
        obj['clues']['crossclimb']=cross
        writes[curated]=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
    daily=ROOT/'data'/'2026-11-02.json'
    if daily.exists():
        obj=json.loads(daily.read_text(encoding='utf-8'))
        if obj.get('date')=='2026-11-02':
            games=obj.get('games',{})
            for game,clues in (('pinpoint',pin),('crossclimb',cross)):
                if games.get(game,{}).get('status')=='verified':games[game]['clues']=clues
            writes[daily]=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
    for path,contents in writes.items():
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(contents,encoding='utf-8')
        print('Updated:',path.relative_to(ROOT))
    print('Phase 2 refinements applied; test with node --check app.js and scripts/validate.py')

if __name__=='__main__':main()
