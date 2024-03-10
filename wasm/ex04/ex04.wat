(module
    (import "console" "log" (func $log (param i32)))
    (func $if_expr_test
    (param $arg0 i32)
    (result i32)
    (local $i i32)
    local.get $arg0
    if
    i32.const 10
    local.set $i
    else
    i32.const 0
    local.set $i
    end
    local.get $i
    return
    )
    (func $main
    i32.const 1
    call $if_expr_test
    call $log ;; console log 10
    )
    (start $main)
)