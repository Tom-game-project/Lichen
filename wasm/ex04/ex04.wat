(module
    (import "console" "log" (func $log (param i32)))

    ;; - else が存在している
    
    ;;   - すべての処理の中身がreturnで終わる場合
            ;; if (arg0){return 10;}else{return 0;}
            (func $if_expr_test00
            (param $arg0 i32)
            (result i32)
            local.get $arg0
            if
            i32.const 10
            return
            else
            i32.const 0
            return
            end
            ;; return i; #スタックに返り値を積む
            unreachable
            )

    ;;   - すべての処理の中身のすべてがexprである場合
            ;; return (if (arg0){return 10}else{0});
            (func $if_expr_test01
            (param $arg0 i32)
            (result i32)
            (local $#r00 i32)
            local.get $arg0
            if
            i32.const 10
            local.set $#r00
            else
            i32.const 0
            local.set $#r00
            end

            local.set $#r00
            return
            )
    
    ;;   - 上の場合に該当しない場合。例えば、returnがまざっている
            (func $if_expr_test02
            (param $arg0 i32)
            (result i32)
            (local $#r00 i32)
            local.get $arg0
            if
            i32.const 10
            local.set $#r00
            else
            i32.const 0
            local.set $#r00
            end
            local.set $#r00
            return
            )

    ;; - elseが存在していない場合
    (func $if_expr_test03
    (param $arg0 i32)
    (result i32)
    (local $i i32)
    ;; if (arg0){return 10}
    ;; return 0
    local.get $arg0
    if
    i32.const 10
    return
    end
    i32.const 0
    return
    )

    (func $if_expr_test04
    (param $arg0 i32)
    (param $arg1 i32)
    (result i32)
    ;; if (arg1) 
    ;; { return 10;}
    ;; elif(arg1)
    ;; { return 5;}
    ;; else
    ;; { 0;}
    ;; return 0;
    local.get $arg0
    if
        i32.const 10
        return
    else
    local.get $arg1
    if
        i32.const 5
        return 
    else
        i32.const 0
        drop
    end
    end
    i32.const 0
    return 
    )

    (func $if_expr_test05
    (param $arg0 i32)
    (param $arg1 i32)
    (result i32)
    ;; return if (arg0){10}elif (arg1) {5} else {0} + 1;
    (local $#if00 i32)
    local.get $arg0
    if
        i32.const 10
        local.set $#if00
    else
    local.get $arg1
    if
        i32.const 5
        local.set $#if00
    else
        i32.const 0
        local.set $#if00
    end
    end
    local.get $#if00
    i32.const 1
    return
    )

    (func $main
    i32.const 1
    call $if_expr_test00
    call $log ;; console log 10
    )
    (start $main)
)