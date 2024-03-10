(module
    (import "console" "log" (func $log (param i32)))

    (func $while10
        ;;while loop example
        (local $i i32)
        ;; let i = 0;
        i32.const 0
        local.set $i
        (loop $#l0
            (block $#b0
                ;;while (i < 10)
                local.get $i
                i32.const 10
                i32.lt_u
                if
                nop
                else
                br $#b0 ;; end of loop
                end
                ;; ここに処理を書く
                local.get $i
                call $log
                ;; i += 1
                local.get $i
                i32.const 1
                i32.add
                local.set $i
            br $#l0)
        )
    )

    (func $while10_break_test
        ;;while loop example
        (local $i i32)
        ;; let i = 0;
        i32.const 0
        local.set $i
        (loop $#l0
            (block $#b0
                ;;while (i < 10)
                local.get $i
                i32.const 10
                i32.lt_u
                if
                nop
                else
                br $#b0 ;;end of loop
                end
                ;; ここに処理を書く
                local.get $i
                call $log
                ;; i += 1
                local.get $i
                i32.const 1
                i32.add
                local.set $i
            br $#l0)
        )  
    )

    (func $while10_continue_test
        ;;while loop example
        (local $i i32)
        ;; let i = 0;
        i32.const 0
        local.set $i
        (loop $#l0
            (block $#b0
                ;;while (i < 10)
                local.get $i
                i32.const 10
                i32.lt_u
                if
                nop
                else
                br $#b0
                end
                ;; ここに処理を書く

                
                local.get $i

                ;; i += 1
                local.get $i
                i32.const 1
                i32.add
                local.set $i
                
                local.get $i
                i32.const 2
                i32.rem_u
                i32.eqz
                if;; i%2 == 0
                local.get $i
                call $log
                else
                nop
                end
                br $#l0
            )
        )  
    )

    (func $main
        call $while10
    )
    (start $main)
)