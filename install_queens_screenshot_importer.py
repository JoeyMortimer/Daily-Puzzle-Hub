#!/usr/bin/env python3
"""One-off installer for Daily Puzzle Hub's Queens screenshot importer."""
from pathlib import Path
import base64
import zlib

ROOT=Path(__file__).resolve().parent
APP=ROOT/'app.js'
SOLVER=ROOT/'scripts'/'queens_solver.py'
TARGET=ROOT/'scripts'/'import_queens_screenshot.py'
if not SOLVER.exists():
    raise SystemExit('Existing scripts/queens_solver.py is missing; install the verified Queens solver first.')
if not APP.exists():
    raise SystemExit('app.js is missing; run this installer from your repository root.')
content=APP.read_text(encoding='utf8')
old="if(typeof key==='string')return DPH_REGION_COLOURS[key.toLowerCase().trim()]||'#e3e9e5';"
new="if(typeof key==='string')return /^#[0-9a-f]{6}$/i.test(key)?key:(DPH_REGION_COLOURS[key.toLowerCase().trim()]||'#e3e9e5');"
if new in content:
    print('Exact Queens hex colours already supported.')
elif content.count(old)==1:
    APP.write_text(content.replace(old,new,1),encoding='utf8')
    print('Updated app.js to display the original Queens region colours.')
else:
    raise SystemExit('Could not locate the Queens colour function in app.js; no files were changed. Please share the relevant function.')
script=zlib.decompress(base64.b85decode("""c-o~IYj4xY_IrNCuzaxHI!=>r0R_AgOW|ImWnl}f?kYFRPV7lC)E;|h>?Wb=f4}F<!;iECp<4-J&*Qw`e*9=uD>+(nF=FC|l>2H^i1WcuKmGJJFAG@_Do7#unhTndKWfH=B1w@IwPfjVSx}i0l}KFP6cyp3D##_}*`9o;zkbaa`FFjH27_0!C>5cSk(6b8$t0~9oMF2%;|Z^(gp#c+#F|)$o1)HABG?U+WXXu)850#;DC=d$)rO_f;EMfIbIBC>z_YB_68~>QI~nGr<Ry@zDw<{RjN5+)5&5j(bhTlml*Jd8RGuQmRt$iAURG-Kk7jP6iVUzu<(>d5@WfYppsp4i_6cm(6$d0swkm)dMQ^xRM<}iVxAKzfl1jw}D_P_ysti!U6-DfU6bQGwDTtxsIcv7y-NE^y3gMn}T5ZgY5}rVS?!pJ$u+Or&3XE4=RXkD6%3ciymE2DU1pYLn4{v{SP~PTr%|i2YDd~2=b_pwS9k*XgSx7<^Xe%-ICFP2dk9$?I{Pm7kzGroibEQBYQ*uldUSJ3SaD&0s`}dzntoiU4ixud3u?QkiD{8?HA`m5LUd_hy0q_tZ`w@U+vhvSDU{v}V!iacQjb0EOFxu0rV_CobIG?Ym5MbsjF0|P{Xg3jgYxzZ6vo2$?ueelI)RVv<Wh;_`x+Xpi$uh90Syf9xRGs_&ZnzIlP9_8_j_g9R2YHgOyfnuH3&Hs0Lead;nDTiZ5@BI&L$U!G^E^`gE7MDS1-cSG?gZoo5hvqk1esqde>;SwU%=#cX8YtUI(u?qAhkmIlV&y367yHyui9x7@NvQwx!vCFZZ~%kL8m7bUvJQJsVr&`8j3{yQ)491t`1a!JaKiqDIi>I*|G#H1QBV3kI6fhatuL0Fcrvp1uhAsmIXY5Ppw6PK_D*_M4trQEJQ-KAaV-m){>_g7feMOT(Mdy2Df73N8_hqG<gz6=NDo01pYn!IgFm28?*__G8NC}#)tr$M43w}*35TObz8~9TliP<9YZ)E`8BKbo9}D6562;p@B7K=E;!kaL=c2pAse?LPeJD!+z5gm%r5F3qINvt!oIUG?_JXzMYJrLNd2k?8}SiO8!4h(3)(Md*K-XE-PUpt1bXGV<@DT<W$jdhx0bjDO_vK}kIJ_O*;?ac@`g%KxT=QQ8vrP;IL-K1ieWMYR2U^#N|t+wm7s1AjHZ!X4|7I^)#YRIS#TgL*T~6|Cf93iV<ykkido~La>*-6<-VJ!3}cbiHX0S^$;c(ArN7DwT7{PO+1We@T3cAOVi<>Al_y|v97A}F&f^%rX8Sm!`7))XoT846ua{vGwDx03=;+#ds5#s~e(=(Z@!475@b3Aj_l9jD{8SroB}lrEkwCsTT=6BiCgR{C!3?s-+-6nhe6S;;z5%s@YUp!jK_L&UMUJ7n>qZ^XJvr-0PMZvzoXro9iJ-OP6*&6FfpZ|WnOa%*g}`?)O3=aSD&l(DD8VoWMt|UE8kysl@A{jD-WlJ`-HEcNIfzs~n%-KIxJDAqmEe1NdZlGglB`x3=%6B6K{dtF=Oo#%<XT5c476S4)Fp~Ob@q!nqnsrjFJ1>DsGt0Ga2T-8t!H;AoOk&!5|2CDoE}6K<2jas-riC&dflvaKscGl8hY5h3n-D$&f(xuEKbCc?BgV+sc+@gCXh>Q-Rm04Mi482hHL?m#l#*RI+#cxZU9LxVl4NapkY-35=z<5rV*Jk8ABmjfqy1dgvlJNOZ5mh_%pi16mY9=Pm_)GpIn??+jtu4Rg^swb*_tIU&9XWOmHo>;1r%0eSu`>8&I<jj+s0Wr^$SNKMw`>vzAe8Ni$YKgu1oRz=Ws7d+eP$EGzF;M^XPKn4V2`cb<lH(}_2D$H3<%0U^bA-E4q#hZd77PtbZ7Ccr2k4_H?aF=|{d=ywGXI)?n^2Tjya`+Qks+RtI#5vs3r{0UN-tYX1-m_1#b>`CChn9$%5&P>k1VdB_eYCTI6bE_fWHH%e|7O^hk{h8jHw->e>Fg|_az|q4b#?`1Sz(rS%yKW$pa7Ggc<U<vZ1R)dw_BTw1WAl4D4h~|7^_#O7v6L@_u6p1(N$j&>5BX~u)EmA=7-)mnqGe+GV5NaO5lvIy-Uyy+23_QHs~!13@f%|l+BFC@gU}#wV;pVu0&l&@iN=5k!S6Mk@5IZMcV%+ctwD5$1t@X^m7vgBE+Q|}FEzS4R-<UNLSg>Xk+f-SbuEf9!&qx6*$rn~ziY@Lq(ywGHo=iD>P;c4L%V)Xu<nkZPE3r;V|_9bfWW)@*RNjaixWH%nx7!_z>F$pBUlOzS=_W{5&j3&eei#lrn_(-CkCrLY1#t!_q7l#ZXKhyhx9;$mQ(;2vW*Xr!riHcv_CcULmQXHR%|nbHSe1{dR-i!5n~j9WH?4Nk77JKH5jmJ?*q4Ry~h*%=Y?CIR-5?z9_*wC8z2MtZ^7=<{C(I!w-}CF=%+_0*N}&kzI29@AK{~i3oxBN%!$L~goTek#upklV2EQtaX$=bT#zbxsWiIrGk_2OS#0{%K0zbnP@bJ9=NDe^FtkbsY6D>8$Q^-jyg$5<ieyvB*voUzGSKx1Y-H&T^R+KpkIgBh1Z(4Z{32sFh>2dxb&dJ*gI@PjW;%BW8}VY17Rh1}bnaoOTTpw&_c(f<7gqa{#W<x1H!Le-?_=9aU|=bsoUV#)ck5<kZUBItsCNX<aEN7)7fLhMO5;zmW)|6B@Hc$-Zg_cl90C*(OC}FtXwsqCv%r4i;+myzg(Ivqb2@wXD120r*TMt2(>kl-rxvmq1Ed^|D~!p$JuoFtgX4fvgr0@+UTcPCrbRPhdp8dE<8TLNVx}OJtZFFS+J5dhc+>IRLvSsMtuW&uR9Btj@PI|@h&&A^;m_fd@I1T-$KR0&XgL9?IAM63sw&lVG}>;pdxEUFh>{{7t!d8Ov}kl3sLelJvvctEq|7r=+_|U}YcDuXCO8cEm7YY#o~jDT78O{B6Us-}x5HPkV=zVP=307DML3Q;PPAlYMw6phUg{~KIf%8o?nX_0u4kXAA;IDS;3~Gr^bev_wsgYdy71<zz$pN&eB6z67wVb`tOPDz#Cijb_eDIOw9(CiW~PrY=1p>}6_y|iR&CKRE_AUpo;0xs!hucTMTxx%!q%$+Xj$CgWKw7Kh6sHE&A7#k14@E9G;T*R*PS6tb0tz`hI7Zz>l9daYT1@S(|fFFuW_t&yvMs&Y#|j;Z2hd$3_Q=y<}c2gmvQ%HGXF(08tEj`ET6mO4Z~Sq2hcCEz1M+f*Usk$qq2t>NDAmJpgyahW#i(8W;{hmMO`VLGNX$wM_M<A7QAnGYdR@c$i@8u)xE(f&cYju2|ABvSaiRUF@1~uGN58Jx^8z|RqGCbw8w`HZD+=eCG8hox=!0s&Dec_XvfL5o0j2N^|p`Uj`#`HNr_fu5=7*c9v-yu(zVB!_T%OrsH|tS2K|BAI-24cTJ0`qYx&Ndj@{0G#BR;)#&RKS=5(kS9MjPOr@w1xLHlNmOgxGmT@Q5(-w>}I%HJY@JCYV)X1~AxgkM{dO)L9b_jKo^R!U^uGrI7Mg_!&qdcJ+v(>gEc-}tZSHLu;R55_pBo-@<l?&s$7(+yD6OIdIO>37G!)wpP)>~<fqS;J3RAQSI_gEo*FM}SkE2x>rFUj0R`KL0+&V;hX+$p)Ja=)JBCYzr>L0tq@2CTl^q9Abz`Ox<CY86oIblX(_c=EeAxXXIgC@<!eRnW;-?=U$}Ki}Hh`4)@M{wj#Hkn|IF%QhEOqjsgP9=0i@0&=?7cvVx|{?~))HO&7Y{#X%Fqvvus%)#{lG>CW5GV$hAuU7dCsvD@5wgbQ1Jp)-OGl+KTYW{7-mlC08SKuMFRNg?pN%nFBFMn5P6^L^Bm6+QN54UzNs*0bf}v}gM^Dtc3Gex9{IZ|V%uv&E9RWnS(MRUK_5l=?<sTB2#4mrkO3VkWA15`spcyk1b1a2~&*nPR~y`d4@;<gTrMeEH|=OR(_{y6*nU`~CHQJ~dx2zxiR<)avB6k;ok^LA=fOI6(k?E*1icy~QGqy~P4slf}X_x-)&s;D0Vy9V-"""))
TARGET.parent.mkdir(parents=True,exist_ok=True)
if TARGET.exists() and TARGET.read_bytes()!=script:
    raise SystemExit(f'Existing {TARGET} differs; not overwriting it.')
TARGET.write_bytes(script)
print('Installed:',TARGET)
print('Next: python -m pip install pillow')
