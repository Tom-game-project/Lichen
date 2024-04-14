(module
(import "console" "logI32" (func $logI32 (param i32)))
(import "console" "logI32I32" (func $logI32I32 (param i32 i32)))
(func $main
(local $i i32)
(local $j i32)
i32.const 0
local.set $i
(loop $#loop0
(block $#block0
local.get $i
i32.const 10
i32.lt_s
if
nop
else
br $#block0 
end
i32.const 0
local.set $j
(loop $#loop1
(block $#block1
local.get $j
i32.const 10
i32.lt_s
if
nop
else
br $#block1 
end
local.get $i
local.get $j
call $logI32I32
local.get $j
i32.const 1
i32.add
local.set $j
br $#loop1 
))local.get $i
i32.const 1
i32.add
local.set $i
br $#loop0 
)))
(func $main2
(local $i i32)
i32.const 0
local.set $i
(loop $#loop0
(block $#block0
local.get $i
i32.const 10
i32.lt_s
if
nop
else
br $#block0 
end
local.get $i
call $logI32
local.get $i
i32.const 1
i32.add
local.set $i
br $#loop0 
))i32.const 0
local.set $i
(loop $#loop0
(block $#block0
local.get $i
i32.const 10
i32.lt_s
if
nop
else
br $#block0 
end
local.get $i
call $logI32
local.get $i
i32.const 1
i32.add
local.set $i
br $#loop0 
)))
(export "main" (func $main))
(export "main2" (func $main2))
)