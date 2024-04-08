(module
(func $stairs
(param $a i32)
(result i32)
(local $#rif i32)
i32.const 10
local.get $a
i32.lt_u
if
i32.const 2
return
else
i32.const 0
local.get $a
i32.lt_u
local.get $a
i32.const 10
i32.le_u
i32.and
if
i32.const 1
return
else
i32.const 0
return
end
end
unreachable
)
)