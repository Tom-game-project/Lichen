(module
    (func $gcd
    ;; 基本的な関数
        (param i32 i32)
        (result i32)
        (local i32)
        local.get 1
        i32.eqz
        if
            local.get 0
            local.tee 2
            drop
        else
            local.get 1
            local.get 0
            local.get 1
            i32.rem_u
            call $gcd
            local.tee 2
            drop
        end
        local.get 2
    )

    (func $test00
    (result i32)
    (local $a i32)
    
    ;; ローカル変数への代入
    i32.const 10
    local.set $a

    ;; ローカル変数の取得
    ;; 変数に格納した値をスタックに積む
    local.get $a
    return ;; スタックに積んだ変数を返却
    )
    (export "gcd" (func $gcd))
)