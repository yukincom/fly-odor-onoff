# 実行API

`experiment.run()` は指定した実験条件を再実行し、指標と参照記録との照合結果をJSON互換の辞書で返す。

```python
from experiment import run

result = run(2026091701, 1.0, "known_positive")
```

## 引数

| 引数 | 内容 |
|---|---|
| `seed` | protocolに収録した4つの乱数seedのいずれか |
| `gain` | 刺激頻度の倍率。`1.0`または`0.5` |
| `gate` | 実験ごとの入力遮断条件 |
| `experiment` | 既定値は`brain-four-pn-readout`。`brain-orn-entry`、`brain-pn-output`も指定可能 |
| `upstream` | 固定commitの模型checkout。既定はリポジトリ直下の`upstream/` |
| `jdk` | Java 25の`bin`ディレクトリ。省略時は`JAVA_HOME`またはPATHから取得 |
| `out` | 新規の出力ディレクトリ。省略時は`runs/`以下に一意の名前で作成 |

`gain`は刺激に適用され、回路側の`cfg.gain=0.65`とは別のパラメータである。結果ファイルの`hungry`／`satiated`はそれぞれ入力利得1.0／0.5の条件ラベルを表す。

4 PNの`known_positive`条件では、同じseed・入力利得の`control`も実行して対照比を計算する。他の指定では1呼出しにつき1条件を実行する。

## 出力

返り値の項目は `experiment, seed, gain, gate, protocol_sha256, metrics, replay_verification`。同じ内容を出力ディレクトリの`indicators.json`へ保存する。

- `metrics`：実行結果から計算した発火率・対照比・判定。
- `protocol_sha256`：使用した実験条件のハッシュ。
- `replay_verification`：参照記録とバイト一致したファイル数・SHA256。

生記録と実行ログも出力先に保存される。`runs/`はGit管理の対象外。

## 条件と評価

各実験の`protocol.json`に刺激・観測窓・遮断規則を、`cohorts.json`に観測集団を収録している。4 PN実験では、刺激のON／OFFは固定時刻表から与えられる。観測する4 PNと、入力遮断先の全686 ALPNは異なる集合である。

ピーク比70%以上、後半比30%以上、停止後平均3 Hz以下を参考基準として評価する。個別4細胞の0 Hzと、停止後1秒以降の全区間無発火は別の項目として返す。閾値の詳細は各protocolを参照。

## エラーと検証

この実行器は収録済みの条件に対応する。未登録のseed・利得・遮断条件、変更されたprotocolや計測コード、既存の出力先を指定すると、シミュレーション開始前にエラーとなる。再実行した生記録が参照ハッシュと異なる場合もエラーを返す。

別条件の実験には、その条件を記した新しいprotocolと、対応するハーネス・検証処理が必要になる。

```sh
.venv/bin/python verify.py
.venv/bin/python -m unittest test_contract.py
```

`verify.py`は配布ファイル・条件・判定表の整合性を、`test_contract.py`は入力検証と上書き防止を確認する。いずれもシミュレーション自体は実行しない。
