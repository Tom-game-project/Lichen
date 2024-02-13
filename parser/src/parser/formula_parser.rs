

struct Parser<'a>
{
    code :String,
    operator_precedence :Vec<(&'a str,i32)>,

}


impl Parser<'_>
{

    fn new(self,code:String) -> Self
    {
        return Self{
            code : code,
            operator_precedence : vec![
                ("||", -2),
                ("&&", -1),
                ("==", 0),
                ("!=", 0),
                ("<", 0),
                (">", 0),
                ("<=", 0),
                (">=", 0),
                ("+", 1),
                ("-", 1),
                ("*", 2),
                ("/", 2),
                ("%", 2),
                ("^", 3),
                ("**", 3),
            ]
        }

    }

    fn grouping_number(self, strlist:String) -> Vec<String>
    {
        let mut rlist :Vec<String>= Vec::new();
        let mut group :Vec<String>= Vec::new();
        let mut flag:bool = false;

        for i in strlist.chars()
        {
            if  ('A' <= i && i <= 'Z') || //対応する文字
                ('a' <= i && i <= 'z') ||
                ('0' <= i && i <='9')
            {
                group.push(i.to_string());
                flag = true;
            }
            else
            {
                if flag
                {
                    rlist.push(group.join(""));
                    group.clear();
                    flag = false;
                }
                rlist.push(i.to_string());
            }
        }
        return rlist;
    }

    fn grouping_brackets(self, strlist:Vec<String>) ->Vec<String>
    {
        let mut rlist:Vec<String> =Vec::new();
        let mut group:Vec<String> =Vec::new();
        let mut depth:i32 = 0;
        let mut flag:bool = false;

        for i in strlist
        {
            if i == "("
            {
                if depth > 0
                {
                    group.push(i);
                }
                else if depth == 0 {
                    group.push(i);
                }
                else
                {
                    //error
                }
                depth += 1;
            }
            else if i == ")"
            {
                depth -= 1;
                if depth > 0
                {
                    group.push(i);
                }
                else if depth == 0
                {
                    group.push(i);
                    rlist.push(group.join(""));
                    group.clear();
                }
            }
            else
            {
                if flag
                {
                    group.push(i);
                }
                else {
                    rlist.push(i);
                }
            }
        }
        return rlist;
    }

    fn is_symbol(self, index:i32,strlist:Vec<String>) -> (bool,str,i32)
    {
        let size = strlist.len();
        
    }
}
