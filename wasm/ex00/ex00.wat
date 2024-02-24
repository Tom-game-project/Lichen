(module
    (func $gcd
        (param i32 i32)
        (result i32)
        (local i32)
        local.get 1
        i32.eqz
        if
            local.get 0
            local.tee 2
            drop
        else
            local.get 1
            local.get 0
            local.get 1
            i32.rem_u
            call $gcd
            local.tee 2
            drop
        end
        local.get 2
    )
    (export "gcd" (func $gcd))
)