(module
(func $gcd
(param $a i32)
(param $b i32)
(result i32)
local.get $b
i32.eqz
if
local.get $a
return
else
local.get $b
local.get $a
local.get $b
i32.rem_u
call $gcd
return
end
unreachable
)
(func $gcd2
(param $a i32)
(param $b i32) 
(result i32)
(local $#rif i32)
local.get $b
i32.eqz
if
local.get $a
local.set $#rif
else
local.get $b
local.get $a
local.get $b
i32.rem_u
call $gcd2
local.set $#rif
end
local.get $#rif
return 
)
)