# ハエ・コネクトーム模型の残留活動：再現実験ノート

**言ってよいこと：この固定刺激条件では、DM1／VA2の4 PN読み出し＋OFF到来だけの既知正符号eLN→PN停止で、ON応答が保たれ、OFF指標は個別4細胞とも0になり、再ONで応答が戻った。対応する8組すべてで確認した。**

**言ってはいけないこと：生体の嗅覚を再現・完成した、全PNが沈黙した、神経自身が匂いの消失を判断した、別の匂い・強度・時系列でも成立する、特定経路の十分性や唯一の残留源を証明した。**

対象は [fly-brain-minecraft](https://github.com/blendi-remade/fly-brain-minecraft/tree/6cfa30175003ef25da68a237d5eda958f8047b82) の固定コネクトーム由来LIF模型。論文ではなく、同じ模型を回す開発者と、後から読む自分・共同作業者・エージェントのための実験記録である。commit・データハッシュは [upstream.json](upstream.json)。ゲーム本体を起動せずJavaハーネスで測定する。

## 使い方：模型を使う開発者へ

1. **読む細胞**：DM1_lPN `10176`・`10208`、VA2_adPN `10390`・`10561`。平均と個別4細胞を併記する。
2. **OFF規則**：外部の刺激／センサー状態がOFFのときだけ、到来する既知正符号ALLN→ALPN入力を止める。神経の残留出力を見てOFFを決めない。ONでは全入力を通す。到来済みの状態や膜電位をリセットしない。
3. **停止先は全686 ALPN**：読み出し4 PNに停止先も絞った実験ではない。11,069辺＝ACh 10,944＋octopamine 125。unclearと負入力は通す。「既知」は模型の伝達物質ラベルがunclear以外という意味で、生体での興奮性の実証ではない。
4. **匂いの読み出しに使わない平均**：全686 ALPN平均。型の異なる集団を含み、この4 PNの残留とも、全細胞の沈黙とも同一視できない。過去の全回路診断値としての利用は保持する。

この約束を [cohorts.json](experiments/brain-four-pn-readout/cohorts.json) と [protocol.json](experiments/brain-four-pn-readout/protocol.json) にも収録した。身体センサーのON／OFFをゲート入力にする場合も同じ契約だが、今回の実測入力は固定スケジュールであり、身体センサーの実動作を検証した結果ではない。

## 索引：3つの実験記録

| 実験 | 問いと結果 | 読み出し |
|---|---|---|
| [brain-orn-entry](experiments/brain-orn-entry/README.md) | OFF中のPN／LN→残留10 ORNを止めると9細胞は静まるが、PN高活動は維持された | 固定10 ORNと全686 PNの診断値 |
| [brain-pn-output](experiments/brain-pn-output/README.md) | 正符号eLN→PNのOFF到来停止で全PN平均は大幅低下。ただし全PN沈黙ではない | 全686 PNの診断値・個別最大値 |
| [brain-four-pn-readout](experiments/brain-four-pn-readout/README.md) | 固定4 PNでON保持・OFF静穏・再ON回復・再OFF静穏が揃うか | DM1／VA2の4 PN |

入口と出力は元回路から別々に介入した。ORN停止をPN停止へ重ねていない。これらを独立した二つの生物学的ループの証明とは扱わない。

## 記録の3層

- **主張**：各READMEの冒頭。言えること・言えないことを固定。
- **条件と判断**：`protocol.json`、`cohorts.json`、`decision-table.csv`。細胞ID、刺激、時間窓、停止規則、seed、ハッシュ、操作的な判定閾値。
- **結果と同一性**：`results/summary.csv`・`report.json`等、`byte-copy-manifest.json`、`reference-hashes.json`、`MANIFEST.sha256`。全ステップの生記録は同梱せず、再実行して参照SHA256と照合する。

`byte-copy-manifest.json` は過去の凍結記録からバイトを変えずに収録したファイル、`reference-hashes.json` は省略した生記録の照合先、`MANIFEST.sha256` はこの配布物の整合性を示す。**ハッシュがあることと、手元で再実行して一致したことは区別する。** 公開用protocolは元条件を明示的な契約へ整理したもので、元protocolのバイトコピーとは表記しない。

## 再現する

Java 25、Python 3、NumPyを使う。初回だけ上流の固定commitと依存を用意する。接続データは上流から取得し、ハッシュで確認する。

```sh
git clone https://github.com/blendi-remade/fly-brain-minecraft.git upstream
git -C upstream checkout --detach 6cfa30175003ef25da68a237d5eda958f8047b82
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python verify.py
```

4 PN実験の一組（停止条件と新しい対照をともに再実行）：

```sh
.venv/bin/python experiment.py --seed 2026091701 --gain 1 --gate known_positive \
  --jdk /path/to/jdk-25/bin --out runs/four-pn-seed1-gain1
```

Pythonからは `from experiment import run`、`run(2026091701, 1.0, "known_positive")`。`JAVA_HOME`かPATHのJDKを使い、固有の `runs/` フォルダへ保存する。返り値は指標とバイト一致の検証JSON。既存出力先は拒否する。出力には生記録も生成されるが、`runs/` はGit対象外。

全8組は同じ呼出しを4seed×利得1.0／0.5で繰り返す。各呼出しは対照と停止条件を実行するため計16試行となる。元の試験も単一worker、同時実行最大2試行。再現用CLIは1試行ずつ順番に実行する。所要時間・一時ファイル量は実行環境に依存する。

過去2実験の実行例・停止モードは各READMEに記載。新しい条件は既存記録を上書きせず、新しい実験フォルダへprotocolを先に固定し、ハーネスと検査を対応させる。現在の実行入口は凍結した条件専用であり、JSONだけ変えて異なる条件で走ったことにはしない。

## 公開用の再現入口を検証した範囲

公開用の構成で4 PNの対照・停止条件、入口ORNの116辺停止、PN出力の全正符号停止を各1試行、計4試行新規実行し、生記録の参照ハッシュ一致を確認した。4 PN全16試行の再集計は元のCSV・JSONとバイト一致。入口／出力の過去64試行の指標も公開用計算器で再計算して照合した。条件改変・未知条件・記録上書きの拒否検査も通過。これは全80試行を公開用入口から新規再実行したという意味ではない。記録は [reproduction-check.json](reproduction-check.json)。

`verify.py` は配布物・契約・判定表の整合性検査だけで、シミュレーションを実行しない。拒否動作は `.venv/bin/python -m unittest test_contract.py` で確認できる。

## エージェントに渡す小さい契約

渡す対象は、一実験の `protocol.json`、`cohorts.json`、`results/summary.csv`／`report.json` と `run(seed, gain, gate)` の実行契約で足りる。役割は条件違反の検査と、次の条件の事前記述。残留を見てOFFを決める規則、無記録の追加切断、集団平均から全細胞沈黙への読み替えは入れない。[詳細](AGENT_CONTRACT.md)。

出典・上流ライセンスは [NOTICE.md](NOTICE.md)。本ノートの主張は、上記の固定模型・刺激履歴・読み出し集団に限る。
