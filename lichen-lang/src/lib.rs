// # parser
//
//

struct Parser{
    code:String,
    //priority list(演算子優先度リスト)
    left_priority_list:Vec<(String,i32)>,
    right_priority_list:Vec<(String,i32)>,
    prefix_priority_list:Vec<(String,i32)>,
    plusminus_prefix_priority:i32,
}


impl Parser{
    fn new(&self,code:&str) -> Self{
        Self {
            code: code.to_string(),
            left_priority_list: vec![
                ("||".to_string(),-3),
                ("&&".to_string(),-2),
     
                ("==".to_string(),0),
                ("!=".to_string(),0),
                ("<".to_string(),0),
                (">".to_string(),0),
                ("<=".to_string(),0),
                (">=".to_string(),0),
     
                ("+".to_string(),1),
                ("-".to_string(),1),
            ],
            right_priority_list:vec![
                ("=".to_string(),-4),
                ("+=".to_string(),-4),
                ("-=".to_string(),-4),
                ("*=".to_string(),-4),
                ("/=".to_string(),-4),
                // pow
                ("**".to_string(),3),
            ],
            prefix_priority_list:vec![
                ("!".to_string(),-1)
            ],
            plusminus_prefix_priority:4
        }
    }

    fn resolve_quotation <T:Elem>(&self) -> Vec<T>{
        todo!()
    }
}


trait Elem {
    fn new(&self) -> Self where Self: Sized{
        todo!();
    }
    fn get_name(&self) -> String;
    fn get_contents(&self) -> Vec<String>;
}

struct String_Elem{

}

pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
