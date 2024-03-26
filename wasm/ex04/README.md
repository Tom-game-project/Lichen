# 様々なバリエーションのif

以下に説明するプログラムはすべて仮想的な例に過ぎない

## 全集合的(網羅的)に処理できる場合...0

- 例1

```
if (expr1)
{
    ;;1
}else (!expr1)
{
    ;;2
}
```

```
expr1 + !expr1 = U
```
故に
;;1
;;2
のいずれかを**必ず**実行する

例2
```
if (expr1){
    ;;1
} elif (expr2) {
    ;;2
} else (!expr1 and !expr2) {
    ;;3
}
```

```
expr1 + expr2 + (!expr1 and !expr2)

= expr1 + expr2 + !(expr1 or expr2)

= (expr1 + expr2) + !(expr1 + expr2)

= U
```

故に
;;1
;;2
;;3のいずれかを**必ず**実行する

## 全集合的(網羅的)に処理できない場合...1
