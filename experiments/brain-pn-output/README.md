# 出力：高活動PNへの到来監査とeLN出力停止

**言えること：この固定模型では、正符号ALLN→PNのOFF到来停止により全686 PN平均が大幅に低下した。既知正符号だけでは約12 Hz、unclearも含めると約3.7 Hzだった。**

**言えないこと：全PNが沈黙した、約3.7 Hzはすべて嗅覚の残留である、eLN出力だけで残留が生じる十分性や生体の唯一の維持源を証明した。**

主指標は全686 ALPNのOFF19.9〜20秒平均。これは歴史的な回路診断値で、DM1／VA2の匂い読み出しには使わない。

| OFF停止条件 | 辺数 | PN OFF20秒平均Hz | 3 Hz以下／8組 |
|---|---:|---:|---:|
| control | 0 | 132.84〜135.01 | 0 |
| known_positive | 11,069 | 11.69〜11.94 | 0 |
| unclear_only | 1,769 | 104.74〜106.01 | 0 |
| all_positive | 12,838 | 3.66〜3.89 | 0 |
| GABA_only | 6,325 | 193.29〜194.50 | 0 |

`all_positive` 後も25〜27／686細胞が発火し、最大個別値は300〜330 Hz。平均の低下を全細胞の沈黙としない。3 Hz以下の事前参考条件には未達だった。

停止対象は、事前に固定した全ALPNへ到来するALLN入力。known_positiveは模型の正符号かつnt≠unclear（ACh 10,944＋octopamine 125）。unclear_onlyは正符号unclearのみ。all_positiveはその和。GABA_onlyは負符号GABAのみ。負符号glutamate 1,287辺は常に通す。生体の興奮性やoctopamineの速いシナプス作用を実証する区分ではない。

先に8対照の実到来を監査した。OFF19〜20秒に100 Hz以上だったPNへの正のシナプス増分のうち、eLN由来は約81.6%、PN由来は約14.1%、残留10 ORN由来は約0.13%。分母は正の増分総和であり、膜電位や発火の因果的寄与率ではない。負入力は別に計上した。高活動PNの集合は記述用で、停止先の選別には使っていない。詳細は [audit-report.json](results/audit-report.json)。

全40試行で入力の再構成と元バッファをfloat単位で照合し、ON到来停止0、境界、実発信→到来件数、個別PN累積値を独立確認した。正負入力を混ぜて同じ効果と扱わない。

![停止比較](results/PN-OFF20-comparison.png)

## 条件と保存

条件の正本は [protocol.json](protocol.json)、対象集団は [cohorts.json](cohorts.json)、判定表は [decision-table.csv](decision-table.csv)。各停止条件は元回路から開始する。

4seed `2026091701, 2026091711, 2026091721, 2026091731` ×入力利得1.0／0.5。DM1／VA2 ORN 157細胞へ60 Hz×利得。無入力0.5秒→ON1秒→OFF20秒→再ON1秒→再OFF2秒。dt=0.5 ms、遅延2 ms、回路gain=0.65、KC gain=0.25、単一worker、50 ms endTick。その他は固定上流LifConfig。

OFFの積分直前に、その到来時刻で停止対象だけを除いた入力へ差し替える。元のfloat加算順を保ち、遅延バッファの非零件数を整合させる。ON末尾発信→OFF到来は止め、OFF末尾発信→再ON到来は通す。膜電位・到来済みシナプス状態のリセットは行わない。

[結果CSV](results/summary.csv)・[指標JSON](results/report.json)は元の測定から保存した値。[コピー同一性](byte-copy-manifest.json)、[省略した生記録の参照ハッシュ](reference-hashes.json)、各試行の検証JSONを併記する。生の全ステップは配布せず、再実行で生成してSHA256を照合する。記録ハッシュ自体は生理的妥当性の証明ではない。

## 再実行

```sh
.venv/bin/python experiment.py --experiment brain-pn-output \
  --seed 2026091701 --gain 1 --gate all_positive \
  --jdk /path/to/jdk-25/bin --out runs/pn-output-seed1
```

上表の5条件×8組＝40試行。1呼出しで指定1条件を実行し、元の生記録のハッシュを照合する。入口のORN停止は重ねない。
