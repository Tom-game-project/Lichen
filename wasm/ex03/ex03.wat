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
                br $#l0
            )
        )
    )

    (func $while10_test00
        ;; br_if を使用したループ
        (local $i i32)
        i32.const 0
        local.set $i
        (block $block00
            (loop $loop00
                local.get $i
                i32.const 10
                i32.gt_u
                br_if $block00
                local.get $i
                call $log
                ;; i += 1
                local.get $i
                i32.const 1
                i32.add
                local.set $i
                br $loop00
            )
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
                br $#l0
            )
        )  
    )

    (func $while10_break_test2
        ;;while loop example
        (local $i i32)
        (local $j i32)
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
                (loop $#l1
                    (block $#b1
                        ;;while (j < 10)
                        local.get $j
                        i32.const 10
                        i32.lt_u
                        if
                        nop
                        else
                        br $#b1 ;;end of loop
                        end
                        ;; ここに処理を書く
                        local.get $j
                        call $log
                        ;; j += 1
                        local.get $j
                        i32.const 1
                        i32.add
                        local.set $j
                        br $#l1
                    )
                )
                ;; i += 1
                local.get $i
                i32.const 1
                i32.add
                local.set $i
                br $#l0
            )
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
                br $#l0;; loopのcontinueに相当する
            )
        )  
    )
    (func $while10_continue_test0
        (block ;;1
            (loop ;;0
                i32.const 10
                local.get $t
                i32.eq
                br_if 1
                local.get $t
                i32.const 1
                i32.add 
                local.set $t
                br 0
            )
        )
    )

    (func $main
        call $while10_test00
    )
    (start $main)
)