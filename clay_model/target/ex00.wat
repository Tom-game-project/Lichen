(module
(func $add
(param $a i32)
(param $b i32)
(result i32)
local.get $a
local.get $b
i32.add
return
)
(func $sub
(param $a i32)
(param $b i32)
(result i32)
(local $c i32)
local.get $a
local.get $b
i32.sub
local.set $c
local.get $c
return
)
(func $main
(param $a i32)
(param $b i32)
(local $c i32)
(local $d i32)
i32.const 1
i32.const 2
call $add
local.set $c
local.get $a
local.get $b
local.get $c
local.get $d
i32.add
i32.mul
i32.div_u
local.set $d
local.get $c
i32.const 1
local.set $c
local.get $d
i32.const 42
i32.add
local.set $d
local.get $d
return
)
(export "sub" (func $sub))
(export "main" (func $main))
)