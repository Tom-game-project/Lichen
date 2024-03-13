// # parser
//
//

struct Parser{
    code:String,
    //priority list(演算子優先度リスト)
    left_priority_list: Vec<(String,i32)>,
    right_priority_list: Vec<(String,i32)>,
    prefix_priority_list: Vec<(String,i32)>,
    plusminus_prefix_priority:i32,
}



impl Parser{ 
    fn new(code:&str) -> Self{
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

    fn resolve_quotation(&self,code:String,quo_char:char) -> Vec<ParseElem>{
        let mut open_flag = false;
        let mut escape_flag = false;
        let mut rlist:Vec<ParseElem> = Vec::new();
        let mut group:Vec<char> = Vec::new();
        let mut newline_counter:usize = 0;
        let mut column_counter:usize = 0;

        for i in code.chars().into_iter(){
            if i == '\n'{
                column_counter = 0;
                newline_counter += 1;
            }else{
                column_counter += 1
            }

            if escape_flag{
                group.push(i);
                escape_flag = false;
            }else{
                if i == quo_char{
                    if open_flag{
                        group.push(i);
                        let se = StringElem::new(
                            group
                            .clone()
                            .into_iter()
                            .collect()
                        );
                        rlist.push(
                            ParseElem::StringParseElem(se)
                        );
                        group.clear();
                        open_flag = false;
                    }else{
                        group.push(i);
                        open_flag = true;
                    }
                }else{
                    if open_flag{
                        if i == '\\'{
                            escape_flag = true;
                        }else{
                            escape_flag = false;
                        }
                        group.push(i);
                    }else{
                        let ue = UndefElem::new(i.clone().to_string());
                        rlist.push(ParseElem::UndefParseElem(ue));
                    }
                }
            }
        }
        return rlist;
    }

    fn grouping_elements(&self,codelist:Vec<ParseElem>,open_char:String,close_char:String,object_mode:&str) -> Result<Vec<ParseElem>,&str>{
        // object_mode : block | paren | list
        //
        let mut rlist:Vec<ParseElem> = Vec::new();
        let mut group:Vec<ParseElem> = Vec::new();
        let mut depth:usize = 0;

        for i in codelist{
            match i {
                ParseElem::UndefParseElem(v) => {
                    // 不定objectだった場合
                    if v.contents == open_char{
                        if depth > 0 {
                            group.push(ParseElem::UndefParseElem(v));
                        }else if depth == 0 {
                            //pass
                        }else {
                            return Err("Error!");
                        }
                        depth += 1;
                    }else if v.contents == close_char {
                        depth -= 1;
                        if depth > 0{
                            group.push(ParseElem::UndefParseElem(v));
                        }else if depth == 0 {
                            if object_mode == "block"{
                                let be = BlockElem::new(group);
                                rlist.push(ParseElem::BlockParseElem(be));
                            }else if  object_mode == "list"{
                                let le = ListBlockElem::new(group);
                                rlist.push(ParseElem::ListBlockParseElem(le));
                            }else if object_mode == "paren"{
                                let pe = ParenBlockElem::new(group);
                                rlist.push(ParseElem::ParenBlockParseElem(pe));
                            }else{
                                return Err("invalid object_mode");
                            }
                            group.clear();
                        }else{
                            return Err("Error!");
                        }
                    }else{
                        if depth > 0 {
                            group.push(ParseElem::UndefParseElem(v));
                        }else if depth == 0 {
                            let ue = UndefElem::new(v.contents.clone().to_string());
                            rlist.push(ParseElem::UndefParseElem(ue));
                        }else{
                            return Err("Error!");
                        }
                    }
                }
                _ => {
                    //それ以外の場合
                    // ここでは文字列の場合、そのまま返却する
                    //
                }
            }
        }
        return Ok(rlist);
    }
}

/// # 列挙型
/// 


/// # 前要素共通メソッド
///
trait Elem{

}


/// # UndefElem
/// ## 不定な型

struct UndefElem{
    contents:String
}
impl UndefElem{
    // UndefElem 
    // returns
    // contents -> String
    fn new(contents:String) -> Self{
        Self{
            contents:contents
        }
    }
}
impl Elem for UndefElem{}


struct BlockElem{
    contents:Vec<ParseElem>
}
impl BlockElem{
    fn new(contents:Vec<ParseElem>)->Self{
        Self { contents: contents }
    }
}
impl Elem for BlockElem{}


struct ListBlockElem{
    contents:Vec<ParseElem>
}
impl ListBlockElem{
    fn new(contents:Vec<ParseElem>)->Self{
        Self { contents: contents }
    }
}
impl Elem for ListBlockElem{}


struct ParenBlockElem{
    contents:Vec<ParseElem>
}
impl ParenBlockElem{
    fn new(contents:Vec<ParseElem>)->Self{
        Self { contents: contents }
    }
}
impl Elem for ParenBlockElem{}

/// # StringElem
/// ## 文字列
struct StringElem{
    contents:String
}
impl StringElem{
    fn new(contents:String) -> Self{
        Self{
            contents:contents
        }
    }
}
impl Elem for StringElem{}

/// # WordElem
/// ## 単語を格納
struct WordElem{
    contents:String
}
impl WordElem{
    fn new(contents:String) -> Self{
        Self{
            contents:contents
        }
    }
}
impl Elem for WordElem{}



/// # プログラムの要素
enum ParseElem{
    StringParseElem(StringElem),
    WordParseElem(WordElem),
    UndefParseElem(UndefElem),
    //Block
    BlockParseElem(BlockElem),
    ParenBlockParseElem(ParenBlockElem),
    ListBlockParseElem(ListBlockElem),
}
impl ParseElem{
    fn show(&self){
        match self{
            ParseElem::StringParseElem(v) => {
                println!("<string: {}>",v.contents);
            }
            ParseElem::WordParseElem(v) => {
                println!("<word: {}>",v.contents);
            }
            ParseElem::UndefParseElem(v) => {
                println!("{}",v.contents);
            }
            ParseElem::BlockParseElem(v) => {
                println!("<Block>");
            }
            ParseElem::ListBlockParseElem(v) => {
                println!("<List>");
            }
            ParseElem::ParenBlockParseElem(v) => {
                println!("<Paren>");
            }
        }
    }
}



#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_00() {
        let code = "a = \"hello world\";".to_string();
        let mut parser = Parser::new(&code);
        let codelist=parser.resolve_quotation(code, '"');
        for i in codelist{
            i.show();
        }
    }
}