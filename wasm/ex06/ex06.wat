(module
    (import "console" "log" (func $console_log (param i64)))
    (import "js" "mem" (memory 1))
    (data (i32.const 0) "\ff\ff\ff\ff\00\00\00\00\ff\ff\ff\ff")
    (global $global_ptr i32 (i32.const 0))
    (func $main;; log first element
    (param $a i32)
    local.get $a
    i64.load32_u
    call $console_log
    )
    (export "main" (func $main))
)