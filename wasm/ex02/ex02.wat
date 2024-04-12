(module
  ;; import the browser console object, you'll need to pass this in from JavaScript
  (import "console" "log" (func $log (param i32)))

  (func
    ;; create a local variable and initialize it to 0
    ;; 多重ループ
    (local $i i32)
    (local $j i32)

    (loop
      ;; add one to $i
      local.get $i
      i32.const 1
      i32.add
      local.set $i
      
      i32.const 0
      local.set $j
      ;; log the current value of $i
      (loop
        local.get $j
        i32.const 1
        i32.add
        local.set $j

        local.get $j
        local.get $i
        i32.mul
        call $log


        local.get $j
        i32.const 10
        i32.lt_s
        br_if 1
      )
      ;; if $i is less than 10 branch to loop
      local.get $i
      i32.const 10
      i32.lt_s
      br_if 0
    )
    (loop
      ;; add one to $i
      local.get $i
      i32.const 1
      i32.add
      local.set $i
      
      i32.const 0
      local.set $j
      ;; log the current value of $i
      (loop
        local.get $j
        i32.const 1
        i32.add
        local.set $j

        local.get $j
        local.get $i
        i32.mul
        call $log


        local.get $j
        i32.const 10
        i32.lt_s
        br_if 1
      )
      ;; if $i is less than 10 branch to loop
      local.get $i
      i32.const 10
      i32.lt_s
      br_if 0
    )
  )

  (start 1) ;; run the first function automatically
)
