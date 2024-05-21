(module
  (import "console" "print" (func $print (param i32) (param i32)))
  (import "js" "mem" (memory 1))
  (data (i32.const 0) "\00\01\00\00\02\00\00\00\ff\ff\ff\ff")
  ;; 0xffffffff == 2**32 - 1
  ;; 0xffffffffffffffff == 2**64 - 1
  (data (i32.const 12) "helloworld")
  ;;(memory (export "mem") 1 2)
  (func (export "sum") 
    (param $n i32);; 0からnまで足した
    (result i32)  ;; 合計
    (local $i i32)
    (local $ret i32)
    i32.const 0
    local.tee $ret
    local.set $i
    block $exit
      loop $cont
        local.get $i
        local.get $n
        i32.eq
        br_if $exit
        local.get $i
        i32.const 4
        i32.mul
        i32.load
        local.get $ret
        i32.add
        local.set $ret
        local.get  $i
        i32.const 1
        i32.add
        local.set  $i
        br $cont
      end
    end
    local.get $ret)
    (func
    (export "sayHello")
    i32.const 12
    i32.const 10
    call $print
    )
    ;; (func $showbite
    ;; (param $offset i32)
    ;; (param $length i32)
    ;; (local $i i32)
    ;; i32.const 0
    ;; local.set $i

    ;; )
)
