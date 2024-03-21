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

    fn resolve_quotation(&self,code:String,quo_char:char) -> Result<Vec<ParseElem>,&str>{
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
        return Ok(rlist);
    }

    fn grouping_elements(&self,codelist:Vec<ParseElem>,open_char:&str,close_char:&str,object_mode:&str) -> Result<Vec<ParseElem>,&str>{
        // object_mode : block | paren | list
        //
        let mut rlist:Vec<ParseElem> = Vec::new();
        let mut group:Vec<ParseElem> = Vec::new();
        let mut depth:usize = 0;

        for i in codelist{
            match i {
                ParseElem::UndefParseElem(v) => {
                    // 不定objectだった場合
                    if v.contents == open_char.to_string(){
                        if depth > 0 {
                            group.push(ParseElem::UndefParseElem(v));
                        }else if depth == 0 {
                            //pass
                        }else {
                            return Err("Error!");
                        }
                        depth += 1;
                    }else if v.contents == close_char.to_string() {
                        depth -= 1;
                        if depth > 0{
                            group.push(ParseElem::UndefParseElem(v));
                        }else if depth == 0 {
                            // type によって異なる型
                            if object_mode == "block"{
                                let be = BlockElem::new(group.clone());
                                rlist.push(ParseElem::BlockParseElem(be));
                            }else if  object_mode == "list"{
                                let le = ListBlockElem::new(group.clone());
                                rlist.push(ParseElem::ListBlockParseElem(le));
                            }else if object_mode == "paren"{
                                let pe = ParenBlockElem::new(group.clone());
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
                    if depth > 0 {
                        group.push(i);
                    }else if depth == 0 {
                        rlist.push(i);
                    }else{
                        return Err("Error!");
                    }
                }
            }
        }
        return Ok(rlist);
    }

    fn grouping_words(&self)->Result<Vec<ParseElem>,&str>{
        todo!();
    }

    fn code2vec(&self) -> Result<Vec<ParseElem>,&str>{
        let mut codelist = self.resolve_quotation(self.code.clone(),'"');
        if codelist.is_err() {return codelist}
        codelist = self.grouping_elements(codelist.unwrap(), "{", "}", "block");
        if codelist.is_err() {return codelist}
        codelist = self.grouping_elements(codelist.unwrap(), "(", ")", "paren");
        if codelist.is_err() {return codelist}
        codelist = self.grouping_elements(codelist.unwrap(), "[", "]", "list");
        return codelist;
    }
}


/// # 前要素共通メソッド
///
trait Elem{

}


/// # UndefElem
/// ## 不定な型

#[derive(Clone)]
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


#[derive(Clone)]
struct BlockElem{
    contents:Vec<ParseElem>
}
impl BlockElem{
    fn new(contents:Vec<ParseElem>)->Self{
        Self { contents: contents }
    }
}
impl Elem for BlockElem{}


#[derive(Clone)]
struct ListBlockElem{
    contents:Vec<ParseElem>
}
impl ListBlockElem{
    fn new(contents:Vec<ParseElem>)->Self{
        Self { contents: contents }
    }
}
impl Elem for ListBlockElem{}


#[derive(Clone)]
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
#[derive(Clone)]
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
#[derive(Clone)]
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
#[derive(Clone)]
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
    fn show_all(&self)->String{
        match self{
            ParseElem::StringParseElem(v) => {
                let mut r_string = String::new();
                r_string.push_str("<String :");
                r_string.push_str( &v.contents);
                r_string.push_str(">");
                r_string
            }
            ParseElem::WordParseElem(v) => {
                let mut r_string = String::new();
                r_string.push_str("<Word :");
                r_string.push_str( &v.contents);
                r_string.push_str(">");
                r_string
            }
            ParseElem::UndefParseElem(v) => {
                // undef
                let mut r_string = String::new();
                r_string.push_str("<Undef :");
                r_string.push_str( &v.contents);
                r_string.push_str(">");
                r_string
            }
            ParseElem::BlockParseElem(v) => {
                let mut inner_list = Vec::new();
                let mut r_string:String = String::new();
                for i in &v.contents{
                    inner_list.push(i.show_all());
                }
                r_string.push_str("<Block :");
                r_string.push_str(&inner_list.join("\n"));
                r_string.push_str(">");
                r_string
            }
            ParseElem::ListBlockParseElem(v) => {
                let mut inner_list = Vec::new();
                let mut r_string:String = String::new();
                for i in &v.contents{
                    inner_list.push(i.show_all());
                }
                r_string.push_str("<List :");
                r_string.push_str(&inner_list.join("\n"));
                r_string.push_str(">");
                r_string
            }
            ParseElem::ParenBlockParseElem(v) => {
                let mut inner_list = Vec::new();
                let mut r_string:String = String::new();
                for i in &v.contents{
                    inner_list.push(i.show_all());
                }
                r_string.push_str("<Paren :");
                r_string.push_str(&inner_list.join("\n"));
                r_string.push_str(">");
                r_string
            }
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_00() {
        /// # code2vec test
        /// 
        let code = "{a = \"hello world\";}".to_string();
        let parser = Parser::new(&code);
        let codelist = parser.code2vec();
        match codelist {
            Ok(v)=>{
                for i in v{
                    println!("{}",i.show_all());
                }
            }
            Err(e)=>{
                println!("{}",e);
            }
        }
    }

    #[test]
    fn test_01() {

    }
}