(module
    (import "console" "print3" (func $print3 (param i32 i32 i32)))
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

    (func $test01
    (result i32 i32)
    i32.const 10
    i32.const 10
    return
    )

(func $tarai
(param $x i32)
(param $y i32)
(param $z i32)
(result i32)
local.get $x
local.get $y
local.get $z
call $print3
local.get $x
local.get $y
i32.le_s
if (result i32)
local.get $y
else
local.get $x
i32.const 1
i32.sub
local.get $y
local.get $z
call $tarai
local.get $y
i32.const 1
i32.sub
local.get $z
local.get $x
call $tarai
local.get $z
i32.const 1
i32.sub
local.get $x
local.get $y
call $tarai
call $tarai
end
return
)
(func $up
(param $a i32)
(param $b i32)
(result i32 i32)
local.get $a
local.get $b
i32.le_u
if
local.get $a
local.get $b
return
else
local.get $b
local.get $a
return
end
unreachable
)
    (export "gcd" (func $gcd))
    (export "tarai" (func $tarai))
    (export "up" (func $up))
)